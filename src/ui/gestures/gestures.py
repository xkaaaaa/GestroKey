import json
import os
import pathlib
import sys
import copy
import time

from core.logger import get_logger
from core.path_analyzer import PathAnalyzer
from version import APP_NAME, AUTHOR


class GestureLibrary:
    def __init__(self):
        self.logger = get_logger("GestureLibrary")
        
        self.path_analyzer = PathAnalyzer()
        self.gestures_file = self._get_gestures_file_path()
        
        default_gestures = self._load_default_gestures()
        
        if sys.platform != "win32":
            self._convert_actions_for_current_platform()

        self.trigger_paths = default_gestures.get("trigger_paths", {}).copy()
        self.execute_actions = default_gestures.get("execute_actions", {}).copy()
        self.gesture_mappings = default_gestures.get("gesture_mappings", {}).copy()

        self.last_change_type = None
        self.change_timestamp = 0

        self._update_saved_state()
        self.load()

    def _load_default_gestures(self):
        default_gestures_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "default_gestures.json"
        )
        try:
            if os.path.exists(default_gestures_path):
                with open(default_gestures_path, "r", encoding="utf-8") as f:
                    gestures = json.load(f)
                return gestures
            else:
                raise FileNotFoundError(f"默认手势库文件不存在: {default_gestures_path}")
        except Exception as e:
            self.logger.error(f"加载默认手势库失败: {e}")
            raise

    def _convert_actions_for_current_platform(self):
        actions = self.execute_actions
        for action_key, action_data in actions.items():
            if action_data.get("type") == "shortcut":
                action_value = action_data.get("value", "")
                if action_value and "+" in action_value:
                    new_value = self._convert_shortcut_for_current_platform(action_value)
                    if new_value != action_value:
                        action_data["value"] = new_value

    def _convert_shortcut_for_current_platform(self, shortcut):
        if sys.platform == "darwin":
            shortcut = shortcut.replace("Ctrl+", "Cmd+")
            shortcut = shortcut.replace("ctrl+", "cmd+")
        elif sys.platform.startswith("linux"):
            pass
        return shortcut

    def _get_gestures_file_path(self):
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
        try:
            if os.path.exists(self.gestures_file):
                with open(self.gestures_file, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)

                if sys.platform != "win32":
                    self._convert_loaded_actions_for_current_platform(loaded_data)

                self.trigger_paths = loaded_data.get("trigger_paths", {}) or {}
                self.execute_actions = loaded_data.get("execute_actions", {}) or {}
                self.gesture_mappings = loaded_data.get("gesture_mappings", {}) or {}

                self._update_saved_state()
                self.clear_change_marker()
            else:
                self.save()
        except Exception as e:
            self.logger.error(f"加载手势库失败: {e}")
            raise

    def _convert_loaded_actions_for_current_platform(self, loaded_data):
        actions = loaded_data.get("execute_actions", {})
        format_converted = False
        for action_key, action_data in actions.items():
            if action_data.get("type") == "shortcut":
                action_value = action_data.get("value", "")
                if action_value and "+" in action_value:
                    new_value = self._convert_shortcut_for_current_platform(action_value)
                    if new_value != action_value:
                        action_data["value"] = new_value
                        format_converted = True

    def _update_saved_state(self):
        self.saved_trigger_paths = copy.deepcopy(self.trigger_paths)
        self.saved_execute_actions = copy.deepcopy(self.execute_actions)
        self.saved_gesture_mappings = copy.deepcopy(self.gesture_mappings)

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.gestures_file), exist_ok=True)

            data = {
                "trigger_paths": self.trigger_paths,
                "execute_actions": self.execute_actions,
                "gesture_mappings": self.gesture_mappings
            }

            with open(self.gestures_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            self._update_saved_state()
            self.clear_change_marker()
            return True
        except Exception as e:
            self.logger.error(f"保存手势库失败: {e}")
            return False

    def has_changes(self):
        return (
            self.trigger_paths != self.saved_trigger_paths or
            self.execute_actions != self.saved_execute_actions or
            self.gesture_mappings != self.saved_gesture_mappings
        )
    
    def mark_data_changed(self, change_type):
        self.last_change_type = change_type
        self.change_timestamp = time.time()
        
    def get_last_change_info(self):
        return self.last_change_type, self.change_timestamp
        
    def clear_change_marker(self):
        self.last_change_type = None
        self.change_timestamp = 0

    def get_gesture_by_path(self, drawn_path, similarity_threshold=0.70):
        if not drawn_path or not drawn_path.get('points'):
            return None, None, 0.0
        
        normalized_drawn = self.path_analyzer.normalize_path_scale(drawn_path)
        
        best_match_path_key = None
        best_similarity = 0.0
        best_trigger_path = None
        
        for path_key, path_data in self.saved_trigger_paths.items():
            trigger_path = path_data.get("path")
            if not trigger_path:
                continue
            
            normalized_trigger = self.path_analyzer.normalize_path_scale(trigger_path)
            similarity = self.path_analyzer.calculate_similarity(normalized_drawn, normalized_trigger)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_path_key = path_key
                best_trigger_path = path_data
        
        if best_similarity < similarity_threshold:
            return None, None, best_similarity

        matched_gesture = None
        best_match_path_id = int(best_match_path_key) if best_match_path_key and best_match_path_key.isdigit() else None
        
        for mapping_key, mapping_data in self.saved_gesture_mappings.items():
            if mapping_data.get("trigger_path_id") == best_match_path_id:
                matched_gesture = mapping_data
                break
        
        if not matched_gesture:
            return None, None, best_similarity
        
        execute_action_id = matched_gesture.get("execute_action_id")
        execute_action = None
        execute_action_key = str(execute_action_id) if execute_action_id is not None else None
        
        if execute_action_key and execute_action_key in self.saved_execute_actions:
            execute_action = self.saved_execute_actions[execute_action_key]
        
        if not execute_action:
            return None, None, best_similarity
        
        gesture_name = matched_gesture.get("name", f"手势{mapping_key}")
        return gesture_name, execute_action, best_similarity

    def get_gesture_count(self, use_saved=False):
        if use_saved:
            return len(self.saved_gesture_mappings)
        else:
            return len(self.gesture_mappings)

    def _get_next_mapping_id(self):
        max_id = 0
        if self.gesture_mappings:
            for mapping_key in self.gesture_mappings.keys():
                if mapping_key.isdigit():
                    max_id = max(max_id, int(mapping_key))
        return max_id + 1

    def _get_next_path_id(self):
        max_id = 0
        if self.trigger_paths:
            for path_key in self.trigger_paths.keys():
                if path_key.isdigit():
                    max_id = max(max_id, int(path_key))
        return max_id + 1

    def _get_next_action_id(self):
        max_id = 0
        if self.execute_actions:
            for action_key in self.execute_actions.keys():
                if action_key.isdigit():
                    max_id = max(max_id, int(action_key))
        return max_id + 1

    def reset_to_default(self):
        try:
            default_gestures = self._load_default_gestures()

            if sys.platform != "win32":
                self._convert_actions_for_current_platform()

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
        return False


_gesture_library_instance = None

def get_gesture_library():
    global _gesture_library_instance
    if _gesture_library_instance is None:
        _gesture_library_instance = GestureLibrary()
    return _gesture_library_instance