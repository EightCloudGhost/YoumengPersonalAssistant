from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QWidget, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta
from core.task_manager import TaskManager
from utils.logger import logger
from ui.styles.qq_style import QQStyle


class RecycleBinDialog(QDialog):
    """回收站对话框"""
    
    # 信号定义
    task_restored = pyqtSignal(int)  # task_id
    task_permanently_deleted = pyqtSignal(int)  # task_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("回收站")
        self.setModal(True)
        self.setMinimumSize(900, 650)
        
        # 应用统一样式
        self.setStyleSheet(QQStyle.get_dialog_style())
        
        # 初始化任务管理器
        self.task_manager = TaskManager()
        
        # 当前选中的任务ID
        self.current_selected_task_id = None
        
        self._setup_ui()
        self._load_deleted_tasks()
        
    def _setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("🗑️ 回收站")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 统计信息
        self.stats_label = QLabel("已删除任务: 0 个")
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：任务列表
        self.task_list_widget = QListWidget()
        self.task_list_widget.itemClicked.connect(self._on_task_clicked)
        self.splitter.addWidget(self.task_list_widget)
        
        # 右侧：任务详情
        self.detail_widget = self._create_detail_widget()
        self.splitter.addWidget(self.detail_widget)
        
        # 设置分割器比例
        self.splitter.setSizes([400, 400])
        
        layout.addWidget(self.splitter, 1)  # 拉伸因子为1
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 恢复按钮
        self.restore_btn = QPushButton("恢复")
        self.restore_btn.setEnabled(False)
        self.restore_btn.clicked.connect(self._on_restore)
        button_layout.addWidget(self.restore_btn)
        
        # 永久删除按钮
        self.delete_btn = QPushButton("永久删除")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._on_delete_permanently)
        button_layout.addWidget(self.delete_btn)
        
        # 清空回收站按钮
        self.empty_btn = QPushButton("清空回收站")
        self.empty_btn.clicked.connect(self._on_empty_bin)
        button_layout.addWidget(self.empty_btn)
        
        # 关闭按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
    def _create_detail_widget(self) -> QWidget:
        """创建任务详情部件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # 详情标题
        detail_title = QLabel("任务详情")
        detail_font = QFont()
        detail_font.setPointSize(12)
        detail_font.setBold(True)
        detail_title.setFont(detail_font)
        layout.addWidget(detail_title)
        
        # 详情内容
        self.detail_content = QLabel("选择任务以查看详情")
        self.detail_content.setWordWrap(True)
        self.detail_content.setAlignment(Qt.AlignTop)
        layout.addWidget(self.detail_content, 1)  # 拉伸因子为1
        
        # 删除信息
        delete_info_group = QGroupBox("删除信息")
        delete_layout = QFormLayout(delete_info_group)
        
        self.deleted_at_label = QLabel("")
        delete_layout.addRow("删除时间:", self.deleted_at_label)
        
        self.deleted_by_label = QLabel("")
        delete_layout.addRow("删除方式:", self.deleted_by_label)
        
        layout.addWidget(delete_info_group)
        
        return widget
    
    def _load_deleted_tasks(self):
        """加载已删除的任务"""
        try:
            self.task_list_widget.clear()
            
            # 获取已删除的任务
            deleted_tasks = self.task_manager.get_deleted_tasks()
            
            # 添加任务到列表
            for task in deleted_tasks:
                task_id = task.get("id", -1)
                title = task.get("title", "未命名任务")
                deleted_at = task.get("deleted_at", "")
                
                # 创建列表项
                item_text = f"{title}"
                if deleted_at:
                    item_text += f" ({deleted_at})"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, task_id)  # 存储任务ID
                
                # 根据删除时间设置颜色
                self._set_item_color(item, deleted_at)
                
                self.task_list_widget.addItem(item)
            
            # 更新统计信息
            self._update_stats(len(deleted_tasks))
            
        except Exception as e:
            logger.error(f"加载已删除任务失败: {e}")
            QMessageBox.critical(self, "错误", f"加载已删除任务失败: {str(e)}")
    
    def _set_item_color(self, item: QListWidgetItem, deleted_at: str):
        """根据删除时间设置列表项颜色"""
        try:
            if not deleted_at:
                item.setForeground(QColor(128, 128, 128))  # 默认灰色
                return
            
            # 解析删除时间
            deleted_time = datetime.fromisoformat(deleted_at.replace("T", " ").split(".")[0])
            days_since_delete = (datetime.now() - deleted_time).days
            
            # 根据删除天数设置不同颜色
            if days_since_delete <= 7:
                # 7天内 - 橙色（可恢复提示）
                item.setForeground(QColor(QQStyle.ACCENT_ORANGE))
            elif days_since_delete <= 30:
                # 30天内 - 灰色
                item.setForeground(QColor(128, 128, 128))
            else:
                # 30天以上 - 深灰色（即将自动清理）
                item.setForeground(QColor(80, 80, 80))
                
        except Exception:
            item.setForeground(QColor(128, 128, 128))  # 解析失败用默认灰色
    
    def _update_stats(self, task_count: int):
        """更新统计信息"""
        self.stats_label.setText(f"已删除任务: {task_count} 个")
        
        # 更新按钮状态
        self.empty_btn.setEnabled(task_count > 0)
    
    def _on_task_clicked(self, item):
        """任务点击事件"""
        try:
            task_id = item.data(Qt.UserRole)
            self.current_selected_task_id = task_id
            
            # 获取任务详情
            task = self.task_manager.get_task(task_id, include_deleted=True)
            if task:
                self._show_task_detail(task)
                self.restore_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                
        except Exception as e:
            logger.error(f"显示任务详情失败: {e}")
    
    def _show_task_detail(self, task: dict):
        """显示任务详情"""
        try:
            # 构建详情HTML
            title = task.get("title", "未命名任务")
            description = task.get("description", "")
            requirements = task.get("requirements", "")
            priority = task.get("priority", 1)
            section = task.get("section", "daily")
            created_at = task.get("created_at", "")
            deleted_at = task.get("deleted_at", "")
            tags = task.get("tags", [])
            
            # 格式化创建时间
            if created_at and "." in created_at:
                created_at = created_at.split(".")[0]
            if created_at and "T" in created_at:
                created_at = created_at.replace("T", " ")
            
            # 分区显示名称
            section_names = {
                "daily": "日常任务",
                "weekly": "周常任务",
                "once": "特殊任务"
            }
            section_display = section_names.get(section, "未知分区")
            
            # 优先级显示
            priority_names = {
                3: ("紧急", QQStyle.DANGER),
                2: ("优先", QQStyle.ACCENT_ORANGE),
                1: ("普通", QQStyle.PRIMARY),
                0: ("建议", QQStyle.TEXT_SECONDARY)
            }
            priority_text, priority_color = priority_names.get(priority, ("普通", QQStyle.PRIMARY))
            
            # 构建HTML内容
            html = f"""
            <h3 style="color: {QQStyle.TEXT_PRIMARY};">{title}</h3>
            <hr>
            <p><strong>分区:</strong> {section_display}</p>
            <p><strong>优先级:</strong> <span style="color: {priority_color}; font-weight: bold;">{priority_text}</span></p>
            <p><strong>创建时间:</strong> {created_at if created_at else '暂无'}</p>
            """
            
            if description:
                html += f'<p><strong>描述:</strong><br>{description}</p>'
            else:
                html += f'<p><strong>描述:</strong> <span style="color: {QQStyle.TEXT_PLACEHOLDER};">暂无</span></p>'
            
            if requirements:
                html += f'<p><strong>要求:</strong><br>{requirements}</p>'
            else:
                html += f'<p><strong>要求:</strong> <span style="color: {QQStyle.TEXT_PLACEHOLDER};">暂无</span></p>'
            
            if tags:
                tags_html = " ".join([f'<span style="background-color:#e0e0e0;padding:2px 8px;border-radius:8px;margin:2px;">{tag}</span>' for tag in tags])
                html += f'<p><strong>标签:</strong><br>{tags_html}</p>'
            else:
                html += f'<p><strong>标签:</strong> <span style="color: {QQStyle.TEXT_PLACEHOLDER};">暂无</span></p>'
            
            self.detail_content.setText(html)
            
            # 更新删除信息
            if deleted_at and "T" in deleted_at:
                deleted_at = deleted_at.replace("T", " ").split(".")[0]
            self.deleted_at_label.setText(deleted_at)
            self.deleted_by_label.setText("手动删除")
            
        except Exception as e:
            logger.error(f"显示任务详情失败: {e}")
            self.detail_content.setText("加载任务详情失败")
    
    def _on_restore(self):
        """恢复任务"""
        try:
            if not self.current_selected_task_id:
                return
            
            # 确认恢复
            reply = QMessageBox.question(
                self,
                "确认恢复",
                "确定要恢复这个任务吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 恢复任务
                success = self.task_manager.restore_task(self.current_selected_task_id)
                
                if success:
                    # 发射信号
                    self.task_restored.emit(self.current_selected_task_id)
                    
                    # 更新UI
                    self._remove_current_task_from_list()
                    self._clear_detail()
                    
                    QMessageBox.information(self, "成功", "任务已恢复")
                    
        except Exception as e:
            logger.error(f"恢复任务失败: {e}")
            QMessageBox.critical(self, "错误", f"恢复任务失败: {str(e)}")
    
    def _on_delete_permanently(self):
        """永久删除任务"""
        try:
            if not self.current_selected_task_id:
                return
            
            # 确认永久删除
            reply = QMessageBox.question(
                self,
                "确认永久删除",
                "确定要永久删除这个任务吗？\n\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 永久删除任务
                success = self.task_manager.permanent_delete_task(self.current_selected_task_id)
                
                if success:
                    # 发射信号
                    self.task_permanently_deleted.emit(self.current_selected_task_id)
                    
                    # 更新UI
                    self._remove_current_task_from_list()
                    self._clear_detail()
                    
                    QMessageBox.information(self, "成功", "任务已永久删除")
                    
        except Exception as e:
            logger.error(f"永久删除任务失败: {e}")
            QMessageBox.critical(self, "错误", f"永久删除任务失败: {str(e)}")
    
    def _on_empty_bin(self):
        """清空回收站"""
        try:
            # 确认清空
            reply = QMessageBox.question(
                self,
                "确认清空回收站",
                "确定要清空回收站吗？\n\n所有已删除的任务将被永久删除，此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 清空回收站
                count = self.task_manager.empty_recycle_bin()
                
                # 清空列表
                self.task_list_widget.clear()
                self._clear_detail()
                self._update_stats(0)
                
                QMessageBox.information(self, "成功", f"回收站已清空，删除了 {count} 个任务")
                    
        except Exception as e:
            logger.error(f"清空回收站失败: {e}")
            QMessageBox.critical(self, "错误", f"清空回收站失败: {str(e)}")
    
    def _remove_current_task_from_list(self):
        """从列表中移除当前选中的任务"""
        current_item = self.task_list_widget.currentItem()
        if current_item:
            row = self.task_list_widget.row(current_item)
            self.task_list_widget.takeItem(row)
            
            # 更新统计
            task_count = self.task_list_widget.count()
            self._update_stats(task_count)
    
    def _clear_detail(self):
        """清除详情显示"""
        self.current_selected_task_id = None
        self.detail_content.setText("选择任务以查看详情")
        self.deleted_at_label.setText("")
        self.deleted_by_label.setText("")
        self.restore_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
    
    @staticmethod
    def show_recycle_bin(parent=None):
        """静态方法：显示回收站对话框"""
        dialog = RecycleBinDialog(parent)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            return True
        return False