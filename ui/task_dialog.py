from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QSpinBox, QCheckBox, QPushButton, QLabel,
    QDialogButtonBox, QWidget, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime, date
from data.models import TaskSection
from ui.styles.qq_style import QQStyle


class TaskDialog(QDialog):
    """任务对话框（添加/编辑任务）"""
    
    def __init__(self, task_data=None, parent=None):
        """
        初始化任务对话框
        
        Args:
            task_data: 任务数据字典（编辑时传入）
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.task_data = task_data or {}
        self.is_edit_mode = bool(task_data)
        
        self._setup_ui()
        self._load_task_data()
        self._connect_signals()
        
        # 设置窗口属性
        self.setWindowTitle("编辑任务" if self.is_edit_mode else "添加任务")
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        self.setModal(True)
        
        # 应用统一样式
        self.setStyleSheet(QQStyle.get_dialog_style())
    
    def _setup_ui(self):
        """设置UI布局"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(10)
        
        # 标题
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("请输入任务标题")
        form_layout.addRow("标题：", self.title_edit)
        
        # 分区
        self.section_combo = QComboBox()
        self.section_combo.addItem("日常任务", "daily")
        self.section_combo.addItem("周常任务", "weekly")
        self.section_combo.addItem("特殊任务", "once")
        form_layout.addRow("分区：", self.section_combo)
        
        # 描述
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        self.desc_edit.setPlaceholderText("请输入任务描述（可选）")
        form_layout.addRow("描述：", self.desc_edit)
        
        # 截止日期（仅特殊任务显示）
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))
        self.due_date_edit.setMinimumDate(QDate.currentDate())
        self.due_date_label = QLabel("截止日期：")
        form_layout.addRow(self.due_date_label, self.due_date_edit)
        
        # 重置星期（仅周常任务显示）
        self.reset_weekday_combo = QComboBox()
        self.reset_weekday_combo.addItem("星期一", 0)
        self.reset_weekday_combo.addItem("星期二", 1)
        self.reset_weekday_combo.addItem("星期三", 2)
        self.reset_weekday_combo.addItem("星期四", 3)
        self.reset_weekday_combo.addItem("星期五", 4)
        self.reset_weekday_combo.addItem("星期六", 5)
        self.reset_weekday_combo.addItem("星期日", 6)
        self.reset_weekday_label = QLabel("重置星期：")
        form_layout.addRow(self.reset_weekday_label, self.reset_weekday_combo)
        
        # 排序顺序
        self.sort_spin = QSpinBox()
        self.sort_spin.setRange(0, 999)
        self.sort_spin.setValue(0)
        form_layout.addRow("排序：", self.sort_spin)
        
        # 标签
        tags_widget = QWidget()
        tags_layout = QVBoxLayout(tags_widget)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(8)
        
        # 标签输入和添加按钮
        tag_input_layout = QHBoxLayout()
        tag_input_layout.setSpacing(10)
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("输入标签名称，按回车或点击添加")
        self.tag_edit.setMinimumHeight(36)
        tag_input_layout.addWidget(self.tag_edit)
        
        self.add_tag_btn = QPushButton("添加标签")
        self.add_tag_btn.setFixedSize(90, 36)
        self.add_tag_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.ACCENT_TEAL};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00796B;
            }}
        """)
        tag_input_layout.addWidget(self.add_tag_btn)
        tags_layout.addLayout(tag_input_layout)
        
        # 标签列表 - 增大高度和清晰度
        self.tags_list = QListWidget()
        self.tags_list.setMinimumHeight(100)
        self.tags_list.setMaximumHeight(120)
        self.tags_list.setStyleSheet(f"""
            QListWidget {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                background-color: {QQStyle.BG_LIGHT};
                font-size: 15px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QListWidget::item:hover {{
                background-color: {QQStyle.PRIMARY_LIGHT};
            }}
            QListWidget::item:selected {{
                background-color: {QQStyle.PRIMARY};
                color: white;
            }}
        """)
        tags_layout.addWidget(self.tags_list)
        
        # 删除标签按钮
        self.remove_tag_btn = QPushButton("删除选中标签")
        self.remove_tag_btn.setFixedSize(120, 32)
        self.remove_tag_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.DANGER_LIGHT};
                color: {QQStyle.DANGER};
                border: 1px solid {QQStyle.DANGER};
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {QQStyle.DANGER};
                color: white;
            }}
        """)
        tags_layout.addWidget(self.remove_tag_btn, 0, Qt.AlignLeft)
        
        form_layout.addRow("标签：", tags_widget)
        
        main_layout.addLayout(form_layout)
        
        # 按钮区域
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        main_layout.addWidget(button_box)
        
        # 初始隐藏相关字段
        self._update_visibility()
    
    def _load_task_data(self):
        """加载任务数据到表单"""
        if not self.task_data:
            return
        
        # 标题
        self.title_edit.setText(self.task_data.get("title", ""))
        
        # 分区
        section = self.task_data.get("section", "daily")
        index = self.section_combo.findData(section)
        if index >= 0:
            self.section_combo.setCurrentIndex(index)
        
        # 描述
        self.desc_edit.setPlainText(self.task_data.get("description", ""))
        
        # 截止日期
        due_date = self.task_data.get("due_date")
        if due_date:
            try:
                if isinstance(due_date, str):
                    due_date_obj = date.fromisoformat(due_date)
                else:
                    due_date_obj = due_date
                qdate = QDate(due_date_obj.year, due_date_obj.month, due_date_obj.day)
                self.due_date_edit.setDate(qdate)
            except (ValueError, TypeError, AttributeError):
                pass  # 日期格式无效时使用默认值
        
        # 重置星期
        reset_weekday = self.task_data.get("reset_weekday")
        if reset_weekday is not None:
            index = self.reset_weekday_combo.findData(reset_weekday)
            if index >= 0:
                self.reset_weekday_combo.setCurrentIndex(index)
        
        # 排序
        sort_order = self.task_data.get("sort_order", 0)
        self.sort_spin.setValue(sort_order)
        
        # 标签
        tags = self.task_data.get("tags", [])
        for tag in tags:
            self.tags_list.addItem(tag)
    
    def _connect_signals(self):
        """连接信号"""
        # 分区改变时更新可见性
        self.section_combo.currentIndexChanged.connect(self._update_visibility)
        
        # 标签相关信号
        self.tag_edit.returnPressed.connect(self._add_tag)
        self.add_tag_btn.clicked.connect(self._add_tag)
        self.remove_tag_btn.clicked.connect(self._remove_selected_tag)
    
    def _update_visibility(self):
        """根据分区更新字段可见性"""
        section = self.section_combo.currentData()
        
        # 特殊任务：显示截止日期，隐藏重置星期
        if section == "once":
            self.due_date_label.setVisible(True)
            self.due_date_edit.setVisible(True)
            self.reset_weekday_label.setVisible(False)
            self.reset_weekday_combo.setVisible(False)
        
        # 周常任务：显示重置星期，隐藏截止日期
        elif section == "weekly":
            self.due_date_label.setVisible(False)
            self.due_date_edit.setVisible(False)
            self.reset_weekday_label.setVisible(True)
            self.reset_weekday_combo.setVisible(True)
        
        # 日常任务：都隐藏
        else:
            self.due_date_label.setVisible(False)
            self.due_date_edit.setVisible(False)
            self.reset_weekday_label.setVisible(False)
            self.reset_weekday_combo.setVisible(False)
    
    def _add_tag(self):
        """添加标签"""
        tag_text = self.tag_edit.text().strip()
        if not tag_text:
            return
        
        # 检查是否已存在
        existing_items = [
            self.tags_list.item(i).text() 
            for i in range(self.tags_list.count())
        ]
        
        if tag_text not in existing_items:
            self.tags_list.addItem(tag_text)
        
        self.tag_edit.clear()
    
    def _remove_selected_tag(self):
        """删除选中的标签"""
        selected_items = self.tags_list.selectedItems()
        for item in selected_items:
            row = self.tags_list.row(item)
            self.tags_list.takeItem(row)
    
    def get_task_data(self) -> dict:
        """
        获取任务数据
        
        Returns:
            dict: 任务数据字典
        """
        # 基本数据
        task_data = {
            "title": self.title_edit.text().strip(),
            "section": self.section_combo.currentData(),
            "description": self.desc_edit.toPlainText().strip(),
            "sort_order": self.sort_spin.value(),
            "tags": [
                self.tags_list.item(i).text() 
                for i in range(self.tags_list.count())
            ]
        }
        
        # 分区特定数据
        section = task_data["section"]
        
        if section == "once":
            # 特殊任务：截止日期
            qdate = self.due_date_edit.date()
            task_data["due_date"] = date(qdate.year(), qdate.month(), qdate.day())
        
        elif section == "weekly":
            # 周常任务：重置星期
            task_data["reset_weekday"] = self.reset_weekday_combo.currentData()
        
        # 如果是编辑模式，保留ID
        if self.is_edit_mode and "id" in self.task_data:
            task_data["id"] = self.task_data["id"]
        
        return task_data
    
    def validate_input(self) -> bool:
        """验证输入"""
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.setFocus()
            return False
        
        return True
    
    def accept(self):
        """接受对话框"""
        if self.validate_input():
            super().accept()
    
    @staticmethod
    def get_task(parent=None, task_data=None) -> dict:
        """
        静态方法：显示对话框并获取任务数据
        
        Args:
            parent: 父窗口
            task_data: 任务数据字典（编辑时传入）
            
        Returns:
            dict: 任务数据字典，用户取消返回空字典
        """
        dialog = TaskDialog(task_data, parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_task_data()
        return {}