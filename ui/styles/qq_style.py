# -*- coding: utf-8 -*-
"""
QQ风格样式表 - 浅蓝色主题
"""


class QQStyle:
    """QQ风格样式管理器"""
    
    # ==================== 颜色常量 ====================
    
    # 主色调
    PRIMARY = '#12B7F5'
    PRIMARY_HOVER = '#0E8FCC'
    PRIMARY_LIGHT = '#E3F5FF'
    PRIMARY_DARK = '#0A7FB8'
    
    # 辅助色 - 丰富视觉效果
    ACCENT_PURPLE = '#7C4DFF'
    ACCENT_TEAL = '#009688'
    ACCENT_PINK = '#E91E63'
    ACCENT_ORANGE = '#FF9800'
    ACCENT_INDIGO = '#3F51B5'
    
    # 分区颜色
    SECTION_DAILY_BG = '#E3F2FD'
    SECTION_DAILY_TEXT = '#1976D2'
    SECTION_WEEKLY_BG = '#E8F5E9'
    SECTION_WEEKLY_TEXT = '#388E3C'
    SECTION_ONCE_BG = '#FFF3E0'
    SECTION_ONCE_TEXT = '#F57C00'
    
    # 中性色
    WHITE = '#FFFFFF'
    BG_GRAY = '#F5F7FA'
    BG_LIGHT = '#FAFBFC'
    BORDER = '#E4E7ED'
    BORDER_LIGHT = '#EBEEF5'
    
    # 文字颜色
    TEXT_PRIMARY = '#303133'
    TEXT_REGULAR = '#606266'
    TEXT_SECONDARY = '#909399'
    TEXT_PLACEHOLDER = '#C0C4CC'
    
    # 功能色
    SUCCESS = '#67C23A'
    SUCCESS_LIGHT = '#E1F3D8'
    WARNING = '#E6A23C'
    WARNING_LIGHT = '#FAECD8'
    DANGER = '#F56C6C'
    DANGER_LIGHT = '#FDE2E2'
    INFO = '#409EFF'
    INFO_LIGHT = '#D9ECFF'
    
    # 阴影
    SHADOW_LIGHT = 'rgba(0, 0, 0, 0.04)'
    SHADOW_NORMAL = 'rgba(0, 0, 0, 0.08)'
    SHADOW_HOVER = 'rgba(18, 183, 245, 0.15)'
    
    # ==================== 字体大小常量 (进一步增大) ====================
    
    FONT_SIZE_XLARGE = '28px'   # 超大标题
    FONT_SIZE_LARGE = '24px'    # 大标题
    FONT_SIZE_TITLE = '20px'    # 小标题/卡片标题
    FONT_SIZE_NORMAL = '17px'   # 正文（默认）
    FONT_SIZE_SMALL = '15px'    # 小文本
    FONT_SIZE_TINY = '14px'     # 最小文本（标签/注释）
    
    # ==================== 主窗口样式 ====================
    
    @staticmethod
    def get_main_window_style():
        """主窗口样式"""
        return f"""
            QMainWindow {{
                background-color: {QQStyle.WHITE};
            }}
            
            QWidget {{
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
            }}
        """
    
    # ==================== 搜索栏样式 ====================
    
    @staticmethod
    def get_search_bar_style():
        """顶部搜索栏样式"""
        return f"""
            QWidget#search_bar {{
                background-color: {QQStyle.WHITE};
                border-bottom: 1px solid {QQStyle.BORDER};
            }}
            
            QLineEdit#search_input {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 20px;
                padding: 10px 18px 10px 40px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                color: {QQStyle.TEXT_PRIMARY};
                background-color: {QQStyle.BG_GRAY};
                selection-background-color: {QQStyle.PRIMARY_LIGHT};
            }}
            
            QLineEdit#search_input:focus {{
                border: 2px solid {QQStyle.PRIMARY};
                background-color: {QQStyle.WHITE};
            }}
            
            QLineEdit#search_input::placeholder {{
                color: {QQStyle.TEXT_PLACEHOLDER};
            }}
            
            QComboBox#search_mode {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 6px;
                padding: 8px 14px;
                font-size: {QQStyle.FONT_SIZE_SMALL};
                color: {QQStyle.TEXT_REGULAR};
                background-color: {QQStyle.WHITE};
                min-width: 100px;
            }}
            
            QComboBox#search_mode:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            
            QComboBox#search_mode::drop-down {{
                border: none;
                width: 24px;
            }}
        """
    
    # ==================== 导航面板样式 ====================
    
    @staticmethod
    def get_navigation_panel_style():
        """左侧导航面板样式"""
        return f"""
            QWidget#nav_panel {{
                background-color: {QQStyle.WHITE};
                border-right: 1px solid {QQStyle.BORDER};
            }}
            
            QPushButton.nav-button {{
                border: none;
                border-radius: 8px;
                padding: 14px 18px;
                text-align: left;
                font-size: {QQStyle.FONT_SIZE_TITLE};
                color: {QQStyle.TEXT_REGULAR};
                background-color: transparent;
            }}
            
            QPushButton.nav-button:hover {{
                background-color: {QQStyle.BG_GRAY};
                color: {QQStyle.PRIMARY};
            }}
            
            QPushButton.nav-button:checked {{
                background-color: {QQStyle.PRIMARY_LIGHT};
                color: {QQStyle.PRIMARY};
                font-weight: bold;
                border-left: 4px solid {QQStyle.PRIMARY};
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}
            
            QLabel#nav_title {{
                font-size: {QQStyle.FONT_SIZE_SMALL};
                color: {QQStyle.TEXT_SECONDARY};
                padding: 10px 18px;
            }}
            
            QLabel#user_name {{
                font-size: {QQStyle.FONT_SIZE_TITLE};
                font-weight: bold;
                color: {QQStyle.TEXT_PRIMARY};
            }}
        """
    
    # ==================== 任务卡片样式 ====================
    
    @staticmethod
    def get_task_card_style():
        """任务卡片样式"""
        return f"""
            QFrame.task-card {{
                background-color: {QQStyle.WHITE};
                border: 1px solid {QQStyle.BORDER};
                border-radius: 12px;
            }}
            
            QFrame.task-card:hover {{
                border: 1px solid {QQStyle.PRIMARY};
                background-color: {QQStyle.BG_GRAY};
            }}
            
            QFrame.task-card-selected {{
                border: 2px solid {QQStyle.PRIMARY};
                border-left: 4px solid {QQStyle.PRIMARY};
            }}
            
            QFrame.task-card-completed {{
                background-color: #FAFAFA;
                border: 1px solid {QQStyle.BORDER_LIGHT};
            }}
            
            QLabel.task-title {{
                font-size: {QQStyle.FONT_SIZE_TITLE};
                font-weight: bold;
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QLabel.task-title-completed {{
                font-size: {QQStyle.FONT_SIZE_TITLE};
                color: {QQStyle.TEXT_SECONDARY};
                text-decoration: line-through;
            }}
            
            QLabel.task-desc {{
                font-size: {QQStyle.FONT_SIZE_SMALL};
                color: {QQStyle.TEXT_SECONDARY};
            }}
            
            QLabel.task-tag {{
                background-color: {QQStyle.BG_GRAY};
                border-radius: 10px;
                padding: 3px 12px;
                font-size: {QQStyle.FONT_SIZE_TINY};
                color: {QQStyle.TEXT_REGULAR};
            }}
            
            QLabel.section-daily {{
                background-color: {QQStyle.SECTION_DAILY_BG};
                color: {QQStyle.SECTION_DAILY_TEXT};
                border-radius: 4px;
                padding: 3px 10px;
                font-size: {QQStyle.FONT_SIZE_TINY};
            }}
            
            QLabel.section-weekly {{
                background-color: {QQStyle.SECTION_WEEKLY_BG};
                color: {QQStyle.SECTION_WEEKLY_TEXT};
                border-radius: 4px;
                padding: 3px 10px;
                font-size: {QQStyle.FONT_SIZE_TINY};
            }}
            
            QLabel.section-once {{
                background-color: {QQStyle.SECTION_ONCE_BG};
                color: {QQStyle.SECTION_ONCE_TEXT};
                border-radius: 4px;
                padding: 3px 10px;
                font-size: {QQStyle.FONT_SIZE_TINY};
            }}
            
            QCheckBox {{
                spacing: 10px;
            }}
            
            QCheckBox::indicator {{
                width: 24px;
                height: 24px;
                border: 2px solid {QQStyle.BORDER};
                border-radius: 4px;
                background-color: {QQStyle.WHITE};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {QQStyle.PRIMARY};
                border-color: {QQStyle.PRIMARY};
            }}
        """
    
    # ==================== 右侧详情面板样式 ====================
    
    @staticmethod
    def get_detail_panel_style():
        """右侧详情面板样式"""
        return f"""
            QWidget#detail_panel {{
                background-color: {QQStyle.WHITE};
                border-left: 1px solid {QQStyle.BORDER};
            }}
            
            QLabel#detail_title {{
                font-size: {QQStyle.FONT_SIZE_LARGE};
                font-weight: bold;
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QLabel#detail_content {{
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                color: {QQStyle.TEXT_REGULAR};
                line-height: 1.6;
            }}
            
            QPushButton#edit_btn {{
                background-color: {QQStyle.PRIMARY};
                color: {QQStyle.WHITE};
                border: none;
                border-radius: 8px;
                padding: 12px 28px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                font-weight: bold;
            }}
            
            QPushButton#edit_btn:hover {{
                background-color: {QQStyle.PRIMARY_HOVER};
            }}
            
            QPushButton#edit_btn:pressed {{
                background-color: {QQStyle.PRIMARY_DARK};
            }}
            
            QPushButton#delete_btn {{
                background-color: {QQStyle.WHITE};
                color: {QQStyle.DANGER};
                border: 2px solid {QQStyle.DANGER};
                border-radius: 8px;
                padding: 12px 28px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
            }}
            
            QPushButton#delete_btn:hover {{
                background-color: {QQStyle.DANGER_LIGHT};
            }}
        """
    
    # ==================== 切换按钮样式 ====================
    
    @staticmethod
    def get_toggle_button_style():
        """面板切换按钮样式"""
        return f"""
            QPushButton#toggle_btn {{
                background-color: {QQStyle.PRIMARY};
                color: {QQStyle.WHITE};
                border: none;
                border-radius: 22px;
                font-size: {QQStyle.FONT_SIZE_TITLE};
                font-weight: bold;
            }}
            
            QPushButton#toggle_btn:hover {{
                background-color: {QQStyle.PRIMARY_HOVER};
            }}
        """
    
    # ==================== 工具按钮样式 ====================
    
    @staticmethod
    def get_tool_button_style():
        """工具按钮样式"""
        return f"""
            QPushButton.tool-button {{
                background-color: {QQStyle.PRIMARY};
                color: {QQStyle.WHITE};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: {QQStyle.FONT_SIZE_SMALL};
            }}
            
            QPushButton.tool-button:hover {{
                background-color: {QQStyle.PRIMARY_HOVER};
            }}
            
            QPushButton.tool-button-secondary {{
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_REGULAR};
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: {QQStyle.FONT_SIZE_SMALL};
            }}
            
            QPushButton.tool-button-secondary:hover {{
                border-color: {QQStyle.PRIMARY};
                color: {QQStyle.PRIMARY};
            }}
        """
    
    # ==================== 标签列表样式 ====================
    
    @staticmethod
    def get_tag_list_style():
        """标签列表样式"""
        return f"""
            QListWidget#tag_list {{
                background-color: transparent;
                border: none;
                outline: none;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
            }}
            
            QListWidget#tag_list::item {{
                padding: 10px 18px;
                border-radius: 8px;
                color: {QQStyle.TEXT_REGULAR};
            }}
            
            QListWidget#tag_list::item:hover {{
                background-color: {QQStyle.BG_GRAY};
                color: {QQStyle.PRIMARY};
            }}
            
            QListWidget#tag_list::item:selected {{
                background-color: {QQStyle.PRIMARY_LIGHT};
                color: {QQStyle.PRIMARY};
            }}
        """
    
    # ==================== 任务列表样式 ====================
    
    @staticmethod
    def get_task_list_style():
        """任务列表样式"""
        return f"""
            QListWidget#task_list {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            
            QListWidget#task_list::item {{
                padding: 4px;
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                background-color: {QQStyle.BG_GRAY};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {QQStyle.BORDER};
                border-radius: 5px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {QQStyle.TEXT_SECONDARY};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
    
    # ==================== 分隔线样式 ====================
    
    @staticmethod
    def get_separator_style():
        """分隔线样式"""
        return f"""
            QFrame.separator {{
                background-color: {QQStyle.BORDER};
                max-height: 1px;
            }}
        """
    
    # ==================== 状态栏样式 ====================
    
    @staticmethod
    def get_status_bar_style():
        """状态栏样式"""
        return f"""
            QStatusBar {{
                background-color: {QQStyle.BG_GRAY};
                border-top: 1px solid {QQStyle.BORDER};
                color: {QQStyle.TEXT_SECONDARY};
                font-size: {QQStyle.FONT_SIZE_TINY};
                padding: 4px;
            }}
        """
    
    # ==================== 对话框样式 (新增) ====================
    
    @staticmethod
    def get_dialog_style():
        """统一对话框样式 - 用于 TaskDialog, SettingsDialog, RecycleBinDialog"""
        return f"""
            QDialog {{
                background-color: {QQStyle.WHITE};
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }}
            
            QLabel {{
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QLineEdit {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
                selection-background-color: {QQStyle.PRIMARY_LIGHT};
            }}
            
            QLineEdit:focus {{
                border: 2px solid {QQStyle.PRIMARY};
                background-color: {QQStyle.WHITE};
            }}
            
            QLineEdit::placeholder {{
                color: {QQStyle.TEXT_PLACEHOLDER};
            }}
            
            QLineEdit:disabled {{
                background-color: {QQStyle.BG_GRAY};
                color: {QQStyle.TEXT_SECONDARY};
            }}
            
            QTextEdit {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 10px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
                selection-background-color: {QQStyle.PRIMARY_LIGHT};
            }}
            
            QTextEdit:focus {{
                border: 2px solid {QQStyle.PRIMARY};
            }}
            
            QComboBox {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
                min-height: 20px;
            }}
            
            QComboBox:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            
            QComboBox:focus {{
                border: 2px solid {QQStyle.PRIMARY};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox QAbstractItemView {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                background-color: {QQStyle.WHITE};
                selection-background-color: {QQStyle.PRIMARY_LIGHT};
                selection-color: {QQStyle.PRIMARY};
                padding: 4px;
            }}
            
            QSpinBox {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QSpinBox:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            
            QSpinBox:focus {{
                border: 2px solid {QQStyle.PRIMARY};
            }}
            
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 24px;
                border: none;
                background-color: {QQStyle.BG_GRAY};
            }}
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {QQStyle.PRIMARY_LIGHT};
            }}
            
            QDateEdit {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QDateEdit:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            
            QDateEdit:focus {{
                border: 2px solid {QQStyle.PRIMARY};
            }}
            
            QDateEdit::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QTimeEdit {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QTimeEdit:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            
            QTimeEdit:focus {{
                border: 2px solid {QQStyle.PRIMARY};
            }}
            
            QCheckBox {{
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                color: {QQStyle.TEXT_PRIMARY};
                spacing: 10px;
            }}
            
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid {QQStyle.BORDER};
                border-radius: 4px;
                background-color: {QQStyle.WHITE};
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {QQStyle.PRIMARY};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {QQStyle.PRIMARY};
                border-color: {QQStyle.PRIMARY};
            }}
            
            QGroupBox {{
                font-size: {QQStyle.FONT_SIZE_TITLE};
                font-weight: bold;
                color: {QQStyle.TEXT_PRIMARY};
                border: 2px solid {QQStyle.BORDER};
                border-radius: 12px;
                padding: 20px 16px 16px 16px;
                margin-top: 16px;
                background-color: {QQStyle.BG_LIGHT};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 12px;
                left: 16px;
                background-color: {QQStyle.BG_LIGHT};
            }}
            
            QListWidget {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                background-color: {QQStyle.WHITE};
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                padding: 4px;
            }}
            
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 6px;
            }}
            
            QListWidget::item:hover {{
                background-color: {QQStyle.BG_GRAY};
            }}
            
            QListWidget::item:selected {{
                background-color: {QQStyle.PRIMARY_LIGHT};
                color: {QQStyle.PRIMARY};
            }}
            
            QPushButton {{
                border: 2px solid {QQStyle.BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: {QQStyle.FONT_SIZE_NORMAL};
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PRIMARY};
            }}
            
            QPushButton:hover {{
                border-color: {QQStyle.PRIMARY};
                color: {QQStyle.PRIMARY};
                background-color: {QQStyle.PRIMARY_LIGHT};
            }}
            
            QPushButton:pressed {{
                background-color: {QQStyle.PRIMARY};
                color: {QQStyle.WHITE};
            }}
            
            QDialogButtonBox QPushButton {{
                min-width: 90px;
                min-height: 36px;
            }}
            
            QDialogButtonBox QPushButton[text="OK"],
            QDialogButtonBox QPushButton[text="确定"] {{
                background-color: {QQStyle.PRIMARY};
                color: {QQStyle.WHITE};
                border: none;
            }}
            
            QDialogButtonBox QPushButton[text="OK"]:hover,
            QDialogButtonBox QPushButton[text="确定"]:hover {{
                background-color: {QQStyle.PRIMARY_HOVER};
            }}
            
            QSplitter::handle {{
                background-color: {QQStyle.BORDER};
            }}
            
            QSplitter::handle:horizontal {{
                width: 2px;
            }}
            
            QSplitter::handle:vertical {{
                height: 2px;
            }}
        """
    
    # ==================== 统一应用样式 ====================
    
    @classmethod
    def get_all_styles(cls):
        """获取所有样式的组合"""
        return "\n".join([
            cls.get_main_window_style(),
            cls.get_search_bar_style(),
            cls.get_navigation_panel_style(),
            cls.get_task_card_style(),
            cls.get_detail_panel_style(),
            cls.get_toggle_button_style(),
            cls.get_tool_button_style(),
            cls.get_tag_list_style(),
            cls.get_task_list_style(),
            cls.get_separator_style(),
            cls.get_status_bar_style(),
        ])
    
    @classmethod
    def apply_to_app(cls, app):
        """将样式应用到整个应用程序"""
        app.setStyleSheet(cls.get_all_styles())
