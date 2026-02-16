# -*- coding: utf-8 -*-
"""
设置表单组件 - 可嵌入右侧面板
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QTimeEdit, QCheckBox, QSpinBox,
    QPushButton, QLabel, QGroupBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QTime, pyqtSignal

from config.settings import settings
from ..styles.qq_style import QQStyle
from utils.resource import Icons


class SettingsWidget(QWidget):
    """设置表单组件"""
    
    # 信号
    settings_saved = pyqtSignal()
    settings_cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_ui()
        self._load_settings()
        self._connect_signals()
        self._apply_styles()
    
    def _setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 0, 5, 0)  # 增加左右边距
        main_layout.setSpacing(0)
        
        # 可滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 表单容器
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(10, 5, 15, 10)  # 增加内边距
        form_layout.setSpacing(20)
        
        # ===== 任务设置组 =====
        task_group = QGroupBox("任务设置")
        task_layout = QVBoxLayout(task_group)
        task_layout.setSpacing(12)
        
        # 默认分区
        section_layout = QHBoxLayout()
        section_label = QLabel("默认分区:")
        section_label.setMinimumWidth(100)
        self.default_section_combo = QComboBox()
        self.default_section_combo.addItem("日常任务", 0)
        self.default_section_combo.addItem("周常任务", 1)
        self.default_section_combo.addItem("特殊任务", 2)
        self.default_section_combo.setMinimumHeight(36)
        section_layout.addWidget(section_label)
        section_layout.addWidget(self.default_section_combo, 1)
        task_layout.addLayout(section_layout)
        
        # 显示已完成任务
        self.show_completed_check = QCheckBox("显示已完成任务")
        task_layout.addWidget(self.show_completed_check)
        
        form_layout.addWidget(task_group)
        
        # ===== 重置设置组 =====
        reset_group = QGroupBox("重置设置")
        reset_layout = QVBoxLayout(reset_group)
        reset_layout.setSpacing(12)
        
        # 每日重置时间
        time_layout = QHBoxLayout()
        time_label = QLabel("每日重置时间:")
        time_label.setMinimumWidth(100)
        self.reset_time_edit = QTimeEdit()
        self.reset_time_edit.setDisplayFormat("HH:mm")
        self.reset_time_edit.setMinimumHeight(36)
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.reset_time_edit, 1)
        reset_layout.addLayout(time_layout)
        
        # 周常重置日
        weekday_layout = QHBoxLayout()
        weekday_label = QLabel("周常重置日:")
        weekday_label.setMinimumWidth(100)
        self.reset_weekday_combo = QComboBox()
        self.reset_weekday_combo.addItem("星期一", 0)
        self.reset_weekday_combo.addItem("星期二", 1)
        self.reset_weekday_combo.addItem("星期三", 2)
        self.reset_weekday_combo.addItem("星期四", 3)
        self.reset_weekday_combo.addItem("星期五", 4)
        self.reset_weekday_combo.addItem("星期六", 5)
        self.reset_weekday_combo.addItem("星期日", 6)
        self.reset_weekday_combo.setMinimumHeight(36)
        weekday_layout.addWidget(weekday_label)
        weekday_layout.addWidget(self.reset_weekday_combo, 1)
        reset_layout.addLayout(weekday_layout)
        
        # 自动重置
        self.auto_reset_check = QCheckBox("启用自动重置")
        reset_layout.addWidget(self.auto_reset_check)
        
        form_layout.addWidget(reset_group)
        
        # ===== 回收站设置组 =====
        recycle_group = QGroupBox("回收站设置")
        recycle_layout = QVBoxLayout(recycle_group)
        recycle_layout.setSpacing(12)
        
        # 容量
        capacity_layout = QHBoxLayout()
        capacity_label = QLabel("回收站容量:")
        capacity_label.setMinimumWidth(100)
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(10, 1000)
        self.capacity_spin.setSuffix(" 个任务")
        self.capacity_spin.setMinimumHeight(36)
        capacity_layout.addWidget(capacity_label)
        capacity_layout.addWidget(self.capacity_spin, 1)
        recycle_layout.addLayout(capacity_layout)
        
        form_layout.addWidget(recycle_group)
        
        # ===== 数据设置组 =====
        data_group = QGroupBox("数据设置")
        data_layout = QVBoxLayout(data_group)
        data_layout.setSpacing(12)
        
        # 自动备份
        self.auto_backup_check = QCheckBox("启用自动备份")
        data_layout.addWidget(self.auto_backup_check)
        
        # 备份间隔
        backup_layout = QHBoxLayout()
        backup_label = QLabel("备份间隔:")
        backup_label.setMinimumWidth(100)
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 30)
        self.backup_interval_spin.setSuffix(" 天")
        self.backup_interval_spin.setMinimumHeight(36)
        backup_layout.addWidget(backup_label)
        backup_layout.addWidget(self.backup_interval_spin, 1)
        data_layout.addLayout(backup_layout)
        
        form_layout.addWidget(data_group)
        
        form_layout.addStretch()
        
        scroll.setWidget(form_container)
        main_layout.addWidget(scroll, 1)
        
        # 底部按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(0, 16, 0, 0)
        
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
        
        self.save_btn = QPushButton("保存设置")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setStyleSheet(f"""
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
        btn_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(btn_layout)
    
    def _connect_signals(self):
        """连接信号"""
        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.settings_cancelled.emit)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-size: 15px;
                font-weight: bold;
                color: {QQStyle.TEXT_PRIMARY};
                border: 2px solid {QQStyle.BORDER};
                border-radius: 10px;
                padding: 16px 12px 12px 12px;
                margin-top: 12px;
                background-color: {QQStyle.BG_LIGHT};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                left: 12px;
                background-color: {QQStyle.BG_LIGHT};
            }}
            QComboBox, QSpinBox, QTimeEdit {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
            }}
            QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {{
                border: 2px solid {QQStyle.PRIMARY};
            }}
            QCheckBox {{
                font-size: 14px;
                color: {QQStyle.TEXT_PRIMARY};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {QQStyle.BORDER};
                border-radius: 4px;
                background-color: {QQStyle.WHITE};
            }}
            QCheckBox::indicator:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background-color: {QQStyle.WHITE};
                border-color: {QQStyle.PRIMARY};
                image: url({Icons.CHECK_BLUE});
            }}
            QLabel {{
                font-size: 14px;
                color: {QQStyle.TEXT_REGULAR};
            }}
        """)
    
    def _load_settings(self):
        """加载设置"""
        # 任务设置
        default_section = settings.get("ui.default_section", 0)
        self.default_section_combo.setCurrentIndex(default_section)
        
        show_completed = settings.get("ui.show_completed", True)
        self.show_completed_check.setChecked(show_completed)
        
        # 重置设置
        reset_time_str = settings.get("task.daily_reset_time", "06:00")
        try:
            hour, minute = map(int, reset_time_str.split(":"))
            self.reset_time_edit.setTime(QTime(hour, minute))
        except (ValueError, AttributeError):
            self.reset_time_edit.setTime(QTime(6, 0))
        
        reset_weekday = settings.get("task.weekly_reset_day", 0)
        self.reset_weekday_combo.setCurrentIndex(reset_weekday)
        
        auto_reset = settings.get("task.auto_reset_enabled", True)
        self.auto_reset_check.setChecked(auto_reset)
        
        # 回收站设置
        capacity = settings.get("task.recycle_bin_capacity", 100)
        self.capacity_spin.setValue(capacity)
        
        # 数据设置
        auto_backup = settings.get("data.auto_backup", False)
        self.auto_backup_check.setChecked(auto_backup)
        
        backup_interval = settings.get("data.backup_interval", 7)
        self.backup_interval_spin.setValue(backup_interval)
    
    def _on_save(self):
        """保存设置"""
        # 任务设置
        settings.set("ui.default_section", self.default_section_combo.currentIndex(), auto_save=False)
        settings.set("ui.show_completed", self.show_completed_check.isChecked(), auto_save=False)
        
        # 重置设置
        time = self.reset_time_edit.time()
        settings.set("task.daily_reset_time", f"{time.hour():02d}:{time.minute():02d}", auto_save=False)
        settings.set("task.weekly_reset_day", self.reset_weekday_combo.currentIndex(), auto_save=False)
        settings.set("task.auto_reset_enabled", self.auto_reset_check.isChecked(), auto_save=False)
        
        # 回收站设置
        settings.set("task.recycle_bin_capacity", self.capacity_spin.value(), auto_save=False)
        
        # 数据设置
        settings.set("data.auto_backup", self.auto_backup_check.isChecked(), auto_save=False)
        settings.set("data.backup_interval", self.backup_interval_spin.value(), auto_save=False)
        
        # 保存到文件
        settings.save()
        
        self.settings_saved.emit()
    
    def reload_settings(self):
        """重新加载设置"""
        self._load_settings()
