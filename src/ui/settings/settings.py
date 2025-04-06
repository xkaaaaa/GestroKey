import os
import json
import sys
import logging

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger

class Settings:
    """设置管理器，负责保存和加载用户设置"""
    
    def __init__(self):
        self.logger = get_logger("Settings")
        self.DEFAULT_SETTINGS = self._load_default_settings()
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.saved_settings = {}  # 用于存储最后一次保存的设置
        self.settings_file = self._get_settings_file_path()
        self.has_unsaved_changes = False
        self.load()
    
    def _load_default_settings(self):
        """加载默认设置"""
        default_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           "default_settings.json")
        # 默认设置，无论何种情况下都会使用这些值作为备选
        default_values = {
            "pen_width": 3,
            "pen_color": [0, 120, 255]
        }
        
        try:
            if os.path.exists(default_settings_path):
                with open(default_settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.logger.info(f"已从 {default_settings_path} 加载默认设置")
                return settings
            else:
                self.logger.warning(f"默认设置文件 {default_settings_path} 不存在，使用内置默认值")
                return default_values
        except Exception as e:
            self.logger.error(f"加载默认设置失败: {e}，使用内置默认值")
            return default_values
        
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
                self.has_unsaved_changes = False
                # 保存当前加载的设置到saved_settings
                self.saved_settings = self.settings.copy()
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
            self.has_unsaved_changes = False
            # 保存当前设置到saved_settings
            self.saved_settings = self.settings.copy()
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
            # 检查值是否发生变化
            if self.settings[key] != value:
                # 更新当前值
                self.settings[key] = value
                
                # 检查是否与保存的值不同，只有在真正不同时才设置has_unsaved_changes标志
                if not self.saved_settings or key not in self.saved_settings or self.saved_settings[key] != value:
                    self.has_unsaved_changes = True
                    self.logger.debug(f"设置项已更新: {key}={value}, 有未保存更改")
                else:
                    # 设置值与保存的值相同，可能是先改后改回
                    self.logger.debug(f"设置项已更新: {key}={value}, 但与保存的值相同")
            return True
        return False
    
    def reset_to_default(self):
        """重置为默认设置"""
        self.logger.info("重置为默认设置")
        if self.settings != self.DEFAULT_SETTINGS:
            self.settings = self.DEFAULT_SETTINGS.copy()
            self.has_unsaved_changes = True
            
        # 保存设置并更新saved_settings
        success = self.save()
        if success:
            self.saved_settings = self.settings.copy()
            self.has_unsaved_changes = False
        return success
        
    def has_changes(self):
        """检查是否有未保存的更改"""
        # 首先根据标志快速判断
        if not self.has_unsaved_changes:
            return False
            
        # 如果标志为True，进一步比较当前设置与已保存的设置
        if not self.saved_settings:
            # 如果没有已保存的设置记录，则认为有未保存的更改
            return True
            
        # 逐一比较设置项
        for key, value in self.settings.items():
            if key not in self.saved_settings or self.saved_settings[key] != value:
                return True
                
        # 检查是否有已保存的设置项在当前设置中不存在
        for key in self.saved_settings:
            if key not in self.settings:
                return True
                
        # 实际上没有差异，重置标志
        self.has_unsaved_changes = False
        return False


# 创建全局设置实例
settings_manager = Settings()

def get_settings():
    """获取设置管理器实例"""
    return settings_manager 