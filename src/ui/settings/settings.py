import os
import json
import sys
import logging

try:
    from core.logger import get_logger
    from version import APP_NAME  # 导入应用名称
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger
    from version import APP_NAME

# 添加导入Windows注册表操作模块
import winreg

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
            
            # 确保开机自启动设置为关闭状态
            if self.is_autostart_enabled():
                self.set_autostart(False)
                self.logger.info("重置为默认设置时已关闭开机自启动")
                
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
        
    # 以下为新增的开机自启动相关方法
    
    def get_app_path(self):
        """获取应用程序可执行文件路径"""
        try:
            if getattr(sys, 'frozen', False):
                # PyInstaller打包的应用
                return sys.executable
            else:
                # 开发模式下的主脚本
                main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../main.py'))
                python_exe = sys.executable
                return f"{python_exe} {main_script}"
        except Exception as e:
            self.logger.error(f"获取应用程序路径时出错: {e}")
            return None
    
    def is_autostart_enabled(self):
        """检查应用程序是否设置为开机自启动"""
        try:
            if not sys.platform.startswith('win'):
                self.logger.warning("开机自启动功能仅支持Windows系统")
                return False
                
            app_path = self.get_app_path()
            if not app_path:
                self.logger.warning("无法获取应用程序路径")
                return False
                
            # 打开注册表项
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            
            try:
                # 尝试读取注册表值
                value, _ = winreg.QueryValueEx(key, APP_NAME)
                exists = True
            except FileNotFoundError:
                # 注册表项不存在
                exists = False
                
            winreg.CloseKey(key)
            self.logger.debug(f"自启动状态检查: {exists}")
            return exists
            
        except Exception as e:
            self.logger.error(f"检查开机自启动状态时出错: {e}")
            return False
    
    def set_autostart(self, enable):
        """设置开机自启动状态
        
        Args:
            enable (bool): True表示启用开机自启动，False表示禁用
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if not sys.platform.startswith('win'):
                self.logger.warning("开机自启动功能仅支持Windows系统")
                return False
                
            app_path = self.get_app_path()
            if not app_path:
                self.logger.error("无法获取应用程序路径，无法设置自启动")
                return False
                
            # 检查当前状态，如果状态相同则不做改变
            current_state = self.is_autostart_enabled()
            if current_state == enable:
                self.logger.debug(f"自启动状态已经是{'启用' if enable else '禁用'}状态，无需更改")
                return True
                
            # 打开注册表项
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            if enable:
                # 添加自启动项
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{app_path}"')
                self.logger.info(f"已添加开机自启动: {app_path}")
            else:
                # 移除自启动项
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    self.logger.info("已移除开机自启动")
                except FileNotFoundError:
                    # 注册表项不存在，无需处理
                    self.logger.debug("移除自启动项时未找到注册表项，可能已经不存在")
                    
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            self.logger.error(f"设置开机自启动时出错: {e}")
            return False


# 创建全局设置实例
settings_manager = Settings()

def get_settings():
    """获取设置管理器实例"""
    return settings_manager 