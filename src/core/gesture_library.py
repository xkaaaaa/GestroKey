import os
import json
import traceback
from pathlib import Path

try:
    from logger import get_logger
except ImportError:
    from core.logger import get_logger

class GestureLibrary:
    """
    手势库管理类，负责加载、保存和获取手势配置
    
    手势格式为：
    {
        "手势名称": {
            "direction": "方向序列",
            "action": {
                "type": "动作类型",  # 例如: "shortcut"
                "value": "动作值"    # 例如: "ctrl+c"
            }
        }
    }
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """获取手势库管理器的全局单例实例"""
        if cls._instance is None:
            cls._instance = GestureLibrary()
        return cls._instance
    
    def __init__(self):
        """初始化手势库管理器"""
        self.logger = get_logger("GestureLibrary")
        self.gestures = {}
        self.default_gestures = {}
        
        # 配置文件路径
        self.user_dir = self._get_user_dir()
        self.config_dir = self.user_dir / "config"
        self.gesture_file = self.config_dir / "gestures.json"
        
        # 加载默认手势库和用户手势库
        self._load_default_gestures()
        self.load()
        
        self.logger.info("手势库管理器初始化完成")
    
    def _get_user_dir(self):
        """获取用户目录"""
        home = Path.home()
        if os.name == 'nt':  # Windows
            return home / ".gestrokey"
        else:  # Linux/Mac
            return home / ".gestrokey"
    
    def _load_default_gestures(self):
        """从默认手势库文件加载默认手势"""
        try:
            # 尝试从当前目录或父目录加载
            default_file_path = Path(__file__).parent / "default_gestures.json"
            
            if not default_file_path.exists():
                self.logger.error(f"默认手势库文件不存在: {default_file_path}")
                return False
                
            with open(default_file_path, 'r', encoding='utf-8') as f:
                self.default_gestures = json.load(f)
                
            self.logger.info(f"已从 {default_file_path} 加载默认手势库")
            return True
            
        except Exception as e:
            self.logger.error(f"加载默认手势库失败: {e}")
            return False
    
    def load(self):
        """从文件加载手势库"""
        try:
            # 确保配置目录存在
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # 如果用户手势文件不存在，使用默认手势
            if not self.gesture_file.exists():
                self.logger.info(f"用户手势库不存在，使用默认手势库: {self.gesture_file}")
                self.gestures = self.default_gestures.copy()
                self.save()  # 保存默认手势到用户手势文件
                return True
            
            # 加载用户手势库
            with open(self.gesture_file, 'r', encoding='utf-8') as f:
                self.gestures = json.load(f)
                
            self.logger.info(f"已从 {self.gesture_file} 加载手势库")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"手势库文件格式错误，使用默认手势库: {e}")
            self.gestures = self.default_gestures.copy()
            self.save()  # 保存默认手势到用户手势文件
            return True
            
        except Exception as e:
            self.logger.error(f"加载手势库失败: {e}")
            self.logger.error(traceback.format_exc())
            self.gestures = self.default_gestures.copy()
            self.save()  # 保存默认手势到用户手势文件
            return False
    
    def save(self):
        """保存手势库到文件"""
        try:
            # 确保配置目录存在
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存手势库
            with open(self.gesture_file, 'w', encoding='utf-8') as f:
                json.dump(self.gestures, f, ensure_ascii=False, indent=4)
                
            self.logger.info(f"手势库已保存到 {self.gesture_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存手势库失败: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def get_gesture(self, name):
        """获取指定名称的手势"""
        return self.gestures.get(name)
    
    def get_all_gestures(self):
        """获取所有手势"""
        return self.gestures
    
    def get_gesture_by_direction(self, direction):
        """根据方向序列获取匹配的手势"""
        self.logger.debug(f"尝试查找方向为 {direction} 的手势")
        for name, gesture in self.gestures.items():
            if gesture.get("direction") == direction:
                self.logger.debug(f"找到匹配手势: {name}")
                return name, gesture
        self.logger.debug(f"未找到匹配方向 {direction} 的手势")
        return None, None
    
    def add_gesture(self, name, direction, action_type, action_value):
        """添加或更新手势"""
        self.gestures[name] = {
            "direction": direction,
            "action": {
                "type": action_type,
                "value": action_value
            }
        }
        self.logger.info(f"添加手势: {name}, 方向: {direction}, 动作: {action_type}:{action_value}")
        return True
    
    def remove_gesture(self, name):
        """删除手势"""
        if name in self.gestures:
            del self.gestures[name]
            self.logger.info(f"删除手势: {name}")
            return True
        self.logger.warning(f"尝试删除不存在的手势: {name}")
        return False
    
    def reset_to_default(self):
        """重置为默认手势库"""
        self.logger.info("重置为默认手势库")
        self.gestures = self.default_gestures.copy()
        self.save()
        return True
    
    def list_gestures(self):
        """获取所有手势名称列表"""
        return list(self.gestures.keys())

# 提供全局访问函数
def get_gesture_library():
    """获取手势库管理器的全局实例"""
    return GestureLibrary.get_instance()

# 测试代码
if __name__ == "__main__":
    # 获取手势库实例
    library = get_gesture_library()
    
    # 打印所有手势
    print("所有手势:")
    for name, gesture in library.get_all_gestures().items():
        direction = gesture.get("direction")
        action = gesture.get("action")
        print(f"名称: {name}, 方向: {direction}, 动作类型: {action.get('type')}, 动作值: {action.get('value')}") 