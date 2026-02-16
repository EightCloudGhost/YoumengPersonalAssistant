"""
自定义异常模块
"""


class TaskRepositoryError(Exception):
    """任务仓库基础异常"""
    pass


class TaskNotFoundError(TaskRepositoryError):
    """任务不存在异常"""
    pass


class TagNotFoundError(TaskRepositoryError):
    """标签不存在异常"""
    pass


class DatabaseError(TaskRepositoryError):
    """数据库操作异常"""
    pass


class ValidationError(Exception):
    """数据验证异常"""
    pass


class ConfigError(Exception):
    """配置错误异常"""
    pass


class ServiceError(Exception):
    """服务错误异常"""
    pass


class RepositoryError(Exception):
    """数据仓库错误异常"""
    pass


class TaskManagerError(Exception):
    """任务管理器错误异常"""
    pass


class AutoResetError(Exception):
    """自动重置服务错误异常"""
    pass