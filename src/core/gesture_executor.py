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
            gesture_count = self.gesture_library.get_gesture_count(use_saved=True)
        except ImportError as e:
            self.gesture_library = None
            self.logger.error(f"手势库加载失败: {e}")

        GestureExecutor._instance = self

    def execute_gesture_by_path(self, drawn_path):
        """根据绘制路径执行对应的手势动作
        
        使用新的手势库核心逻辑：
        1. 绘制结束后，将当前手势和手势库的触发路径逐一对比
        2. 选出相似度大于阈值中相似度最高的一个手势
        3. 找到它的执行操作部分
        4. 将执行操作部分的内容交给操作执行模块执行
        
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

        # 使用手势库的新核心逻辑查找匹配的手势
        gesture_name, execute_action, similarity = self.gesture_library.get_gesture_by_path(drawn_path, similarity_threshold)

        if not execute_action:
            self.logger.info(f"未找到匹配的手势，最高相似度: {similarity:.3f}，阈值: {similarity_threshold}")
            return False

        self.logger.info(f"识别到手势: {gesture_name}，相似度: {similarity:.3f}")

        # 获取动作类型和值
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
                gesture_count = self.gesture_library.get_gesture_count(use_saved=True)
                self.logger.info(f"已刷新手势库，共有 {gesture_count} 个保存的手势")
            else:
                self.logger.warning("手势库实例不存在，无法刷新")
        except Exception as e:
            self.logger.error(f"刷新手势库失败: {e}")
            self.logger.error(traceback.format_exc())
            
    def find_similar_paths(self, test_path):
        """查找与测试路径相似的所有触发路径
        
        Args:
            test_path: 要测试的路径 {'points': [...], 'total_distance': ..., 'direction': ...}
            
        Returns:
            list: 相似路径列表，格式为 [(path_key, similarity, path_data), ...]
        """
        if not self.gesture_library:
            self.logger.error("手势库未正确加载，无法测试相似度")
            return []
            
        if not test_path or not test_path.get('points'):
            self.logger.warning("测试路径为空")
            return []
            
        try:
            # 使用手势库的路径匹配功能获取所有相似路径
            results = []
            trigger_paths = self.gesture_library.trigger_paths
            
            # 逐个对比所有触发路径
            for path_key, path_data in trigger_paths.items():
                stored_path = path_data.get('path')
                if not stored_path:
                    continue
                    
                # 归一化路径用于比较
                normalized_test = self.gesture_library.path_analyzer.normalize_path_scale(test_path)
                normalized_stored = self.gesture_library.path_analyzer.normalize_path_scale(stored_path)
                
                # 计算相似度
                similarity = self.gesture_library.path_analyzer.calculate_similarity(normalized_test, normalized_stored)
                
                # 添加到结果中（不设阈值，显示所有结果）
                results.append((path_key, similarity, path_data))
            
            # 按相似度降序排序
            results.sort(key=lambda x: x[1], reverse=True)
            
            self.logger.info(f"找到 {len(results)} 个路径进行相似度比较")
            return results
            
        except Exception as e:
            self.logger.error(f"查找相似路径时出错: {e}")
            return []


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
    result = executor.execute_gesture_by_path({"points": [[0, 0], [1, 1]], "connections": [[0, 1]]})
    print(f"执行结果: {'成功' if result else '失败'}")

    # 等待一段时间以便测试手势效果
    import time

    time.sleep(1)

    # 测试不存在的手势
    print("测试执行不存在的手势...")
    result = executor.execute_gesture_by_path({"points": [[0, 0], [1, 1], [2, 2]], "connections": [[0, 1], [1, 2]]})
    print(f"执行结果: {'成功' if result else '失败'}")
