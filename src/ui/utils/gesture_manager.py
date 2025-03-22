import os
import json
import copy
from PyQt5.QtCore import QObject, pyqtSignal

from app.log import log

class GestureManager(QObject):
    """手势管理器，负责管理手势数据的存储和检索"""
    
    # 信号定义
    gesturesChanged = pyqtSignal(dict)  # 当手势数据变更时发出，参数为新的手势数据
    
    def __init__(self, config_file=None):
        """初始化手势管理器
        
        Args:
            config_file: 手势配置文件路径，如果为None则使用默认路径
        """
        super().__init__()
        
        # 设置配置文件路径
        if config_file is None:
            # 获取应用程序数据目录
            app_data_dir = os.path.join(os.path.expanduser("~"), ".gestrokey")
            if not os.path.exists(app_data_dir):
                os.makedirs(app_data_dir)
            
            self.config_file = os.path.join(app_data_dir, "gestures.json")
        else:
            self.config_file = config_file
        
        # 默认手势配置
        self.default_gestures = {
            "up": {
                "name": "向上",
                "directions": "up",
                "action": "maximize_current_window"
            },
            "down": {
                "name": "向下",
                "directions": "down",
                "action": "minimize_current_window"
            },
            "left": {
                "name": "向左",
                "directions": "left",
                "action": "prev_window"
            },
            "right": {
                "name": "向右",
                "directions": "right",
                "action": "next_window"
            },
            "circ": {
                "name": "画圈",
                "directions": "up,right,down,left",
                "action": "restore_all"
            }
        }
        
        # 当前手势数据
        self.gestures = {}
        
        # 加载手势数据
        self.load_gestures()
        
        log.info("手势管理器已初始化")
        
    def load_gestures(self):
        """从配置文件加载手势数据"""
        try:
            # 如果配置文件存在，从文件加载
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_gestures = json.load(f)
                    
                    # 验证加载的数据是否符合格式要求
                    if isinstance(loaded_gestures, dict):
                        self.gestures = loaded_gestures
                        log.info(f"从配置文件 {self.config_file} 加载了 {len(self.gestures)} 个手势")
                    else:
                        log.error("配置文件格式错误，使用默认配置")
                        self.gestures = copy.deepcopy(self.default_gestures)
            else:
                # 文件不存在，使用默认配置并保存
                log.info("配置文件不存在，使用默认配置")
                self.gestures = copy.deepcopy(self.default_gestures)
                self.save_gestures()
                
        except Exception as e:
            log.error(f"加载手势配置失败: {str(e)}")
            self.gestures = copy.deepcopy(self.default_gestures)
        
    def save_gestures(self):
        """将手势数据保存到配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.gestures, f, ensure_ascii=False, indent=2)
                
            log.info(f"保存了 {len(self.gestures)} 个手势到配置文件 {self.config_file}")
            return True
            
        except Exception as e:
            log.error(f"保存手势配置失败: {str(e)}")
            return False
        
    def get_all_gestures(self):
        """获取所有手势
        
        Returns:
            包含所有手势的字典
        """
        return copy.deepcopy(self.gestures)
        
    def get_gesture(self, key):
        """获取指定键名的手势
        
        Args:
            key: 手势键名
            
        Returns:
            手势数据字典，不存在则返回None
        """
        return copy.deepcopy(self.gestures.get(key))
        
    def add_gesture(self, key, name, directions, action):
        """添加新手势
        
        Args:
            key: 手势键名
            name: 手势名称
            directions: 手势方向
            action: 触发操作
            
        Returns:
            是否添加成功
        """
        # 检查键名是否已存在
        if key in self.gestures:
            log.warning(f"添加手势失败: 键名 {key} 已存在")
            return False
            
        # 添加手势
        self.gestures[key] = {
            "name": name,
            "directions": directions,
            "action": action
        }
        
        # 保存并发出信号
        result = self.save_gestures()
        if result:
            self.gesturesChanged.emit(self.get_all_gestures())
            log.info(f"添加了新手势: {key} ({name})")
            
        return result
        
    def update_gesture(self, old_key, new_key, name, directions, action):
        """更新手势
        
        Args:
            old_key: 原手势键名
            new_key: 新手势键名
            name: 手势名称
            directions: 手势方向
            action: 触发操作
            
        Returns:
            是否更新成功
        """
        # 检查原键名是否存在
        if old_key not in self.gestures:
            log.warning(f"更新手势失败: 键名 {old_key} 不存在")
            return False
            
        # 如果键名发生变化，检查新键名是否已存在
        if old_key != new_key and new_key in self.gestures:
            log.warning(f"更新手势失败: 新键名 {new_key} 已存在")
            return False
            
        # 如果键名发生变化，需要删除旧键名并添加新键名
        if old_key != new_key:
            # 删除旧键名
            gesture_data = self.gestures.pop(old_key)
            # 添加新键名
            self.gestures[new_key] = {
                "name": name,
                "directions": directions,
                "action": action
            }
            log.info(f"手势键名已从 {old_key} 更改为 {new_key}")
        else:
            # 键名未变，直接更新数据
            self.gestures[old_key] = {
                "name": name,
                "directions": directions,
                "action": action
            }
            
        # 保存并发出信号
        result = self.save_gestures()
        if result:
            self.gesturesChanged.emit(self.get_all_gestures())
            log.info(f"更新了手势: {new_key} ({name})")
            
        return result
        
    def delete_gesture(self, key):
        """删除手势
        
        Args:
            key: 手势键名
            
        Returns:
            是否删除成功
        """
        # 检查键名是否存在
        if key not in self.gestures:
            log.warning(f"删除手势失败: 键名 {key} 不存在")
            return False
            
        # 删除手势
        gesture_data = self.gestures.pop(key)
        
        # 保存并发出信号
        result = self.save_gestures()
        if result:
            self.gesturesChanged.emit(self.get_all_gestures())
            log.info(f"删除了手势: {key} ({gesture_data.get('name', '')})")
            
        return result
        
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.gestures = copy.deepcopy(self.default_gestures)
        
        # 保存并发出信号
        result = self.save_gestures()
        if result:
            self.gesturesChanged.emit(self.get_all_gestures())
            log.info("已重置为默认手势配置")
            
        return result

if __name__ == "__main__":
    import sys
    import tempfile
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
        temp_path = temp.name
        
    # 创建手势管理器
    gesture_manager = GestureManager(temp_path)
    
    # 测试添加手势
    gesture_manager.add_gesture("test1", "测试手势1", "up,down", "next_window")
    
    # 测试更新手势
    gesture_manager.update_gesture("test1", "test2", "测试手势2", "left,right", "prev_window")
    
    # 测试删除手势
    gesture_manager.delete_gesture("test2")
    
    # 打印所有手势
    print(json.dumps(gesture_manager.get_all_gestures(), ensure_ascii=False, indent=2))
    
    # 重置为默认配置
    gesture_manager.reset_to_defaults()
    
    # 再次打印所有手势
    print(json.dumps(gesture_manager.get_all_gestures(), ensure_ascii=False, indent=2))
    
    # 清理临时文件
    os.unlink(temp_path) 