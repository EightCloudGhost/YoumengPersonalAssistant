"""
通用工具模块
"""
from datetime import datetime, date
from typing import Optional, Any
from utils.logger import logger


def safe_isoformat(dt: Optional[datetime | date]) -> Optional[str]:
    """安全地将日期时间转换为ISO格式字符串（处理None值）"""
    if dt is None:
        return None
    try:
        return dt.isoformat()
    except Exception as e:
        logger.warning(f"日期转换失败: {e}")
        return None


def safe_parse_isoformat(iso_str: Optional[str], is_date: bool = False) -> Optional[datetime | date]:
    """安全地解析ISO格式字符串为日期时间对象"""
    if iso_str is None:
        return None
    try:
        if is_date:
            return date.fromisoformat(iso_str)
        return datetime.fromisoformat(iso_str)
    except (ValueError, TypeError) as e:
        logger.warning(f"解析ISO日期失败: {e}, 字符串: {iso_str}")
        return None


def validate_weekday(weekday: int) -> bool:
    """验证星期几是否有效（0=周一, 6=周日）"""
    return isinstance(weekday, int) and 0 <= weekday <= 6


def escape_sql_in_list(ids: list[int]) -> str:
    """安全地生成SQL IN子句的ID列表（防止注入）"""
    if not ids:
        return "()"
    # 确保所有ID都是整数
    valid_ids = [str(int(id_)) for id_ in ids if isinstance(id_, int)]
    return f"({','.join(valid_ids)})"