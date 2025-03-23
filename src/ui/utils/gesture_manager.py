import os
import json
import copy
import sys
import uuid
import base64

# 导入版本信息
try:
    from version import __version__
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from version import __version__

# 尝试导入log模块
try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

from PyQt5.QtCore import QObject, pyqtSignal

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
                        
                        # 预处理手势动作，解码Base64
                        if 'gestures' in loaded_gestures and isinstance(loaded_gestures['gestures'], dict):
                            for gesture_key, gesture_data in loaded_gestures['gestures'].items():
                                if isinstance(gesture_data, dict) and 'action' in gesture_data:
                                    try:
                                        # 解码Base64保存到decoded_action字段
                                        base64_action = gesture_data['action']
                                        decoded_action = base64.b64decode(base64_action).decode('utf-8')
                                        gesture_data['decoded_action'] = decoded_action
                                        log.debug(f"预处理手势 '{gesture_key}' 的动作代码")
                                    except Exception as e:
                                        log.warning(f"解码手势 '{gesture_key}' 的动作代码时出错: {str(e)}")
                        
                        self.gestures = loaded_gestures
                        log.info(f"从配置文件 {self.config_file} 加载了 {len(loaded_gestures.get('gestures', {}))} 个手势")
                    # 验证加载的数据是否符合旧版格式要求
                    elif isinstance(loaded_gestures, dict):
                        # 处理旧版格式的手势，同样进行预解码
                        for gesture_key, gesture_data in loaded_gestures.items():
                            if gesture_key != 'version' and isinstance(gesture_data, dict) and 'action' in gesture_data:
                                try:
                                    # 解码Base64保存到decoded_action字段
                                    base64_action = gesture_data['action']
                                    decoded_action = base64.b64decode(base64_action).decode('utf-8')
                                    gesture_data['decoded_action'] = decoded_action
                                    log.debug(f"预处理旧版格式手势 '{gesture_key}' 的动作代码")
                                except Exception as e:
                                    log.warning(f"解码旧版格式手势 '{gesture_key}' 的动作代码时出错: {str(e)}")
                        
                        self.gestures = loaded_gestures
                        log.info(f"从配置文件 {self.config_file} 加载了 {len(self.gestures)} 个手势")
                    else:
                        log.error("配置文件格式错误，使用默认配置")
                        self.gestures = copy.deepcopy(self.default_gestures)
                        self._preprocess_default_gestures()
            else:
                # 文件不存在，使用默认配置并保存
                log.info("配置文件不存在，使用默认配置")
                self.gestures = copy.deepcopy(self.default_gestures)
                self._preprocess_default_gestures()
                self.save_gestures()
                
        except Exception as e:
            log.error(f"加载手势配置失败: {str(e)}")
            self.gestures = copy.deepcopy(self.default_gestures)
            self._preprocess_default_gestures()
        
    def _preprocess_default_gestures(self):
        """预处理默认手势，解码Base64动作"""
        if isinstance(self.gestures, dict):
            if 'gestures' in self.gestures and isinstance(self.gestures['gestures'], dict):
                # 新版格式处理
                for gesture_key, gesture_data in self.gestures['gestures'].items():
                    if isinstance(gesture_data, dict) and 'action' in gesture_data:
                        try:
                            # 解码Base64保存到decoded_action字段
                            base64_action = gesture_data['action']
                            if isinstance(base64_action, str):
                                decoded_action = base64.b64decode(base64_action).decode('utf-8')
                                gesture_data['decoded_action'] = decoded_action
                                log.debug(f"预处理默认手势 '{gesture_key}' 的动作代码")
                        except Exception as e:
                            log.warning(f"解码默认手势 '{gesture_key}' 的动作代码时出错: {str(e)}")
            else:
                # 旧版格式处理
                for gesture_key, gesture_data in self.gestures.items():
                    if gesture_key != 'version' and isinstance(gesture_data, dict) and 'action' in gesture_data:
                        try:
                            # 解码Base64保存到decoded_action字段
                            base64_action = gesture_data['action']
                            if isinstance(base64_action, str):
                                decoded_action = base64.b64decode(base64_action).decode('utf-8')
                                gesture_data['decoded_action'] = decoded_action
                                log.debug(f"预处理默认手势 '{gesture_key}' 的动作代码")
                        except Exception as e:
                            log.warning(f"解码默认手势 '{gesture_key}' 的动作代码时出错: {str(e)}")

    def save_gestures(self):
        """保存手势到文件
        
        Returns:
            是否保存成功
        """
        try:
            # 确保使用新格式保存
            if 'version' not in self.gestures:
                self.gestures['version'] = __version__
                
            if 'gestures' not in self.gestures:
                # 创建gestures字段并移动所有手势到此字段下
                new_gestures = {'version': self.gestures.get('version', __version__), 'gestures': {}}
                
                # 复制所有手势
                for key, value in self.gestures.items():
                    if key != 'version':
                        new_gestures['gestures'][key] = value
                        
                self.gestures = new_gestures
            
            # 创建一个深拷贝用于保存，移除decoded_action字段以避免重复存储
            save_data = copy.deepcopy(self.gestures)
            if 'gestures' in save_data and isinstance(save_data['gestures'], dict):
                for gesture_data in save_data['gestures'].values():
                    if isinstance(gesture_data, dict) and 'decoded_action' in gesture_data:
                        del gesture_data['decoded_action']
                
            # 转换为JSON并保存
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
                
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
            key: 手势的键名
            name: 手势的显示名称
            directions: 手势方向序列
            action: 手势触发的操作脚本
            
        Returns:
            是否添加成功
        """
        try:
            log.info(f"添加手势 {key}: {name}, 方向: {directions}")
            
            # 确保手势库使用新格式
            if 'gestures' not in self.gestures:
                self.gestures['gestures'] = {}
                
            # 检查手势键名是否已存在
            if 'gestures' in self.gestures and key in self.gestures['gestures']:
                log.warning(f"手势键名 {key} 已存在，无法添加")
                return False
                
            # 预处理方向
            if isinstance(directions, list):
                directions_str = ','.join(directions)
            else:
                directions_str = directions
                
            # 预解码action
            decoded_action = None
            try:
                decoded_action = base64.b64decode(action).decode('utf-8')
                log.debug(f"预解码手势动作成功: {decoded_action[:50]}..." if len(decoded_action) > 50 else decoded_action)
            except Exception as e:
                log.warning(f"预解码手势动作失败: {str(e)}")
            
            # 添加到手势库
            self.gestures['gestures'][key] = {
                'name': name,
                'directions': directions_str,
                'action': action,
                'decoded_action': decoded_action
            }
            
            # 保存手势库
            result = self.save_gestures()
            
            # 发出手势变更信号
            self.gesturesChanged.emit(copy.deepcopy(self.gestures))
            
            return result
        except Exception as e:
            log.error(f"添加手势失败: {str(e)}")
            return False
        
    def update_gesture(self, old_key, new_key, name, directions, action):
        """更新手势
        
        Args:
            old_key: 原手势键名
            new_key: 新手势键名
            name: 手势显示名称
            directions: 手势方向序列
            action: 手势触发的操作脚本
            
        Returns:
            是否更新成功
        """
        try:
            log.info(f"更新手势 {old_key} -> {new_key}: {name}, 方向: {directions}")
            
            # 确保手势库使用新格式
            if 'gestures' not in self.gestures:
                log.warning("手势库不是新格式，无法更新")
                return False
                
            # 检查原手势键名是否存在
            if old_key not in self.gestures['gestures']:
                log.warning(f"手势键名 {old_key} 不存在，无法更新")
                return False
                
            # 检查新键名是否已存在（且不是原键名）
            if new_key != old_key and new_key in self.gestures['gestures']:
                log.warning(f"新手势键名 {new_key} 已存在，无法更新")
                return False
                
            # 预解码action
            decoded_action = None
            try:
                decoded_action = base64.b64decode(action).decode('utf-8')
                log.debug(f"预解码更新的手势动作成功: {decoded_action[:50]}..." if len(decoded_action) > 50 else decoded_action)
            except Exception as e:
                log.warning(f"预解码更新的手势动作失败: {str(e)}")
                
            # 预处理方向
            if isinstance(directions, list):
                directions_str = ','.join(directions)
            else:
                directions_str = directions
                
            # 创建新的手势数据
            gesture_data = {
                'name': name,
                'directions': directions_str,
                'action': action,
                'decoded_action': decoded_action
            }
            
            # 处理键名变更
            if new_key != old_key:
                # 删除原手势
                del self.gestures['gestures'][old_key]
                # 添加新手势
                self.gestures['gestures'][new_key] = gesture_data
            else:
                # 更新手势
                self.gestures['gestures'][old_key] = gesture_data
            
            # 保存手势库
            result = self.save_gestures()
            
            # 发出手势变更信号
            self.gesturesChanged.emit(copy.deepcopy(self.gestures))
            
            return result
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

    def _init_default_gestures(self):
        """初始化默认手势数据"""
        # 默认手势库，包含一些基本的手势
        self.gestures = {
            'version': __version__,
            'gestures': {}
        }
        log.info("已初始化空手势库")

    def export_demo_gestures(self):
        """导出演示用的手势库
        
        Returns:
            True/False: 是否成功导出
        """
        # 创建演示手势
        demo_gestures = {
            'version': __version__,
            'gestures': {
                'up': {
                    "name": "向上",
                    "directions": "up",
                    "action": "maximize_current_window"
                },
                'down': {
                    "name": "向下",
                    "directions": "down",
                    "action": "minimize_current_window"
                },
                'left': {
                    "name": "向左",
                    "directions": "left",
                    "action": "prev_window"
                },
                'right': {
                    "name": "向右",
                    "directions": "right",
                    "action": "next_window"
                },
                'circ': {
                    "name": "画圈",
                    "directions": "up,right,down,left",
                    "action": "restore_all"
                }
            }
        }

        # 将手势库转换为字符串
        demo_gestures_str = json.dumps(demo_gestures, ensure_ascii=False, indent=2)

        # 将字符串保存到文件
        demo_gestures_path = os.path.join(os.path.dirname(self.config_file), "demo_gestures.json")
        with open(demo_gestures_path, 'w', encoding='utf-8') as f:
            f.write(demo_gestures_str)

        log.info(f"已成功导出演示手势库到 {demo_gestures_path}")
        return True

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