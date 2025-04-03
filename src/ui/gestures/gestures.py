import os
import json
import sys
import pathlib

from core.logger import get_logger

class GestureLibrary:
    """手势库管理器，负责保存和加载用户手势库"""
    
    def __init__(self):
        self.logger = get_logger("GestureLibrary")
        self.DEFAULT_GESTURES = self._load_default_gestures()
        self.gestures = self.DEFAULT_GESTURES.copy()
        self.gestures_file = self._get_gestures_file_path()
        self.load()
    
    def _load_default_gestures(self):
        """从JSON文件加载默认手势库"""
        default_gestures_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           "default_gestures.json")
        try:
            if os.path.exists(default_gestures_path):
                with open(default_gestures_path, 'r', encoding='utf-8') as f:
                    gestures = json.load(f)
                self.logger.info(f"已从 {default_gestures_path} 加载默认手势库")
                return gestures
            else:
                self.logger.error(f"默认手势库文件 {default_gestures_path} 不存在")
                raise FileNotFoundError(f"默认手势库文件不存在: {default_gestures_path}")
        except Exception as e:
            self.logger.error(f"加载默认手势库失败: {e}")
            raise
        
    def _get_gestures_file_path(self):
        """获取手势库文件路径"""
        if sys.platform.startswith('win'):
            # Windows系统使用用户文档目录
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(user_dir, ".gestrokey", "config")
        else:
            # 其他系统默认使用home目录
            config_dir = os.path.join(os.path.expanduser("~"), ".gestrokey", "config")
        
        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, "gestures.json")
    
    def load(self):
        """从文件加载手势库"""
        try:
            if os.path.exists(self.gestures_file):
                with open(self.gestures_file, 'r', encoding='utf-8') as f:
                    loaded_gestures = json.load(f)
                    
                # 更新手势库，确保所有默认手势都存在
                for key, value in loaded_gestures.items():
                    self.gestures[key] = value
                        
                self.logger.info(f"已从 {self.gestures_file} 加载手势库")
            else:
                self.logger.info("未找到手势库文件，使用默认手势库")
                self.save()  # 保存默认手势库
        except Exception as e:
            self.logger.error(f"加载手势库失败: {e}")
            # 出错时使用默认手势库并尝试保存
            self.gestures = self.DEFAULT_GESTURES.copy()
            self.save()
    
    def save(self):
        """保存手势库到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.gestures_file), exist_ok=True)
            
            with open(self.gestures_file, 'w', encoding='utf-8') as f:
                json.dump(self.gestures, f, indent=4, ensure_ascii=False)
            self.logger.info(f"手势库已保存到 {self.gestures_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存手势库失败: {e}")
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
        self.gestures = self.DEFAULT_GESTURES.copy()
        return self.save()
    
    def list_gestures(self):
        """获取所有手势名称列表"""
        return list(self.gestures.keys())


# 创建全局手势库实例
gesture_library = GestureLibrary()

def get_gesture_library():
    """获取手势库管理器实例"""
    return gesture_library 