# -*- coding: utf-8 -*-
"""
任务卡片控件 - QQ风格
"""

from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QCheckBox, 
    QLabel, QWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QColor
from datetime import date

from ui.styles.qq_style import QQStyle
from utils.resource import Icons


class TaskCard(QFrame):
    """任务卡片控件 - QQ风格"""
    
    # 信号定义
    completed = pyqtSignal(int, bool)  # task_id, is_completed
    clicked = pyqtSignal(int)  # task_id
    double_clicked = pyqtSignal(int)  # task_id
    
    def __init__(self, task_data: dict, parent=None):
        """
        初始化任务卡片
        
        Args:
            task_data: 任务数据字典
            parent: 父控件
        """
        super().__init__(parent)
        self.task_id = task_data.get("id", -1)
        self.task_data = task_data
        self._is_selected = False
        self._is_hovered = False
        
        self._setup_ui()
        self._apply_styles()
        self._connect_signals()
        self._setup_shadow()
        
        # 设置鼠标跟踪以启用hover效果
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
    
    def _setup_ui(self):
        """设置UI布局"""
        # 设置卡片属性
        self.setObjectName("task_card")
        self.setFrameStyle(QFrame.NoFrame)
        self.setMinimumHeight(80)
        self.setMaximumHeight(130)
        
        # 获取优先级信息
        priority = self.task_data.get("priority", 1)
        priority_colors = {
            3: QQStyle.DANGER,        # 紧急 - 红色
            2: QQStyle.ACCENT_ORANGE, # 优先 - 橙色
            1: QQStyle.PRIMARY,       # 普通 - 蓝色
            0: QQStyle.TEXT_SECONDARY # 建议 - 灰色
        }
        self._priority_color = priority_colors.get(priority, QQStyle.PRIMARY)
        
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 18, 0)
        main_layout.setSpacing(0)
        
        # 左侧优先级颜色条
        self.priority_bar = QFrame()
        self.priority_bar.setFixedWidth(5)
        self.priority_bar.setStyleSheet(f"""
            background-color: {self._priority_color};
            border-top-left-radius: 12px;
            border-bottom-left-radius: 12px;
        """)
        main_layout.addWidget(self.priority_bar)
        
        # 内容区域
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(14, 14, 0, 14)
        content_layout.setSpacing(14)
        
        # 左侧：复选框 - 增大
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(bool(self.task_data.get("is_completed", False)))
        self.checkbox.setFixedSize(26, 26)
        self.checkbox.setCursor(Qt.PointingHandCursor)
        self.checkbox.setStyleSheet(f"""
            QCheckBox {{
                spacing: 0px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid {QQStyle.BORDER};
                border-radius: 6px;
                background-color: {QQStyle.WHITE};
            }}
            QCheckBox::indicator:hover {{
                border-color: {QQStyle.SUCCESS};
            }}
            QCheckBox::indicator:checked {{
                background-color: {QQStyle.WHITE};
                border-color: {QQStyle.SUCCESS};
                image: url({Icons.CHECK_GREEN});
            }}
        """)
        content_layout.addWidget(self.checkbox)
        
        # 中间：任务信息
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)
        
        # 标题 - 增大字体
        self.title_label = QLabel(self.task_data.get("title", "未命名任务"))
        self.title_label.setObjectName("task_title")
        self.title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {QQStyle.TEXT_PRIMARY};
        """)
        info_layout.addWidget(self.title_label)
        
        # 描述（如果有）- 增大字体
        description = self.task_data.get("description", "")
        if description:
            self.desc_label = QLabel(description)
            self.desc_label.setObjectName("task_desc")
            self.desc_label.setWordWrap(True)
            self.desc_label.setMaximumHeight(45)
            self.desc_label.setStyleSheet(f"""
                font-size: 15px;
                color: {QQStyle.TEXT_SECONDARY};
            """)
            info_layout.addWidget(self.desc_label)
        else:
            self.desc_label = None
        
        # 标签区域 - 使用辅助色
        tags = self.task_data.get("tags", [])
        if tags:
            tags_widget = QWidget()
            tags_layout = QHBoxLayout(tags_widget)
            tags_layout.setContentsMargins(0, 2, 0, 0)
            tags_layout.setSpacing(8)
            
            # 为标签分配不同的辅助色
            tag_colors = [
                (QQStyle.ACCENT_PURPLE, "#EDE7F6"),
                (QQStyle.ACCENT_TEAL, "#E0F2F1"),
                (QQStyle.ACCENT_PINK, "#FCE4EC"),
                (QQStyle.ACCENT_ORANGE, "#FFF3E0"),
                (QQStyle.ACCENT_INDIGO, "#E8EAF6"),
            ]
            
            for i, tag in enumerate(tags[:3]):  # 最多显示3个标签
                color, bg = tag_colors[i % len(tag_colors)]
                tag_label = QLabel(tag)
                tag_label.setStyleSheet(f"""
                    background-color: {bg};
                    border-radius: 12px;
                    padding: 5px 14px;
                    font-size: 13px;
                    font-weight: bold;
                    color: {color};
                """)
                tags_layout.addWidget(tag_label)
            
            if len(tags) > 3:
                more_label = QLabel(f"+{len(tags) - 3}")
                more_label.setStyleSheet(f"""
                    font-size: 13px;
                    color: {QQStyle.TEXT_SECONDARY};
                """)
                tags_layout.addWidget(more_label)
            
            tags_layout.addStretch()
            info_layout.addWidget(tags_widget)
        
        info_layout.addStretch()
        content_layout.addWidget(info_widget, 1)  # 拉伸因子为1
        
        # 右侧：状态信息
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(6)
        status_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        
        # 分区标签 - 使用辅助色
        section = self.task_data.get("section", "daily")
        section_config = {
            "daily": ("日常", QQStyle.PRIMARY, QQStyle.PRIMARY_LIGHT),
            "weekly": ("周常", QQStyle.ACCENT_TEAL, "#E0F2F1"),
            "once": ("特殊", QQStyle.ACCENT_ORANGE, "#FFF3E0")
        }
        section_text, section_color, section_bg = section_config.get(
            section, ("日常", QQStyle.PRIMARY, QQStyle.PRIMARY_LIGHT)
        )
        
        self.section_label = QLabel(section_text)
        self.section_label.setStyleSheet(f"""
            background-color: {section_bg};
            color: {section_color};
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 13px;
            font-weight: bold;
        """)
        status_layout.addWidget(self.section_label)
        
        # 截止日期（仅特殊任务）
        due_date = self.task_data.get("due_date")
        if section == "once" and due_date:
            try:
                due_date_obj = date.fromisoformat(due_date) if isinstance(due_date, str) else due_date
                today = date.today()
                days_left = (due_date_obj - today).days
                
                self.due_label = QLabel(f"{due_date_obj.month}/{due_date_obj.day}")
                
                if days_left < 0:
                    due_color = QQStyle.DANGER
                    due_bg = QQStyle.DANGER_LIGHT
                elif days_left == 0:
                    due_color = QQStyle.WARNING
                    due_bg = QQStyle.WARNING_LIGHT
                elif days_left <= 3:
                    due_color = "#F57C00"
                    due_bg = "#FFF3E0"
                else:
                    due_color = QQStyle.TEXT_SECONDARY
                    due_bg = QQStyle.BG_GRAY
                
                self.due_label.setStyleSheet(f"""
                    background-color: {due_bg};
                    color: {due_color};
                    border-radius: 6px;
                    padding: 3px 8px;
                    font-size: 13px;
                """)
                status_layout.addWidget(self.due_label)
            except (ValueError, TypeError, AttributeError):
                pass  # 日期格式无效时跳过显示
        
        status_layout.addStretch()
        content_layout.addWidget(status_widget)
        
        main_layout.addLayout(content_layout)
    
    def _apply_styles(self):
        """应用样式"""
        is_completed = bool(self.task_data.get("is_completed", False))
        
        if is_completed:
            # 已完成任务的样式
            self.setStyleSheet(f"""
                QFrame#task_card {{
                    background-color: #FAFAFA;
                    border: 1px solid {QQStyle.BORDER_LIGHT};
                    border-radius: 12px;
                }}
            """)
            
            # 优先级条变淡
            self.priority_bar.setStyleSheet(f"""
                background-color: {QQStyle.BORDER_LIGHT};
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            """)
            
            # 更新标题样式（删除线）- 增大字体
            self.title_label.setStyleSheet(f"""
                font-size: 18px;
                font-weight: normal;
                color: {QQStyle.TEXT_SECONDARY};
                text-decoration: line-through;
            """)
            
            if self.desc_label:
                self.desc_label.setStyleSheet(f"""
                    font-size: 15px;
                    color: {QQStyle.TEXT_PLACEHOLDER};
                """)
        else:
            # 未完成任务的样式
            if self._is_selected:
                border_style = f"2px solid {QQStyle.PRIMARY}"
            elif self._is_hovered:
                border_style = f"1px solid {QQStyle.PRIMARY}"
            else:
                border_style = f"1px solid {QQStyle.BORDER}"
            
            bg_color = QQStyle.BG_GRAY if self._is_hovered else QQStyle.WHITE
            
            self.setStyleSheet(f"""
                QFrame#task_card {{
                    background-color: {bg_color};
                    border: {border_style};
                    border-radius: 12px;
                }}
            """)
            
            # 优先级条保持原色
            self.priority_bar.setStyleSheet(f"""
                background-color: {self._priority_color};
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            """)
            
            # 增大字体
            self.title_label.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {QQStyle.TEXT_PRIMARY};
            """)
            
            if self.desc_label:
                self.desc_label.setStyleSheet(f"""
                    font-size: 15px;
                    color: {QQStyle.TEXT_SECONDARY};
                """)
    
    def _setup_shadow(self):
        """设置阴影效果"""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(8)
        self._shadow.setOffset(0, 2)
        self._shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(self._shadow)
    
    def _update_shadow(self, hovered: bool):
        """更新阴影效果"""
        if hovered:
            self._shadow.setBlurRadius(16)
            self._shadow.setOffset(0, 4)
            self._shadow.setColor(QColor(18, 183, 245, 40))  # 蓝色阴影
        else:
            self._shadow.setBlurRadius(8)
            self._shadow.setOffset(0, 2)
            self._shadow.setColor(QColor(0, 0, 0, 15))
    
    def _connect_signals(self):
        """连接信号"""
        self.checkbox.stateChanged.connect(self._on_checkbox_changed)
    
    def _on_checkbox_changed(self, state):
        """复选框状态改变"""
        is_checked = state == Qt.Checked
        self.completed.emit(self.task_id, is_checked)
        
        # 更新样式
        self.task_data["is_completed"] = is_checked
        self._apply_styles()
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self._is_hovered = True
        self._apply_styles()
        self._update_shadow(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._is_hovered = False
        self._apply_styles()
        self._update_shadow(False)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击了复选框区域
            checkbox_rect = self.checkbox.geometry()
            if not checkbox_rect.contains(event.pos()):
                self.clicked.emit(self.task_id)
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            checkbox_rect = self.checkbox.geometry()
            if not checkbox_rect.contains(event.pos()):
                self.double_clicked.emit(self.task_id)
        super().mouseDoubleClickEvent(event)
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self._is_selected = selected
        self._apply_styles()
    
    def update_task_data(self, new_data: dict):
        """更新任务数据"""
        self.task_data.update(new_data)
        
        # 更新UI
        self.title_label.setText(self.task_data.get("title", "未命名任务"))
        
        # 更新复选框状态
        is_completed = bool(self.task_data.get("is_completed", False))
        self.checkbox.setChecked(is_completed)
        
        # 重新应用样式
        self._apply_styles()
    
    def get_task_id(self) -> int:
        """获取任务ID"""
        return self.task_id
    
    def is_completed(self) -> bool:
        """检查任务是否已完成"""
        return self.checkbox.isChecked()
    
    def sizeHint(self):
        """返回推荐尺寸"""
        # 根据内容计算高度
        height = 85  # 基础高度
        if self.desc_label:
            height += 25
        if self.task_data.get("tags"):
            height += 25
        return QSize(400, height)
