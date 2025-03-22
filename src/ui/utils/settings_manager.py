import os
import json
import copy
from PyQt5.QtCore import QObject, pyqtSignal

from app.log import log

class SettingsManager(QObject):
    """设置管理器类，负责管理应用程序设置"""
    
    # 信号定义
    settingsChanged = pyqtSignal(dict)  # 当设置变更时发出，参数为新的设置
    
    def __init__(self, config_file=None):
        """初始化设置管理器
        
        Args:
            config_file: 设置配置文件路径，如果为None则使用默认路径
        """
        super().__init__()
        
        # 设置配置文件路径
        if config_file is None:
            # 获取应用程序数据目录
            app_data_dir = os.path.join(os.path.expanduser("~"), ".gestrokey")
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)
            
            self.config_file = os.path.join(app_data_dir, "settings.json")
        else:
            self.config_file = config_file
        
        # 默认设置
        self.default_settings = {
            # 绘制设置
            "drawing": {
                "speed_factor": 1.0,  # 速度因子
                "base_width": 3.0,   # 基础宽度
                "min_width": 1.0,    # 最小宽度
                "max_width": 5.0,    # 最大宽度
                "smoothing": 0.7,    # 平滑度
                "color": "#4299E1",  # 绘制颜色
                "fade_time": 1.0,    # 淡出时间（秒）
                "advanced_brush": False,  # 高级笔刷
                "auto_smoothing": True,   # 自动平滑
            },
            # 手势设置
            "gesture": {
                "min_points": 10,     # 最小点数
                "max_pause_ms": 300,  # 最大暂停时间（毫秒）
                "min_length": 50,     # 最小手势长度
                "sensitivity": 0.8,   # 识别灵敏度
            },
            # 应用程序设置
            "app": {
                "start_with_windows": False,  # 开机启动
                "start_minimized": False,     # 启动时最小化
                "minimize_to_tray": True,     # 最小化到系统托盘
                "auto_start_recognition": False,  # 自动开始识别
                "show_notifications": True,   # 显示通知
                "log_level": "info",          # 日志级别
            }
        }
        
        # 当前设置
        self.settings = {}
        
        # 加载设置
        self.load_settings()
        
        log.info("设置管理器已初始化")
        
    def load_settings(self):
        """从配置文件加载设置"""
        try:
            # 如果配置文件存在，从文件加载
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    
                    # 将加载的设置与默认设置合并
                    self.settings = self.merge_settings(self.default_settings, loaded_settings)
                    log.info(f"已从配置文件 {self.config_file} 加载设置")
            else:
                # 文件不存在，使用默认设置并保存
                log.info("配置文件不存在，使用默认设置")
                self.settings = copy.deepcopy(self.default_settings)
                self.save_settings(self.settings)
                
                # 同时创建空的手势库文件
                gestures_file = os.path.join(os.path.dirname(self.config_file), "gestures.json")
                if not os.path.exists(gestures_file):
                    empty_gestures = {
                        "version": "1.0",
                        "gestures": {}
                    }
                    try:
                        with open(gestures_file, 'w', encoding='utf-8') as f:
                            json.dump(empty_gestures, f, ensure_ascii=False, indent=4)
                        log.info(f"已创建空的手势库文件 {gestures_file}")
                    except Exception as e:
                        log.error(f"创建手势库文件失败: {str(e)}")
                
        except Exception as e:
            log.error(f"加载设置失败: {str(e)}")
            self.settings = copy.deepcopy(self.default_settings)
        
    def save_settings(self, settings=None):
        """保存设置到配置文件
        
        Args:
            settings: 要保存的设置，如果为None则保存当前设置
            
        Returns:
            是否保存成功
        """
        if settings is not None:
            # 更新当前设置
            self.settings = self.merge_settings(self.default_settings, settings)
            
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                
            log.info(f"设置已保存到配置文件 {self.config_file}")
            
            # 发出设置变更信号
            self.settingsChanged.emit(copy.deepcopy(self.settings))
            
            return True
            
        except Exception as e:
            log.error(f"保存设置失败: {str(e)}")
            return False
        
    def get_settings(self):
        """获取当前设置
        
        Returns:
            当前设置的副本
        """
        return copy.deepcopy(self.settings)
        
    def get_setting(self, category, key, default=None):
        """获取指定设置项
        
        Args:
            category: 设置类别（如"drawing", "gesture", "app"）
            key: 设置键名
            default: 如果设置不存在，返回的默认值
            
        Returns:
            设置值，如果不存在则返回默认值
        """
        if category in self.settings and key in self.settings[category]:
            return self.settings[category][key]
        return default
        
    def set_setting(self, category, key, value):
        """设置指定设置项
        
        Args:
            category: 设置类别（如"drawing", "gesture", "app"）
            key: 设置键名
            value: 设置值
            
        Returns:
            是否设置成功
        """
        # 确保类别存在
        if category not in self.settings:
            self.settings[category] = {}
            
        # 设置值
        self.settings[category][key] = value
        
        # 发出设置变更信号
        self.settingsChanged.emit(copy.deepcopy(self.settings))
        
        return True
        
    def reset_to_defaults(self):
        """重置为默认设置
        
        Returns:
            是否重置成功
        """
        self.settings = copy.deepcopy(self.default_settings)
        
        result = self.save_settings()
        if result:
            log.info("设置已重置为默认值")
            
        return result
        
    def merge_settings(self, defaults, user_settings):
        """合并默认设置和用户设置
        
        Args:
            defaults: 默认设置
            user_settings: 用户设置
            
        Returns:
            合并后的设置
        """
        result = copy.deepcopy(defaults)
        
        # 遍历用户设置，将有效的值合并到结果中
        for category, category_settings in user_settings.items():
            if category in result:
                # 类别存在，合并键值
                for key, value in category_settings.items():
                    if key in result[category]:
                        result[category][key] = value
            else:
                # 类别不存在，整个添加
                result[category] = copy.deepcopy(category_settings)
                
        return result

if __name__ == "__main__":
    import sys
    import tempfile
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
        temp_path = temp.name
        
    # 创建设置管理器
    settings_manager = SettingsManager(temp_path)
    
    # 打印默认设置
    print("默认设置:")
    print(json.dumps(settings_manager.get_settings(), ensure_ascii=False, indent=2))
    
    # 修改设置
    settings_manager.set_setting("drawing", "color", "#FF0000")
    settings_manager.set_setting("app", "start_with_windows", True)
    
    # 保存设置
    settings_manager.save_settings()
    
    # 重新加载设置
    new_manager = SettingsManager(temp_path)
    
    # 打印加载的设置
    print("\n修改后的设置:")
    print(json.dumps(new_manager.get_settings(), ensure_ascii=False, indent=2))
    
    # 重置为默认设置
    new_manager.reset_to_defaults()
    
    # 打印重置后的设置
    print("\n重置后的设置:")
    print(json.dumps(new_manager.get_settings(), ensure_ascii=False, indent=2))
    
    # 清理临时文件
    os.unlink(temp_path) 