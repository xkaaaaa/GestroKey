import os
import json
import copy
import sys

# 导入版本信息
try:
    from version import __version__
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from version import __version__

try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

from PyQt5.QtCore import QObject, pyqtSignal

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
            # 优先查找项目目录下的配置文件
            src_dir_config = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "settings.json")
            
            if os.path.exists(src_dir_config):
                self.config_file = src_dir_config
                log.info(f"使用项目目录下的配置文件: {src_dir_config}")
            else:
                # 获取应用程序数据目录
                app_data_dir = os.path.join(os.path.expanduser("~"), ".gestrokey")
                if not os.path.exists(app_data_dir):
                    os.makedirs(app_data_dir)
                
                self.config_file = os.path.join(app_data_dir, "settings.json")
                log.info(f"使用用户目录下的配置文件: {self.config_file}")
        else:
            self.config_file = config_file
        
        # 默认设置
        self.default_settings = self.get_default_settings()
        
        # 当前设置
        self.settings = {}
        
        # 加载设置
        self.load_settings()
        
        log.info("设置管理器已初始化")
        
    def get_default_settings(self):
        """获取默认设置
        
        Returns:
            dict: 默认设置字典
        """
        # 默认设置，当没有找到配置文件或者配置文件出错时使用
        default_settings = {
            "app": {
                "start_minimized": False,  # 是否在启动时最小化
                "auto_start_recognition": False,  # 是否在启动时自动开始识别
                "show_tray_notifications": True,  # 是否显示托盘通知
                "stay_on_top": False,  # 是否置顶窗口
                "language": "zh_CN",  # 界面语言
                "theme": "light",  # 界面主题
                "version": __version__  # 使用version模块的版本号
            },
            # 绘制设置
            "drawing": {
                "speed_factor": 1.2,    # 速度因子
                "base_width": 6.0,      # 基础宽度
                "min_width": 3.0,       # 最小宽度
                "max_width": 15.0,      # 最大宽度
                "smoothing": 0.7,       # 平滑度
                "color": "#4299E1",     # 绘制颜色
                "fade_time": 0.5,       # 淡出时间（秒）
                "advanced_brush": True,  # 高级笔刷
                "auto_smoothing": True,  # 自动平滑
                "min_distance": 20,      # 最小触发距离（像素）
                "max_stroke_points": 200, # 最大笔画点数
                "max_stroke_duration": 5, # 最大笔画持续时间（秒）
                "hardware_acceleration": True, # 硬件加速
                "canvas_border": 1,      # 画布边框大小（像素）
                "min_points": 10,     # 最小点数（原手势设置）
                "max_pause_ms": 300,  # 最大暂停时间（毫秒）（原手势设置）
                "min_length": 50,     # 最小长度（原手势设置）
                "sensitivity": 0.8,   # 灵敏度（原手势设置）
            }
        }
        
        return default_settings
        
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
                        "gestures": {
                            "示例手势1": {
                                "directions": "URDL",
                                "action": "ctrl+c"
                            },
                            "示例手势2": {
                                "directions": "LR",
                                "action": "alt+tab"
                            }
                        }
                    }
                    try:
                        with open(gestures_file, 'w', encoding='utf-8') as f:
                            json.dump(empty_gestures, f, ensure_ascii=False, indent=4)
                        log.info(f"已创建示例手势库文件 {gestures_file}")
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
            log.debug(f"合并新设置到默认设置中")
            self.settings = self.merge_settings(self.default_settings, settings)
            
        try:
            # 确保目录存在
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                log.info(f"创建配置目录: {config_dir}")
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
                
            log.info(f"设置已保存到配置文件 {self.config_file}")
            
            # 读取设置以验证是否正确保存
            with open(self.config_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                log.debug(f"验证保存的设置: 成功读取 {len(saved_data)} 个分类")
            
            # 发出设置变更信号
            self.settingsChanged.emit(copy.deepcopy(self.settings))
            
            return True
            
        except Exception as e:
            log.error(f"保存设置失败: {str(e)}")
            import traceback
            log.error(f"错误堆栈: {traceback.format_exc()}")
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
        log.debug(f"设置 {category}/{key} = {value}")
        
        # 确保类别存在
        if category not in self.settings:
            self.settings[category] = {}
            
        # 保存旧值以便日志输出
        old_value = self.settings[category].get(key, "None")
            
        # 设置值
        self.settings[category][key] = value
        
        # 记录日志
        log.info(f"设置已更新: {category}/{key} = {value} (原值: {old_value})")
        
        # 立即保存到文件
        try:
            # 确保目录存在
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            log.debug(f"设置已立即保存到文件: {category}/{key} = {value}")
        except Exception as e:
            log.error(f"保存设置到文件失败: {str(e)}")
            import traceback
            log.error(f"错误堆栈: {traceback.format_exc()}")
        
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
        
        # 特殊设置键名映射 - 根级别设置到正确的类别
        special_keys_mapping = {
            "force_topmost": ("app", "force_topmost"),
            "start_with_system": ("app", "start_with_windows")
        }
        
        # 遍历用户设置，将有效的值合并到结果中
        for category, category_settings in user_settings.items():
            # 首先检查是否为特殊键名
            if category in special_keys_mapping:
                target_category, target_key = special_keys_mapping[category]
                result[target_category][target_key] = category_settings
                log.debug(f"特殊设置 '{category}' 已移动到 '{target_category}/{target_key}'")
                continue
                
            if category in result and isinstance(result[category], dict) and isinstance(category_settings, dict):
                # 类别存在且是字典类型，合并键值
                for key, value in category_settings.items():
                    # 检查类别内特殊键名映射
                    if category == "app" and key == "start_with_system":
                        result[category]["start_with_windows"] = value
                        log.debug(f"设置键名映射: {category}/start_with_system -> {category}/start_with_windows")
                    else:
                        result[category][key] = value
            elif category in ["drawing", "gesture", "app"]:
                # 确保核心类别存在并是字典
                if category not in result:
                    result[category] = {}
                if isinstance(category_settings, dict):
                    for key, value in category_settings.items():
                        # 检查类别内特殊键名映射
                        if category == "app" and key == "start_with_system":
                            result[category]["start_with_windows"] = value
                            log.debug(f"设置键名映射: {category}/start_with_system -> {category}/start_with_windows")
                        else:
                            result[category][key] = value
            else:
                # 处理可能出现在根级别的设置 - 尝试找出它应该属于哪个类别
                if isinstance(category_settings, dict) or not self._is_setting_key_in_defaults(category, defaults):
                    # 这是一个未知的分类或复杂结构，保留它
                    result[category] = copy.deepcopy(category_settings)
                else:
                    # 这可能是一个应该在已知分类中的设置
                    category_found = False
                    for default_category, default_settings in defaults.items():
                        if isinstance(default_settings, dict) and category in default_settings:
                            # 找到了应该放置的类别
                            result[default_category][category] = category_settings
                            category_found = True
                            log.debug(f"设置 '{category}' 已移动到 '{default_category}' 类别")
                            break
                    
                    if not category_found:
                        # 没有找到对应的类别，保留在根级别
                        result[category] = category_settings
                        log.debug(f"未知的设置项 '{category}' 保留在根级别")
                
        return result
        
    def _is_setting_key_in_defaults(self, key, defaults):
        """检查一个设置键是否存在于默认设置的任何类别中
        
        Args:
            key: 要检查的设置键
            defaults: 默认设置
            
        Returns:
            布尔值，指示键是否存在
        """
        for category, settings in defaults.items():
            if isinstance(settings, dict) and key in settings:
                return True
        return False

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