from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from utils.common import safe_isoformat, safe_parse_isoformat


class TaskSection(str, Enum):
    """任务分区枚举"""
    DAILY = "daily"      # 日常任务
    WEEKLY = "weekly"    # 周常任务
    ONCE = "once"        # 特殊任务

    @classmethod
    def from_str(cls, value: str) -> 'TaskSection':
        """从字符串安全创建枚举（容错）"""
        try:
            return cls(value.lower().strip())
        except ValueError:
            return cls.DAILY


@dataclass
class Task:
    """任务数据模型（优化转换逻辑）"""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    requirements: str = ""
    priority: int = 1
    section: TaskSection = TaskSection.DAILY
    is_completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    reset_weekday: Optional[int] = None  # 0=周一, 6=周日
    reset_time: Optional[str] = None
    sort_order: int = 0
    deleted_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转换为数据库存储字典"""
        return {
            "id": self.id,
            "title": self.title.strip(),
            "description": self.description.strip(),
            "requirements": self.requirements.strip(),
            "priority": self.priority,
            "section": self.section.value,
            "is_completed": 1 if self.is_completed else 0,
            "created_at": safe_isoformat(self.created_at),
            "due_date": safe_isoformat(self.due_date),
            "completed_at": safe_isoformat(self.completed_at),
            "reset_weekday": self.reset_weekday,
            "reset_time": self.reset_time,
            "sort_order": self.sort_order,
            "deleted_at": safe_isoformat(self.deleted_at)
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """从字典创建实例（优化日期解析）"""
        # 日期字段解析
        created_at = safe_parse_isoformat(data.get("created_at")) or datetime.now()
        due_date = safe_parse_isoformat(data.get("due_date"), is_date=True)
        completed_at = safe_parse_isoformat(data.get("completed_at"))
        deleted_at = safe_parse_isoformat(data.get("deleted_at"))

        # 分区解析
        section = TaskSection.from_str(data.get("section", ""))

        # 星期几验证
        reset_weekday = data.get("reset_weekday")
        if reset_weekday is not None and (not isinstance(reset_weekday, int) or reset_weekday < 0 or reset_weekday > 6):
            reset_weekday = None

        return cls(
            id=data.get("id"),
            title=data.get("title", "").strip(),
            description=data.get("description", "").strip(),
            requirements=data.get("requirements", "").strip(),
            priority=int(data.get("priority", 1)),
            section=section,
            is_completed=bool(data.get("is_completed", 0)),
            created_at=created_at,
            due_date=due_date,
            completed_at=completed_at,
            reset_weekday=reset_weekday,
            reset_time=data.get("reset_time"),
            sort_order=int(data.get("sort_order", 0)),
            deleted_at=deleted_at,
            tags=[tag.strip() for tag in data.get("tags", []) if tag.strip()]
        )

    def is_deleted(self) -> bool:
        """检查是否已删除"""
        return self.deleted_at is not None

    def is_overdue(self) -> bool:
        """检查特殊任务是否过期（优化逻辑）"""
        if self.section != TaskSection.ONCE or self.is_completed or self.due_date is None:
            return False
        return self.due_date < date.today()

    def days_until_due(self) -> Optional[int]:
        """计算距离截止日期的天数（处理负数）"""
        if self.section != TaskSection.ONCE or self.due_date is None:
            return None
        delta = self.due_date - date.today()
        return max(delta.days, 0) if delta.days < 0 else delta.days


@dataclass
class Tag:
    """标签数据模型"""
    id: Optional[int] = None
    name: str = ""

    def __post_init__(self):
        """自动清理标签名称"""
        self.name = self.name.strip()

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict) -> 'Tag':
        return cls(id=data.get("id"), name=data.get("name", ""))


@dataclass
class AppState:
    """应用状态数据模型"""
    key: str = ""
    value: str = ""

    def to_dict(self) -> dict:
        return {"key": self.key.strip(), "value": self.value.strip()}

    @classmethod
    def from_dict(cls, data: dict) -> 'AppState':
        return cls(key=data.get("key", ""), value=data.get("value", ""))