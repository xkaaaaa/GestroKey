import json
import os
import pathlib
import sys

try:
    from core.logger import get_logger
    from version import APP_NAME, AUTHOR
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger
    from version import APP_NAME, AUTHOR


class GestureLibrary:
    """手势库管理器，负责保存和加载用户手势库"""

    def __init__(self):
        self.logger = get_logger("GestureLibrary")
        self.DEFAULT_GESTURES = self._load_default_gestures()

        # 检查系统平台并调整默认手势快捷键格式
        import sys

        if sys.platform != "win32":
            self.logger.info(f"初始化默认手势库：检测到非Windows系统({sys.platform})，调整默认快捷键格式...")
            for name, gesture in self.DEFAULT_GESTURES.items():
                action = gesture.get("action", {})
                if action.get("type") == "shortcut":
                    action_value = action.get("value", "")
                    if action_value and "+" in action_value:
                        # 转换为当前平台的快捷键格式
                        new_value = self._convert_shortcut_for_current_platform(
                            action_value
                        )
                        if new_value != action_value:
                            self.logger.info(
                                f"转换默认快捷键格式: {name}: {action_value} -> {new_value}"
                            )
                            action["value"] = new_value

        self.gestures = self.DEFAULT_GESTURES.copy()
        self.saved_gestures = self.DEFAULT_GESTURES.copy()  # 初始化saved_gestures为默认手势库的副本
        self.gestures_file = self._get_gestures_file_path()
        self.load()

    def _load_default_gestures(self):
        """从JSON文件加载默认手势库"""
        default_gestures_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "default_gestures.json"
        )
        try:
            if os.path.exists(default_gestures_path):
                with open(default_gestures_path, "r", encoding="utf-8") as f:
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
        # 按现有ID排序手势，没有ID的放在最后
        gestures_with_ids = []
        gestures_without_ids = []
        
        for name, gesture in gestures.items():
            if "id" in gesture and isinstance(gesture["id"], int) and gesture["id"] > 0:
                gestures_with_ids.append((name, gesture))
            else:
                gestures_without_ids.append((name, gesture))
        
        # 按ID排序已有ID的手势
        gestures_with_ids.sort(key=lambda x: x[1]["id"])
        
        # 重新分配连续的ID
        next_id = 1
        for name, gesture in gestures_with_ids + gestures_without_ids:
            if gesture.get("id") != next_id:
                old_id = gesture.get("id", "无")
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
        if sys.platform.startswith("win"):
            # Windows系统使用用户文档目录
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(
                user_dir, f".{AUTHOR}", APP_NAME.lower(), "config"
            )
        elif sys.platform.startswith("darwin"):
            # macOS系统使用Library/Application Support目录
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(
                user_dir,
                "Library",
                "Application Support",
                f"{AUTHOR}",
                APP_NAME,
                "config",
            )
        else:
            # Linux和其他系统遵循XDG标准，使用~/.config/目录
            xdg_config_home = os.environ.get(
                "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
            )
            config_dir = os.path.join(xdg_config_home, f"{AUTHOR}", APP_NAME, "config")

        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)

        return os.path.join(config_dir, "gestures.json")

    def load(self):
        """从文件加载手势库"""
        try:
            if os.path.exists(self.gestures_file):
                with open(self.gestures_file, "r", encoding="utf-8") as f:
                    loaded_gestures = json.load(f)

                # 检查系统平台并调整加载的手势快捷键格式
                import sys

                if sys.platform != "win32":
                    self.logger.info(f"加载手势库：检测到非Windows系统({sys.platform})，检查快捷键格式...")
                    format_converted = False
                    for name, gesture in loaded_gestures.items():
                        action = gesture.get("action", {})
                        if action.get("type") == "shortcut":
                            action_value = action.get("value", "")
                            if action_value and "+" in action_value:
                                # 检查是否需要转换（排除已经是平台特定格式的情况）
                                is_windows_format = True
                                for part in action_value.split("+"):
                                    # 检测macOS符号
                                    if (
                                        part in ["⌃", "⌥", "⇧", "⌘"]
                                        or " " in action_value
                                    ):
                                        is_windows_format = False
                                        break
                                    # 检测Linux格式
                                    if part == "Super":
                                        is_windows_format = False
                                        break

                                if is_windows_format:
                                    # 转换为当前平台的快捷键格式
                                    new_value = (
                                        self._convert_shortcut_for_current_platform(
                                            action_value
                                        )
                                    )
                                    if new_value != action_value:
                                        self.logger.info(
                                            f"转换加载的快捷键格式: {name}: {action_value} -> {new_value}"
                                        )
                                        action["value"] = new_value
                                        format_converted = True

                    # 如果有转换，需要保存
                    if format_converted:
                        self.save()  # 自动保存转换后的格式

                # 更新手势库，确保所有默认手势都存在
                for name, gesture in loaded_gestures.items():
                    self.gestures[name] = gesture

                # 确保所有手势都有有效的ID
                self._ensure_valid_ids(self.gestures)

                self.logger.info(f"已从 {self.gestures_file} 加载手势库")
                # 保存当前加载的手势库到saved_gestures
                self.saved_gestures = self.gestures.copy()
            else:
                self.logger.info("未找到手势库文件，使用默认手势库")
                self.save()  # 保存默认手势库
        except Exception as e:
            self.logger.error(f"加载手势库失败: {e}")
            import traceback

            self.logger.error(traceback.format_exc())
            raise

    def save(self):
        """保存手势库到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.gestures_file), exist_ok=True)

            # 确保所有手势都有有效的ID
            self._ensure_valid_ids(self.gestures)

            with open(self.gestures_file, "w", encoding="utf-8") as f:
                json.dump(self.gestures, f, indent=4, ensure_ascii=False)
            self.logger.info(f"手势库已保存到 {self.gestures_file}")
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
        """添加新手势

        Args:
            name: 手势名称
            direction: 手势方向
            action_type: 动作类型
            action_value: 动作值
            gesture_id: 手势ID，如果不提供则自动生成
        """
        # 如果没有指定ID，生成新的
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
            "action": {"type": action_type, "value": action_value},
        }

        # 添加手势
        self.gestures[name] = new_gesture
        self.logger.info(
            f"添加手势: {name}, ID: {gesture_id}, 方向: {direction}, 动作: {action_type}:{action_value}"
        )
        return True

    def update_gesture_by_id(self, gesture_id, name, direction, action_type, action_value):
        """通过ID更新手势的所有属性

        Args:
            gesture_id: 手势ID
            name: 新的手势名称
            direction: 新的手势方向
            action_type: 新的动作类型
            action_value: 新的动作值

        Returns:
            bool: 操作是否成功
        """
        # 找到具有指定ID的手势
        old_name = None
        for gesture_name, gesture_data in self.gestures.items():
            if gesture_data.get("id") == gesture_id:
                old_name = gesture_name
                break
        
        if old_name is None:
            self.logger.warning(f"尝试更新不存在的手势ID: {gesture_id}")
            return False
        
        # 如果名称发生了变化，检查新名称是否已被其他手势使用
        if name != old_name:
            for other_name, other_data in self.gestures.items():
                if other_name == name and other_data.get("id") != gesture_id:
                    self.logger.warning(f"无法更新手势，新名称已被其他手势使用: {name}")
                    return False
        
        # 创建新的手势数据
        new_gesture = {
            "id": gesture_id,
            "direction": direction,
            "action": {"type": action_type, "value": action_value},
        }
        
        # 如果名称发生了变化，需要删除旧的键并添加新的键
        if name != old_name:
            del self.gestures[old_name]
        
        # 更新手势数据
        self.gestures[name] = new_gesture
        
        self.logger.info(
            f"通过ID更新手势: ID={gesture_id}, {old_name} -> {name}, 方向: {direction}, 动作: {action_type}:{action_value}"
        )
        return True

    def remove_gesture(self, name):
        """删除手势并重新排序剩余手势的ID以保持连续"""
        if name not in self.gestures:
            self.logger.warning(f"尝试删除不存在的手势: {name}")
            return False

        # 获取要删除的手势ID
        deleted_id = self.gestures[name].get("id")

        # 删除手势
        del self.gestures[name]

        # 重新排序所有手势的ID以保持连续
        self._ensure_valid_ids(self.gestures)

        self.logger.info(f"删除手势: {name}, ID: {deleted_id}，已重新排序剩余手势ID以保持连续")
        return True

    def _convert_shortcut_for_current_platform(self, shortcut_str):
        """根据当前操作系统转换快捷键格式

        Args:
            shortcut_str: Windows格式的快捷键字符串(如'Ctrl+C')

        Returns:
            str: 当前平台适用的快捷键格式
        """
        import sys

        # 如果是Windows，保持原样
        if sys.platform == "win32":
            return shortcut_str

        # 将快捷键分解为各个部分
        parts = shortcut_str.split("+")
        result_parts = []

        # macOS特殊映射
        if sys.platform == "darwin":
            # macOS使用特殊符号
            mac_mapping = {
                "Ctrl": "⌃",
                "Control": "⌃",
                "Alt": "⌥",
                "Shift": "⇧",
                "Win": "⌘",
                "Cmd": "⌘",
                "Command": "⌘",
                "Meta": "⌘",
            }

            for part in parts:
                if part in mac_mapping:
                    result_parts.append(mac_mapping[part])
                else:
                    result_parts.append(part)

            # macOS使用空格而不是加号连接
            return " ".join(result_parts)

        # Linux特殊映射
        else:
            # Linux平台映射
            linux_mapping = {
                "Win": "Super",
                "Cmd": "Super",
                "Command": "Super",
                "Meta": "Super",
            }

            for part in parts:
                if part in linux_mapping:
                    result_parts.append(linux_mapping[part])
                else:
                    result_parts.append(part)

            # Linux仍使用加号连接
            return "+".join(result_parts)

    def reset_to_default(self):
        """重置为默认手势库"""
        self.logger.info("重置为默认手势库")
        try:
            default_gestures = self._load_default_gestures()

            # 根据操作系统调整快捷键格式
            import sys

            if sys.platform != "win32":
                self.logger.info(f"检测到非Windows系统({sys.platform})，调整快捷键格式...")
                for name, gesture in default_gestures.items():
                    action = gesture.get("action", {})
                    if action.get("type") == "shortcut":
                        action_value = action.get("value", "")
                        if action_value and "+" in action_value:
                            # 转换为当前平台的快捷键格式
                            new_value = self._convert_shortcut_for_current_platform(
                                action_value
                            )
                            if new_value != action_value:
                                self.logger.info(
                                    f"转换快捷键格式: {name}: {action_value} -> {new_value}"
                                )
                                action["value"] = new_value

            if self.gestures != default_gestures:
                self.gestures = default_gestures.copy()

            # 保存并更新saved_gestures
            success = self.save()
            if success:
                self.saved_gestures = self.gestures.copy()

            return success
        except Exception as e:
            self.logger.error(f"重置为默认手势库失败: {e}")
            import traceback

            self.logger.error(traceback.format_exc())
            return False



    def has_changes(self):
        """检查是否有未保存的更改"""
        # 如果没有已保存的手势库记录，则认为有未保存的更改
        if not self.saved_gestures:
            result = True if self.gestures else False
            self.logger.debug(f"手势库检查变更: 没有已保存手势记录, 结果={result}")
            return result

        # 检查手势数量是否相同
        if len(self.gestures) != len(self.saved_gestures):
            self.logger.debug(f"手势库检查变更: 数量不同 - 当前={len(self.gestures)}, 已保存={len(self.saved_gestures)}")
            return True

        # 逐一比较手势
        for name, gesture in self.gestures.items():
            if name not in self.saved_gestures:
                self.logger.debug(f"手势库检查变更: 新手势 - {name}")
                return True

            if self.saved_gestures[name] != gesture:
                self.logger.debug(f"手势库检查变更: 手势内容不同 - {name}")
                self.logger.debug(f"  当前: {gesture}")
                self.logger.debug(f"  已保存: {self.saved_gestures[name]}")
                return True

        # 检查是否有已保存的手势在当前手势库中不存在
        for name in self.saved_gestures:
            if name not in self.gestures:
                self.logger.debug(f"手势库检查变更: 已保存的手势在当前库中不存在 - {name}")
                return True

        self.logger.debug("手势库检查变更: 没有发现差异")
        return False


# 创建全局手势库实例
gesture_library = GestureLibrary()


def get_gesture_library():
    """获取手势库管理器实例"""
    return gesture_library
