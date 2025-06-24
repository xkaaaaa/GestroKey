import os
import re
import sys
import threading
import time
import traceback

from pynput.keyboard import Controller, Key, KeyCode

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library


class GestureExecutor:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GestureExecutor()
        return cls._instance

    def __init__(self):
        if GestureExecutor._instance is not None:
            raise Exception("GestureExecutor已经初始化，请使用get_instance()获取实例")

        self.logger = get_logger("GestureExecutor")

        try:
            self.keyboard = Controller()
        except ImportError as e:
            self.keyboard = None
            self.logger.error(f"键盘控制器初始化失败: {e}")

        self.special_keys = {
            "ctrl": Key.ctrl,
            "control": Key.ctrl,
            "alt": Key.alt,
            "shift": Key.shift,
            "win": Key.cmd,
            "cmd": Key.cmd,
            "command": Key.cmd,
            "meta": Key.cmd,
            "super": Key.cmd,
            "⌃": Key.ctrl,
            "⌥": Key.alt,
            "⇧": Key.shift,
            "⌘": Key.cmd,
            "tab": Key.tab,
            "esc": Key.esc,
            "escape": Key.esc,
            "enter": Key.enter,
            "return": Key.enter,
            "backspace": Key.backspace,
            "delete": Key.delete,
            "del": Key.delete,
            "space": Key.space,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "↑": Key.up,
            "↓": Key.down,
            "←": Key.left,
            "→": Key.right,
            "page_up": Key.page_up,
            "pageup": Key.page_up,
            "pgup": Key.page_up,
            "pg_up": Key.page_up,
            "page_down": Key.page_down,
            "pagedown": Key.page_down,
            "pgdn": Key.page_down,
            "pg_dn": Key.page_down,
            "home": Key.home,
            "end": Key.end,
            "insert": Key.insert,
            "ins": Key.insert,
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
            "print": Key.print_screen,
            "print_screen": Key.print_screen,
            "printscreen": Key.print_screen,
            "prt_sc": Key.print_screen,
            "prt sc": Key.print_screen,
            "prtsc": Key.print_screen,
            "psc": Key.print_screen,
            "pause": Key.pause,
            "break": Key.pause,
            "menu": Key.menu,
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

        try:
            self.gesture_library = get_gesture_library()
        except ImportError as e:
            self.gesture_library = None
            self.logger.error(f"手势库加载失败: {e}")

        GestureExecutor._instance = self

    def execute_gesture_by_path(self, drawn_path):
        """根据绘制路径执行对应的手势动作"""
        if not drawn_path or not drawn_path.get('points'):
            self.logger.debug("绘制路径为空，不执行任何动作")
            return False

        self.logger.info(f"准备根据路径执行手势，路径点数: {len(drawn_path.get('points', []))}")

        if not self.gesture_library:
            self.logger.error("手势库未正确加载，无法执行手势")
            return False

        if not self.keyboard:
            self.logger.error("键盘控制器未正确加载，无法执行手势")
            return False
        try:
            from ui.settings.settings import get_settings
            settings = get_settings()
            similarity_threshold = settings.get("gesture.similarity_threshold", 0.70)
        except Exception as e:
            self.logger.warning(f"无法获取相似度阈值设置，使用默认值0.70: {e}")
            similarity_threshold = 0.70

        gesture_name, execute_action, similarity = self.gesture_library.get_gesture_by_path(drawn_path, similarity_threshold)

        if not execute_action:
            self.logger.info(f"未找到匹配的手势，最高相似度: {similarity:.3f}，阈值: {similarity_threshold}")
            return False

        self.logger.info(f"识别到手势: {gesture_name}，相似度: {similarity:.3f}")

        action_type = execute_action.get("type")
        action_value = execute_action.get("value")

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
            if " " in shortcut_str and "+" not in shortcut_str:
                keys = shortcut_str.lower().split()
                self.logger.debug(f"检测到macOS格式快捷键，解析为: {keys}")
            else:
                keys = shortcut_str.lower().split("+")
                self.logger.debug(f"解析标准格式快捷键: {keys}")

            modifier_keys = []
            regular_keys = []

            for key in keys:
                key = key.strip()
                if key in self.special_keys:
                    modifier_keys.append(self.special_keys[key])
                    self.logger.debug(f"添加修饰键: {key}")
                elif len(key) == 1:
                    regular_keys.append(key)
                    self.logger.debug(f"添加普通键: {key}")
                elif re.match(r"^f\d+$", key):
                    if key in self.special_keys:
                        regular_keys.append(self.special_keys[key])
                        self.logger.debug(f"添加函数键: {key}")
                else:
                    self.logger.warning(f"未知的键值: {key}")
                    return False

            self.logger.debug(
                f"修饰键: {[str(k) for k in modifier_keys]}, 普通键: {regular_keys}"
            )

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

            processed_keys = []
            for key in regular_keys:
                if isinstance(key, str) and len(key) == 1 and key.isalpha():
                    processed_keys.append(key.lower())
                    self.logger.debug(f"将字母键 {key} 转换为小写 {key.lower()}")
                else:
                    processed_keys.append(key)

            for key in modifier_keys:
                self.keyboard.press(key)
                self.logger.debug(f"按下修饰键: {key}")

            for key in processed_keys:
                if isinstance(key, Key) or isinstance(key, KeyCode):
                    self.keyboard.press(key)
                else:
                    self.keyboard.press(key)
                self.logger.debug(f"按下普通键: {key}")

            time.sleep(0.1)

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
            for key in [Key.ctrl, Key.shift, Key.alt, Key.cmd]:
                self.keyboard.release(key)
                self.logger.debug(f"释放修饰键: {key}")

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

            for char in "abcdefghijklmnopqrstuvwxyz":
                self.keyboard.release(char)
                self.logger.debug(f"释放字母键: {char}")

            for num in "0123456789":
                self.keyboard.release(num)
                self.logger.debug(f"释放数字键: {num}")

            self.logger.info("所有按键已释放")

        except Exception as e:
            self.logger.error(f"释放按键失败: {e}")
            self.logger.error(traceback.format_exc())


def get_gesture_executor():
    """获取手势执行器的全局实例"""
    return GestureExecutor.get_instance()