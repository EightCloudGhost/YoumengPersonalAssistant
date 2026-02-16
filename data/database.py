import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from utils.logger import logger
from utils.exceptions import DatabaseError


@contextmanager
def get_connection(db_path: str = "data.db"):
    """
    数据库连接上下文管理器（自动处理连接/提交/回滚/关闭）
    
    Args:
        db_path: 数据库文件路径
        
    Yields:
        sqlite3.Connection: 数据库连接
        
    Raises:
        DatabaseError: 数据库操作失败
    """
    conn = None
    try:
        # 确保目录存在
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # 创建连接
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        
        logger.debug(f"数据库连接已建立: {db_path}")
        yield conn
        
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"数据库操作失败: {e}")
        raise DatabaseError(str(e)) from e
    finally:
        if conn:
            conn.close()
            logger.debug(f"数据库连接已关闭: {db_path}")


def init_database(db_path: str = "data.db") -> bool:
    """初始化数据库表结构（优化索引和初始数据）"""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # 任务表（优化字段约束）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    requirements TEXT DEFAULT '',
                    priority INTEGER DEFAULT 1,
                    section TEXT NOT NULL CHECK(section IN ('daily', 'weekly', 'once')),
                    is_completed BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    due_date DATE,
                    completed_at TIMESTAMP,
                    reset_weekday INTEGER CHECK(reset_weekday BETWEEN 0 AND 6),
                    reset_time TEXT,
                    sort_order INTEGER DEFAULT 0,
                    deleted_at TIMESTAMP
                )
            """)
            
            # 数据库迁移：为旧数据库添加新字段
            _migrate_add_column(cursor, "tasks", "requirements", "TEXT DEFAULT ''")
            _migrate_add_column(cursor, "tasks", "priority", "INTEGER DEFAULT 1")
            
            # 标签表（唯一索引优化）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            
            # 任务-标签关联表（优化外键级联）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_tags (
                    task_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (task_id, tag_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)
            
            # 应用状态表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL DEFAULT ''
                )
            """)
            
            # 初始数据（原子操作）
            cursor.execute("""
                INSERT OR IGNORE INTO app_state (key, value) VALUES 
                    ('daily_reset_time', '06:00'),
                    ('last_daily_reset', ''),
                    ('recycle_bin_capacity', '100')
            """)
            
            # 优化索引（减少冗余索引）
            indexes = [
                ("idx_tasks_section_deleted", "tasks(section, deleted_at)"),
                ("idx_tasks_completed", "tasks(is_completed)"),
                ("idx_tasks_created_sort", "tasks(sort_order, created_at)"),
                ("idx_tasks_priority", "tasks(priority)"),
                ("idx_task_tags_task", "task_tags(task_id)"),
                ("idx_task_tags_tag", "task_tags(tag_id)"),
                ("idx_tags_name", "tags(name)")  # 加速标签查询
            ]
            
            for idx_name, idx_cols in indexes:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_cols}")
        
        logger.info(f"数据库初始化成功: {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False


def _migrate_add_column(cursor, table: str, column: str, definition: str):
    """数据库迁移：安全添加新列"""
    try:
        # 检查列是否存在
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            logger.info(f"数据库迁移：添加列 {table}.{column}")
    except Exception as e:
        logger.warning(f"添加列 {table}.{column} 失败: {e}")


def execute_query(query: str, params: tuple = (), db_path: str = "data.db") -> List[Dict[str, Any]]:
    """执行查询语句（优化结果转换）"""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
    except DatabaseError:
        return []


def execute_update(query: str, params: tuple = (), db_path: str = "data.db") -> int:
    """执行更新语句（INSERT/UPDATE/DELETE）"""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    except DatabaseError:
        return 0


def execute_many(query: str, params_list: List[tuple], db_path: str = "data.db") -> int:
    """批量执行更新语句"""
    if not params_list:
        return 0
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount
    except DatabaseError:
        return 0


def get_last_insert_id(db_path: str = "data.db") -> Optional[int]:
    """获取最后插入的ID"""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_insert_rowid()")
            result = cursor.fetchone()
            return result[0] if result else None
    except DatabaseError:
        return None