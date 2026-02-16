#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
幽梦个人助手 - 主程序入口
作者: 幽梦开发团队
"""

import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

# 项目模块导入
from data.database import init_database
from ui.main_window import MainWindow
from core.auto_reset_service import AutoResetService
from config.settings import settings, APP_NAME, APP_VERSION
from utils.logger import logger


def setup_application():
    """设置应用程序"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("幽梦工作室")
    
    # 设置字体 - 增大默认字体
    font = QFont("Microsoft YaHei", 11)
    app.setFont(font)
    
    return app


def show_splash_screen():
    """显示启动画面"""
    try:
        # 创建启动画面
        splash_pix = QPixmap(400, 300)
        splash_pix.fill(Qt.white)
        
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # 显示启动信息
        splash.showMessage(
            f"正在初始化{APP_NAME}...\n\n"
            f"版本 {APP_VERSION}\n"
            "© 2024 幽梦工作室",
            Qt.AlignBottom | Qt.AlignHCenter,
            Qt.black
        )
        
        splash.show()
        QApplication.processEvents()
        
        return splash
    except Exception:
        # 如果启动画面失败，继续执行
        return None


def initialize_database():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 初始化数据库
        success = init_database()
        
        if success:
            logger.info("数据库初始化成功")
            return True
        else:
            logger.error("数据库初始化失败")
            return False
            
    except Exception as e:
        logger.error(f"数据库初始化异常: {e}")
        logger.error(traceback.format_exc())
        return False


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """处理未捕获的异常"""
    logger.critical("未捕获的异常:", exc_info=(exc_type, exc_value, exc_traceback))
    
    # 显示错误对话框
    error_msg = f"""
    发生未预期的错误：
    
    错误类型: {exc_type.__name__}
    错误信息: {str(exc_value)}
    
    应用程序将退出。
    
    请检查日志文件以获取详细信息。
    """
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("应用程序错误")
    msg_box.setText("发生严重错误")
    msg_box.setInformativeText(error_msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
    
    sys.exit(1)


def main():
    """主函数"""
    # 设置未捕获异常处理器
    sys.excepthook = handle_uncaught_exception
    
    logger.info("=" * 50)
    logger.info(f"{APP_NAME} v{APP_VERSION} 启动")
    logger.info("=" * 50)
    
    # 设置应用程序
    app = setup_application()
    
    # 显示启动画面
    splash = show_splash_screen()
    
    try:
        # 初始化数据库
        if splash:
            splash.showMessage("正在初始化数据库...", Qt.AlignBottom | Qt.AlignHCenter, Qt.black)
            QApplication.processEvents()
        
        if not initialize_database():
            if splash:
                splash.close()
            
            QMessageBox.critical(
                None,
                "初始化失败",
                "数据库初始化失败，应用程序无法启动。\n\n请检查日志文件以获取详细信息。"
            )
            return 1
        
        # 创建主窗口
        if splash:
            splash.showMessage("正在加载主界面...", Qt.AlignBottom | Qt.AlignHCenter, Qt.black)
            QApplication.processEvents()
        
        logger.info("创建主窗口...")
        main_window = MainWindow()
        
        # 创建并启动自动重置服务
        logger.info("初始化自动重置服务...")
        auto_reset_service = AutoResetService(main_window.task_manager)
        
        # 连接重置信号到主窗口
        auto_reset_service.daily_reset_performed.connect(main_window._on_daily_reset)
        auto_reset_service.weekly_reset_performed.connect(main_window._on_weekly_reset)
        
        # 启动自动重置服务
        auto_reset_service.start()
        
        # 保存服务引用
        main_window.auto_reset_service = auto_reset_service
        
        # 恢复窗口状态或使用默认值
        try:
            # 获取当前屏幕信息
            screen = app.primaryScreen()
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # 默认窗口大小为屏幕的一半
            default_width = screen_width // 2
            default_height = screen_height // 2
            
            # 从设置中读取窗口状态
            maximized = settings.get("window.maximized", False)
            
            if maximized:
                main_window.showMaximized()
            else:
                # 检查是否有保存的窗口位置
                saved_x = settings.get("window.x")
                saved_y = settings.get("window.y")
                saved_width = settings.get("window.width")
                saved_height = settings.get("window.height")
                
                if saved_x is not None and saved_y is not None:
                    # 使用保存的位置和大小
                    width = saved_width if saved_width else default_width
                    height = saved_height if saved_height else default_height
                    main_window.setGeometry(saved_x, saved_y, width, height)
                else:
                    # 首次启动：居中显示，大小为屏幕的一半
                    center_x = screen_geometry.x() + (screen_width - default_width) // 2
                    center_y = screen_geometry.y() + (screen_height - default_height) // 2
                    main_window.setGeometry(center_x, center_y, default_width, default_height)
                    
        except Exception as e:
            logger.warning(f"恢复窗口状态失败: {e}")
            # 使用默认大小并居中
            main_window.resize(960, 540)
            main_window.move(100, 100)
        
        # 关闭启动画面并显示主窗口
        if splash:
            # 延迟关闭启动画面，确保主窗口完全加载
            QTimer.singleShot(500, splash.close)
            QTimer.singleShot(500, main_window.show)
        else:
            main_window.show()
        
        logger.info("应用程序启动完成")
        
        # 运行应用程序
        return_code = app.exec_()
        
        # 停止自动重置服务
        auto_reset_service.stop()
        
        logger.info("应用程序退出")
        logger.info("=" * 50)
        
        return return_code
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        logger.error(traceback.format_exc())
        
        if splash:
            splash.close()
        
        QMessageBox.critical(
            None,
            "启动失败",
            f"应用程序启动失败：\n\n{str(e)}\n\n请检查日志文件以获取详细信息。"
        )
        
        return 1


if __name__ == "__main__":
    # 设置控制台编码（Windows）- 仅在有控制台时执行
    if sys.platform == "win32":
        import io
        if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 运行主函数
    exit_code = main()
    sys.exit(exit_code)