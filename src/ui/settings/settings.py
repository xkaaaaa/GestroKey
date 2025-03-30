import os
import json
import sys

from core.logger import get_logger

class Settings:
    """设置管理器，负责保存和加载用户设置"""
    
    def __init__(self):
        self.logger = get_logger("Settings")
        self.DEFAULT_SETTINGS = self._load_default_settings()
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.settings_file = self._get_settings_file_path()
        self.load()
    
    def _load_default_settings(self):
        """加载默认设置"""
        default_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           "default_settings.json")
        try:
            if os.path.exists(default_settings_path):
                with open(default_settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.logger.info(f"已从 {default_settings_path} 加载默认设置")
                return settings
            else:
                self.logger.warning(f"默认设置文件 {default_settings_path} 不存在，使用内置默认设置")
        except Exception as e:
            self.logger.error(f"加载默认设置失败: {e}")
        
        # 内置默认设置
        default_settings = {
            "pen_width": 3
        }
        return default_settings
        
    def _get_settings_file_path(self):
        """获取设置文件路径"""
        if sys.platform.startswith('win'):
            # Windows系统使用用户文档目录
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(user_dir, ".gestrokey", "config")
        else:
            # 其他系统默认使用home目录
            config_dir = os.path.join(os.path.expanduser("~"), ".gestrokey", "config")
        
        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, "settings.json")
    
    def load(self):
        """从文件加载设置"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    
                # 更新设置，确保所有默认设置都存在
                for key, value in loaded_settings.items():
                    if key in self.settings:
                        self.settings[key] = value
                        
                self.logger.info(f"已从 {self.settings_file} 加载设置")
            else:
                self.logger.info("未找到设置文件，使用默认设置")
                self.save()  # 保存默认设置
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
            # 出错时使用默认设置并尝试保存
            self.settings = self.DEFAULT_SETTINGS.copy()
            self.save()
    
    def save(self):
        """保存设置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            self.logger.info(f"设置已保存到 {self.settings_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取设置项"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """设置设置项"""
        if key in self.settings:
            self.settings[key] = value
            self.logger.debug(f"设置项已更新: {key}={value}")
            return True
        return False
    
    def reset_to_default(self):
        """重置为默认设置"""
        self.logger.info("重置为默认设置")
        self.settings = self.DEFAULT_SETTINGS.copy()
        return self.save()


# 创建全局设置实例
settings_manager = Settings()

def get_settings():
    """获取设置管理器实例"""
    return settings_manager 