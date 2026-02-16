# -*- coding: utf-8 -*-
"""
顶部搜索栏组件
"""

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, 
    QPushButton, QLabel
)

from ..styles.qq_style import QQStyle
from config.settings import APP_NAME


class SearchBar(QWidget):
    """顶部搜索栏组件"""
    
    # 搜索信号 - 只传关键词
    search_triggered = pyqtSignal(str, str)  # (关键词, 搜索模式) - 保持接口兼容
    search_cleared = pyqtSignal()  # 搜索清空信号
    add_task_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setObjectName("search_bar")
        self.setFixedHeight(70)  # 增大高度
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 12, 12)
        layout.setSpacing(16)
        
        # 左侧 Logo
        self.logo_label = QLabel(APP_NAME)
        self.logo_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {QQStyle.PRIMARY};
        """)
        layout.addWidget(self.logo_label)
        
        # 左侧弹性空间
        layout.addStretch()
        
        # 搜索框容器（居中）- 带内置清空按钮
        search_container = QWidget()
        search_container.setObjectName("search_container")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(16, 0, 8, 0)
        search_layout.setSpacing(0)
        
        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input_inner")
        self.search_input.setPlaceholderText("输入关键词搜索任务...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setMinimumHeight(40)
        self.search_input.returnPressed.connect(self._on_search)
        self.search_input.textChanged.connect(self._on_text_changed)
        search_layout.addWidget(self.search_input)
        
        # 清空按钮（×）- 在输入框内右侧
        self.clear_btn = QPushButton("×")
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.setFixedSize(28, 28)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self._on_clear)
        self.clear_btn.setVisible(False)  # 默认隐藏
        search_layout.addWidget(self.clear_btn)
        
        # 搜索按钮
        self.search_btn = QPushButton("搜索")
        self.search_btn.setProperty("class", "tool-button")
        self.search_btn.setFixedSize(70, 40)
        self.search_btn.clicked.connect(self._on_search)
        search_layout.addWidget(self.search_btn)
        
        layout.addWidget(search_container)
        
        # 右侧弹性空间
        layout.addStretch()
        
        # 快捷操作按钮
        # 添加任务按钮 - 使用辅助色
        self.add_btn = QPushButton("+ 添加任务")
        self.add_btn.setProperty("class", "tool-button-accent")
        self.add_btn.setFixedSize(120, 40)
        self.add_btn.clicked.connect(self.add_task_clicked.emit)
        layout.addWidget(self.add_btn)
        
        # 设置按钮
        self.settings_btn = QPushButton("设置")
        self.settings_btn.setProperty("class", "tool-button-secondary")
        self.settings_btn.setFixedSize(70, 40)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.settings_btn)
        
        layout.addSpacing(16)
        
        # 右侧窗口控制按钮（最小化、最大化、关闭）
        self.min_btn = QPushButton("─")
        self.min_btn.setProperty("class", "window-control")
        self.min_btn.setFixedSize(36, 36)
        self.min_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.min_btn)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setProperty("class", "window-control")
        self.max_btn.setFixedSize(36, 36)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.max_btn)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setProperty("class", "window-control-close")
        self.close_btn.setFixedSize(36, 36)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.close_btn)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QWidget#search_bar {{
                background-color: {QQStyle.WHITE};
                border-bottom: 2px solid {QQStyle.BORDER};
            }}
            
            QWidget#search_container {{
                background-color: {QQStyle.BG_GRAY};
                border: 2px solid {QQStyle.BORDER};
                border-radius: 20px;
            }}
            
            QWidget#search_container:focus-within {{
                border: 2px solid {QQStyle.PRIMARY};
                background-color: {QQStyle.WHITE};
            }}
            
            QLineEdit#search_input_inner {{
                border: none;
                background-color: transparent;
                font-size: 15px;
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QPushButton#clear_btn {{
                background-color: transparent;
                color: {QQStyle.TEXT_PLACEHOLDER};
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
            }}
            
            QPushButton#clear_btn:hover {{
                background-color: {QQStyle.BORDER};
                color: {QQStyle.TEXT_SECONDARY};
            }}
            
            QPushButton[class="window-control"] {{
                background-color: transparent;
                color: {QQStyle.TEXT_SECONDARY};
                border: none;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
            }}
            
            QPushButton[class="window-control"]:hover {{
                background-color: {QQStyle.BG_GRAY};
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QPushButton[class="window-control-close"] {{
                background-color: transparent;
                color: {QQStyle.TEXT_SECONDARY};
                border: none;
                border-radius: 18px;
                font-size: 18px;
                font-weight: bold;
            }}
            
            QPushButton[class="window-control-close"]:hover {{
                background-color: {QQStyle.DANGER};
                color: {QQStyle.WHITE};
            }}
            
            QPushButton[class="tool-button"] {{
                background-color: {QQStyle.PRIMARY};
                color: {QQStyle.WHITE};
                border: none;
                border-radius: 18px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            
            QPushButton[class="tool-button"]:hover {{
                background-color: {QQStyle.PRIMARY_HOVER};
            }}
            
            QPushButton[class="tool-button-accent"] {{
                background-color: {QQStyle.ACCENT_PURPLE};
                color: {QQStyle.WHITE};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 15px;
                font-weight: bold;
            }}
            
            QPushButton[class="tool-button-accent"]:hover {{
                background-color: #6A3DE8;
            }}
            
            QPushButton[class="tool-button-secondary"] {{
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_REGULAR};
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }}
            
            QPushButton[class="tool-button-secondary"]:hover {{
                border-color: {QQStyle.PRIMARY};
                color: {QQStyle.PRIMARY};
                background-color: {QQStyle.PRIMARY_LIGHT};
            }}
        """)
    
    def _on_search(self):
        """执行搜索 - 只在点击按钮或按回车时触发"""
        keyword = self.search_input.text().strip()
        if keyword:
            # 使用模糊搜索作为默认模式
            self.search_triggered.emit(keyword, "fuzzy")
    
    def _on_text_changed(self, text):
        """输入文本变化 - 控制清空按钮显示"""
        self.clear_btn.setVisible(bool(text.strip()))
    
    def _on_clear(self):
        """清空搜索"""
        self.search_input.clear()
        self.search_cleared.emit()
    
    def get_search_text(self):
        """获取搜索文本"""
        return self.search_input.text().strip()
    
    def clear_search(self):
        """清空搜索框"""
        self.search_input.clear()
    
    def focus_search(self):
        """聚焦搜索框"""
        self.search_input.setFocus()
        self.search_input.selectAll()
