# -*- coding: utf-8 -*-
"""
任务表单组件 - 可嵌入右侧面板
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QComboBox, QDateEdit,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QGroupBox, QButtonGroup
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from datetime import date

from ..styles.qq_style import QQStyle
from utils.resource import Icons


class TaskFormWidget(QWidget):
    """任务表单组件 - 用于添加/编辑任务"""
    
    # 信号
    task_submitted = pyqtSignal(dict)  # 提交任务数据
    form_cancelled = pyqtSignal()  # 取消
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.task_data = {}  # 编辑模式时的任务数据
        self.is_edit_mode = False
        self.all_tags = []  # 所有可用标签
        
        self._setup_ui()
        self._connect_signals()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 5, 0)
        main_layout.setSpacing(0)
        
        # 可滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 表单容器
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(10, 5, 15, 10)
        form_layout.setSpacing(14)
        
        # ===== 1. 标题 =====
        title_label = QLabel("标题")
        title_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {QQStyle.TEXT_PRIMARY};")
        form_layout.addWidget(title_label)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("请输入任务标题")
        self.title_edit.setMinimumHeight(40)
        form_layout.addWidget(self.title_edit)
        
        # ===== 2. 描述 =====
        desc_label = QLabel("描述")
        desc_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {QQStyle.TEXT_PRIMARY};")
        form_layout.addWidget(desc_label)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(70)
        self.desc_edit.setPlaceholderText("请输入任务描述（可选）")
        form_layout.addWidget(self.desc_edit)
        
        # ===== 3. 要求 =====
        req_label = QLabel("要求")
        req_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {QQStyle.TEXT_PRIMARY};")
        form_layout.addWidget(req_label)
        
        self.requirements_edit = QTextEdit()
        self.requirements_edit.setMaximumHeight(70)
        self.requirements_edit.setPlaceholderText("请输入任务要求（可选）")
        form_layout.addWidget(self.requirements_edit)
        
        # ===== 4. 任务类别（原分区）=====
        category_label = QLabel("任务类别")
        category_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {QQStyle.TEXT_PRIMARY};")
        form_layout.addWidget(category_label)
        
        self.section_combo = QComboBox()
        self.section_combo.addItem("日常任务", "daily")
        self.section_combo.addItem("周常任务", "weekly")
        self.section_combo.addItem("特殊任务", "once")  # 改名：一次性→特殊
        self.section_combo.setMinimumHeight(40)
        form_layout.addWidget(self.section_combo)
        
        # 截止日期（仅特殊任务显示）
        self.due_date_label = QLabel("截止日期")
        self.due_date_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {QQStyle.TEXT_PRIMARY};")
        form_layout.addWidget(self.due_date_label)
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))
        self.due_date_edit.setMinimumDate(QDate.currentDate())
        self.due_date_edit.setMinimumHeight(40)
        form_layout.addWidget(self.due_date_edit)
        
        # 重置星期（仅周常任务显示）
        self.reset_weekday_label = QLabel("重置星期")
        self.reset_weekday_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {QQStyle.TEXT_PRIMARY};")
        form_layout.addWidget(self.reset_weekday_label)
        
        self.reset_weekday_combo = QComboBox()
        self.reset_weekday_combo.addItem("星期一", 0)
        self.reset_weekday_combo.addItem("星期二", 1)
        self.reset_weekday_combo.addItem("星期三", 2)
        self.reset_weekday_combo.addItem("星期四", 3)
        self.reset_weekday_combo.addItem("星期五", 4)
        self.reset_weekday_combo.addItem("星期六", 5)
        self.reset_weekday_combo.addItem("星期日", 6)
        self.reset_weekday_combo.setMinimumHeight(40)
        form_layout.addWidget(self.reset_weekday_combo)
        
        # 优先级选择按钮
        priority_label = QLabel("优先级")
        priority_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {QQStyle.TEXT_PRIMARY};")
        form_layout.addWidget(priority_label)
        
        priority_layout = QHBoxLayout()
        priority_layout.setSpacing(8)
        
        self.priority_btn_group = QButtonGroup(self)
        self.priority_btn_group.setExclusive(True)
        
        priority_options = [
            ("紧急", 3, QQStyle.DANGER),
            ("优先", 2, QQStyle.ACCENT_ORANGE),
            ("普通", 1, QQStyle.PRIMARY),
            ("建议", 0, QQStyle.TEXT_SECONDARY),
        ]
        
        for text, value, color in priority_options:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setMinimumHeight(36)
            btn.setMinimumWidth(60)
            btn.setProperty("priority_value", value)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {QQStyle.BG_LIGHT};
                    color: {QQStyle.TEXT_REGULAR};
                    border: 2px solid {QQStyle.BORDER};
                    border-radius: 6px;
                    font-size: 13px;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    border-color: {color};
                    color: {color};
                }}
                QPushButton:checked {{
                    background-color: {color};
                    color: white;
                    border-color: {color};
                }}
            """)
            self.priority_btn_group.addButton(btn, value)
            priority_layout.addWidget(btn)
        
        priority_layout.addStretch()
        form_layout.addLayout(priority_layout)
        
        # 默认选择普通
        if self.priority_btn_group.button(1):
            self.priority_btn_group.button(1).setChecked(True)
        
        # ===== 5. 标签 =====
        tags_group = QGroupBox("标签")
        tags_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                color: {QQStyle.TEXT_PRIMARY};
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        tags_layout = QVBoxLayout(tags_group)
        tags_layout.setSpacing(10)
        
        # 已选标签
        selected_label = QLabel("已选标签")
        selected_label.setStyleSheet(f"font-size: 13px; color: {QQStyle.TEXT_SECONDARY}; font-weight: normal;")
        tags_layout.addWidget(selected_label)
        
        self.selected_tags_list = QListWidget()
        self.selected_tags_list.setMaximumHeight(70)
        self.selected_tags_list.setSelectionMode(QListWidget.MultiSelection)
        tags_layout.addWidget(self.selected_tags_list)
        
        # 移除已选标签按钮
        self.remove_tag_btn = QPushButton("移除选中")
        self.remove_tag_btn.setFixedWidth(90)
        self.remove_tag_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.DANGER_LIGHT};
                color: {QQStyle.DANGER};
                border: 1px solid {QQStyle.DANGER};
                border-radius: 4px;
                font-size: 12px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {QQStyle.DANGER};
                color: white;
            }}
        """)
        tags_layout.addWidget(self.remove_tag_btn, 0, Qt.AlignLeft)
        
        # 待选标签（已有标签）
        available_label = QLabel("可选标签（点击添加）")
        available_label.setStyleSheet(f"font-size: 13px; color: {QQStyle.TEXT_SECONDARY}; font-weight: normal;")
        tags_layout.addWidget(available_label)
        
        self.available_tags_list = QListWidget()
        self.available_tags_list.setMaximumHeight(70)
        self.available_tags_list.setSelectionMode(QListWidget.MultiSelection)
        tags_layout.addWidget(self.available_tags_list)
        
        # 添加已选标签按钮
        self.add_selected_tag_btn = QPushButton("添加选中")
        self.add_selected_tag_btn.setFixedWidth(90)
        self.add_selected_tag_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.PRIMARY_LIGHT};
                color: {QQStyle.PRIMARY};
                border: 1px solid {QQStyle.PRIMARY};
                border-radius: 4px;
                font-size: 12px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {QQStyle.PRIMARY};
                color: white;
            }}
        """)
        tags_layout.addWidget(self.add_selected_tag_btn, 0, Qt.AlignLeft)
        
        # 新建标签
        new_tag_label = QLabel("新建标签")
        new_tag_label.setStyleSheet(f"font-size: 13px; color: {QQStyle.TEXT_SECONDARY}; font-weight: normal;")
        tags_layout.addWidget(new_tag_label)
        
        new_tag_layout = QHBoxLayout()
        new_tag_layout.setSpacing(8)
        
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("输入新标签名称")
        self.tag_edit.setMinimumHeight(34)
        new_tag_layout.addWidget(self.tag_edit)
        
        self.add_new_tag_btn = QPushButton("创建")
        self.add_new_tag_btn.setFixedSize(60, 34)
        self.add_new_tag_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.ACCENT_TEAL};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #00796B;
            }}
        """)
        new_tag_layout.addWidget(self.add_new_tag_btn)
        tags_layout.addLayout(new_tag_layout)
        
        form_layout.addWidget(tags_group)
        
        form_layout.addStretch()
        
        scroll.setWidget(form_container)
        main_layout.addWidget(scroll, 1)
        
        # 底部按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(10, 16, 10, 0)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_REGULAR};
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                font-size: 15px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                border-color: {QQStyle.PRIMARY};
                color: {QQStyle.PRIMARY};
            }}
        """)
        btn_layout.addWidget(self.cancel_btn)
        
        self.submit_btn = QPushButton("保存")
        self.submit_btn.setMinimumHeight(40)
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.PRIMARY};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {QQStyle.PRIMARY_HOVER};
            }}
        """)
        btn_layout.addWidget(self.submit_btn)
        
        main_layout.addLayout(btn_layout)
        
        # 初始更新可见性
        self._update_visibility()
    
    def _connect_signals(self):
        """连接信号"""
        self.section_combo.currentIndexChanged.connect(self._update_visibility)
        self.tag_edit.returnPressed.connect(self._add_new_tag)
        self.add_new_tag_btn.clicked.connect(self._add_new_tag)
        self.add_selected_tag_btn.clicked.connect(self._add_from_available)
        self.remove_tag_btn.clicked.connect(self._remove_selected_tags)
        self.submit_btn.clicked.connect(self._on_submit)
        self.cancel_btn.clicked.connect(self.form_cancelled.emit)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QLineEdit, QTextEdit, QComboBox, QDateEdit {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 2px solid {QQStyle.PRIMARY};
            }}
            QListWidget {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 6px;
                background-color: {QQStyle.BG_LIGHT};
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 5px 8px;
                border-radius: 4px;
                margin: 1px;
            }}
            QListWidget::item:hover {{
                background-color: {QQStyle.PRIMARY_LIGHT};
            }}
            QListWidget::item:selected {{
                background-color: {QQStyle.PRIMARY};
                color: white;
            }}
            QCheckBox {{
                font-size: 14px;
                color: {QQStyle.TEXT_PRIMARY};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {QQStyle.BORDER};
                border-radius: 4px;
                background-color: {QQStyle.WHITE};
            }}
            QCheckBox::indicator:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                border-color: {QQStyle.PRIMARY};
                background-color: {QQStyle.WHITE};
                image: url({Icons.CHECK_BLUE});
            }}
        """)
    
    def _update_visibility(self):
        """根据任务类别更新字段可见性"""
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
    
    def _add_new_tag(self):
        """创建并添加新标签"""
        tag_text = self.tag_edit.text().strip()
        if not tag_text:
            return
        
        # 检查已选列表是否已存在
        existing = [
            self.selected_tags_list.item(i).text() 
            for i in range(self.selected_tags_list.count())
        ]
        
        if tag_text not in existing:
            self.selected_tags_list.addItem(tag_text)
            # 如果是新标签，也添加到待选列表（供以后使用）
            available = [
                self.available_tags_list.item(i).text()
                for i in range(self.available_tags_list.count())
            ]
            if tag_text not in available:
                self.available_tags_list.addItem(tag_text)
        
        self.tag_edit.clear()
    
    def _add_from_available(self):
        """从待选列表添加标签"""
        selected_items = self.available_tags_list.selectedItems()
        existing = [
            self.selected_tags_list.item(i).text() 
            for i in range(self.selected_tags_list.count())
        ]
        
        for item in selected_items:
            tag_text = item.text()
            if tag_text not in existing:
                self.selected_tags_list.addItem(tag_text)
        
        # 清除选择
        self.available_tags_list.clearSelection()
    
    def _remove_selected_tags(self):
        """从已选列表移除标签（仅对当前任务生效）"""
        selected_items = self.selected_tags_list.selectedItems()
        for item in selected_items:
            row = self.selected_tags_list.row(item)
            self.selected_tags_list.takeItem(row)
    
    def _on_submit(self):
        """提交表单"""
        # 验证
        title = self.title_edit.text().strip()
        if not title:
            self.title_edit.setFocus()
            return
        
        # 获取当前选中的优先级
        checked_btn = self.priority_btn_group.checkedButton()
        priority = checked_btn.property("priority_value") if checked_btn else 1
        
        # 构建数据
        task_data = {
            "title": title,
            "section": self.section_combo.currentData(),
            "description": self.desc_edit.toPlainText().strip(),
            "requirements": self.requirements_edit.toPlainText().strip(),
            "priority": priority,
            "sort_order": priority,  # 同时设置排序（高优先级排前面）
            "tags": [
                self.selected_tags_list.item(i).text() 
                for i in range(self.selected_tags_list.count())
            ]
        }
        
        section = task_data["section"]
        
        if section == "once":
            qdate = self.due_date_edit.date()
            task_data["due_date"] = date(qdate.year(), qdate.month(), qdate.day())
        elif section == "weekly":
            task_data["reset_weekday"] = self.reset_weekday_combo.currentData()
        
        # 编辑模式保留ID
        if self.is_edit_mode and "id" in self.task_data:
            task_data["id"] = self.task_data["id"]
        
        self.task_submitted.emit(task_data)
    
    def set_available_tags(self, tags: list):
        """设置可选标签列表"""
        self.all_tags = tags
        self._refresh_available_tags()
    
    def _refresh_available_tags(self):
        """刷新待选标签列表"""
        self.available_tags_list.clear()
        
        # 获取已选标签
        selected = [
            self.selected_tags_list.item(i).text() 
            for i in range(self.selected_tags_list.count())
        ]
        
        # 显示未选择的标签
        for tag in self.all_tags:
            if tag not in selected:
                self.available_tags_list.addItem(tag)
    
    def set_task_data(self, task_data: dict):
        """设置任务数据（编辑模式）"""
        self.task_data = task_data or {}
        self.is_edit_mode = bool(task_data)
        
        if not task_data:
            return
        
        # 填充数据
        self.title_edit.setText(task_data.get("title", ""))
        
        section = task_data.get("section", "daily")
        index = self.section_combo.findData(section)
        if index >= 0:
            self.section_combo.setCurrentIndex(index)
        
        self.desc_edit.setPlainText(task_data.get("description", ""))
        
        self.requirements_edit.setPlainText(task_data.get("requirements", ""))
        
        due_date = task_data.get("due_date")
        if due_date:
            try:
                if isinstance(due_date, str):
                    due_date_obj = date.fromisoformat(due_date)
                else:
                    due_date_obj = due_date
                qdate = QDate(due_date_obj.year, due_date_obj.month, due_date_obj.day)
                self.due_date_edit.setDate(qdate)
            except (ValueError, TypeError, AttributeError):
                pass
        
        reset_weekday = task_data.get("reset_weekday")
        if reset_weekday is not None:
            index = self.reset_weekday_combo.findData(reset_weekday)
            if index >= 0:
                self.reset_weekday_combo.setCurrentIndex(index)
        
        # 设置优先级按钮
        priority = task_data.get("priority", 1)
        btn = self.priority_btn_group.button(priority)
        if btn:
            btn.setChecked(True)
        
        # 已选标签
        self.selected_tags_list.clear()
        for tag in task_data.get("tags", []):
            self.selected_tags_list.addItem(tag)
        
        # 刷新待选标签（排除已选的）
        self._refresh_available_tags()
        
        self._update_visibility()
    
    def clear_form(self):
        """清空表单"""
        self.task_data = {}
        self.is_edit_mode = False
        
        self.title_edit.clear()
        self.section_combo.setCurrentIndex(0)
        self.desc_edit.clear()
        self.requirements_edit.clear()
        self.due_date_edit.setDate(QDate.currentDate().addDays(7))
        self.reset_weekday_combo.setCurrentIndex(0)
        
        # 重置优先级为普通
        btn = self.priority_btn_group.button(1)
        if btn:
            btn.setChecked(True)
        
        self.selected_tags_list.clear()
        self.tag_edit.clear()
        
        # 刷新待选标签
        self._refresh_available_tags()
        
        self._update_visibility()
