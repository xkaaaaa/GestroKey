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
        self.saved_gestures = self.DEFAULT_GESTURES.copy()  # 初始化saved_gestures为默认手势库的副本
        self.gestures_file = self._get_gestures_file_path()
        self.has_unsaved_changes = False
        self.load()
    
    def _load_default_gestures(self):
        """从JSON文件加载默认手势库"""
        default_gestures_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                           "default_gestures.json")
        try:
            if os.path.exists(default_gestures_path):
                with open(default_gestures_path, 'r', encoding='utf-8') as f:
                    gestures = json.load(f)
                
                # 确保所有手势都有正确的ID
                self._ensure_valid_ids(gestures)
                
                self.logger.info(f"已从 {default_gestures_path} 加载默认手势库")
                return gestures
            else:
                self.logger.error(f"默认手势库文件 {default_gestures_path} 不存在")
                raise FileNotFoundError(f"默认手势库文件不存在: {default_gestures_path}")
        except Exception as e:
            self.logger.error(f"加载默认手势库失败: {e}")
            raise
    
    def _ensure_valid_ids(self, gestures):
        """确保所有手势都有有效的整数ID，并且ID是连续的
        
        Args:
            gestures: 手势字典
        """
        # 首先提取所有已有的ID
        valid_ids = []
        for name, gesture in gestures.items():
            if "id" in gesture and isinstance(gesture["id"], int):
                valid_ids.append(gesture["id"])
        
        # 排序ID
        valid_ids.sort()
        
        # 创建ID到名称的映射，用于按ID排序
        id_to_name = {}
        for name, gesture in gestures.items():
            if "id" in gesture:
                id_to_name[gesture["id"]] = name
        
        # 从1开始，确保ID是连续的整数
        next_id = 1
        for name, gesture in list(gestures.items()):
            # 如果没有ID或ID不是整数，分配新ID
            if "id" not in gesture or not isinstance(gesture["id"], int):
                gesture["id"] = next_id
                next_id += 1
                continue
                
            # 如果有ID但不连续，重新分配
            if gesture["id"] != next_id:
                old_id = gesture["id"]
                gesture["id"] = next_id
                self.logger.debug(f"重新分配手势ID: {name}, {old_id} -> {next_id}")
            
            next_id += 1
    
    def _get_next_id(self):
        """获取下一个可用的ID"""
        ids = [gesture.get("id", 0) for gesture in self.gestures.values()]
        ids = [id for id in ids if isinstance(id, int)]
        return max(ids + [0]) + 1
    
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
                for name, gesture in loaded_gestures.items():
                    self.gestures[name] = gesture
                
                # 确保所有手势都有有效的ID
                self._ensure_valid_ids(self.gestures)
                        
                self.logger.info(f"已从 {self.gestures_file} 加载手势库")
                self.has_unsaved_changes = False
                # 保存当前加载的手势库到saved_gestures
                self.saved_gestures = self.gestures.copy()
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
            
            # 确保所有手势都有有效的ID
            self._ensure_valid_ids(self.gestures)
            
            with open(self.gestures_file, 'w', encoding='utf-8') as f:
                json.dump(self.gestures, f, indent=4, ensure_ascii=False)
            self.logger.info(f"手势库已保存到 {self.gestures_file}")
            self.has_unsaved_changes = False
            # 保存当前手势库到saved_gestures
            self.saved_gestures = self.gestures.copy()
            return True
        except Exception as e:
            self.logger.error(f"保存手势库失败: {e}")
            return False
    
    def get_gesture(self, name):
        """获取指定名称的手势"""
        return self.gestures.get(name)
    
    def get_gesture_by_id(self, gesture_id):
        """根据ID获取手势"""
        for name, gesture in self.gestures.items():
            if gesture.get("id") == gesture_id:
                return name, gesture
        return None, None
    
    def get_all_gestures(self, use_saved=False):
        """获取所有手势
        
        Args:
            use_saved: 是否使用已保存的手势库，默认为False表示返回当前手势库
        """
        return self.saved_gestures if use_saved else self.gestures
    
    def get_all_gestures_sorted(self, use_saved=False):
        """获取按ID排序的所有手势
        
        Args:
            use_saved: 是否使用已保存的手势库，默认为False表示返回当前手势库
        """
        # 获取所有手势
        gestures = self.get_all_gestures(use_saved=use_saved)
        
        # 按ID排序
        sorted_gestures = {}
        sorted_items = sorted(gestures.items(), key=lambda x: x[1].get("id", 0))
        
        # 构建排序后的字典
        for name, gesture in sorted_items:
            sorted_gestures[name] = gesture
            
        return sorted_gestures
    
    def get_gesture_by_direction(self, direction):
        """根据方向序列获取匹配的手势"""
        self.logger.debug(f"尝试查找方向为 {direction} 的手势")
        # 从已保存的手势库中查找，而不是从当前可能未保存的手势库中查找
        for name, gesture in self.saved_gestures.items():
            if gesture.get("direction") == direction:
                self.logger.debug(f"找到匹配手势: {name}")
                return name, gesture
        self.logger.debug(f"未找到匹配方向 {direction} 的手势")
        return None, None
    
    def add_gesture(self, name, direction, action_type, action_value, gesture_id=None):
        """添加或更新手势
        
        Args:
            name: 手势名称
            direction: 手势方向
            action_type: 动作类型
            action_value: 动作值
            gesture_id: 手势ID，如果不提供则自动生成
        """
        # 使用整数ID而非字符串
        if gesture_id is None:
            # 检查是否是更新已有手势（通过名称查找）
            existing_gesture = self.gestures.get(name)
            if existing_gesture:
                gesture_id = existing_gesture.get("id")
            
            # 如果仍然没有ID，生成新的
            if gesture_id is None:
                gesture_id = self._get_next_id()
        
        # 确保ID是整数
        if not isinstance(gesture_id, int):
            try:
                gesture_id = int(gesture_id)
            except (ValueError, TypeError):
                gesture_id = self._get_next_id()
        
        # 新的手势数据
        new_gesture = {
            "id": gesture_id,
            "direction": direction,
            "action": {
                "type": action_type,
                "value": action_value
            }
        }
        
        # 检查是否是修改现有手势
        current_gesture = self.gestures.get(name, {})
        if current_gesture != new_gesture:
            self.gestures[name] = new_gesture
            self.has_unsaved_changes = True
            self.logger.info(f"更新手势: {name}, ID: {gesture_id}, 方向: {direction}, 动作: {action_type}:{action_value}")
            return True
        return False
    
    def update_gesture_name(self, old_name, new_name):
        """更新手势名称
        
        Args:
            old_name: 旧名称
            new_name: 新名称
            
        Returns:
            bool: 操作是否成功
        """
        if old_name not in self.gestures:
            self.logger.warning(f"尝试重命名不存在的手势: {old_name}")
            return False
            
        if old_name == new_name:
            return True  # 名称未变，视为成功
            
        if new_name in self.gestures:
            self.logger.warning(f"无法重命名手势，新名称已存在: {new_name}")
            return False
            
        # 复制手势数据并更新名称
        gesture_data = self.gestures[old_name]
        self.gestures[new_name] = gesture_data
        del self.gestures[old_name]
        
        self.has_unsaved_changes = True
        self.logger.info(f"重命名手势: {old_name} -> {new_name}, ID: {gesture_data.get('id')}")
        return True
    
    def remove_gesture(self, name):
        """删除手势并重新排序剩余手势的ID"""
        if name not in self.gestures:
            self.logger.warning(f"尝试删除不存在的手势: {name}")
            return False
            
        # 获取要删除的手势ID
        deleted_id = self.gestures[name].get("id")
        
        # 删除手势
        del self.gestures[name]
        
        # 如果ID无效，无需重排序
        if not isinstance(deleted_id, int):
            self.has_unsaved_changes = True
            return True
            
        # 重排序其他手势的ID
        for other_name, other_gesture in self.gestures.items():
            other_id = other_gesture.get("id")
            if isinstance(other_id, int) and other_id > deleted_id:
                # 将ID减1
                other_gesture["id"] = other_id - 1
                self.logger.debug(f"重排序手势ID: {other_name}, {other_id} -> {other_id-1}")
                
        self.has_unsaved_changes = True
        self.logger.info(f"删除手势: {name}, ID: {deleted_id}, 并重排序剩余手势的ID")
        return True
    
    def reset_to_default(self):
        """重置为默认手势库"""
        self.logger.info("重置为默认手势库")
        if self.gestures != self.DEFAULT_GESTURES:
            self.gestures = self.DEFAULT_GESTURES.copy()
            self.has_unsaved_changes = True
        return True
    
    def list_gestures(self):
        """获取所有手势名称列表"""
        return list(self.gestures.keys())
        
    def has_changes(self):
        """检查是否有未保存的更改"""
        # 首先根据标志快速判断
        if not self.has_unsaved_changes:
            return False
            
        # 如果标志为True，进一步比较当前手势库与已保存的手势库
        if not self.saved_gestures:
            # 如果没有已保存的手势库记录，则认为有未保存的更改
            return True if self.gestures else False
            
        # 检查手势数量是否相同
        if len(self.gestures) != len(self.saved_gestures):
            return True
            
        # 逐一比较手势
        for name, gesture in self.gestures.items():
            if name not in self.saved_gestures:
                return True
            
            if self.saved_gestures[name] != gesture:
                return True
                
        # 检查是否有已保存的手势在当前手势库中不存在
        for name in self.saved_gestures:
            if name not in self.gestures:
                return True
                
        # 实际上没有差异，重置标志
        self.has_unsaved_changes = False
        return False


# 创建全局手势库实例
gesture_library = GestureLibrary()

def get_gesture_library():
    """获取手势库管理器实例"""
    return gesture_library 