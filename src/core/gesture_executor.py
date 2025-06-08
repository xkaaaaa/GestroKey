import os
import re
import sys
import threading
import time
import traceback

from pynput.keyboard import Controller, Key, KeyCode

try:
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library


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
        if GestureExecutor._instance is not None:
            raise Exception("GestureExecutor已经初始化，请使用get_instance()获取实例")

        # 初始化日志记录器
        self.logger = get_logger("GestureExecutor")

        # 初始化键盘控制器
        try:
            self.keyboard = Controller()
            self.logger.info("键盘控制器初始化成功")
        except ImportError as e:
            self.keyboard = None
            self.logger.error(f"键盘控制器初始化失败: {e}")

        # 初始化特殊键映射字典
        self.special_keys = {
            # 修饰键 - 根据不同操作系统调整
            "ctrl": Key.ctrl,
            "control": Key.ctrl,
            "alt": Key.alt,
            "shift": Key.shift,
            "win": Key.cmd,
            "cmd": Key.cmd,
            "command": Key.cmd,
            "meta": Key.cmd,
            "super": Key.cmd,  # Linux中的Super键
            # macOS符号
            "⌃": Key.ctrl,  # Control符号
            "⌥": Key.alt,  # Option符号
            "⇧": Key.shift,  # Shift符号
            "⌘": Key.cmd,  # Command符号
            # 功能键
            "tab": Key.tab,
            "esc": Key.esc,
            "escape": Key.esc,
            "enter": Key.enter,
            "return": Key.enter,
            "backspace": Key.backspace,
            "delete": Key.delete,
            "del": Key.delete,
            "space": Key.space,
            # 方向键
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "↑": Key.up,
            "↓": Key.down,
            "←": Key.left,
            "→": Key.right,
            # 分页键
            "page_up": Key.page_up,
            "pageup": Key.page_up,
            "pgup": Key.page_up,
            "pg_up": Key.page_up,
            "page_down": Key.page_down,
            "pagedown": Key.page_down,
            "pgdn": Key.page_down,
            "pg_dn": Key.page_down,
            # 位置键
            "home": Key.home,
            "end": Key.end,
            "insert": Key.insert,
            "ins": Key.insert,
            # 锁定键
            "caps_lock": Key.caps_lock,
            "capslock": Key.caps_lock,
            "caps": Key.caps_lock,
            "num_lock": Key.num_lock,
            "numlock": Key.num_lock,
            "numlk": Key.num_lock,
            "num_lk": Key.num_lock,
            "scroll_lock": Key.scroll_lock,
            "scrolllock": Key.scroll_lock,
            "scrlk": Key.scroll_lock,
            "scr_lk": Key.scroll_lock,
            # 特殊功能键
            "print": Key.print_screen,  # PrintScreen键
            "print_screen": Key.print_screen,
            "printscreen": Key.print_screen,
            "prt_sc": Key.print_screen,
            "prt sc": Key.print_screen,
            "prtsc": Key.print_screen,
            "psc": Key.print_screen,
            "pause": Key.pause,
            "break": Key.pause,
            "menu": Key.menu,  # 菜单键
            # F1-F12 功能键
            "f1": Key.f1,
            "f2": Key.f2,
            "f3": Key.f3,
            "f4": Key.f4,
            "f5": Key.f5,
            "f6": Key.f6,
            "f7": Key.f7,
            "f8": Key.f8,
            "f9": Key.f9,
            "f10": Key.f10,
            "f11": Key.f11,
            "f12": Key.f12,
        }
        self.logger.debug("特殊键映射字典初始化完成")

        # 加载手势库
        try:
            self.gesture_library = get_gesture_library()
            self.logger.info("手势库加载成功")

            # 获取所有手势 - 使用已保存的手势库
            gestures = self.gesture_library.get_all_gestures(use_saved=True)
            self.logger.info(f"成功加载已保存的手势库，包含 {len(gestures)} 个手势")

            # 打印所有已加载的手势
            for name, gesture in gestures.items():
                self.logger.debug(
                    f"已加载手势: {name}, 方向: {gesture.get('direction', '未知')}, 动作: {gesture.get('action', {}).get('value', '未知')}"
                )

        except ImportError as e:
            self.gesture_library = None
            self.logger.error(f"手势库加载失败: {e}")

        # 设置为单例实例
        GestureExecutor._instance = self

        self.logger.info("手势执行器初始化完成")

    def execute_gesture(self, direction):
        """根据方向序列执行对应的手势动作（向后兼容）"""
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

    def execute_gesture_by_path(self, drawn_path):
        """根据绘制路径执行对应的手势动作
        
        Args:
            drawn_path: 绘制的路径 {'points': [...], 'connections': [...]}
            
        Returns:
            bool: 是否成功执行手势
        """
        if not drawn_path or not drawn_path.get('points'):
            self.logger.debug("绘制路径为空，不执行任何动作")
            return False

        self.logger.info(f"准备根据路径执行手势，路径点数: {len(drawn_path.get('points', []))}")

        # 检查手势库是否正确加载
        if not self.gesture_library:
            self.logger.error("手势库未正确加载，无法执行手势")
            return False

        # 检查键盘控制器是否正确加载
        if not self.keyboard:
            self.logger.error("键盘控制器未正确加载，无法执行手势")
            return False

        # 从设置中获取相似度阈值
        try:
            from ui.settings.settings import get_settings
            settings = get_settings()
            similarity_threshold = settings.get("gesture.similarity_threshold", 0.70)
        except Exception as e:
            self.logger.warning(f"无法获取相似度阈值设置，使用默认值0.70: {e}")
            similarity_threshold = 0.70

        # 查找匹配的手势
        name, gesture, similarity = self.gesture_library.get_gesture_by_path(drawn_path, similarity_threshold)

        if not gesture:
            self.logger.info(f"未找到匹配的手势，最高相似度: {similarity:.3f}，阈值: {similarity_threshold}")
            return False

        self.logger.info(f"识别到手势: {name}，相似度: {similarity:.3f}")

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
            # 处理macOS上可能的空格分隔符格式（如 "⌘ C"）
            if " " in shortcut_str and "+" not in shortcut_str:
                keys = shortcut_str.lower().split()
                self.logger.debug(f"检测到macOS格式快捷键，解析为: {keys}")
            else:
                # 处理标准的加号分隔格式（如 "Ctrl+C"）
                keys = shortcut_str.lower().split("+")
                self.logger.debug(f"解析标准格式快捷键: {keys}")

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
                elif re.match(r"^f\d+$", key):  # F1-F12 函数键
                    if key in self.special_keys:
                        regular_keys.append(self.special_keys[key])
                        self.logger.debug(f"添加函数键: {key}")
                else:
                    self.logger.warning(f"未知的键值: {key}")
                    return False

            self.logger.debug(
                f"修饰键: {[str(k) for k in modifier_keys]}, 普通键: {regular_keys}"
            )

            # 创建新线程执行快捷键，避免阻塞主线程
            thread = threading.Thread(
                target=self._press_keys, args=(modifier_keys, regular_keys)
            )
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

            # 处理普通键，将字母转为小写
            processed_keys = []
            for key in regular_keys:
                if isinstance(key, str) and len(key) == 1 and key.isalpha():
                    processed_keys.append(key.lower())  # 字母统一转小写
                    self.logger.debug(f"将字母键 {key} 转换为小写 {key.lower()}")
                else:
                    processed_keys.append(key)

            # 按下所有修饰键
            for key in modifier_keys:
                self.keyboard.press(key)
                self.logger.debug(f"按下修饰键: {key}")

            # 按下所有普通键
            for key in processed_keys:
                # 如果是特殊键的实例
                if isinstance(key, Key) or isinstance(key, KeyCode):
                    self.keyboard.press(key)
                else:
                    self.keyboard.press(key)
                self.logger.debug(f"按下普通键: {key}")

            # 短暂延迟确保按键被识别
            time.sleep(0.1)

            # 释放所有按键（先普通键，后修饰键）
            for key in reversed(processed_keys):
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

    def release_all_keys(self):
        """释放所有可能按下的键，用于程序退出前的清理操作"""
        if not self.keyboard:
            self.logger.error("键盘控制器未初始化，无法释放按键")
            return

        self.logger.info("开始释放所有可能按下的键...")

        try:
            # 释放所有常用修饰键
            for key in [Key.ctrl, Key.shift, Key.alt, Key.cmd]:
                self.keyboard.release(key)
                self.logger.debug(f"释放修饰键: {key}")

            # 释放所有功能键
            for key in [
                Key.f1,
                Key.f2,
                Key.f3,
                Key.f4,
                Key.f5,
                Key.f6,
                Key.f7,
                Key.f8,
                Key.f9,
                Key.f10,
                Key.f11,
                Key.f12,
            ]:
                self.keyboard.release(key)
                self.logger.debug(f"释放功能键: {key}")

            # 释放常用特殊键
            for key in [
                Key.space,
                Key.enter,
                Key.tab,
                Key.esc,
                Key.backspace,
                Key.delete,
                Key.insert,
                Key.home,
                Key.end,
                Key.page_up,
                Key.page_down,
                Key.up,
                Key.down,
                Key.left,
                Key.right,
            ]:
                self.keyboard.release(key)
                self.logger.debug(f"释放特殊键: {key}")

            # 释放所有字母键
            for char in "abcdefghijklmnopqrstuvwxyz":
                self.keyboard.release(char)
                self.logger.debug(f"释放字母键: {char}")

            # 释放所有数字键
            for num in "0123456789":
                self.keyboard.release(num)
                self.logger.debug(f"释放数字键: {num}")

            self.logger.info("所有按键已释放")

        except Exception as e:
            self.logger.error(f"释放按键失败: {e}")
            self.logger.error(traceback.format_exc())

    def refresh_gestures(self):
        """刷新手势库，确保使用最新的已保存手势库"""
        try:
            if self.gesture_library:
                gestures = self.gesture_library.get_all_gestures(use_saved=True)
                self.logger.info(f"已刷新手势库，共有 {len(gestures)} 个保存的手势")
            else:
                self.logger.warning("手势库实例不存在，无法刷新")
        except Exception as e:
            self.logger.error(f"刷新手势库失败: {e}")
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
