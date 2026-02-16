# -*- coding: utf-8 -*-
"""
日志管理模块 - 按启动时间分类日志，自动清理过期日志
"""

import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path


class LogManager:
    """日志管理器 - 管理日志文件的创建和清理"""
    
    LOG_DIR = "logs"
    LOG_RETENTION_DAYS = 7  # 日志保留天数
    
    def __init__(self):
        self.startup_time = datetime.now()
        self.session_dir = None
        self.logger = None
        
    def setup(self, name="youmeng", log_level=logging.INFO):
        """
        配置应用程序日志
        
        Args:
            name: 日志器名称
            log_level: 日志级别
            
        Returns:
            logging.Logger: 配置好的日志器
        """
        # 清理过期日志
        self._cleanup_old_logs()
        
        # 创建本次会话的日志目录
        self.session_dir = self._create_session_dir()
        
        # 创建日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # 主日志文件
        main_log = os.path.join(self.session_dir, "app.log")
        main_handler = logging.FileHandler(main_log, encoding="utf-8")
        main_handler.setLevel(log_level)
        main_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        main_handler.setFormatter(main_format)
        self.logger.addHandler(main_handler)
        
        # 错误日志文件（仅记录WARNING及以上）
        error_log = os.path.join(self.session_dir, "error.log")
        error_handler = logging.FileHandler(error_log, encoding="utf-8")
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(main_format)
        self.logger.addHandler(error_handler)
        
        # 调试日志文件（记录所有级别，包括DEBUG）
        debug_log = os.path.join(self.session_dir, "debug.log")
        debug_handler = logging.FileHandler(debug_log, encoding="utf-8")
        debug_handler.setLevel(logging.DEBUG)
        debug_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        debug_handler.setFormatter(debug_format)
        self.logger.addHandler(debug_handler)
        
        self.logger.info(f"日志系统初始化完成，会话目录: {self.session_dir}")
        
        return self.logger
    
    def _create_session_dir(self) -> str:
        """创建本次会话的日志目录"""
        # 格式: logs/2024-01-15_14-30-25
        dir_name = self.startup_time.strftime("%Y-%m-%d_%H-%M-%S")
        session_dir = os.path.join(self.LOG_DIR, dir_name)
        
        os.makedirs(session_dir, exist_ok=True)
        
        return session_dir
    
    def _cleanup_old_logs(self):
        """清理超过保留天数的日志"""
        if not os.path.exists(self.LOG_DIR):
            os.makedirs(self.LOG_DIR)
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.LOG_RETENTION_DAYS)
        cleaned_count = 0
        
        try:
            for item in os.listdir(self.LOG_DIR):
                item_path = os.path.join(self.LOG_DIR, item)
                
                # 只处理目录
                if not os.path.isdir(item_path):
                    # 清理旧的单文件日志（如果存在）
                    if item.endswith('.log'):
                        try:
                            file_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                            if file_time < cutoff_date:
                                os.remove(item_path)
                                cleaned_count += 1
                        except (OSError, ValueError):
                            pass
                    continue
                
                # 尝试从目录名解析日期
                try:
                    # 格式: 2024-01-15_14-30-25
                    dir_date = datetime.strptime(item, "%Y-%m-%d_%H-%M-%S")
                    
                    if dir_date < cutoff_date:
                        shutil.rmtree(item_path)
                        cleaned_count += 1
                        
                except ValueError:
                    # 无法解析的目录名，检查修改时间
                    try:
                        dir_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                        if dir_time < cutoff_date:
                            shutil.rmtree(item_path)
                            cleaned_count += 1
                    except (OSError, ValueError):
                        pass
            
            if cleaned_count > 0:
                print(f"已清理 {cleaned_count} 个过期日志目录/文件")
                
        except Exception as e:
            print(f"清理日志时出错: {e}")
    
    def get_session_dir(self) -> str:
        """获取当前会话的日志目录"""
        return self.session_dir
    
    def get_all_sessions(self) -> list:
        """获取所有日志会话列表"""
        sessions = []
        
        if not os.path.exists(self.LOG_DIR):
            return sessions
        
        for item in os.listdir(self.LOG_DIR):
            item_path = os.path.join(self.LOG_DIR, item)
            if os.path.isdir(item_path):
                try:
                    session_time = datetime.strptime(item, "%Y-%m-%d_%H-%M-%S")
                    sessions.append({
                        "name": item,
                        "path": item_path,
                        "time": session_time
                    })
                except ValueError:
                    pass
        
        # 按时间倒序排列
        sessions.sort(key=lambda x: x["time"], reverse=True)
        return sessions


# 创建全局日志管理器实例
_log_manager = LogManager()


def setup_logger(name="youmeng", log_level=logging.INFO):
    """
    配置应用程序日志（兼容旧接口）
    
    Args:
        name: 日志器名称
        log_level: 日志级别
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    return _log_manager.setup(name, log_level)


def get_log_manager() -> LogManager:
    """获取日志管理器实例"""
    return _log_manager


# 创建默认日志器
logger = setup_logger()
