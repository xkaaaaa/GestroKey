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
            # 优先查找项目目录下的手势库文件
            try:
                # 尝试获取项目目录
                current_dir = os.path.dirname(os.path.abspath(__file__))  # utils目录
                project_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))  # 项目根目录
                src_dir = os.path.join(project_dir, "src")  # src目录
                
                src_gestures_path = os.path.join(src_dir, "gestures.json")
                if os.path.exists(src_gestures_path):
                    log.info(f"使用项目目录下的手势库文件: {src_gestures_path}")
                    self.config_file = src_gestures_path
                else:
                    # 获取应用程序数据目录
                    app_data_dir = os.path.join(os.path.expanduser("~"), ".gestrokey")
                    if not os.path.exists(app_data_dir):
                        os.makedirs(app_data_dir)
                    
                    self.config_file = os.path.join(app_data_dir, "gestures.json")
                    log.info(f"使用用户目录下的手势库文件: {self.config_file}")
            except Exception as e:
                log.error(f"获取项目目录时出错: {str(e)}")
                # 如果出错，使用默认的用户目录路径
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
                    
                    # 检查是否为新版手势库格式 (有 version 和 gestures 字段)
                    if isinstance(loaded_gestures, dict) and 'version' in loaded_gestures and 'gestures' in loaded_gestures:
                        log.info(f"检测到新版手势库文件格式，版本: {loaded_gestures.get('version', '未知')}")
                        self.gestures = loaded_gestures
                        log.info(f"从配置文件 {self.config_file} 加载了 {len(loaded_gestures.get('gestures', {}))} 个手势")
                    # 验证加载的数据是否符合旧版格式要求
                    elif isinstance(loaded_gestures, dict):
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
        """保存手势到文件
        
        Returns:
            是否保存成功
        """
        try:
            # 确保使用新格式保存
            if 'version' not in self.gestures:
                self.gestures['version'] = "1.0"
                
            if 'gestures' not in self.gestures:
                # 创建gestures字段并移动所有手势到此字段下
                new_gestures = {'version': self.gestures.get('version', "1.0"), 'gestures': {}}
                
                # 复制所有手势
                for key, value in self.gestures.items():
                    if key != 'version':
                        new_gestures['gestures'][key] = value
                        
                self.gestures = new_gestures
                
            # 转换为JSON并保存
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.gestures, f, ensure_ascii=False, indent=2)
                
            log.info(f"手势已保存到 {self.config_file}")
            return True
        except Exception as e:
            log.error(f"保存手势失败: {str(e)}")
            return False
        
    def get_all_gestures(self):
        """获取所有手势
        
        Returns:
            包含所有手势的字典
        """
        gestures_data = copy.deepcopy(self.gestures)
        
        # 检查是否为新版格式
        if 'gestures' in gestures_data:
            # 确保所有手势都有 name 字段，如果没有则使用键名作为默认名称
            for key, gesture in gestures_data['gestures'].items():
                if isinstance(gesture, dict) and 'name' not in gesture:
                    gesture['name'] = key
                
                # 处理方向字段可能是字符串的情况
                if isinstance(gesture, dict) and 'directions' in gesture:
                    directions = gesture['directions']
                    if isinstance(directions, str):
                        if ',' in directions:
                            gesture['directions'] = [d.strip() for d in directions.split(',')]
                        else:
                            gesture['directions'] = [directions] if directions else []
            
            log.debug(f"获取所有手势（新版格式）: {len(gestures_data['gestures'])} 个手势")
        else:
            # 旧版格式的处理
            # 创建新格式的数据结构
            new_format = {
                'version': '1.0',
                'gestures': {}
            }
            
            # 复制所有手势到新格式，确保每个手势都有name字段
            for key, gesture in gestures_data.items():
                if key == 'version':
                    new_format['version'] = gesture
                    continue
                    
                if isinstance(gesture, dict):
                    # 复制手势数据
                    new_format['gestures'][key] = copy.deepcopy(gesture)
                    
                    # 确保有name字段
                    if 'name' not in new_format['gestures'][key]:
                        new_format['gestures'][key]['name'] = key
                    
                    # 处理方向字段可能是字符串的情况
                    if 'directions' in new_format['gestures'][key]:
                        directions = new_format['gestures'][key]['directions']
                        if isinstance(directions, str):
                            if ',' in directions:
                                new_format['gestures'][key]['directions'] = [d.strip() for d in directions.split(',')]
                            else:
                                new_format['gestures'][key]['directions'] = [directions] if directions else []
            
            gestures_data = new_format
            log.debug(f"获取所有手势（旧版格式转换为新版）: {len(gestures_data['gestures'])} 个手势")
        
        return gestures_data
        
    def get_gesture(self, key):
        """获取指定键名的手势
        
        Args:
            key: 手势键名
            
        Returns:
            手势数据字典，不存在则返回None
        """
        # 检查是否是新版手势库格式
        if 'gestures' in self.gestures:
            gesture = copy.deepcopy(self.gestures['gestures'].get(key))
            
            # 确保返回的方向是列表格式
            if gesture and 'directions' in gesture:
                directions = gesture['directions']
                if not isinstance(directions, list):
                    if isinstance(directions, str):
                        if ',' in directions:
                            gesture['directions'] = [d.strip() for d in directions.split(',')]
                            log.info(f"获取手势 {key}: 将方向字符串 '{directions}' 转换为列表 {gesture['directions']}")
                        else:
                            gesture['directions'] = [directions] if directions else []
                            log.info(f"获取手势 {key}: 将单个方向 '{directions}' 转换为列表 {gesture['directions']}")
                    else:
                        gesture['directions'] = []
                        log.warning(f"获取手势 {key}: 无法识别的方向格式 {directions}, 转换为空列表")
                else:
                    log.info(f"获取手势 {key}: 方向已是列表格式 {directions}")
                    
            # 确保返回的手势数据包含name字段
            if gesture and 'name' not in gesture:
                gesture['name'] = key
                log.debug(f"获取手势 {key}: 未找到name字段，使用键名作为默认名称")
                        
            log.info(f"获取手势: 键名={key}, 数据={gesture}")
            return gesture
        else:
            gesture = copy.deepcopy(self.gestures.get(key))
            
            # 确保返回的方向是列表格式
            if gesture and 'directions' in gesture:
                directions = gesture['directions']
                if not isinstance(directions, list):
                    if isinstance(directions, str):
                        if ',' in directions:
                            gesture['directions'] = [d.strip() for d in directions.split(',')]
                            log.info(f"获取手势 {key}: 将方向字符串 '{directions}' 转换为列表 {gesture['directions']}")
                        else:
                            gesture['directions'] = [directions] if directions else []
                            log.info(f"获取手势 {key}: 将单个方向 '{directions}' 转换为列表 {gesture['directions']}")
                    else:
                        gesture['directions'] = []
                        log.warning(f"获取手势 {key}: 无法识别的方向格式 {directions}, 转换为空列表")
                else:
                    log.info(f"获取手势 {key}: 方向已是列表格式 {directions}")
                    
            # 确保返回的手势数据包含name字段
            if gesture and 'name' not in gesture:
                gesture['name'] = key
                log.debug(f"获取手势 {key}: 未找到name字段，使用键名作为默认名称")
                    
            log.info(f"获取手势(旧格式): 键名={key}, 数据={gesture}")
            return gesture
        
    def add_gesture(self, key, name, directions, action):
        """添加新手势
        
        Args:
            key: 手势键名
            name: 手势名称（可选），如果为空则使用键名
            directions: 手势方向列表
            action: 手势操作代码
            
        Returns:
            是否添加成功
        """
        try:
            # 确保名称不为空
            if not name:
                name = key
                
            # 确保directions是列表格式
            if isinstance(directions, str):
                if ',' in directions:
                    directions = [d.strip() for d in directions.split(',')]
                else:
                    directions = [directions] if directions else []
            
            # 检查是否是新版格式
            if 'gestures' in self.gestures:
                # 检查键名是否已存在
                if key in self.gestures['gestures']:
                    log.warning(f"添加手势失败: 键名 {key} 已存在")
                    return False
                
                # 添加新手势
                self.gestures['gestures'][key] = {
                    "name": name,
                    "directions": directions,
                    "action": action
                }
            else:
                # 旧版格式，直接添加到根字典
                # 检查键名是否已存在
                if key in self.gestures:
                    log.warning(f"添加手势失败: 键名 {key} 已存在")
                    return False
                
                # 添加新手势
                self.gestures[key] = {
                    "name": name,
                    "directions": directions,
                    "action": action
                }
            
            # 保存手势配置
            success = self.save_gestures()
            
            # 发出信号
            if success:
                self.gesturesChanged.emit(self.get_all_gestures())
            
            return success
        except Exception as e:
            log.error(f"添加手势失败: {str(e)}")
            return False
        
    def update_gesture(self, old_key, new_key, name, directions, action):
        """更新现有手势
        
        Args:
            old_key: 原手势键名
            new_key: 新手势键名（可以与原键名相同）
            name: 手势名称（可选），如果为空则使用键名
            directions: 手势方向列表
            action: 手势操作代码
            
        Returns:
            是否更新成功
        """
        try:
            # 确保名称不为空
            if not name:
                name = new_key
                
            # 确保directions是列表格式
            if isinstance(directions, str):
                if ',' in directions:
                    directions = [d.strip() for d in directions.split(',')]
                else:
                    directions = [directions] if directions else []
            
            # 检查是否是新版格式
            if 'gestures' in self.gestures:
                target_gestures = self.gestures['gestures']
            else:
                target_gestures = self.gestures
                
            # 检查原键名是否存在
            if old_key not in target_gestures:
                log.warning(f"更新手势失败: 键名 {old_key} 不存在")
                return False
            
            # 如果新键名与旧键名不同，检查新键名是否已存在
            if old_key != new_key and new_key in target_gestures:
                log.warning(f"更新手势失败: 新键名 {new_key} 已存在")
                return False
            
            # 如果键名有变更，需要删除旧手势并添加新手势
            if old_key != new_key:
                # 保存旧手势数据（可能有其他字段）
                old_gesture = target_gestures.pop(old_key)
                
                # 更新数据
                updated_gesture = {
                    "name": name,
                    "directions": directions,
                    "action": action
                }
                
                # 如果旧手势有其他字段，保留它们
                for key, value in old_gesture.items():
                    if key not in updated_gesture:
                        updated_gesture[key] = value
                
                # 添加新手势
                target_gestures[new_key] = updated_gesture
            else:
                # 键名未变，直接更新
                target_gestures[old_key] = {
                    "name": name,
                    "directions": directions,
                    "action": action
                }
            
            # 保存手势配置
            success = self.save_gestures()
            
            # 发出信号
            if success:
                self.gesturesChanged.emit(self.get_all_gestures())
                log.info(f"更新了手势: {old_key} -> {new_key} ({name})")
            
            return success
        except Exception as e:
            log.error(f"更新手势失败: {str(e)}")
            return False
        
    def delete_gesture(self, key):
        """删除手势
        
        Args:
            key: 手势键名
            
        Returns:
            是否删除成功
        """
        # 检查是否是新版格式
        is_new_format = 'version' in self.gestures and 'gestures' in self.gestures
        
        # 根据格式确定操作的对象
        target_gestures = self.gestures['gestures'] if is_new_format else self.gestures
        
        # 检查键名是否存在
        if key not in target_gestures:
            log.warning(f"删除手势失败: 键名 {key} 不存在")
            return False
            
        # 删除手势
        gesture_data = target_gestures.pop(key)
        
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