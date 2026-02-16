from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFormLayout, QSpinBox, QComboBox,
    QCheckBox, QTimeEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtGui import QFont
from config.settings import settings
from utils.logger import logger
from ui.styles.qq_style import QQStyle


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setMinimumSize(550, 650)
        
        # 应用统一样式
        self.setStyleSheet(QQStyle.get_dialog_style())
        
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 重置设置组
        reset_group = QGroupBox("重置设置")
        reset_layout = QFormLayout(reset_group)
        
        # 日常重置时间
        self.daily_reset_time = QTimeEdit()
        self.daily_reset_time.setDisplayFormat("HH:mm")
        reset_layout.addRow("日常重置时间:", self.daily_reset_time)
        
        # 周常重置星期
        self.weekly_reset_day = QComboBox()
        self.weekly_reset_day.addItems([
            "星期一", "星期二", "星期三", "星期四", 
            "星期五", "星期六", "星期日"
        ])
        reset_layout.addRow("周常重置星期:", self.weekly_reset_day)
        
        # 自动重置开关
        self.auto_reset_enabled = QCheckBox("启用自动重置")
        reset_layout.addRow(self.auto_reset_enabled)
        
        layout.addWidget(reset_group)
        
        # 界面设置组
        ui_group = QGroupBox("界面设置")
        ui_layout = QFormLayout(ui_group)
        
        # 默认分区
        self.default_section = QComboBox()
        self.default_section.addItems(["日常任务", "周常任务", "特殊任务"])
        ui_layout.addRow("默认分区:", self.default_section)
        
        # 显示已完成任务
        self.show_completed = QCheckBox("显示已完成任务")
        ui_layout.addRow(self.show_completed)
        
        # 自动展开右侧面板
        self.auto_expand_panel = QCheckBox("自动展开右侧面板")
        ui_layout.addRow(self.auto_expand_panel)
        
        layout.addWidget(ui_group)
        
        # 数据设置组
        data_group = QGroupBox("数据设置")
        data_layout = QFormLayout(data_group)
        
        # 回收站容量
        self.recycle_bin_capacity = QSpinBox()
        self.recycle_bin_capacity.setRange(10, 1000)
        self.recycle_bin_capacity.setSuffix(" 个任务")
        data_layout.addRow("回收站容量:", self.recycle_bin_capacity)
        
        # 自动备份
        self.auto_backup = QCheckBox("启用自动备份")
        data_layout.addRow(self.auto_backup)
        
        # 备份间隔
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(1, 30)
        self.backup_interval.setSuffix(" 天")
        self.backup_interval.setEnabled(False)
        data_layout.addRow("备份间隔:", self.backup_interval)
        
        # 连接自动备份信号
        self.auto_backup.stateChanged.connect(
            lambda state: self.backup_interval.setEnabled(state == Qt.Checked)
        )
        
        layout.addWidget(data_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 保存按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        # 重置按钮
        self.reset_btn = QPushButton("重置为默认")
        self.reset_btn.clicked.connect(self._on_reset)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
        
    def _load_settings(self):
        """加载设置"""
        try:
            # 重置设置
            daily_reset_str = settings.get("daily_reset_time", "06:00")
            reset_time = QTime.fromString(daily_reset_str, "HH:mm")
            if reset_time.isValid():
                self.daily_reset_time.setTime(reset_time)
            
            weekly_day = settings.get("weekly_reset_day", 0)  # 0=星期一
            self.weekly_reset_day.setCurrentIndex(weekly_day)
            
            auto_reset = settings.get("auto_reset_enabled", True)
            self.auto_reset_enabled.setChecked(auto_reset)
            
            # 界面设置
            default_section = settings.get("default_section", 0)  # 0=日常任务
            self.default_section.setCurrentIndex(default_section)
            
            show_completed = settings.get("show_completed", True)
            self.show_completed.setChecked(show_completed)
            
            auto_expand = settings.get("auto_expand_panel", False)
            self.auto_expand_panel.setChecked(auto_expand)
            
            # 数据设置
            recycle_capacity = settings.get("recycle_bin_capacity", 100)
            self.recycle_bin_capacity.setValue(recycle_capacity)
            
            auto_backup = settings.get("auto_backup", False)
            self.auto_backup.setChecked(auto_backup)
            
            backup_interval = settings.get("backup_interval", 7)
            self.backup_interval.setValue(backup_interval)
            self.backup_interval.setEnabled(auto_backup)
            
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            QMessageBox.warning(self, "错误", f"加载设置失败: {str(e)}")
    
    def _on_save(self):
        """保存设置"""
        try:
            # 重置设置
            daily_reset_time = self.daily_reset_time.time().toString("HH:mm")
            settings.set("daily_reset_time", daily_reset_time)
            
            weekly_reset_day = self.weekly_reset_day.currentIndex()
            settings.set("weekly_reset_day", weekly_reset_day)
            
            auto_reset_enabled = self.auto_reset_enabled.isChecked()
            settings.set("auto_reset_enabled", auto_reset_enabled)
            
            # 界面设置
            default_section = self.default_section.currentIndex()
            settings.set("default_section", default_section)
            
            show_completed = self.show_completed.isChecked()
            settings.set("show_completed", show_completed)
            
            auto_expand_panel = self.auto_expand_panel.isChecked()
            settings.set("auto_expand_panel", auto_expand_panel)
            
            # 数据设置
            recycle_bin_capacity = self.recycle_bin_capacity.value()
            settings.set("recycle_bin_capacity", recycle_bin_capacity)
            
            auto_backup = self.auto_backup.isChecked()
            settings.set("auto_backup", auto_backup)
            
            backup_interval = self.backup_interval.value()
            settings.set("backup_interval", backup_interval)
            
            # 保存到文件
            if settings.save():
                logger.info("设置保存成功")
                QMessageBox.information(self, "成功", "设置已保存")
                self.accept()
            else:
                logger.error("设置保存失败")
                QMessageBox.critical(self, "错误", "设置保存失败")
                
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
    
    def _on_reset(self):
        """重置为默认设置"""
        try:
            reply = QMessageBox.question(
                self,
                "确认重置",
                "确定要重置所有设置为默认值吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 重置设置
                settings.reset_to_defaults()
                
                # 重新加载设置到UI
                self._load_settings()
                
                logger.info("设置已重置为默认值")
                QMessageBox.information(self, "成功", "设置已重置为默认值")
                
        except Exception as e:
            logger.error(f"重置设置失败: {e}")
            QMessageBox.critical(self, "错误", f"重置设置失败: {str(e)}")
    
    @staticmethod
    def get_settings(parent=None):
        """静态方法：打开设置对话框"""
        dialog = SettingsDialog(parent)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            return True
        return False