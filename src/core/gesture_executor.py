import threading
import time
from pynput.keyboard import Controller, Key, KeyCode
import re
import traceback

try:
    from logger import get_logger
    from ui.gestures.gestures import get_gesture_library  # 从ui.gestures导入手势库
except ImportError:
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library  # 从ui.gestures导入手势库

class GestureExecutor:
    """
    手势执行器，根据识别的手势方向执行对应的动作
    
    目前支持的动作类型：
    - shortcut: 执行快捷键，如 "ctrl+c"、"alt+tab" 等
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """获取手势执行器的全局单例实例"""
        if cls._instance is None:
            cls._instance = GestureExecutor()
        return cls._instance
    
    def __init__(self):
        """初始化手势执行器"""
        self.logger = get_logger("GestureExecutor")
        
        try:
            self.keyboard = Controller()
            self.logger.info("成功初始化键盘控制器")
        except Exception as e:
            self.logger.error(f"初始化键盘控制器失败: {e}")
            self.logger.error(traceback.format_exc())
            # 创建一个空的键盘控制器占位，后续会检查
            self.keyboard = None
            
        try:
            self.gesture_library = get_gesture_library()
            # 获取所有手势
            gestures = self.gesture_library.get_all_gestures()
            self.logger.info(f"成功加载手势库，包含 {len(gestures)} 个手势")
            
            # 打印所有已加载的手势
            for name, gesture in gestures.items():
                self.logger.debug(f"已加载手势: {name}, 方向: {gesture.get('direction', '未知')}, 动作: {gesture.get('action', {}).get('value', '未知')}")
                
        except Exception as e:
            self.logger.error(f"加载手势库失败: {e}")
            self.logger.error(traceback.format_exc())
            # 创建空占位
            self.gesture_library = None
        
        # 特殊键映射
        self.special_keys = {
            'ctrl': Key.ctrl,
            'alt': Key.alt,
            'shift': Key.shift,
            'win': Key.cmd,  # Windows键
            'cmd': Key.cmd,  # macOS命令键
            'tab': Key.tab,
            'esc': Key.esc,
            'space': Key.space,
            'enter': Key.enter,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'home': Key.home,
            'end': Key.end,
            'pageup': Key.page_up,
            'pagedown': Key.page_down,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'f1': Key.f1,
            'f2': Key.f2,
            'f3': Key.f3,
            'f4': Key.f4,
            'f5': Key.f5,
            'f6': Key.f6,
            'f7': Key.f7,
            'f8': Key.f8,
            'f9': Key.f9,
            'f10': Key.f10,
            'f11': Key.f11,
            'f12': Key.f12
        }
        
        self.logger.info("手势执行器初始化完成")
    
    def execute_gesture(self, direction):
        """根据方向序列执行对应的手势动作"""
        if not direction or direction in ["无方向", "无明显方向"]:
            self.logger.debug("无法识别的方向序列，不执行任何动作")
            return False
        
        self.logger.info(f"准备执行方向为 {direction} 的手势")
        
        # 检查手势库是否正确加载
        if not self.gesture_library:
            self.logger.error("手势库未正确加载，无法执行手势")
            return False
            
        # 检查键盘控制器是否正确加载
        if not self.keyboard:
            self.logger.error("键盘控制器未正确加载，无法执行手势")
            return False
            
        # 查找匹配的手势
        name, gesture = self.gesture_library.get_gesture_by_direction(direction)
        
        if not gesture:
            self.logger.info(f"未找到匹配的手势: {direction}")
            return False
        
        self.logger.info(f"识别到手势: {name}，方向: {direction}")
        
        # 获取动作类型和值
        action = gesture.get("action", {})
        action_type = action.get("type")
        action_value = action.get("value")
        
        self.logger.debug(f"手势动作类型: {action_type}, 值: {action_value}")
        
        if action_type == "shortcut":
            return self._execute_shortcut(action_value)
        else:
            self.logger.warning(f"不支持的动作类型: {action_type}")
            return False
    
    def _execute_shortcut(self, shortcut_str):
        """执行快捷键"""
        self.logger.info(f"执行快捷键: {shortcut_str}")
        
        if not shortcut_str:
            self.logger.warning("快捷键字符串为空")
            return False
            
        if not self.keyboard:
            self.logger.error("键盘控制器未初始化，无法执行快捷键")
            return False
        
        try:
            # 分割快捷键字符串
            keys = shortcut_str.lower().split('+')
            self.logger.debug(f"解析快捷键: {keys}")
            
            # 提取修饰键和普通键
            modifier_keys = []
            regular_keys = []
            
            for key in keys:
                key = key.strip()
                if key in self.special_keys:
                    modifier_keys.append(self.special_keys[key])
                    self.logger.debug(f"添加修饰键: {key}")
                elif len(key) == 1:  # 单个字符
                    regular_keys.append(key)
                    self.logger.debug(f"添加普通键: {key}")
                elif re.match(r'^f\d+$', key):  # F1-F12 函数键
                    if key in self.special_keys:
                        regular_keys.append(self.special_keys[key])
                        self.logger.debug(f"添加函数键: {key}")
                else:
                    self.logger.warning(f"未知的键值: {key}")
                    return False
            
            self.logger.debug(f"修饰键: {[str(k) for k in modifier_keys]}, 普通键: {regular_keys}")
            
            # 创建新线程执行快捷键，避免阻塞主线程
            thread = threading.Thread(target=self._press_keys, 
                                      args=(modifier_keys, regular_keys))
            thread.daemon = True
            thread.start()
            
            self.logger.info(f"快捷键 {shortcut_str} 执行线程已启动")
            return True
        
        except Exception as e:
            self.logger.error(f"执行快捷键失败: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    def _press_keys(self, modifier_keys, regular_keys):
        """按下并释放快捷键"""
        try:
            self.logger.debug("开始按键操作...")
            
            # 按下所有修饰键
            for key in modifier_keys:
                self.keyboard.press(key)
                self.logger.debug(f"按下修饰键: {key}")
            
            # 按下所有普通键
            for key in regular_keys:
                # 如果是特殊键的实例
                if isinstance(key, Key) or isinstance(key, KeyCode):
                    self.keyboard.press(key)
                else:
                    self.keyboard.press(key)
                self.logger.debug(f"按下普通键: {key}")
            
            # 短暂延迟确保按键被识别
            time.sleep(0.1)
            
            # 释放所有按键（先普通键，后修饰键）
            for key in reversed(regular_keys):
                if isinstance(key, Key) or isinstance(key, KeyCode):
                    self.keyboard.release(key)
                else:
                    self.keyboard.release(key)
                self.logger.debug(f"释放普通键: {key}")
            
            for key in reversed(modifier_keys):
                self.keyboard.release(key)
                self.logger.debug(f"释放修饰键: {key}")
                
            self.logger.info("快捷键执行完成")
            
        except Exception as e:
            self.logger.error(f"按键操作失败: {e}")
            self.logger.error(traceback.format_exc())


# 提供全局访问函数
def get_gesture_executor():
    """获取手势执行器的全局实例"""
    return GestureExecutor.get_instance()


# 测试代码
if __name__ == "__main__":
    # 获取手势执行器实例
    executor = get_gesture_executor()
    
    # 模拟执行手势动作
    print("测试执行'复制'手势...")
    result = executor.execute_gesture("右-下")
    print(f"执行结果: {'成功' if result else '失败'}")
    
    # 等待一段时间以便测试手势效果
    import time
    time.sleep(1)
    
    # 测试不存在的手势
    print("测试执行不存在的手势...")
    result = executor.execute_gesture("上-上-上")
    print(f"执行结果: {'成功' if result else '失败'}") 