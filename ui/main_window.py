# -*- coding: utf-8 -*-
"""
主窗口 - QQ风格UI
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QSplitter, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QFrame, QScrollArea,
    QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QFont, QKeySequence, QCursor

from core.task_manager import TaskManager
from ui.task_card import TaskCard
from ui.task_dialog import TaskDialog
from ui.settings_dialog import SettingsDialog
from ui.recycle_bin_dialog import RecycleBinDialog
from ui.components.animated_stacked_widget import AnimatedStackedWidget
from ui.components.search_bar import SearchBar
from ui.components.sliding_panel import SlidingPanel
from ui.components.task_form_widget import TaskFormWidget
from ui.components.settings_widget import SettingsWidget
from ui.styles.qq_style import QQStyle
from config.settings import settings, APP_NAME
from utils.logger import logger


class MainWindow(QMainWindow):
    """主窗口 - QQ风格"""
    
    # 信号定义
    section_changed = pyqtSignal(str)  # section_name
    
    # 边缘调整大小常量
    EDGE_MARGIN = 8  # 边缘检测区域宽度
    
    # 边缘位置枚举
    EDGE_NONE = 0
    EDGE_LEFT = 1
    EDGE_RIGHT = 2
    EDGE_TOP = 3
    EDGE_BOTTOM = 4
    EDGE_TOP_LEFT = 5
    EDGE_TOP_RIGHT = 6
    EDGE_BOTTOM_LEFT = 7
    EDGE_BOTTOM_RIGHT = 8
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 无边框窗口拖拽支持
        self._drag_pos = None
        
        # 边缘调整大小支持
        self._resize_edge = self.EDGE_NONE
        self._resize_start_pos = None
        self._resize_start_geometry = None
        
        # 初始化任务管理器
        self.task_manager = TaskManager()
        
        # 当前状态
        self.current_section = "daily"  # 当前分区
        self.current_tag = None  # 当前标签筛选
        self.current_selected_task_id = None  # 当前选中任务ID
        
        # 初始化任务列表字典
        self.pending_lists = {}
        self.completed_lists = {}
        
        self._setup_ui()
        self._connect_signals()
        self._setup_shortcuts()
        
        # 加载初始数据
        self._load_initial_data()
        
        logger.info("主窗口初始化完成")
    
    def _setup_ui(self):
        """设置UI布局"""
        # 设置窗口属性
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(900, 600)  # 设置最小窗口大小
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # 应用主窗口样式
        self.setStyleSheet(QQStyle.get_main_window_style())
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局（垂直）
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部搜索栏
        self.search_bar = SearchBar()
        main_layout.addWidget(self.search_bar)
        
        # 内容区域（水平布局）
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 左侧导航栏
        self.left_panel = self._create_left_panel()
        content_layout.addWidget(self.left_panel)
        
        # 中央任务区域
        self.center_panel = self._create_center_panel()
        content_layout.addWidget(self.center_panel, 1)  # 拉伸因子为1
        
        # 右侧详情面板（使用滑动面板）
        self.right_panel = self._create_right_panel()
        content_layout.addWidget(self.right_panel)
        
        main_layout.addWidget(content_widget, 1)
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        self.statusBar().setStyleSheet(QQStyle.get_status_bar_style())
    
    def _create_left_panel(self) -> QWidget:
        """创建左侧导航栏"""
        panel = QFrame()
        panel.setObjectName("nav_panel")
        panel.setFixedWidth(230)  # 增大导航栏宽度
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 18, 14, 18)
        layout.setSpacing(10)
        
        # 用户信息区域（简化）
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setContentsMargins(10, 10, 10, 10)
        user_layout.setSpacing(12)
        
        # 小头像
        avatar_label = QLabel("👤")
        avatar_label.setFixedSize(40, 40)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet(f"""
            background-color: {QQStyle.ACCENT_PURPLE};
            border-radius: 20px;
            font-size: 20px;
        """)
        user_layout.addWidget(avatar_label)
        
        # 用户名
        username_label = QLabel("幽梦")
        username_label.setObjectName("user_name")
        username_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {QQStyle.TEXT_PRIMARY};
        """)
        user_layout.addWidget(username_label)
        user_layout.addStretch()
        
        layout.addWidget(user_widget)
        
        # 分隔线
        self._add_separator(layout)
        
        # 分区按钮
        sections_widget = QWidget()
        sections_layout = QVBoxLayout(sections_widget)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(6)
        
        # 日常任务按钮
        self.daily_btn = self._create_nav_button("日常任务", "daily", checked=True)
        sections_layout.addWidget(self.daily_btn)
        
        # 周常任务按钮
        self.weekly_btn = self._create_nav_button("周常任务", "weekly")
        sections_layout.addWidget(self.weekly_btn)
        
        # 特殊任务按钮
        self.once_btn = self._create_nav_button("特殊任务", "once")
        sections_layout.addWidget(self.once_btn)
        
        layout.addWidget(sections_widget)
        
        # 分隔线
        self._add_separator(layout)
        
        # 标签区域
        tags_header = QLabel("标签筛选")
        tags_header.setObjectName("nav_title")
        tags_header.setStyleSheet(f"""
            font-size: 14px;
            color: {QQStyle.TEXT_SECONDARY};
            padding: 10px 10px 6px 10px;
            font-weight: bold;
        """)
        layout.addWidget(tags_header)
        
        self.tags_list = QListWidget()
        self.tags_list.setObjectName("tag_list")
        self.tags_list.setMaximumHeight(200)
        self.tags_list.setStyleSheet(QQStyle.get_tag_list_style())
        layout.addWidget(self.tags_list)
        
        # 填充剩余空间
        layout.addStretch()
        
        # 分隔线
        self._add_separator(layout)
        
        # 回收站按钮
        self.recycle_bin_btn = self._create_nav_button("回收站", "recycle")
        layout.addWidget(self.recycle_bin_btn)
        
        # 应用导航面板样式
        panel.setStyleSheet(QQStyle.get_navigation_panel_style())
        
        return panel
    
    def _create_nav_button(self, text: str, name: str, checked: bool = False) -> QPushButton:
        """创建导航按钮"""
        btn = QPushButton(text)
        btn.setObjectName(f"{name}_btn")
        btn.setProperty("class", "nav-button")
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        
        # 为不同分区使用不同的辅助色
        accent_colors = {
            "daily": (QQStyle.PRIMARY, QQStyle.PRIMARY_LIGHT),
            "weekly": (QQStyle.ACCENT_TEAL, "#E0F2F1"),
            "once": (QQStyle.ACCENT_ORANGE, "#FFF3E0"),
            "recycle": (QQStyle.DANGER, QQStyle.DANGER_LIGHT)
        }
        
        color, light_color = accent_colors.get(name, (QQStyle.PRIMARY, QQStyle.PRIMARY_LIGHT))
        
        btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 10px;
                padding: 12px 16px;
                text-align: left;
                font-size: 16px;
                color: {QQStyle.TEXT_REGULAR};
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-color: {light_color};
                color: {color};
            }}
            QPushButton:checked {{
                background-color: {light_color};
                color: {color};
                font-weight: bold;
                border-left: 4px solid {color};
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
            }}
        """)
        
        return btn
    
    def _add_separator(self, layout: QVBoxLayout):
        """添加分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {QQStyle.BORDER};")
        layout.addWidget(separator)
    
    def _create_center_panel(self) -> QWidget:
        """创建中央任务区域"""
        panel = QWidget()
        panel.setStyleSheet(f"background-color: {QQStyle.BG_GRAY};")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 使用AnimatedStackedWidget替代QTabWidget
        self.stacked_widget = AnimatedStackedWidget()
        self.stacked_widget.set_animation_type(AnimatedStackedWidget.ANIMATION_NONE)
        self.stacked_widget.set_animation_duration(250)
        
        # 日常任务页面
        self.daily_page = self._create_task_page("daily", "日常任务")
        self.stacked_widget.addWidget(self.daily_page)
        
        # 周常任务页面
        self.weekly_page = self._create_task_page("weekly", "周常任务")
        self.stacked_widget.addWidget(self.weekly_page)
        
        # 特殊任务页面
        self.once_page = self._create_task_page("once", "特殊任务")
        self.stacked_widget.addWidget(self.once_page)
        
        layout.addWidget(self.stacked_widget)
        
        return panel
    
    def _create_task_page(self, section: str, title: str) -> QWidget:
        """创建任务页面"""
        page = QWidget()
        page.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        
        # 页面标题栏
        header = QWidget()
        header.setStyleSheet(f"""
            background-color: {QQStyle.WHITE};
            border-radius: 12px;
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {QQStyle.TEXT_PRIMARY};
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # 任务统计
        self.stats_labels = getattr(self, 'stats_labels', {})
        stats_label = QLabel("0 个任务")
        stats_label.setStyleSheet(f"""
            font-size: 15px;
            color: {QQStyle.TEXT_SECONDARY};
        """)
        self.stats_labels[section] = stats_label
        header_layout.addWidget(stats_label)
        
        layout.addWidget(header)
        
        # 任务列表容器
        list_container = QWidget()
        list_container.setStyleSheet(f"""
            background-color: {QQStyle.WHITE};
            border-radius: 12px;
        """)
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(14, 14, 14, 14)
        list_layout.setSpacing(10)
        
        # 待办任务标题
        pending_header = QLabel("待办")
        pending_header.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {QQStyle.TEXT_SECONDARY};
            padding: 6px 0px;
        """)
        list_layout.addWidget(pending_header)
        
        # 待办任务列表
        self.pending_lists[section] = QListWidget()
        self.pending_lists[section].setObjectName("task_list")
        self.pending_lists[section].setStyleSheet(QQStyle.get_task_list_style())
        self.pending_lists[section].setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.pending_lists[section].setMinimumHeight(180)
        list_layout.addWidget(self.pending_lists[section], 1)
        
        # 已完成任务标题
        completed_header = QLabel("已完成")
        completed_header.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {QQStyle.TEXT_SECONDARY};
            padding: 10px 0px 6px 0px;
        """)
        list_layout.addWidget(completed_header)
        
        # 已完成任务列表
        self.completed_lists[section] = QListWidget()
        self.completed_lists[section].setObjectName("task_list")
        self.completed_lists[section].setStyleSheet(QQStyle.get_task_list_style())
        self.completed_lists[section].setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.completed_lists[section].setMaximumHeight(280)
        list_layout.addWidget(self.completed_lists[section])
        
        layout.addWidget(list_container, 1)
        
        return page
    
    def _create_right_panel(self) -> SlidingPanel:
        """创建右侧多功能面板"""
        panel = SlidingPanel(direction='right')
        panel.set_title("任务详情")
        panel.set_target_width(400)  # 增大宽度以容纳表单
        
        # 使用QStackedWidget来切换不同内容
        from PyQt5.QtWidgets import QStackedWidget
        self.panel_stack = QStackedWidget()
        
        # ===== 页面0: 任务详情 =====
        detail_page = QWidget()
        detail_layout = QVBoxLayout(detail_page)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(12)
        
        self.detail_content = QLabel("选择任务以查看详情")
        self.detail_content.setWordWrap(True)
        self.detail_content.setAlignment(Qt.AlignTop)
        self.detail_content.setStyleSheet(f"""
            font-size: 15px;
            color: {QQStyle.TEXT_REGULAR};
            line-height: 1.6;
        """)
        detail_layout.addWidget(self.detail_content, 1)
        
        # 详情页按钮
        detail_btn_layout = QHBoxLayout()
        detail_btn_layout.setSpacing(10)
        
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setEnabled(False)
        self.edit_btn.setFixedHeight(40)
        self.edit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.PRIMARY};
                color: {QQStyle.WHITE};
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {QQStyle.PRIMARY_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {QQStyle.BORDER};
                color: {QQStyle.TEXT_PLACEHOLDER};
            }}
        """)
        detail_btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {QQStyle.WHITE};
                color: {QQStyle.DANGER};
                border: 2px solid {QQStyle.DANGER};
                border-radius: 8px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {QQStyle.DANGER_LIGHT};
            }}
            QPushButton:disabled {{
                background-color: {QQStyle.WHITE};
                color: {QQStyle.TEXT_PLACEHOLDER};
                border-color: {QQStyle.BORDER};
            }}
        """)
        detail_btn_layout.addWidget(self.delete_btn)
        detail_layout.addLayout(detail_btn_layout)
        
        self.panel_stack.addWidget(detail_page)
        
        # ===== 页面1: 任务表单 =====
        self.task_form = TaskFormWidget()
        self.task_form.task_submitted.connect(self._on_task_form_submitted)
        self.task_form.form_cancelled.connect(self._on_form_cancelled)
        self.panel_stack.addWidget(self.task_form)
        
        # ===== 页面2: 设置 =====
        self.settings_widget = SettingsWidget()
        self.settings_widget.settings_saved.connect(self._on_settings_saved)
        self.settings_widget.settings_cancelled.connect(self._on_form_cancelled)
        self.panel_stack.addWidget(self.settings_widget)
        
        panel.set_content(self.panel_stack)
        
        # 当前面板模式: 'detail', 'add_task', 'edit_task', 'settings'
        self._panel_mode = 'detail'
        
        return panel
    
    def _connect_signals(self):
        """连接信号"""
        # 窗口控制按钮
        self.search_bar.close_btn.clicked.connect(self.close)
        self.search_bar.min_btn.clicked.connect(self.showMinimized)
        self.search_bar.max_btn.clicked.connect(self._toggle_maximize)
        
        # 搜索栏信号
        self.search_bar.search_triggered.connect(self._on_search)
        self.search_bar.search_cleared.connect(self._on_search_cleared)
        self.search_bar.add_task_clicked.connect(self._on_add_task)
        self.search_bar.settings_clicked.connect(self._on_settings)
        
        # 分区按钮
        self.daily_btn.clicked.connect(lambda: self._switch_section("daily"))
        self.weekly_btn.clicked.connect(lambda: self._switch_section("weekly"))
        self.once_btn.clicked.connect(lambda: self._switch_section("once"))
        
        # 堆叠窗口页面切换
        self.stacked_widget.page_changed.connect(self._on_page_changed)
        
        # 任务管理器信号
        self.task_manager.task_added.connect(self._on_task_added)
        self.task_manager.task_updated.connect(self._on_task_updated)
        self.task_manager.task_deleted.connect(self._on_task_deleted)
        self.task_manager.task_completed.connect(self._on_task_completed)
        self.task_manager.task_uncompleted.connect(self._on_task_uncompleted)
        self.task_manager.tags_updated.connect(self._on_tags_updated)
        
        # 标签列表点击事件
        self.tags_list.itemClicked.connect(self._on_tag_clicked)
        
        # 回收站按钮
        self.recycle_bin_btn.clicked.connect(self._on_recycle_bin)
        
        # 编辑和删除按钮
        self.edit_btn.clicked.connect(self._on_edit_task)
        self.delete_btn.clicked.connect(self._on_delete_task)
        
        # 右侧面板信号
        self.right_panel.panel_shown.connect(self._on_panel_shown)
        self.right_panel.panel_hidden.connect(self._on_panel_hidden)
    
    def _setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+F 聚焦搜索框
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.search_bar.focus_search)
        
        # Ctrl+N 新建任务
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(self._on_add_task)
        
        # Escape 关闭右侧面板
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(lambda: self.right_panel.hide_panel())
    
    def _load_initial_data(self):
        """加载初始数据"""
        # 加载标签
        self._load_tags()
        
        # 加载当前分区的任务
        self._load_tasks(self.current_section)
        
        # 更新统计信息
        self._update_stats()
    
    def _load_tasks(self, section: str):
        """加载指定分区的任务"""
        try:
            # 清空现有任务列表
            if section in self.pending_lists:
                self.pending_lists[section].clear()
            if section in self.completed_lists:
                self.completed_lists[section].clear()
            
            # 获取任务数据
            tasks = self.task_manager.get_tasks(section=section, tag=self.current_tag)
            
            logger.debug(f"加载分区 {section} 的任务，共 {len(tasks)} 个")
            
            # 按完成状态分类
            pending_tasks = []
            completed_tasks = []
            
            for task in tasks:
                if task.get("is_completed"):
                    completed_tasks.append(task)
                else:
                    pending_tasks.append(task)
            
            # 按优先级降序排序（高优先级在前），相同优先级按创建时间降序
            pending_tasks.sort(key=lambda x: (-x.get("priority", 1), x.get("created_at", "")), reverse=False)
            completed_tasks.sort(key=lambda x: (-x.get("priority", 1), x.get("created_at", "")), reverse=False)
            
            # 添加待办任务
            for task in pending_tasks:
                self._add_task_to_list(section, task, is_completed=False)
            
            # 添加已完成任务
            for task in completed_tasks:
                self._add_task_to_list(section, task, is_completed=True)
            
            # 更新页面统计
            if section in self.stats_labels:
                total = len(pending_tasks) + len(completed_tasks)
                self.stats_labels[section].setText(f"{len(pending_tasks)} 待办 / {total} 总计")
            
            logger.debug(f"加载了 {len(pending_tasks)} 个待办任务和 {len(completed_tasks)} 个已完成任务")
            
        except Exception as e:
            logger.error(f"加载任务失败: {e}")
    
    def _add_task_to_list(self, section: str, task_data: dict, is_completed: bool = False):
        """添加任务到列表"""
        try:
            # 创建任务卡片
            task_card = TaskCard(task_data)
            
            # 连接信号
            task_card.completed.connect(self._on_task_card_completed)
            task_card.clicked.connect(self._on_task_card_clicked)
            task_card.double_clicked.connect(self._on_task_card_double_clicked)
            
            # 创建列表项
            item = QListWidgetItem()
            card_size = task_card.sizeHint()
            item.setSizeHint(QSize(card_size.width(), card_size.height() + 8))
            
            # 添加到相应列表
            if is_completed:
                list_widget = self.completed_lists.get(section)
            else:
                list_widget = self.pending_lists.get(section)
            
            # 注意：PyQt5的QWidget在布尔上下文中可能返回False，需要用is not None检查
            if list_widget is not None:
                list_widget.addItem(item)
                list_widget.setItemWidget(item, task_card)
                
        except Exception as e:
            logger.error(f"添加任务到列表失败: {e}")
    
    def _load_tags(self):
        """加载标签"""
        try:
            self.tags_list.clear()
            
            # 获取所有标签
            tags = self.task_manager.get_all_tags()
            
            # 添加"全部"选项
            all_item = QListWidgetItem("全部")
            all_item.setData(Qt.UserRole, None)
            self.tags_list.addItem(all_item)
            
            # 添加标签项
            for tag in tags:
                tag_name = tag.get("name", "")
                task_count = tag.get("task_count", 0)
                
                if tag_name:
                    item_text = f"{tag_name} ({task_count})"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, tag_name)
                    self.tags_list.addItem(item)
            
            # 默认选中"全部"
            self.tags_list.setCurrentRow(0)
            
        except Exception as e:
            logger.error(f"加载标签失败: {e}")
    
    def _switch_section(self, section: str):
        """切换分区"""
        if section == self.current_section:
            return
        
        # 更新按钮状态
        self.daily_btn.setChecked(section == "daily")
        self.weekly_btn.setChecked(section == "weekly")
        self.once_btn.setChecked(section == "once")
        
        # 更新堆叠窗口（带动画）
        page_index = {"daily": 0, "weekly": 1, "once": 2}.get(section, 0)
        self.stacked_widget.setCurrentIndex(page_index)
        
        # 更新当前分区
        self.current_section = section
        
        # 发射信号
        self.section_changed.emit(section)
        
        # 加载任务
        self._load_tasks(section)
    
    def _on_page_changed(self, index: int):
        """页面切换完成事件"""
        sections = ["daily", "weekly", "once"]
        if 0 <= index < len(sections):
            section = sections[index]
            if section != self.current_section:
                self.current_section = section
                self._update_nav_buttons(section)
    
    def _update_nav_buttons(self, section: str):
        """更新导航按钮状态"""
        self.daily_btn.setChecked(section == "daily")
        self.weekly_btn.setChecked(section == "weekly")
        self.once_btn.setChecked(section == "once")
    
    def _on_add_task(self):
        """添加任务 - 在右侧面板中显示表单（支持切换）"""
        # 如果面板已展开且当前模式是添加任务，则收回面板
        if self.right_panel.is_expanded() and self._panel_mode == 'add_task':
            self.right_panel.hide_panel()
            return
        
        self._panel_mode = 'add_task'
        self.right_panel.set_title("添加任务")
        
        # 加载所有可用标签
        all_tags = self.task_manager.repository.get_all_tag_names()
        self.task_form.set_available_tags(all_tags)
        
        self.task_form.clear_form()
        
        # 设置默认分区为当前分区
        section_index = {"daily": 0, "weekly": 1, "once": 2}.get(self.current_section, 0)
        self.task_form.section_combo.setCurrentIndex(section_index)
        
        self.panel_stack.setCurrentIndex(1)  # 切换到任务表单页
        
        if not self.right_panel.is_expanded():
            self.right_panel.show_panel()
    
    def _update_stats(self):
        """更新统计信息"""
        try:
            stats = self.task_manager.get_stats()
            
            if stats:
                section_stats = stats.get("sections", {})
                daily_pending = section_stats.get("daily", {}).get("pending", 0)
                weekly_pending = section_stats.get("weekly", {}).get("pending", 0)
                once_pending = section_stats.get("once", {}).get("pending", 0)
                
                status_text = f"日常: {daily_pending} | 周常: {weekly_pending} | 特殊: {once_pending}"
                self.statusBar().showMessage(status_text)
                
        except Exception as e:
            logger.error(f"更新统计信息失败: {e}")
    
    def _on_delete_task(self):
        """删除任务"""
        try:
            if not self.current_selected_task_id:
                QMessageBox.information(self, "提示", "请先选择一个任务")
                return
            
            reply = QMessageBox.question(
                self, 
                "确认删除",
                "确定要删除这个任务吗？\n\n任务将被移动到回收站，可以恢复。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.task_manager.delete_task(self.current_selected_task_id)
                
                if success:
                    self.statusBar().showMessage("任务已移动到回收站", 3000)
                    self.current_selected_task_id = None
                    self.edit_btn.setEnabled(False)
                    self.delete_btn.setEnabled(False)
                    self.detail_content.setText("选择任务以查看详情")
                    self.right_panel.hide_panel()
                    
        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            QMessageBox.critical(self, "错误", f"删除任务失败: {str(e)}")
    
    def _on_task_card_completed(self, task_id: int, is_completed: bool):
        """任务卡片完成状态改变"""
        try:
            if is_completed:
                self.task_manager.complete_task(task_id)
            else:
                self.task_manager.uncomplete_task(task_id)
        except Exception as e:
            logger.error(f"更新任务完成状态失败: {e}")
    
    def _on_task_card_clicked(self, task_id: int):
        """任务卡片点击事件 - 显示任务详情（支持切换）"""
        try:
            # 如果面板已展开且当前是详情模式且点击的是同一个任务，则收回面板
            if (self.right_panel.is_expanded() and 
                self._panel_mode == 'detail' and 
                self.current_selected_task_id == task_id):
                self.right_panel.hide_panel()
                return
            
            task = self.task_manager.get_task(task_id)
            if task:
                # 切换到详情模式
                self._panel_mode = 'detail'
                self.right_panel.set_title("任务详情")
                self.panel_stack.setCurrentIndex(0)  # 确保显示详情页
                
                self._show_task_detail(task)
                self.current_selected_task_id = task_id
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                
                # 显示右侧面板
                if not self.right_panel.is_expanded():
                    self.right_panel.show_panel()
        except Exception as e:
            logger.error(f"显示任务详情失败: {e}")
    
    def _on_task_card_double_clicked(self, task_id: int):
        """任务卡片双击事件"""
        self._on_edit_task()
    
    def _on_tag_clicked(self, item):
        """标签点击事件"""
        try:
            tag_name = item.data(Qt.UserRole)
            self.current_tag = tag_name
            
            self._load_tasks(self.current_section)
            
            if tag_name:
                self.statusBar().showMessage(f"筛选标签: {tag_name}", 3000)
            else:
                self.statusBar().showMessage("显示全部任务", 3000)
                
        except Exception as e:
            logger.error(f"标签筛选失败: {e}")
    
    def _on_tags_updated(self):
        """标签更新事件"""
        self._load_tags()
    
    def _show_task_detail(self, task: dict):
        """显示任务详情"""
        try:
            title = task.get("title", "")
            description = task.get("description", "")
            requirements = task.get("requirements", "")
            section = task.get("section", "daily")
            priority = task.get("priority", 1)
            is_completed = task.get("is_completed", False)
            created_at = task.get("created_at", "")
            due_date = task.get("due_date", "")
            tags = task.get("tags", [])
            
            # 格式化创建时间（只精确到秒）
            if created_at:
                # 处理 ISO 格式时间，截取到秒
                if "." in created_at:
                    created_at = created_at.split(".")[0]
                if "T" in created_at:
                    created_at = created_at.replace("T", " ")
            
            section_names = {
                "daily": "日常任务",
                "weekly": "周常任务",
                "once": "特殊任务"
            }
            section_display = section_names.get(section, "未知")
            
            priority_names = {
                3: ("紧急", QQStyle.DANGER),
                2: ("优先", QQStyle.ACCENT_ORANGE),
                1: ("普通", QQStyle.PRIMARY),
                0: ("建议", QQStyle.TEXT_SECONDARY)
            }
            priority_text, priority_color = priority_names.get(priority, ("普通", QQStyle.PRIMARY))
            
            status_display = "已完成" if is_completed else "进行中"
            status_color = QQStyle.SUCCESS if is_completed else QQStyle.PRIMARY
            
            # 构建HTML
            html = f"""
            <h3 style="color: {QQStyle.TEXT_PRIMARY}; margin-bottom: 16px;">{title if title else '未命名任务'}</h3>
            
            <p style="margin: 8px 0;"><span style="color: {QQStyle.TEXT_SECONDARY};">状态：</span>
               <span style="color: {status_color}; font-weight: bold;">{status_display}</span></p>
            
            <p style="margin: 8px 0;"><span style="color: {QQStyle.TEXT_SECONDARY};">类别：</span>{section_display}</p>
            
            <p style="margin: 8px 0;"><span style="color: {QQStyle.TEXT_SECONDARY};">优先级：</span>
               <span style="color: {priority_color}; font-weight: bold;">{priority_text}</span></p>
            
            <p style="margin: 8px 0;"><span style="color: {QQStyle.TEXT_SECONDARY};">创建时间：</span>{created_at if created_at else '暂无'}</p>
            """
            
            # 截止日期（仅特殊任务显示）
            if section == "once":
                html += f'<p style="margin: 8px 0;"><span style="color: {QQStyle.TEXT_SECONDARY};">截止日期：</span>{due_date if due_date else "暂无"}</p>'
            
            # 描述
            html += f'''
            <p style="margin: 14px 0 6px 0;"><span style="color: {QQStyle.TEXT_SECONDARY};">描述：</span></p>
            <p style="color: {QQStyle.TEXT_REGULAR}; line-height: 1.6; padding-left: 8px;">{description if description else '<span style="color: ' + QQStyle.TEXT_PLACEHOLDER + ';">暂无</span>'}</p>
            '''
            
            # 要求
            html += f'''
            <p style="margin: 14px 0 6px 0;"><span style="color: {QQStyle.TEXT_SECONDARY};">要求：</span></p>
            <p style="color: {QQStyle.TEXT_REGULAR}; line-height: 1.6; padding-left: 8px;">{requirements if requirements else '<span style="color: ' + QQStyle.TEXT_PLACEHOLDER + ';">暂无</span>'}</p>
            '''
            
            # 标签
            html += f'<p style="margin: 14px 0 6px 0;"><span style="color: {QQStyle.TEXT_SECONDARY};">标签：</span></p>'
            if tags:
                tags_html = " ".join([f'<span style="background-color: {QQStyle.BG_GRAY}; padding: 4px 10px; border-radius: 12px; margin: 2px; font-size: 12px;">{tag}</span>' for tag in tags])
                html += f'<p style="padding-left: 8px;">{tags_html}</p>'
            else:
                html += f'<p style="color: {QQStyle.TEXT_PLACEHOLDER}; padding-left: 8px;">暂无</p>'
            
            self.detail_content.setText(html)
            
        except Exception as e:
            logger.error(f"显示任务详情失败: {e}")
            self.detail_content.setText("加载任务详情失败")
    
    def _on_edit_task(self):
        """编辑任务 - 在右侧面板中显示表单（支持切换）"""
        try:
            if not self.current_selected_task_id:
                QMessageBox.information(self, "提示", "请先选择一个任务")
                return
            
            # 如果面板已展开且当前是编辑模式，则收回面板
            if self.right_panel.is_expanded() and self._panel_mode == 'edit_task':
                self.right_panel.hide_panel()
                return
            
            task = self.task_manager.get_task(self.current_selected_task_id)
            if not task:
                QMessageBox.warning(self, "错误", "任务不存在")
                return
            
            self._panel_mode = 'edit_task'
            self.right_panel.set_title("编辑任务")
            
            # 加载所有可用标签
            all_tags = self.task_manager.repository.get_all_tag_names()
            self.task_form.set_available_tags(all_tags)
            
            self.task_form.set_task_data(task)
            self.panel_stack.setCurrentIndex(1)  # 切换到任务表单页
            
            if not self.right_panel.is_expanded():
                self.right_panel.show_panel()
                    
        except Exception as e:
            logger.error(f"编辑任务失败: {e}")
            QMessageBox.critical(self, "错误", f"编辑任务失败: {str(e)}")
    
    def _on_search(self, keyword: str, mode: str):
        """搜索任务"""
        if not keyword:
            # 清空搜索时恢复原来的任务列表
            self._load_tasks(self.current_section)
            self.statusBar().showMessage("已清除搜索", 2000)
            return
        
        results = self.task_manager.search_tasks(keyword, mode)
        
        # 显示搜索结果数量
        self.statusBar().showMessage(f"找到 {len(results)} 个匹配的任务", 3000)
        
        # 清空所有任务列表
        for section in self.pending_lists:
            self.pending_lists[section].clear()
        for section in self.completed_lists:
            self.completed_lists[section].clear()
        
        # 显示搜索结果
        for task in results:
            section = task.get("section", "daily")
            is_completed = task.get("is_completed", False)
            self._add_task_to_list(section, task, is_completed)
    
    def _on_search_cleared(self):
        """搜索清空事件"""
        self._load_tasks(self.current_section)
        self.statusBar().showMessage("已清除搜索", 2000)
    
    def _on_settings(self):
        """打开设置 - 在右侧面板中显示（支持切换）"""
        # 如果面板已展开且当前是设置模式，则收回面板
        if self.right_panel.is_expanded() and self._panel_mode == 'settings':
            self.right_panel.hide_panel()
            return
        
        self._panel_mode = 'settings'
        self.right_panel.set_title("设置")
        self.settings_widget.reload_settings()
        self.panel_stack.setCurrentIndex(2)  # 切换到设置页
        
        if not self.right_panel.is_expanded():
            self.right_panel.show_panel()
    
    def _apply_settings(self):
        """应用设置"""
        try:
            default_section = settings.get("ui.default_section", 0)
            sections = ["daily", "weekly", "once"]
            if 0 <= default_section < len(sections):
                self._switch_section(sections[default_section])
            
            logger.debug("设置已应用")
            
        except Exception as e:
            logger.error(f"应用设置失败: {e}")
    
    def _on_recycle_bin(self):
        """打开回收站"""
        try:
            dialog = RecycleBinDialog(self)
            dialog.task_restored.connect(self._on_task_restored)
            dialog.task_permanently_deleted.connect(self._on_task_permanently_deleted)
            
            if dialog.exec_():
                self.statusBar().showMessage("回收站操作完成", 3000)
                
        except Exception as e:
            logger.error(f"打开回收站失败: {e}")
            QMessageBox.critical(self, "错误", f"打开回收站失败: {str(e)}")
    
    def _on_task_restored(self, task_id: int):
        """任务恢复事件"""
        try:
            self._load_tasks(self.current_section)
            self._update_stats()
            logger.info(f"任务 {task_id} 已恢复")
        except Exception as e:
            logger.error(f"处理任务恢复事件失败: {e}")
    
    def _on_task_permanently_deleted(self, task_id: int):
        """任务永久删除事件"""
        try:
            self._update_stats()
            logger.info(f"任务 {task_id} 已永久删除")
        except Exception as e:
            logger.error(f"处理任务永久删除事件失败: {e}")
    
    def _on_panel_shown(self):
        """面板显示事件"""
        pass
    
    def _on_panel_hidden(self):
        """面板隐藏事件"""
        pass
    
    def _on_daily_reset(self, reset_count: int):
        """日常重置事件"""
        try:
            self._load_tasks(self.current_section)
            self._update_stats()
            self.statusBar().showMessage(f"日常重置完成: 重置了{reset_count}个任务", 5000)
            logger.info(f"日常重置完成: 重置了{reset_count}个任务")
        except Exception as e:
            logger.error(f"处理日常重置事件失败: {e}")
    
    def _on_weekly_reset(self, reset_count: int):
        """周常重置事件"""
        try:
            self._load_tasks(self.current_section)
            self._update_stats()
            self.statusBar().showMessage(f"周常重置完成: 重置了{reset_count}个任务", 5000)
            logger.info(f"周常重置完成: 重置了{reset_count}个任务")
        except Exception as e:
            logger.error(f"处理周常重置事件失败: {e}")
    
    def _on_task_added(self, task_id: int):
        """任务添加事件"""
        self._load_tasks(self.current_section)
        self._update_stats()
    
    def _on_task_updated(self, task_id: int):
        """任务更新事件"""
        self._load_tasks(self.current_section)
        self._update_stats()
    
    def _on_task_deleted(self, task_id: int):
        """任务删除事件"""
        self._load_tasks(self.current_section)
        self._update_stats()
    
    def _on_task_completed(self, task_id: int):
        """任务完成事件"""
        self._load_tasks(self.current_section)
        self._update_stats()
    
    def _on_task_uncompleted(self, task_id: int):
        """任务取消完成事件"""
        self._load_tasks(self.current_section)
        self._update_stats()
    
    def _on_task_form_submitted(self, task_data: dict):
        """任务表单提交事件"""
        try:
            if self._panel_mode == 'add_task':
                # 添加新任务
                task_id = self.task_manager.add_task(
                    title=task_data["title"],
                    section=task_data["section"],
                    description=task_data.get("description", ""),
                    requirements=task_data.get("requirements", ""),
                    priority=task_data.get("priority", 1),
                    due_date=task_data.get("due_date"),
                    reset_weekday=task_data.get("reset_weekday"),
                    tags=task_data.get("tags", []),
                    sort_order=task_data.get("sort_order", 0)
                )
                
                if task_id != -1:
                    self.statusBar().showMessage(f"任务添加成功: {task_data['title']}", 3000)
                    self._load_tasks(self.current_section)
                    self._update_stats()
                    self._load_tags()
                    
                    # 返回详情页
                    self._switch_to_detail_mode()
                else:
                    QMessageBox.warning(self, "错误", "添加任务失败")
                    
            elif self._panel_mode == 'edit_task':
                # 更新任务
                task_id = task_data.get("id", self.current_selected_task_id)
                if task_id:
                    success = self.task_manager.update_task(task_id, **task_data)
                    
                    if success:
                        self.statusBar().showMessage(f"任务更新成功: {task_data['title']}", 3000)
                        self._load_tasks(self.current_section)
                        
                        # 清理未使用的标签
                        self.task_manager.repository.cleanup_unused_tags()
                        self._load_tags()
                        
                        # 更新详情并返回详情页
                        self._show_task_detail(task_data)
                        self._switch_to_detail_mode()
                    else:
                        QMessageBox.warning(self, "错误", "更新任务失败")
                        
        except Exception as e:
            logger.error(f"任务表单提交失败: {e}")
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")
    
    def _on_settings_saved(self):
        """设置保存事件"""
        self.statusBar().showMessage("设置已保存", 3000)
        self._apply_settings()
        self._switch_to_detail_mode()
    
    def _on_form_cancelled(self):
        """表单取消事件"""
        self._switch_to_detail_mode()
    
    def _switch_to_detail_mode(self):
        """切换到详情模式"""
        self._panel_mode = 'detail'
        self.right_panel.set_title("任务详情")
        self.panel_stack.setCurrentIndex(0)
        
        # 如果没有选中任务，隐藏面板
        if not self.current_selected_task_id:
            self.right_panel.hide_panel()

    def _toggle_maximize(self):
        """切换最大化/还原"""
        if self.isMaximized():
            self.showNormal()
            self.search_bar.max_btn.setText("□")
        else:
            self.showMaximized()
            self.search_bar.max_btn.setText("❐")
    
    def _get_edge_at_pos(self, pos: QPoint) -> int:
        """检测鼠标位置所在的窗口边缘"""
        rect = self.rect()
        x, y = pos.x(), pos.y()
        margin = self.EDGE_MARGIN
        
        left = x < margin
        right = x > rect.width() - margin
        top = y < margin
        bottom = y > rect.height() - margin
        
        if top and left:
            return self.EDGE_TOP_LEFT
        elif top and right:
            return self.EDGE_TOP_RIGHT
        elif bottom and left:
            return self.EDGE_BOTTOM_LEFT
        elif bottom and right:
            return self.EDGE_BOTTOM_RIGHT
        elif left:
            return self.EDGE_LEFT
        elif right:
            return self.EDGE_RIGHT
        elif top:
            return self.EDGE_TOP
        elif bottom:
            return self.EDGE_BOTTOM
        
        return self.EDGE_NONE
    
    def _update_cursor_for_edge(self, edge: int):
        """根据边缘位置更新鼠标光标"""
        cursors = {
            self.EDGE_LEFT: Qt.SizeHorCursor,
            self.EDGE_RIGHT: Qt.SizeHorCursor,
            self.EDGE_TOP: Qt.SizeVerCursor,
            self.EDGE_BOTTOM: Qt.SizeVerCursor,
            self.EDGE_TOP_LEFT: Qt.SizeFDiagCursor,
            self.EDGE_BOTTOM_RIGHT: Qt.SizeFDiagCursor,
            self.EDGE_TOP_RIGHT: Qt.SizeBDiagCursor,
            self.EDGE_BOTTOM_LEFT: Qt.SizeBDiagCursor,
        }
        
        if edge in cursors:
            self.setCursor(cursors[edge])
        else:
            self.unsetCursor()
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于窗口拖拽和边缘调整大小"""
        if event.button() == Qt.LeftButton:
            # 最大化状态下不允许调整大小
            if self.isMaximized():
                # 只允许标题栏拖拽
                if event.pos().y() <= self.search_bar.height():
                    self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
                super().mousePressEvent(event)
                return
            
            # 检测是否点击边缘
            edge = self._get_edge_at_pos(event.pos())
            if edge != self.EDGE_NONE:
                self._resize_edge = edge
                self._resize_start_pos = event.globalPos()
                self._resize_start_geometry = self.geometry()
            elif event.pos().y() <= self.search_bar.height():
                # 顶部搜索栏区域可拖拽
                self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 用于窗口拖拽和边缘调整大小"""
        # 正在调整大小
        if self._resize_edge != self.EDGE_NONE and self._resize_start_pos is not None:
            self._do_resize(event.globalPos())
            return
        
        # 正在拖拽
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            if not self.isMaximized():
                self.move(event.globalPos() - self._drag_pos)
            return
        
        # 更新鼠标光标（非拖拽/调整状态时）
        if not self.isMaximized():
            edge = self._get_edge_at_pos(event.pos())
            self._update_cursor_for_edge(edge)
        
        super().mouseMoveEvent(event)
    
    def _do_resize(self, global_pos: QPoint):
        """执行窗口调整大小"""
        if not self._resize_start_geometry:
            return
        
        delta = global_pos - self._resize_start_pos
        geo = QRect(self._resize_start_geometry)
        min_w, min_h = self.minimumWidth(), self.minimumHeight()
        
        edge = self._resize_edge
        
        # 根据边缘调整几何
        if edge in (self.EDGE_LEFT, self.EDGE_TOP_LEFT, self.EDGE_BOTTOM_LEFT):
            new_left = geo.left() + delta.x()
            new_width = geo.right() - new_left + 1
            if new_width >= min_w:
                geo.setLeft(new_left)
        
        if edge in (self.EDGE_RIGHT, self.EDGE_TOP_RIGHT, self.EDGE_BOTTOM_RIGHT):
            new_width = geo.width() + delta.x()
            if new_width >= min_w:
                geo.setWidth(new_width)
        
        if edge in (self.EDGE_TOP, self.EDGE_TOP_LEFT, self.EDGE_TOP_RIGHT):
            new_top = geo.top() + delta.y()
            new_height = geo.bottom() - new_top + 1
            if new_height >= min_h:
                geo.setTop(new_top)
        
        if edge in (self.EDGE_BOTTOM, self.EDGE_BOTTOM_LEFT, self.EDGE_BOTTOM_RIGHT):
            new_height = geo.height() + delta.y()
            if new_height >= min_h:
                geo.setHeight(new_height)
        
        self.setGeometry(geo)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self._drag_pos = None
        self._resize_edge = self.EDGE_NONE
        self._resize_start_pos = None
        self._resize_start_geometry = None
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件 - 最大化/还原"""
        if event.pos().y() <= self.search_bar.height():
            self._toggle_maximize()
        super().mouseDoubleClickEvent(event)

    def closeEvent(self, event):
        """窗口关闭事件"""
        settings.set("window.width", self.width())
        settings.set("window.height", self.height())
        settings.set("window.maximized", self.isMaximized())
        
        if not self.isMaximized():
            settings.set("window.x", self.x())
            settings.set("window.y", self.y())
        
        settings.save()
        
        logger.info("应用程序关闭")
        event.accept()
