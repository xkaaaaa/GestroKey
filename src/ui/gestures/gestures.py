import json
import os
import pathlib
import sys
import copy

try:
    from core.logger import get_logger
    from core.path_analyzer import PathAnalyzer
    from version import APP_NAME, AUTHOR
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger
    from core.path_analyzer import PathAnalyzer
    from version import APP_NAME, AUTHOR


class GestureLibrary:
    """手势库管理器，负责保存和加载用户手势库
    
    新的手势库结构分为三部分：
    1. trigger_paths: 触发路径（绘制的轨迹）
    2. execute_actions: 执行操作（要执行的动作）
    3. gesture_mappings: 手势映射（将路径和操作关联起来）
    """

    def __init__(self):
        self.logger = get_logger("GestureLibrary")
        
        self.path_analyzer = PathAnalyzer()
        self.gestures_file = self._get_gestures_file_path()
        
        default_gestures = self._load_default_gestures()
        
        if sys.platform != "win32":
            self.logger.info(f"检测到非Windows系统({sys.platform})，调整快捷键格式...")
            self._convert_actions_for_current_platform()

        self.trigger_paths = default_gestures.get("trigger_paths", {}).copy()
        self.execute_actions = default_gestures.get("execute_actions", {}).copy()
        self.gesture_mappings = default_gestures.get("gesture_mappings", {}).copy()

        self._update_saved_state()
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

                self.logger.info(f"已从 {default_gestures_path} 加载默认手势库")
                return gestures
            else:
                self.logger.error(f"默认手势库文件 {default_gestures_path} 不存在")
                raise FileNotFoundError(f"默认手势库文件不存在: {default_gestures_path}")
        except Exception as e:
            self.logger.error(f"加载默认手势库失败: {e}")
            raise

    def _convert_actions_for_current_platform(self):
        """转换操作的快捷键格式为当前平台格式"""
        actions = self.execute_actions
        for action_key, action_data in actions.items():
            if action_data.get("type") == "shortcut":
                action_value = action_data.get("value", "")
                if action_value and "+" in action_value:
                    new_value = self._convert_shortcut_for_current_platform(action_value)
                    if new_value != action_value:
                        self.logger.info(
                            f"转换默认快捷键格式: {action_data.get('name', action_key)}: {action_value} -> {new_value}"
                        )
                        action_data["value"] = new_value

    def _convert_shortcut_for_current_platform(self, shortcut):
        """将快捷键转换为当前平台的格式"""
        import sys
        if sys.platform == "darwin":
            # macOS系统转换
            shortcut = shortcut.replace("Ctrl+", "Cmd+")
            shortcut = shortcut.replace("ctrl+", "cmd+")
        elif sys.platform.startswith("linux"):
            # Linux系统转换（通常与Windows相同）
            pass
        return shortcut

    def _get_gestures_file_path(self):
        """获取手势库文件路径"""
        if sys.platform.startswith("win"):
            user_dir = os.path.expanduser("~")
            config_dir = os.path.join(
                user_dir, f".{AUTHOR}", APP_NAME.lower(), "config"
            )
        elif sys.platform.startswith("darwin"):
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
            xdg_config_home = os.environ.get(
                "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
            )
            config_dir = os.path.join(xdg_config_home, f"{AUTHOR}", APP_NAME, "config")

        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "gestures.json")

    def load(self):
        """从文件加载手势库"""
        try:
            if os.path.exists(self.gestures_file):
                with open(self.gestures_file, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)

                import sys
                if sys.platform != "win32":
                    self.logger.info(f"加载手势库：检测到非Windows系统({sys.platform})，检查快捷键格式...")
                    self._convert_loaded_actions_for_current_platform(loaded_data)

                self.trigger_paths = loaded_data.get("trigger_paths", {})
                self.execute_actions = loaded_data.get("execute_actions", {})
                self.gesture_mappings = loaded_data.get("gesture_mappings", {})

                self.logger.info(f"已从 {self.gestures_file} 加载手势库")
                self._update_saved_state()
            else:
                self.logger.info("未找到手势库文件，使用默认手势库")
                self.save()
        except Exception as e:
            self.logger.error(f"加载手势库失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise

    def _convert_loaded_actions_for_current_platform(self, loaded_data):
        """转换加载的操作快捷键格式为当前平台格式"""
        actions = loaded_data.get("execute_actions", {})
        format_converted = False
        for action_key, action_data in actions.items():
            if action_data.get("type") == "shortcut":
                action_value = action_data.get("value", "")
                if action_value and "+" in action_value:
                    new_value = self._convert_shortcut_for_current_platform(action_value)
                    if new_value != action_value:
                        self.logger.info(
                            f"转换快捷键格式: {action_data.get('name', action_key)}: {action_value} -> {new_value}"
                        )
                        action_data["value"] = new_value
                        format_converted = True
        
        if format_converted:
            self.logger.info("快捷键格式已转换，将自动保存")

    def _update_saved_state(self):
        """更新已保存状态"""
        self.saved_trigger_paths = copy.deepcopy(self.trigger_paths)
        self.saved_execute_actions = copy.deepcopy(self.execute_actions)
        self.saved_gesture_mappings = copy.deepcopy(self.gesture_mappings)

    def save(self):
        """保存手势库到文件"""
        try:
            os.makedirs(os.path.dirname(self.gestures_file), exist_ok=True)

            data = {
                "trigger_paths": self.trigger_paths,
                "execute_actions": self.execute_actions,
                "gesture_mappings": self.gesture_mappings
            }

            with open(self.gestures_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"手势库已保存到 {self.gestures_file}")
            self._update_saved_state()
            return True
        except Exception as e:
            self.logger.error(f"保存手势库失败: {e}")
            return False

    def has_changes(self):
        """检查是否有未保存的更改"""
        return (
            self.trigger_paths != self.saved_trigger_paths or
            self.execute_actions != self.saved_execute_actions or
            self.gesture_mappings != self.saved_gesture_mappings
        )
    
    def get_gesture_by_path(self, drawn_path, similarity_threshold=0.70):
        """根据绘制的路径获取匹配的手势
        
        核心逻辑：
        1. 将绘制路径与所有触发路径对比
        2. 找到相似度最高且超过阈值的触发路径
        3. 通过映射关系找到对应的执行操作
        4. 返回操作信息给执行器
        
        Args:
            drawn_path: 绘制的路径 {'points': [...], 'connections': [...]}
            similarity_threshold: 相似度阈值
            
        Returns:
            tuple: (手势名称, 操作数据, 相似度) 或 (None, None, 0.0)
        """
        if not drawn_path or not drawn_path.get('points'):
            self.logger.debug("绘制路径为空")
            return None, None, 0.0
        
        # 归一化绘制路径
        normalized_drawn = self.path_analyzer.normalize_path_scale(drawn_path)
        
        best_match_path_id = None
        best_similarity = 0.0
        best_trigger_path = None
        
        self.logger.debug(f"开始路径匹配，相似度阈值: {similarity_threshold}")
        
        # 步骤1：将当前绘制路径与触发路径库中的每个路径对比
        for path_key, path_data in self.saved_trigger_paths.items():
            trigger_path = path_data.get("path")
            if not trigger_path:
                continue
            
            # 归一化触发路径
            normalized_trigger = self.path_analyzer.normalize_path_scale(trigger_path)
            
            # 计算相似度
            similarity = self.path_analyzer.calculate_similarity(normalized_drawn, normalized_trigger)
            
            path_name = path_data.get("name", path_key)
            self.logger.debug(f"触发路径 '{path_name}' 相似度: {similarity:.3f}")
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_path_id = path_data.get("id")
                best_trigger_path = path_data
        
        if best_similarity < similarity_threshold:
            self.logger.debug(f"没有触发路径达到相似度阈值 {similarity_threshold}，最高相似度: {best_similarity:.3f}")
            return None, None, best_similarity

        # 步骤2：通过映射关系找到对应的手势
        matched_gesture = None
        for mapping_key, mapping_data in self.saved_gesture_mappings.items():
            if mapping_data.get("trigger_path_id") == best_match_path_id:
                matched_gesture = mapping_data
                break
        
        if not matched_gesture:
            self.logger.warning(f"找到匹配的触发路径(ID:{best_match_path_id})，但没有找到对应的手势映射")
            return None, None, best_similarity
        
        # 步骤3：获取对应的执行操作
        execute_action_id = matched_gesture.get("execute_action_id")
        execute_action = None
        for action_key, action_data in self.saved_execute_actions.items():
            if action_data.get("id") == execute_action_id:
                execute_action = action_data
                break
        
        if not execute_action:
            self.logger.warning(f"找到手势映射，但没有找到对应的执行操作(ID:{execute_action_id})")
            return None, None, best_similarity
        
        gesture_name = matched_gesture.get("name", f"手势{matched_gesture.get('id')}")
        
        self.logger.info(f"识别到手势: {gesture_name}，相似度: {best_similarity:.3f}，操作: {execute_action.get('name')}")
        return gesture_name, execute_action, best_similarity

    def get_gesture_count(self, use_saved=False):
        """获取手势数量"""
        if use_saved:
            return len(self.saved_gesture_mappings)
        else:
            return len(self.gesture_mappings)

    def _get_next_mapping_id(self):
        """获取下一个映射ID"""
        max_id = 0
        for mapping_data in self.gesture_mappings.values():
            max_id = max(max_id, mapping_data.get("id", 0))
        return max_id + 1

    def _get_next_path_id(self):
        """获取下一个路径ID"""
        max_id = 0
        for path_data in self.trigger_paths.values():
            max_id = max(max_id, path_data.get("id", 0))
        return max_id + 1

    def _get_next_action_id(self):
        """获取下一个操作ID"""
        max_id = 0
        for action_data in self.execute_actions.values():
            max_id = max(max_id, action_data.get("id", 0))
        return max_id + 1

    def reset_to_default(self):
        """重置为默认手势库"""
        self.logger.info("重置为默认手势库")
        try:
            default_gestures = self._load_default_gestures()

            # 根据操作系统调整快捷键格式
            import sys
            if sys.platform != "win32":
                self.logger.info(f"检测到非Windows系统({sys.platform})，调整快捷键格式...")
                self._convert_actions_for_current_platform()

            # 重置三个部分的数据
            if (self.trigger_paths != default_gestures.get("trigger_paths", {}) or
                self.execute_actions != default_gestures.get("execute_actions", {}) or
                self.gesture_mappings != default_gestures.get("gesture_mappings", {})):
                
                self.trigger_paths = default_gestures.get("trigger_paths", {}).copy()
                self.execute_actions = default_gestures.get("execute_actions", {}).copy()
                self.gesture_mappings = default_gestures.get("gesture_mappings", {}).copy()

            success = self.save()
            if success:
                self._update_saved_state()

            return success
        except Exception as e:
            self.logger.error(f"重置为默认手势库失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        return False


_gesture_library_instance = None

def get_gesture_library():
    """获取手势库管理器实例"""
    global _gesture_library_instance
    if _gesture_library_instance is None:
        _gesture_library_instance = GestureLibrary()
    return _gesture_library_instance
