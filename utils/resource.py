import os
import sys


def resource_path(relative_path):
    """
    获取资源的绝对路径，支持PyInstaller打包
    
    Args:
        relative_path: 相对于项目根目录的资源路径
        
    Returns:
        str: 资源的绝对路径
    """
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except AttributeError:
        # 正常Python环境
        base_path = os.path.abspath(".")
    
    # 构建完整路径
    full_path = os.path.join(base_path, relative_path)
    
    # 标准化路径
    return os.path.normpath(full_path)


def get_icon_path(icon_name):
    """
    获取图标文件的路径（Qt样式表兼容格式）
    
    Args:
        icon_name: 图标文件名
        
    Returns:
        str: 图标文件的绝对路径，使用正斜杠分隔
    """
    path = resource_path(os.path.join("resources", "icons", icon_name))
    # 使用正斜杠以兼容Qt样式表
    return path.replace("\\", "/")


def get_stylesheet_path(theme="light"):
    """
    获取样式表文件的路径
    
    Args:
        theme: 主题名称（'light' 或 'dark'）
        
    Returns:
        str: 样式表文件的绝对路径
    """
    return resource_path(os.path.join("resources", "styles", f"{theme}.qss"))


def ensure_directory(path):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        bool: 是否成功
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False


class Icons:
    """图标路径常量 - 统一管理所有图标引用"""
    CHECK_GREEN = get_icon_path("check_green.svg")
    CHECK_BLUE = get_icon_path("check_blue.svg")