import json
import os
from typing import Any, Dict, Optional
from utils.logger import logger


# 应用程序版本号（统一管理）
APP_VERSION = "1.0.0"
APP_NAME = "幽梦个人助手"


class Settings:
    """应用程序设置管理类"""
    
    def __init__(self, config_file="config.json"):
        """
        初始化设置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self._settings: Dict[str, Any] = {}
        self._default_settings = {
            "app": {
                "name": APP_NAME,
                "version": APP_VERSION,
                "theme": "light",
                "language": "zh_CN"
            },
            "window": {
                "width": 1200,
                "height": 800,
                "maximized": False,
                "sidebar_width": 200,
                "right_panel_width": 300
            },
            "task": {
                "daily_reset_time": "06:00",
                "weekly_reset_day": 0,  # 0=星期一
                "auto_reset_enabled": True,
                "recycle_bin_capacity": 100,
                "auto_save": True,
                "save_interval": 300  # 5分钟
            },
            "ui": {
                "default_section": 0,  # 0=日常任务
                "show_completed": True,
                "auto_expand_panel": False
            },
            "data": {
                "auto_backup": False,
                "backup_interval": 7
            },
            "notification": {
                "enabled": True,
                "sound": True,
                "show_in_taskbar": True
            }
        }
        
        # 加载配置
        self.load()
    
    def load(self) -> bool:
        """
        从文件加载配置
        
        Returns:
            bool: 是否成功加载
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # 合并默认配置和加载的配置
                self._settings = self._deep_merge(self._default_settings, loaded_settings)
                logger.info(f"配置已从 {self.config_file} 加载")
                return True
            else:
                # 使用默认配置
                self._settings = self._default_settings.copy()
                logger.info("使用默认配置")
                return False
                
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self._settings = self._default_settings.copy()
            return False
    
    def save(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            bool: 是否成功保存
        """
        try:
            # 确保目录存在（只有当路径包含目录时才创建）
            dir_path = os.path.dirname(self.config_file)
            if dir_path:  # 只有目录不为空时才创建
                os.makedirs(dir_path, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已保存到 {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔（如 'app.name'）
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        try:
            keys = key.split('.')
            value = self._settings
            
            for k in keys:
                value = value[k]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔（如 'app.name'）
            value: 配置值
            auto_save: 是否自动保存
            
        Returns:
            bool: 是否成功设置
        """
        try:
            keys = key.split('.')
            target = self._settings
            
            # 导航到最后一个字典
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            
            # 设置值
            target[keys[-1]] = value
            
            # 自动保存
            if auto_save:
                return self.save()
            
            return True
        except Exception as e:
            logger.error(f"设置配置失败: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            bool: 是否成功重置
        """
        self._settings = self._default_settings.copy()
        return self.save()
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        深度合并两个字典
        
        Args:
            base: 基础字典
            update: 更新字典
            
        Returns:
            Dict: 合并后的字典
        """
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @property
    def all_settings(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        Returns:
            Dict[str, Any]: 所有配置
        """
        return self._settings.copy()


# 创建全局设置实例
settings = Settings()