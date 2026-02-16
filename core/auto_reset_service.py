import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from core.task_manager import TaskManager
from config.settings import settings
from utils.logger import logger
from utils.exceptions import DatabaseError

# 集中管理常量
DEFAULT_DAILY_RESET_TIME = "06:00"
DEFAULT_WEEKLY_RESET_WEEKDAY = 0  # 0=周一
CHECK_INTERVAL_HOUR = 3600  # 每小时检查一次（秒）


class AutoResetService(QObject):
    """自动重置服务"""
    
    # 信号定义
    daily_reset_performed = pyqtSignal(int)  # 重置的任务数量
    weekly_reset_performed = pyqtSignal(int)  # 重置的任务数量
    service_started = pyqtSignal()
    service_stopped = pyqtSignal()
    
    def __init__(self, task_manager: Optional[TaskManager] = None):
        super().__init__()
        
        # 初始化任务管理器
        self.task_manager = task_manager or TaskManager()
        
        # 服务状态
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self._lock = threading.Lock()  # 线程安全锁
        
        # 重置状态跟踪
        self._last_daily_reset_date: Optional[datetime] = None
        self._last_weekly_reset_week: Optional[int] = None
        
        # 加载上次重置状态
        self._load_last_reset_state()
        
        # Qt 析构处理（替代 __del__）
        self.destroyed.connect(self.stop)
    
    def _parse_reset_time(self, time_str: str) -> Tuple[int, int]:
        """
        通用方法：解析重置时间字符串为小时和分钟
        
        Args:
            time_str: 时间字符串（HH:MM 格式）
            
        Returns:
            Tuple[int, int]: 小时、分钟
            
        Raises:
            ValueError: 时间格式无效
        """
        try:
            hour, minute = map(int, time_str.split(":"))
            if not (0 <= hour < 24 and 0 <= minute < 60):
                raise ValueError(f"无效的时间值：{hour}:{minute}")
            return hour, minute
        except (ValueError, AttributeError) as e:
            raise ValueError(f"时间格式解析失败（预期 HH:MM）：{time_str}") from e
    
    def _calculate_reset_time(self, current_time: datetime, reset_time_str: str) -> datetime:
        """通用方法：计算指定日期的重置时间"""
        reset_hour, reset_minute = self._parse_reset_time(reset_time_str)
        return current_time.replace(
            hour=reset_hour, 
            minute=reset_minute, 
            second=0, 
            microsecond=0
        )
    
    def _load_last_reset_state(self):
        """加载上次重置状态"""
        try:
            with self._lock:  # 加锁保证线程安全
                last_daily = self.task_manager.repository.get_app_state("last_daily_reset")
                last_weekly = self.task_manager.repository.get_app_state("last_weekly_reset")
                
                if last_daily:
                    self._last_daily_reset_date = datetime.fromisoformat(last_daily)
                
                if last_weekly:
                    self._last_weekly_reset_week = int(last_weekly)
                    
        except ValueError as e:
            logger.error(f"重置状态解析失败（格式错误）：{e}")
        except DatabaseError as e:
            logger.error(f"数据库读取失败：{e}")
        except Exception as e:
            logger.error(f"加载上次重置状态失败: {e}")
    
    def _save_last_reset_state(self):
        """保存上次重置状态"""
        try:
            with self._lock:  # 加锁保证线程安全
                if self._last_daily_reset_date:
                    self.task_manager.repository.set_app_state(
                        "last_daily_reset", 
                        self._last_daily_reset_date.isoformat()
                    )
                
                if self._last_weekly_reset_week is not None:
                    self.task_manager.repository.set_app_state(
                        "last_weekly_reset", 
                        str(self._last_weekly_reset_week)
                    )
                    
        except DatabaseError as e:
            logger.error(f"数据库写入失败：{e}")
        except Exception as e:
            logger.error(f"保存上次重置状态失败: {e}")
    
    @pyqtSlot()
    def start(self):
        """启动自动重置服务"""
        with self._lock:
            if self.is_running:
                logger.warning("自动重置服务已经在运行")
                return
            
            self.is_running = True
            self.stop_event.clear()
        
        # 创建并启动线程
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        logger.info("自动重置服务已启动")
        self.service_started.emit()
    
    @pyqtSlot()
    def stop(self):
        """停止自动重置服务"""
        with self._lock:
            if not self.is_running:
                return
            
            self.is_running = False
            self.stop_event.set()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("自动重置服务已停止")
        self.service_stopped.emit()
    
    def _run(self):
        """服务主循环（优化：启动时检测一次，然后每小时检测一次）"""
        logger.info("自动重置服务线程启动")
        
        # 启动时立即检查一次
        try:
            self._check_and_perform_resets()
        except Exception as e:
            logger.error(f"启动时重置检查失败: {e}")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # 每小时检查一次
                self.stop_event.wait(timeout=CHECK_INTERVAL_HOUR)
                
                if self.is_running and not self.stop_event.is_set():
                    self._check_and_perform_resets()
                
            except Exception as e:
                logger.error(f"自动重置服务运行错误: {e}")
                # 出错后等待1小时再继续
                self.stop_event.wait(timeout=CHECK_INTERVAL_HOUR)
    
    def _calculate_next_check_seconds(self) -> int:
        """计算下次检查的间隔秒数（固定为1小时）"""
        return CHECK_INTERVAL_HOUR
    
    def _check_and_perform_resets(self):
        """检查并执行重置"""
        try:
            # 检查是否启用自动重置
            auto_reset_enabled = settings.get("task.auto_reset_enabled", True)
            if not auto_reset_enabled:
                return
            
            current_time = datetime.now()
            
            # 检查日常重置
            self._check_daily_reset(current_time)
            
            # 检查周常重置
            self._check_weekly_reset(current_time)
            
        except Exception as e:
            logger.error(f"检查重置失败: {e}")
    
    def _check_daily_reset(self, current_time: datetime):
        """检查日常重置"""
        try:
            # 获取重置时间设置
            reset_time_str = settings.get("task.daily_reset_time", DEFAULT_DAILY_RESET_TIME)
            
            # 计算今天的重置时间
            reset_time_today = self._calculate_reset_time(current_time, reset_time_str)
            
            # 线程安全读取状态
            with self._lock:
                last_daily_reset_date = self._last_daily_reset_date
            
            # 判断是否需要重置
            reset_needed = (
                current_time >= reset_time_today and
                (last_daily_reset_date is None or last_daily_reset_date.date() < current_time.date())
            )
            
            if reset_needed:
                # 执行日常重置
                reset_count = self.task_manager.perform_daily_reset()
                
                if reset_count > 0:
                    with self._lock:
                        self._last_daily_reset_date = current_time
                    self._save_last_reset_state()
                    self.daily_reset_performed.emit(reset_count)
                    logger.info(f"自动日常重置完成: 重置了{reset_count}个任务")
                
        except ValueError as e:
            logger.error(f"日常重置时间解析失败：{e}")
        except Exception as e:
            logger.error(f"检查日常重置失败: {e}")
    
    def _check_weekly_reset(self, current_time: datetime):
        """检查周常重置"""
        try:
            # 获取重置星期设置（0=星期一）
            reset_weekday = settings.get("task.weekly_reset_day", DEFAULT_WEEKLY_RESET_WEEKDAY)
            current_weekday = current_time.weekday()
            current_week = current_time.isocalendar()[1]
            
            # 线程安全读取状态
            with self._lock:
                last_weekly_reset_week = self._last_weekly_reset_week
            
            # 判断是否需要重置
            reset_needed = (
                current_weekday == reset_weekday and
                (last_weekly_reset_week is None or last_weekly_reset_week < current_week)
            )
            
            if reset_needed:
                # 执行周常重置
                reset_count = self.task_manager.perform_weekly_reset(reset_weekday)
                
                if reset_count > 0:
                    with self._lock:
                        self._last_weekly_reset_week = current_week
                    self._save_last_reset_state()
                    self.weekly_reset_performed.emit(reset_count)
                    logger.info(f"自动周常重置完成: 星期{reset_weekday}, 重置了{reset_count}个任务")
                
        except Exception as e:
            logger.error(f"检查周常重置失败: {e}")
    
    def force_daily_reset(self) -> int:
        """强制执行日常重置"""
        try:
            reset_count = self.task_manager.perform_daily_reset()
            
            if reset_count > 0:
                with self._lock:
                    self._last_daily_reset_date = datetime.now()
                self._save_last_reset_state()
                self.daily_reset_performed.emit(reset_count)
                logger.info(f"强制日常重置完成: 重置了{reset_count}个任务")
            
            return reset_count
            
        except Exception as e:
            logger.error(f"强制日常重置失败: {e}")
            return 0
    
    def force_weekly_reset(self) -> int:
        """强制执行周常重置"""
        try:
            reset_weekday = settings.get("task.weekly_reset_day", DEFAULT_WEEKLY_RESET_WEEKDAY)
            reset_count = self.task_manager.perform_weekly_reset(reset_weekday)
            
            if reset_count > 0:
                current_week = datetime.now().isocalendar()[1]
                with self._lock:
                    self._last_weekly_reset_week = current_week
                self._save_last_reset_state()
                self.weekly_reset_performed.emit(reset_count)
                logger.info(f"强制周常重置完成: 重置了{reset_count}个任务")
            
            return reset_count
            
        except Exception as e:
            logger.error(f"强制周常重置失败: {e}")
            return 0
    
    def get_status(self) -> dict:
        """获取服务状态"""
        with self._lock:
            return {
                "is_running": self.is_running,
                "last_daily_reset": self._last_daily_reset_date.isoformat() if self._last_daily_reset_date else None,
                "last_weekly_reset_week": self._last_weekly_reset_week,
                "next_daily_reset": self._get_next_daily_reset_time(),
                "next_weekly_reset": self._get_next_weekly_reset_time()
            }
    
    def _get_next_daily_reset_time(self) -> Optional[str]:
        """获取下次日常重置时间"""
        try:
            reset_time_str = settings.get("task.daily_reset_time", DEFAULT_DAILY_RESET_TIME)
            current_time = datetime.now()
            reset_time_today = self._calculate_reset_time(current_time, reset_time_str)
            
            if current_time < reset_time_today:
                return reset_time_today.isoformat()
            else:
                reset_time_tomorrow = reset_time_today + timedelta(days=1)
                return reset_time_tomorrow.isoformat()
                
        except Exception as e:
            logger.error(f"计算下次日常重置时间失败: {e}")
            return None
    
    def _get_next_weekly_reset_time(self) -> Optional[str]:
        """获取下次周常重置时间"""
        try:
            reset_weekday = settings.get("task.weekly_reset_day", DEFAULT_WEEKLY_RESET_WEEKDAY)
            current_time = datetime.now()
            current_weekday = current_time.weekday()
            current_week = current_time.isocalendar()[1]
            
            # 计算距离下次重置还有多少天
            days_until_reset = (reset_weekday - current_weekday) % 7
            
            with self._lock:
                last_weekly_reset_week = self._last_weekly_reset_week
            
            # 如果今天是重置日但已完成本周重置，顺延到下周
            if days_until_reset == 0 and last_weekly_reset_week == current_week:
                days_until_reset = 7
            
            next_reset_date = current_time + timedelta(days=days_until_reset)
            next_reset_date = next_reset_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            return next_reset_date.isoformat()
            
        except Exception as e:
            logger.error(f"计算下次周常重置时间失败: {e}")
            return None