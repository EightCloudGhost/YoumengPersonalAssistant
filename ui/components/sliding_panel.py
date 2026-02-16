# -*- coding: utf-8 -*-
"""
可滑入滑出的侧边面板组件
"""

from PyQt5.QtCore import (
    QPropertyAnimation, QParallelAnimationGroup, QEasingCurve,
    pyqtSignal, Qt
)
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget
)

from ..styles.qq_style import QQStyle


class SlidingPanel(QFrame):
    """可滑入滑出的侧边面板"""
    
    # 面板状态变化信号
    panel_shown = pyqtSignal()
    panel_hidden = pyqtSignal()
    
    def __init__(self, parent=None, direction='right'):
        """
        初始化滑动面板
        
        Args:
            parent: 父控件
            direction: 滑动方向 ('left' 或 'right')
        """
        super().__init__(parent)
        
        self._direction = direction
        self._is_expanded = False
        self._is_animating = False
        self._target_width = 350
        self._animation_duration = 300
        
        self.setObjectName("sliding_panel")
        self.setFrameShape(QFrame.NoFrame)
        
        # 初始状态：收起
        self.setMaximumWidth(0)
        self.setMinimumWidth(0)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("详情")
        self.title_label.setObjectName("panel_title")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # 关闭按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.hide_panel)
        header_layout.addWidget(self.close_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {QQStyle.BORDER}; max-height: 1px;")
        self.main_layout.addWidget(separator)
        
        # 内容区域（由外部设置）
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.main_layout.addWidget(self.content_widget, 1)
        
        # 底部操作区域
        self.action_layout = QHBoxLayout()
        self.action_layout.setSpacing(10)
        self.main_layout.addLayout(self.action_layout)
    
    def _apply_styles(self):
        """应用样式"""
        border_side = "left" if self._direction == "right" else "right"
        
        self.setStyleSheet(f"""
            QFrame#sliding_panel {{
                background-color: {QQStyle.WHITE};
                border-{border_side}: 1px solid {QQStyle.BORDER};
            }}
            
            QLabel#panel_title {{
                font-size: 18px;
                font-weight: bold;
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QPushButton#close_btn {{
                background-color: transparent;
                border: none;
                border-radius: 15px;
                font-size: 20px;
                color: {QQStyle.TEXT_SECONDARY};
            }}
            
            QPushButton#close_btn:hover {{
                background-color: {QQStyle.BG_GRAY};
                color: {QQStyle.TEXT_PRIMARY};
            }}
        """)
    
    def set_title(self, title: str):
        """设置面板标题"""
        self.title_label.setText(title)
    
    def set_target_width(self, width: int):
        """设置展开后的目标宽度"""
        self._target_width = width
    
    def set_animation_duration(self, duration: int):
        """设置动画时长"""
        self._animation_duration = duration
    
    def set_content(self, widget: QWidget):
        """设置内容控件"""
        # 清空现有内容
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        self.content_layout.addWidget(widget)
    
    def add_action_button(self, button: QPushButton):
        """添加操作按钮"""
        self.action_layout.addWidget(button)
    
    def clear_action_buttons(self):
        """清空操作按钮"""
        while self.action_layout.count():
            item = self.action_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
    
    def show_panel(self, animated: bool = True):
        """展开面板"""
        if self._is_expanded or self._is_animating:
            return
        
        self._is_animating = True
        self._is_expanded = True
        
        if not animated:
            self.setMaximumWidth(self._target_width)
            self.setMinimumWidth(self._target_width)
            self._is_animating = False
            self.panel_shown.emit()
            return
        
        # 确保可见
        self.show()
        
        # 创建宽度动画
        self._width_anim = QPropertyAnimation(self, b"maximumWidth")
        self._width_anim.setDuration(self._animation_duration)
        self._width_anim.setStartValue(0)
        self._width_anim.setEndValue(self._target_width)
        self._width_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 同时创建最小宽度动画以保持同步
        self._min_width_anim = QPropertyAnimation(self, b"minimumWidth")
        self._min_width_anim.setDuration(self._animation_duration)
        self._min_width_anim.setStartValue(0)
        self._min_width_anim.setEndValue(self._target_width)
        self._min_width_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 并行动画组（不使用透明度动画以避免与子组件的 graphics effect 冲突）
        self._anim_group = QParallelAnimationGroup()
        self._anim_group.addAnimation(self._width_anim)
        self._anim_group.addAnimation(self._min_width_anim)
        
        def on_finished():
            self._is_animating = False
            self.panel_shown.emit()
        
        self._anim_group.finished.connect(on_finished)
        self._anim_group.start()
    
    def hide_panel(self, animated: bool = True):
        """收起面板"""
        if not self._is_expanded or self._is_animating:
            return
        
        self._is_animating = True
        self._is_expanded = False
        
        if not animated:
            self.setMaximumWidth(0)
            self.setMinimumWidth(0)
            self._is_animating = False
            self.panel_hidden.emit()
            return
        
        # 创建宽度动画
        self._width_anim = QPropertyAnimation(self, b"maximumWidth")
        self._width_anim.setDuration(self._animation_duration)
        self._width_anim.setStartValue(self._target_width)
        self._width_anim.setEndValue(0)
        self._width_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self._min_width_anim = QPropertyAnimation(self, b"minimumWidth")
        self._min_width_anim.setDuration(self._animation_duration)
        self._min_width_anim.setStartValue(self._target_width)
        self._min_width_anim.setEndValue(0)
        self._min_width_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 并行动画组（不使用透明度动画以避免与子组件的 graphics effect 冲突）
        self._anim_group = QParallelAnimationGroup()
        self._anim_group.addAnimation(self._width_anim)
        self._anim_group.addAnimation(self._min_width_anim)
        
        def on_finished():
            self._is_animating = False
            self.panel_hidden.emit()
        
        self._anim_group.finished.connect(on_finished)
        self._anim_group.start()
    
    def toggle_panel(self):
        """切换面板状态"""
        if self._is_expanded:
            self.hide_panel()
        else:
            self.show_panel()
    
    def is_expanded(self) -> bool:
        """返回面板是否展开"""
        return self._is_expanded
