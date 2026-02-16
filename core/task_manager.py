import re
from typing import List, Dict, Optional, TypedDict, Tuple
from datetime import datetime, date
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from data.repository import TaskRepository
from data.models import TaskSection
from utils.logger import logger
from utils.exceptions import DatabaseError

# 常量定义
DEFAULT_DAILY_RESET_TIME = "06:00"

# 类型提示增强
class TaskStats(TypedDict):
    pending: int
    completed: int

class SectionStats(TypedDict):
    sections: Dict[str, TaskStats]
    total: Dict[str, int]

class TagInfo(TypedDict):
    id: int
    name: str
    task_count: int

class TaskDict(TypedDict):
    id: int
    title: str
    section: str
    description: str
    requirements: str
    priority: int
    is_completed: bool
    due_date: Optional[str]
    reset_weekday: Optional[int]
    reset_time: Optional[str]
    sort_order: int
    tags: List[str]
    completed_at: Optional[str]


class TaskManager(QObject):
    """任务管理器，业务逻辑层"""
    
    # 信号定义
    task_added = pyqtSignal(int)  # task_id
    task_updated = pyqtSignal(int)  # task_id
    task_deleted = pyqtSignal(int)  # task_id (软删除)
    task_restored = pyqtSignal(int)  # task_id
    task_permanent_deleted = pyqtSignal(int)  # task_id
    task_completed = pyqtSignal(int)  # task_id
    task_uncompleted = pyqtSignal(int)  # task_id
    daily_reset_performed = pyqtSignal(int)  # count
    weekly_reset_performed = pyqtSignal(int)  # count
    tags_updated = pyqtSignal()
    recycle_bin_updated = pyqtSignal()
    
    def __init__(self, db_path: str = "data.db", repository: Optional[TaskRepository] = None):
        """
        初始化任务管理器
        
        Args:
            db_path: 数据库文件路径
            repository: 任务仓库实例（用于依赖注入，方便测试）
        """
        super().__init__()
        self.repository = repository or TaskRepository(db_path)
        logger.info("任务管理器初始化完成")
    
    # ========== 通用匹配方法 ==========
    def _match_text(self, text: str, keyword: str, mode: str = "fuzzy") -> bool:
        """
        通用文本匹配方法
        
        Args:
            text: 待匹配文本
            keyword: 搜索关键词
            mode: 匹配模式（fuzzy/regular）
            
        Returns:
            bool: 是否匹配
        """
        if not text or not keyword:
            return False
        
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        if mode == "fuzzy":
            return keyword_lower in text_lower
        else:
            try:
                pattern = re.compile(keyword, re.IGNORECASE)
                return bool(pattern.search(text))
            except re.error:
                # 正则表达式无效，回退到模糊匹配
                return keyword_lower in text_lower
    
    # ========== 任务核心操作 ==========
    @pyqtSlot(str, str, dict, result=int)
    def add_task(self, title: str, section: str, **kwargs) -> int:
        """
        添加任务
        
        Args:
            title: 任务标题
            section: 分区（daily/weekly/once）
            **kwargs: 其他任务属性
            
        Returns:
            int: 任务ID，失败返回-1
        """
        try:
            # 验证必要参数
            if not title or not section:
                logger.error("任务标题和分区不能为空")
                return -1
                
            # 构建任务字典
            task_dict: TaskDict = {
                "id": -1,  # 占位，由仓库生成
                "title": title,
                "section": section,
                "description": kwargs.get("description", ""),
                "requirements": kwargs.get("requirements", ""),
                "priority": kwargs.get("priority", 1),
                "is_completed": kwargs.get("is_completed", False),
                "due_date": kwargs.get("due_date"),
                "reset_weekday": kwargs.get("reset_weekday"),
                "reset_time": kwargs.get("reset_time"),
                "sort_order": kwargs.get("sort_order", 0),
                "tags": kwargs.get("tags", []),
                "completed_at": kwargs.get("completed_at")
            }
            
            # 添加任务
            task_id = self.repository.add_task(task_dict)
            
            if task_id != -1:
                self.task_added.emit(task_id)
                logger.info(f"任务添加成功: ID={task_id}, 标题={title}")
            
            return task_id
            
        except DatabaseError as e:
            logger.error(f"数据库添加任务失败: {e}")
            return -1
        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            return -1
    
    @pyqtSlot(int)
    def get_task(self, task_id: int, include_deleted: bool = False) -> Optional[TaskDict]:
        """
        获取单个任务
        
        Args:
            task_id: 任务ID
            include_deleted: 是否包含已删除的任务
            
        Returns:
            Optional[TaskDict]: 任务字典，不存在返回None
        """
        try:
            return self.repository.get_task(task_id, include_deleted)
        except DatabaseError as e:
            logger.error(f"数据库获取任务失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            return None
    
    @pyqtSlot(str, str)
    def get_tasks(self, section: Optional[str] = None, tag: Optional[str] = None) -> List[TaskDict]:
        """
        获取任务列表
        
        Args:
            section: 分区筛选（daily/weekly/once）
            tag: 标签筛选
            
        Returns:
            List[TaskDict]: 任务字典列表
        """
        try:
            return self.repository.get_tasks(section=section, tag=tag, include_deleted=False)
        except DatabaseError as e:
            logger.error(f"数据库获取任务列表失败: {e}")
            return []
        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            return []
    
    @pyqtSlot(int, dict, result=bool)
    def update_task(self, task_id: int, **updates) -> bool:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            **updates: 更新字段
            
        Returns:
            bool: 是否成功
        """
        try:
            success = self.repository.update_task(task_id, updates)
            
            if success:
                self.task_updated.emit(task_id)
                logger.info(f"任务更新成功: ID={task_id}")
            
            return success
            
        except DatabaseError as e:
            logger.error(f"数据库更新任务失败: {e}")
            return False
        except Exception as e:
            logger.error(f"更新任务失败: {e}")
            return False
    
    @pyqtSlot(int, result=bool)
    def delete_task(self, task_id: int) -> bool:
        """
        删除任务（软删除，移动到回收站）
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功
        """
        try:
            success = self.repository.soft_delete(task_id)
            
            if success:
                self.task_deleted.emit(task_id)
                self.recycle_bin_updated.emit()
                logger.info(f"任务删除成功: ID={task_id}")
            
            return success
            
        except DatabaseError as e:
            logger.error(f"数据库删除任务失败: {e}")
            return False
        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return False
    
    @pyqtSlot(int, result=bool)
    def restore_task(self, task_id: int) -> bool:
        """
        恢复已删除的任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功
        """
        try:
            success = self.repository.restore(task_id)
            
            if success:
                self.task_restored.emit(task_id)
                self.recycle_bin_updated.emit()
                logger.info(f"任务恢复成功: ID={task_id}")
            
            return success
            
        except DatabaseError as e:
            logger.error(f"数据库恢复任务失败: {e}")
            return False
        except Exception as e:
            logger.error(f"恢复任务失败: {e}")
            return False
    
    @pyqtSlot(int, result=bool)
    def permanent_delete_task(self, task_id: int) -> bool:
        """
        永久删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功
        """
        try:
            success = self.repository.permanent_delete(task_id)
            
            if success:
                self.task_permanent_deleted.emit(task_id)
                self.recycle_bin_updated.emit()
                logger.info(f"任务永久删除成功: ID={task_id}")
            
            return success
            
        except DatabaseError as e:
            logger.error(f"数据库永久删除任务失败: {e}")
            return False
        except Exception as e:
            logger.error(f"永久删除任务失败: {e}")
            return False
    
    @pyqtSlot(int, result=bool)
    def complete_task(self, task_id: int) -> bool:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功
        """
        try:
            success = self.repository.complete_task(task_id)
            
            if success:
                self.task_completed.emit(task_id)
                logger.info(f"任务完成: ID={task_id}")
            
            return success
            
        except DatabaseError as e:
            logger.error(f"数据库完成任务失败: {e}")
            return False
        except Exception as e:
            logger.error(f"完成任务失败: {e}")
            return False
    
    @pyqtSlot(int, result=bool)
    def uncomplete_task(self, task_id: int) -> bool:
        """
        取消完成任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功
        """
        try:
            success = self.repository.uncomplete_task(task_id)
            
            if success:
                self.task_uncompleted.emit(task_id)
                logger.info(f"任务取消完成: ID={task_id}")
            
            return success
            
        except DatabaseError as e:
            logger.error(f"数据库取消完成任务失败: {e}")
            return False
        except Exception as e:
            logger.error(f"取消完成任务失败: {e}")
            return False
    
    # ========== 统计 ==========
    @pyqtSlot()
    def get_deleted_tasks(self) -> List[TaskDict]:
        """
        获取已删除任务列表
        
        Returns:
            List[TaskDict]: 已删除任务字典列表
        """
        try:
            return self.repository.get_deleted_tasks()
        except DatabaseError as e:
            logger.error(f"数据库获取已删除任务失败: {e}")
            return []
        except Exception as e:
            logger.error(f"获取已删除任务失败: {e}")
            return []

    @pyqtSlot(result=int)
    def empty_recycle_bin(self) -> int:
        """
        清空回收站，永久删除所有已删除的任务
        
        Returns:
            int: 删除的任务数量
        """
        try:
            count = self.repository.empty_recycle_bin()
            
            if count > 0:
                self.recycle_bin_updated.emit()
                logger.info(f"清空回收站成功: 删除了{count}个任务")
            
            return count
            
        except DatabaseError as e:
            logger.error(f"数据库清空回收站失败: {e}")
            return 0
        except Exception as e:
            logger.error(f"清空回收站失败: {e}")
            return 0

    @pyqtSlot()
    def get_stats(self) -> SectionStats:
        """
        获取统计信息
        
        Returns:
            SectionStats: 统计信息字典
        """
        try:
            stats = self.repository.get_task_count_by_section()
            
            # 计算总计
            total_pending = sum(section_stats["pending"] for section_stats in stats.values())
            total_completed = sum(section_stats["completed"] for section_stats in stats.values())
            total_tasks = total_pending + total_completed
            
            # 获取回收站数量
            deleted_count = len(self.repository.get_deleted_tasks())
            
            return {
                "sections": stats,
                "total": {
                    "pending": total_pending,
                    "completed": total_completed,
                    "tasks": total_tasks,
                    "deleted": deleted_count
                }
            }
            
        except DatabaseError as e:
            logger.error(f"数据库获取统计信息失败: {e}")
            return {"sections": {}, "total": {"pending": 0, "completed": 0, "tasks": 0, "deleted": 0}}
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {"sections": {}, "total": {"pending": 0, "completed": 0, "tasks": 0, "deleted": 0}}
    
    # ========== 重置 ==========
    @pyqtSlot(result=int)
    def perform_daily_reset(self) -> int:
        """
        执行每日任务重置
        
        Returns:
            int: 重置的任务数量
        """
        try:
            count = self.repository.reset_daily_tasks()
            
            if count > 0:
                self.daily_reset_performed.emit(count)
                logger.info(f"每日任务重置完成: 重置了{count}个任务")
            
            return count
            
        except DatabaseError as e:
            logger.error(f"数据库执行每日重置失败: {e}")
            return 0
        except Exception as e:
            logger.error(f"执行每日重置失败: {e}")
            return 0
    
    @pyqtSlot(int, result=int)
    def perform_weekly_reset(self, weekday: int) -> int:
        """
        执行周常任务重置
        
        Args:
            weekday: 星期几（0=周一, 6=周日）
            
        Returns:
            int: 重置的任务数量
        """
        try:
            if not 0 <= weekday <= 6:
                logger.error(f"无效的星期值：{weekday}（预期 0-6）")
                return 0
                
            count = self.repository.reset_weekly_tasks(weekday)
            
            if count > 0:
                self.weekly_reset_performed.emit(count)
                logger.info(f"周常任务重置完成: 星期{weekday}, 重置了{count}个任务")
            
            return count
            
        except DatabaseError as e:
            logger.error(f"数据库执行周常重置失败: {e}")
            return 0
        except Exception as e:
            logger.error(f"执行周常重置失败: {e}")
            return 0
    
    @pyqtSlot(result=str)
    def get_global_daily_reset_time(self) -> str:
        """
        获取全局每日重置时间
        
        Returns:
            str: 重置时间字符串（HH:MM格式）
        """
        try:
            reset_time = self.repository.get_app_state("daily_reset_time")
            return reset_time if reset_time else DEFAULT_DAILY_RESET_TIME
        except DatabaseError as e:
            logger.error(f"数据库获取每日重置时间失败: {e}")
            return DEFAULT_DAILY_RESET_TIME
        except Exception as e:
            logger.error(f"获取每日重置时间失败: {e}")
            return DEFAULT_DAILY_RESET_TIME
    
    @pyqtSlot(str, result=bool)
    def set_global_daily_reset_time(self, time_str: str) -> bool:
        """
        设置全局每日重置时间（增强：支持 6:00 自动补全为 06:00）
        
        Args:
            time_str: 时间字符串（HH:MM 或 H:MM 格式）
            
        Returns:
            bool: 是否成功
        """
        try:
            # 标准化时间格式（补全前导零）
            parts = time_str.split(":")
            if len(parts) != 2:
                logger.error(f"时间格式无效: {time_str}（预期 HH:MM）")
                return False
                
            hour = parts[0].zfill(2)
            minute = parts[1].zfill(2)
            normalized_time = f"{hour}:{minute}"
            
            # 验证时间格式
            datetime.strptime(normalized_time, "%H:%M")
            
            success = self.repository.set_app_state("daily_reset_time", normalized_time)
            
            if success:
                logger.info(f"每日重置时间已更新: {normalized_time}")
            
            return success
            
        except ValueError as e:
            logger.error(f"时间格式无效: {time_str} - {e}")
            return False
        except DatabaseError as e:
            logger.error(f"数据库设置每日重置时间失败: {e}")
            return False
        except Exception as e:
            logger.error(f"设置每日重置时间失败: {e}")
            return False
    
    # ========== 标签 ==========
    @pyqtSlot()
    def get_all_tags(self) -> List[TagInfo]:
        """
        获取所有标签（优化：一次 JOIN 查询获取任务数，提升性能）
        
        Returns:
            List[TagInfo]: 标签列表（包含任务数）
        """
        try:
            # 优化：通过仓库的 JOIN 查询获取标签及任务数，替代循环查询
            return self.repository.get_all_tags_with_task_count()
            
        except DatabaseError as e:
            logger.error(f"数据库获取标签失败: {e}")
            return []
        except Exception as e:
            logger.error(f"获取所有标签失败: {e}")
            return []
    
    # ========== 搜索功能 ==========
    @pyqtSlot(str, str)
    def search_tasks(self, keyword: str, mode: str = "fuzzy") -> List[TaskDict]:
        """
        搜索任务（优化：提取通用匹配方法，提前导入 re）
        
        Args:
            keyword: 搜索关键词
            mode: 搜索模式（fuzzy/regular）
            
        Returns:
            List[TaskDict]: 搜索结果列表
        """
        try:
            if not keyword:
                return self.get_tasks()
            
            # 获取所有未删除的任务
            all_tasks = self.repository.get_tasks(include_deleted=False)
            results = []
            
            for task in all_tasks:
                # 检查标题、描述、要求、标签
                title_match = self._match_text(task["title"], keyword, mode)
                desc_match = self._match_text(task.get("description", ""), keyword, mode)
                req_match = self._match_text(task.get("requirements", ""), keyword, mode)
                
                tag_match = False
                for tag in task.get("tags", []):
                    if self._match_text(tag, keyword, mode):
                        tag_match = True
                        break
                
                # 任何字段匹配则加入结果
                if title_match or desc_match or req_match or tag_match:
                    results.append(task)
            
            return results
            
        except DatabaseError as e:
            logger.error(f"数据库搜索任务失败: {e}")
            return []
        except Exception as e:
            logger.error(f"搜索任务失败: {e}")
            return []