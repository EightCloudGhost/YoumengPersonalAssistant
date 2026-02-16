from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, timedelta
from data.models import Task, Tag, AppState, TaskSection
from data.database import (
    execute_query, execute_update, execute_many,
    get_last_insert_id, get_connection
)
from utils.logger import logger
from utils.common import safe_isoformat, validate_weekday, escape_sql_in_list
from utils.exceptions import TaskNotFoundError, TagNotFoundError, TaskRepositoryError


class TaskRepository:
    """任务数据仓库（优化性能和错误处理）"""

    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path

    # ========== 任务操作 ==========
    def add_task(self, task_dict: Dict) -> int:
        """添加任务（优化标签批量处理）"""
        try:
            task = Task.from_dict(task_dict)
            if not task.title:
                logger.warning("任务标题不能为空")
                return -1

            # 在同一个连接中插入并获取ID
            with get_connection(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO tasks (
                        title, description, requirements, priority, section, is_completed, 
                        created_at, due_date, completed_at, reset_weekday, 
                        reset_time, sort_order, deleted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                params = (
                    task.title,
                    task.description,
                    task_dict.get("requirements", ""),
                    task_dict.get("priority", 1),
                    task.section.value,
                    1 if task.is_completed else 0,
                    safe_isoformat(task.created_at) or datetime.now().isoformat(),
                    safe_isoformat(task.due_date),
                    safe_isoformat(task.completed_at),
                    task.reset_weekday,
                    task.reset_time,
                    task.sort_order,
                    safe_isoformat(task.deleted_at)
                )

                cursor.execute(query, params)
                
                if cursor.rowcount > 0:
                    task_id = cursor.lastrowid
                    logger.info(f"任务添加成功: ID={task_id}, 标题={task.title}")
                    
                    # 标签在事务提交后添加
                    if task.tags:
                        # 提交当前事务，然后添加标签
                        pass  # 标签将在下面添加
                else:
                    return -1
            
            # 任务添加成功后，添加标签关联
            if task_id and task.tags:
                self._batch_add_task_tags(task_id, task.tags)
            
            return task_id

        except Exception as e:
            logger.error(f"添加任务失败: {e}")
            return -1

    def get_task(self, task_id: int, include_deleted: bool = False) -> Optional[Dict]:
        """获取单个任务
        
        Args:
            task_id: 任务ID
            include_deleted: 是否包含已删除的任务
            
        Returns:
            任务字典，不存在返回None
        """
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"无效的任务ID: {task_id}")
            return None

        try:
            if include_deleted:
                query = "SELECT * FROM tasks WHERE id = ?"
            else:
                query = "SELECT * FROM tasks WHERE id = ? AND deleted_at IS NULL"
            results = execute_query(query, (task_id,), self.db_path)

            if not results:
                raise TaskNotFoundError(f"任务ID {task_id} 不存在")

            task_data = results[0]
            task_data["tags"] = self.get_task_tags(task_id)
            return task_data

        except TaskNotFoundError as e:
            logger.warning(str(e))
            return None
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            return None

    def get_tasks(self, section: Optional[str] = None, tag: Optional[str] = None,
                  include_deleted: bool = False) -> List[Dict]:
        """获取任务列表（优化SQL JOIN，提升性能）"""
        try:
            # 构建基础查询（使用JOIN替代后筛选）
            conditions = ["1=1"]
            params = []

            if not include_deleted:
                conditions.append("t.deleted_at IS NULL")

            if section:
                try:
                    section_val = TaskSection.from_str(section).value
                    conditions.append("t.section = ?")
                    params.append(section_val)
                except ValueError:
                    logger.warning(f"无效的分区: {section}")
                    return []

            # 标签筛选（JOIN优化）
            join_clause = ""
            if tag:
                tag_id = self.get_tag_id(tag)
                if not tag_id:
                    return []
                join_clause = "JOIN task_tags tt ON t.id = tt.task_id JOIN tags tg ON tt.tag_id = tg.id"
                conditions.append("tg.id = ?")
                params.append(tag_id)

            # 构建最终查询
            query = f"""
                SELECT DISTINCT t.* 
                FROM tasks t {join_clause}
                WHERE {' AND '.join(conditions)}
                ORDER BY t.sort_order ASC, t.created_at DESC
            """

            tasks = execute_query(query, tuple(params), self.db_path)

            # 批量获取标签（减少SQL查询次数）
            task_ids = [task["id"] for task in tasks]
            if task_ids:
                tag_map = self._get_task_tags_batch(task_ids)
                for task in tasks:
                    task["tags"] = tag_map.get(task["id"], [])
            else:
                for task in tasks:
                    task["tags"] = []

            return tasks

        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            return []

    def update_task(self, task_id: int, updates: Dict) -> bool:
        """更新任务（优化参数验证）"""
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"无效的任务ID: {task_id}")
            return False

        if not updates:
            return False

        try:
            # 检查任务是否存在
            if not self.get_task(task_id):
                raise TaskNotFoundError(f"任务ID {task_id} 不存在")

            # 构建更新语句
            set_clauses = []
            params = []

            for key, value in updates.items():
                if key == "tags":
                    continue  # 标签单独处理
                elif key == "is_completed":
                    set_clauses.append(f"{key} = ?")
                    params.append(1 if value else 0)
                elif key in ["due_date", "completed_at", "deleted_at"] and value:
                    # 处理日期时间字段
                    if isinstance(value, (datetime, date)):
                        set_clauses.append(f"{key} = ?")
                        params.append(safe_isoformat(value))
                    else:
                        set_clauses.append(f"{key} = ?")
                        params.append(value)
                else:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(task_id)

            affected = execute_update(query, tuple(params), self.db_path)

            # 更新标签
            if "tags" in updates:
                # 先删除所有现有标签
                self._remove_all_task_tags(task_id)
                # 添加新标签
                if updates["tags"]:
                    self._batch_add_task_tags(task_id, updates["tags"])

            success = affected > 0
            if success:
                logger.info(f"任务更新成功: ID={task_id}")

            return success

        except TaskNotFoundError as e:
            logger.warning(str(e))
            return False
        except Exception as e:
            logger.error(f"更新任务失败: {e}")
            return False

    def soft_delete(self, task_id: int) -> bool:
        """软删除任务（移动到回收站）"""
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"无效的任务ID: {task_id}")
            return False

        try:
            query = "UPDATE tasks SET deleted_at = ? WHERE id = ?"
            deleted_at = datetime.now().isoformat()
            affected = execute_update(query, (deleted_at, task_id), self.db_path)

            success = affected > 0
            if success:
                logger.info(f"任务软删除成功: ID={task_id}")

            return success

        except Exception as e:
            logger.error(f"软删除任务失败: {e}")
            return False

    def restore(self, task_id: int) -> bool:
        """恢复已删除的任务"""
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"无效的任务ID: {task_id}")
            return False

        try:
            query = "UPDATE tasks SET deleted_at = NULL WHERE id = ?"
            affected = execute_update(query, (task_id,), self.db_path)

            success = affected > 0
            if success:
                logger.info(f"任务恢复成功: ID={task_id}")

            return success

        except Exception as e:
            logger.error(f"恢复任务失败: {e}")
            return False

    def permanent_delete(self, task_id: int) -> bool:
        """永久删除任务"""
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"无效的任务ID: {task_id}")
            return False

        try:
            query = "DELETE FROM tasks WHERE id = ?"
            affected = execute_update(query, (task_id,), self.db_path)

            success = affected > 0
            if success:
                logger.info(f"任务永久删除成功: ID={task_id}")

            return success

        except Exception as e:
            logger.error(f"永久删除任务失败: {e}")
            return False

    def complete_task(self, task_id: int) -> bool:
        """完成任务"""
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"无效的任务ID: {task_id}")
            return False

        try:
            query = "UPDATE tasks SET is_completed = 1, completed_at = ? WHERE id = ?"
            completed_at = datetime.now().isoformat()
            affected = execute_update(query, (completed_at, task_id), self.db_path)

            success = affected > 0
            if success:
                logger.info(f"任务完成成功: ID={task_id}")

            return success

        except Exception as e:
            logger.error(f"完成任务失败: {e}")
            return False

    def uncomplete_task(self, task_id: int) -> bool:
        """取消完成任务"""
        if not isinstance(task_id, int) or task_id <= 0:
            logger.warning(f"无效的任务ID: {task_id}")
            return False

        try:
            query = "UPDATE tasks SET is_completed = 0, completed_at = NULL WHERE id = ?"
            affected = execute_update(query, (task_id,), self.db_path)

            success = affected > 0
            if success:
                logger.info(f"任务取消完成成功: ID={task_id}")

            return success

        except Exception as e:
            logger.error(f"取消完成任务失败: {e}")
            return False

    # ========== 标签操作 ==========
    def get_task_tags(self, task_id: int) -> List[str]:
        """获取任务的标签列表"""
        if not isinstance(task_id, int) or task_id <= 0:
            return []

        try:
            query = """
                SELECT t.name 
                FROM tags t
                JOIN task_tags tt ON t.id = tt.tag_id
                WHERE tt.task_id = ?
                ORDER BY t.name
            """
            results = execute_query(query, (task_id,), self.db_path)
            return [row["name"] for row in results]
        except Exception as e:
            logger.error(f"获取任务标签失败: {e}")
            return []

    def get_tag_id(self, tag_name: str) -> Optional[int]:
        """获取标签ID（如果不存在则创建）"""
        tag_name = tag_name.strip()
        if not tag_name:
            return None

        try:
            # 先尝试获取现有标签
            query = "SELECT id FROM tags WHERE name = ? LIMIT 1"
            results = execute_query(query, (tag_name,), self.db_path)

            if results:
                return results[0]["id"]

            # 创建新标签（在同一个连接中获取ID）
            with get_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                
                if cursor.rowcount > 0:
                    tag_id = cursor.lastrowid
                    logger.debug(f"标签创建成功: ID={tag_id}, 名称={tag_name}")
                    return tag_id

            return None

        except Exception as e:
            logger.error(f"获取/创建标签失败: {e}")
            return None

    def add_tag(self, tag_name: str) -> int:
        """添加标签（返回标签ID）"""
        tag_name = tag_name.strip()
        if not tag_name:
            return -1

        try:
            # 先查询是否存在
            query = "SELECT id FROM tags WHERE name = ? LIMIT 1"
            results = execute_query(query, (tag_name,), self.db_path)
            if results:
                return results[0]["id"]
            
            # 在同一个连接中插入并获取ID
            with get_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                
                if cursor.rowcount > 0:
                    tag_id = cursor.lastrowid
                    logger.info(f"标签添加成功: ID={tag_id}, 名称={tag_name}")
                    return tag_id
                else:
                    # 如果INSERT被忽略（标签已存在），重新查询
                    cursor.execute("SELECT id FROM tags WHERE name = ? LIMIT 1", (tag_name,))
                    result = cursor.fetchone()
                    return result[0] if result else -1

        except Exception as e:
            logger.error(f"添加标签失败: {e}")
            return -1

    def rename_tag(self, tag_id: int, new_name: str) -> bool:
        """重命名标签（优化参数验证）"""
        if not isinstance(tag_id, int) or tag_id <= 0:
            logger.warning(f"无效的标签ID: {tag_id}")
            return False

        new_name = new_name.strip()
        if not new_name:
            logger.warning("标签名称不能为空")
            return False

        try:
            query = "UPDATE tags SET name = ? WHERE id = ?"
            affected = execute_update(query, (new_name, tag_id), self.db_path)

            success = affected > 0
            if success:
                logger.info(f"标签重命名成功: ID={tag_id}, 新名称={new_name}")
            return success
        except Exception as e:
            logger.error(f"重命名标签失败: {e}")
            return False

    def merge_tags(self, source_id: int, target_id: int) -> bool:
        """合并标签（优化事务处理）"""
        if source_id == target_id or not (isinstance(source_id, int) and isinstance(target_id, int)):
            logger.warning(f"无效的合并参数: source_id={source_id}, target_id={target_id}")
            return False

        try:
            # 检查标签是否存在
            source_exists = execute_query("SELECT 1 FROM tags WHERE id = ?", (source_id,), self.db_path)
            target_exists = execute_query("SELECT 1 FROM tags WHERE id = ?", (target_id,), self.db_path)
            if not source_exists or not target_exists:
                raise TagNotFoundError("源标签或目标标签不存在")

            # 使用上下文管理器确保事务安全
            with get_connection(self.db_path) as conn:
                cursor = conn.cursor()

                # 1. 更新标签关联（避免重复）
                cursor.execute("""
                    INSERT OR IGNORE INTO task_tags (task_id, tag_id)
                    SELECT task_id, ? FROM task_tags WHERE tag_id = ?
                """, (target_id, source_id))

                # 2. 删除源标签关联
                cursor.execute("DELETE FROM task_tags WHERE tag_id = ?", (source_id,))

                # 3. 删除源标签
                cursor.execute("DELETE FROM tags WHERE id = ?", (source_id,))

            logger.info(f"标签合并成功: 源ID={source_id} -> 目标ID={target_id}")
            return True

        except TagNotFoundError as e:
            logger.warning(str(e))
            return False
        except Exception as e:
            logger.error(f"合并标签失败: {e}")
            return False

    def delete_tag(self, tag_id: int) -> bool:
        """删除标签（优化参数验证）"""
        if not isinstance(tag_id, int) or tag_id <= 0:
            logger.warning(f"无效的标签ID: {tag_id}")
            return False

        try:
            query = "DELETE FROM tags WHERE id = ?"
            affected = execute_update(query, (tag_id,), self.db_path)

            success = affected > 0
            if success:
                logger.info(f"标签删除成功: ID={tag_id}")
            return success
        except Exception as e:
            logger.error(f"删除标签失败: {e}")
            return False

    # ========== 重置与统计 ==========
    def reset_daily_tasks(self) -> int:
        """重置每日任务（优化时间过滤）"""
        try:
            query = """
                UPDATE tasks 
                SET is_completed = 0, completed_at = NULL
                WHERE section = ? 
                AND deleted_at IS NULL 
                AND is_completed = 1
            """
            affected = execute_update(query, (TaskSection.DAILY.value,), self.db_path)
            logger.info(f"每日任务重置完成: 重置了{affected}个任务")
            return affected
        except Exception as e:
            logger.error(f"重置每日任务失败: {e}")
            return 0

    def reset_weekly_tasks(self, weekday: int) -> int:
        """重置周常任务（优化时间和星期验证）"""
        if not validate_weekday(weekday):
            logger.warning(f"无效的星期数: {weekday}")
            return 0

        try:
            query = """
                UPDATE tasks 
                SET is_completed = 0, completed_at = NULL
                WHERE section = ? 
                AND reset_weekday = ?
                AND deleted_at IS NULL 
                AND is_completed = 1
            """
            affected = execute_update(query, (TaskSection.WEEKLY.value, weekday), self.db_path)
            logger.info(f"周常任务重置完成: 星期{weekday}, 重置了{affected}个任务")
            return affected
        except Exception as e:
            logger.error(f"重置周常任务失败: {e}")
            return 0

    def get_app_state(self, key: str) -> str:
        """获取应用状态（优化参数验证）"""
        key = key.strip()
        if not key:
            return ""

        try:
            query = "SELECT value FROM app_state WHERE key = ? LIMIT 1"
            results = execute_query(query, (key,), self.db_path)
            return results[0]["value"] if results else ""
        except Exception as e:
            logger.error(f"获取应用状态失败: {e}")
            return ""

    def set_app_state(self, key: str, value: str) -> bool:
        """设置应用状态（优化参数验证）"""
        key = key.strip()
        value = value.strip()
        if not key:
            logger.warning("状态键不能为空")
            return False

        try:
            query = """
                INSERT OR REPLACE INTO app_state (key, value) 
                VALUES (?, ?)
            """
            affected = execute_update(query, (key, value), self.db_path)
            success = affected > 0
            if success:
                logger.debug(f"应用状态设置成功: {key}={value}")
            return success
        except Exception as e:
            logger.error(f"设置应用状态失败: {e}")
            return False

    # ========== 回收站操作 ==========
    def get_deleted_tasks(self) -> List[Dict]:
        """获取已删除任务（优化批量标签查询）"""
        try:
            query = """
                SELECT * FROM tasks 
                WHERE deleted_at IS NOT NULL
                ORDER BY deleted_at DESC
            """
            tasks = execute_query(query, (), self.db_path)

            # 批量获取标签
            task_ids = [task["id"] for task in tasks]
            tag_map = self._get_task_tags_batch(task_ids)
            for task in tasks:
                task["tags"] = tag_map.get(task["id"], [])

            return tasks
        except Exception as e:
            logger.error(f"获取已删除任务失败: {e}")
            return []

    def empty_recycle_bin(self) -> int:
        """清空回收站，永久删除所有已删除的任务
        
        Returns:
            int: 删除的任务数量
        """
        try:
            # 先获取数量
            count_query = "SELECT COUNT(*) as count FROM tasks WHERE deleted_at IS NOT NULL"
            result = execute_query(count_query, (), self.db_path)
            count = result[0]["count"] if result else 0
            
            if count > 0:
                # 删除所有已删除的任务
                delete_query = "DELETE FROM tasks WHERE deleted_at IS NOT NULL"
                execute_update(delete_query, (), self.db_path)
                logger.info(f"清空回收站成功: 删除了{count}个任务")
            
            return count
        except Exception as e:
            logger.error(f"清空回收站失败: {e}")
            return 0

    def delete_older_than(self, days: int) -> int:
        """删除早于指定天数的任务（优化参数验证）"""
        if not isinstance(days, int) or days < 1:
            logger.warning(f"无效的天数: {days}")
            return 0

        try:
            cutoff_date = safe_isoformat(datetime.now() - timedelta(days=days))
            query = """
                DELETE FROM tasks 
                WHERE deleted_at IS NOT NULL 
                AND deleted_at < ?
            """
            affected = execute_update(query, (cutoff_date,), self.db_path)
            logger.info(f"删除早于{days}天的已删除任务: 删除了{affected}个任务")
            return affected
        except Exception as e:
            logger.error(f"删除旧任务失败: {e}")
            return 0

    def keep_latest_n(self, limit: int) -> int:
        """保留最新N个已删除任务（修复SQL注入风险）"""
        if not isinstance(limit, int) or limit < 0:
            logger.warning(f"无效的保留数量: {limit}")
            return 0

        try:
            # 安全获取需要删除的任务ID
            query = """
                SELECT id FROM tasks 
                WHERE deleted_at IS NOT NULL
                ORDER BY deleted_at DESC
                LIMIT -1 OFFSET ?
            """
            results = execute_query(query, (limit,), self.db_path)
            task_ids = [row["id"] for row in results]

            if not task_ids:
                return 0

            # 安全生成IN子句
            ids_str = escape_sql_in_list(task_ids)
            delete_query = f"DELETE FROM tasks WHERE id IN {ids_str}"
            affected = execute_update(delete_query, (), self.db_path)

            logger.info(f"保留最新{limit}个已删除任务: 删除了{affected}个任务")
            return affected
        except Exception as e:
            logger.error(f"保留最新任务失败: {e}")
            return 0

    # ========== 辅助方法 ==========
    def _batch_add_task_tags(self, task_id: int, tags: List[str]) -> None:
        """批量添加任务标签（提升性能）"""
        if not tags or not isinstance(task_id, int) or task_id <= 0:
            return

        # 批量获取/创建标签ID
        tag_params = []
        for tag_name in tags:
            tag_name = tag_name.strip()
            if not tag_name:
                continue
            tag_id = self.add_tag(tag_name)
            if tag_id != -1:
                tag_params.append((task_id, tag_id))

        # 批量插入标签关联
        if tag_params:
            query = "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)"
            execute_many(query, tag_params, self.db_path)

    def _remove_all_task_tags(self, task_id: int) -> None:
        """移除任务所有标签（优化参数验证）"""
        if not isinstance(task_id, int) or task_id <= 0:
            return

        try:
            query = "DELETE FROM task_tags WHERE task_id = ?"
            execute_update(query, (task_id,), self.db_path)
        except Exception as e:
            logger.error(f"移除任务所有标签失败: {e}")

    def _get_task_tags_batch(self, task_ids: List[int]) -> Dict[int, List[str]]:
        """批量获取多个任务的标签（减少SQL查询）"""
        if not task_ids:
            return {}

        try:
            ids_str = escape_sql_in_list(task_ids)
            query = f"""
                SELECT tt.task_id, t.name 
                FROM tags t
                JOIN task_tags tt ON t.id = tt.tag_id
                WHERE tt.task_id IN {ids_str}
            """
            results = execute_query(query, (), self.db_path)

            # 构建标签映射
            tag_map = {task_id: [] for task_id in task_ids}
            for row in results:
                tag_map[row["task_id"]].append(row["name"])

            return tag_map
        except Exception as e:
            logger.error(f"批量获取任务标签失败: {e}")
            return {}

    def get_all_tags(self) -> List[Dict]:
        """获取所有标签（优化排序）"""
        try:
            query = "SELECT * FROM tags ORDER BY LOWER(name)"  # 不区分大小写排序
            return execute_query(query, (), self.db_path)
        except Exception as e:
            logger.error(f"获取所有标签失败: {e}")
            return []
    
    def get_all_tag_names(self) -> List[str]:
        """获取所有标签名称列表"""
        try:
            query = "SELECT name FROM tags ORDER BY LOWER(name)"
            results = execute_query(query, (), self.db_path)
            return [row["name"] for row in results]
        except Exception as e:
            logger.error(f"获取标签名称列表失败: {e}")
            return []
    
    def cleanup_unused_tags(self) -> int:
        """清理没有被任何任务使用的标签
        
        Returns:
            int: 删除的标签数量
        """
        try:
            # 查找没有关联任务的标签
            query = """
                SELECT t.id FROM tags t
                LEFT JOIN task_tags tt ON t.id = tt.tag_id
                WHERE tt.task_id IS NULL
            """
            results = execute_query(query, (), self.db_path)
            
            if not results:
                return 0
            
            # 删除这些标签
            tag_ids = [row["id"] for row in results]
            ids_str = escape_sql_in_list(tag_ids)
            delete_query = f"DELETE FROM tags WHERE id IN {ids_str}"
            affected = execute_update(delete_query, (), self.db_path)
            
            if affected > 0:
                logger.info(f"清理了 {affected} 个未使用的标签")
            
            return affected
        except Exception as e:
            logger.error(f"清理未使用标签失败: {e}")
            return 0
            return []

    def get_all_tags_with_task_count(self) -> List[Dict]:
        """获取所有标签及其任务数（优化JOIN查询）"""
        try:
            query = """
                SELECT 
                    t.id,
                    t.name,
                    COUNT(tt.task_id) as task_count
                FROM tags t
                LEFT JOIN task_tags tt ON t.id = tt.tag_id
                GROUP BY t.id, t.name
                ORDER BY LOWER(t.name)
            """
            results = execute_query(query, (), self.db_path)
            
            # 确保task_count是整数类型
            for row in results:
                row["task_count"] = int(row["task_count"]) if row["task_count"] else 0
            
            return results
        except Exception as e:
            logger.error(f"获取标签及任务数失败: {e}")
            return []

    def get_task_count_by_section(self) -> Dict[str, Dict[str, int]]:
        """按分区统计任务（优化SQL查询）"""
        try:
            # 单次查询获取所有统计数据（减少SQL调用）
            query = """
                SELECT 
                    section,
                    is_completed,
                    COUNT(*) as count
                FROM tasks 
                WHERE deleted_at IS NULL
                GROUP BY section, is_completed
            """
            results = execute_query(query, (), self.db_path)

            # 初始化统计结果
            stats = {
                section.value: {"pending": 0, "completed": 0, "total": 0}
                for section in TaskSection
            }

            # 填充统计数据
            for row in results:
                section = row["section"]
                if section not in stats:
                    continue
                if row["is_completed"] == 0:
                    stats[section]["pending"] = row["count"]
                else:
                    stats[section]["completed"] = row["count"]
                stats[section]["total"] = stats[section]["pending"] + stats[section]["completed"]

            return stats
        except Exception as e:
            logger.error(f"统计任务数量失败: {e}")
            return {}