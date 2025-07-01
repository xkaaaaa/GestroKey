import base64
import copy
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

current_dir = Path(__file__).parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library
from ui.settings.settings import get_settings


class SelfChecker:
    def __init__(self):
        self.logger = get_logger("SelfChecker")
        self.errors = []
        self.warnings = []
        self.repairs = []
        self.corrupted_data = []
        
        self.src_dir = Path(__file__).parent.parent
        self.gestures_dir = self.src_dir / "ui" / "gestures"
        self.settings_dir = self.src_dir / "ui" / "settings"

    def run_full_check(self) -> bool:
        self.logger.info("开始程序自检...")
        
        try:
            self._check_and_repair_gestures()
            self._check_and_repair_settings()
            self._output_check_results()
            
            if self.errors:
                self.logger.error(f"自检发现 {len(self.errors)} 个错误")
                return False
            
            self.logger.info("自检完成，所有检查通过")
            return True
            
        except Exception as e:
            self.logger.error(f"自检过程中发生异常: {e}")
            self.logger.error(traceback.format_exc())
            return False

    def _load_default_data(self, file_path: Path, data_type: str) -> Optional[Dict]:
        try:
            if not file_path.exists():
                self.errors.append(f"默认{data_type}文件不存在: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except json.JSONDecodeError as e:
            self.errors.append(f"默认{data_type}文件JSON格式错误: {e}")
            return None
        except Exception as e:
            self.errors.append(f"读取默认{data_type}文件时出错: {e}")
            return None

    def _check_and_repair_gestures(self):
        self.logger.info("检查手势库...")
        
        default_file = self.gestures_dir / "default_gestures.json"
        default_data = self._load_default_data(default_file, "手势库")
        if not default_data:
            return
        
        gesture_lib = get_gesture_library()
        user_file = Path(gesture_lib.gestures_file)
        
        if not user_file.exists():
            self.logger.debug("用户手势库不存在，将使用默认手势库")
            return
        
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            repaired_data = self._repair_gesture_data(user_data, default_data)
            
            if repaired_data != user_data:
                self._save_repaired_data(user_file, repaired_data, "手势库")
                gesture_lib.load()
                gesture_lib.save()
                self.logger.info("已重新加载并保存手势库")
                
        except json.JSONDecodeError as e:
            self.warnings.append(f"用户手势库JSON格式错误: {e}")
            self._backup_and_reset(user_file, default_data, "手势库")
            gesture_lib.load()
            gesture_lib.save()
            self.logger.info("已重新加载并保存重置的手势库")
        except Exception as e:
            self.warnings.append(f"检查用户手势库时出错: {e}")

    def _repair_gesture_data(self, user_data: Dict, default_data: Dict) -> Dict:
        repaired = copy.deepcopy(user_data)
        
        # 1. 检查和修复主键结构
        for main_key in default_data:
            if main_key not in repaired:
                repaired[main_key] = {}
                self.repairs.append(f"添加缺失的手势库主键: {main_key}")
            
            if not isinstance(repaired[main_key], dict):
                repaired[main_key] = {}
                self.repairs.append(f"修复手势库主键类型: {main_key}")
        
        for key in list(repaired.keys()):
            if key not in default_data:
                del repaired[key]
                self.repairs.append(f"删除无效的手势库主键: {key}")
        
        # 2. 检查和修复各部分的详细格式
        repaired = self._repair_trigger_paths(repaired, default_data)
        repaired = self._repair_execute_actions(repaired, default_data)
        repaired = self._repair_gesture_mappings(repaired, default_data)
        
        # 3. 检查和修复引用完整性
        repaired = self._repair_reference_integrity(repaired)
        
        # 4. 检查和修复顺序
        repaired = self._repair_data_order(repaired)
        
        return repaired

    def _repair_trigger_paths(self, user_data: Dict, default_data: Dict) -> Dict:
        if "trigger_paths" not in default_data or not default_data["trigger_paths"]:
            return user_data
        
        default_sample = next(iter(default_data["trigger_paths"].values()))
        trigger_paths = user_data["trigger_paths"]
        
        for path_key, path_data in list(trigger_paths.items()):
            # 检查键格式（应为数字字符串）
            if not path_key.isdigit():
                new_key = str(len(trigger_paths) + 1)
                trigger_paths[new_key] = trigger_paths.pop(path_key)
                self.repairs.append(f"修复trigger_paths键格式: {path_key} -> {new_key}")
                path_key = new_key
                path_data = trigger_paths[path_key]
            
            # 检查必要字段
            if not isinstance(path_data, dict):
                trigger_paths[path_key] = copy.deepcopy(default_sample)
                self.repairs.append(f"修复trigger_paths[{path_key}]整体格式")
                continue
            
            # 检查name字段
            if "name" not in path_data or not isinstance(path_data["name"], str):
                path_data["name"] = f"路径{path_key}"
                self.repairs.append(f"修复trigger_paths[{path_key}].name")
            
            # 检查path字段
            if "path" not in path_data or not isinstance(path_data["path"], dict):
                path_data["path"] = copy.deepcopy(default_sample["path"])
                self.repairs.append(f"修复trigger_paths[{path_key}].path")
            else:
                path_data["path"] = self._repair_path_structure(path_data["path"], default_sample["path"], path_key)
        
        return user_data

    def _repair_path_structure(self, path_data: Dict, default_path: Dict, path_key: str) -> Dict:
        # 检查points字段
        if "points" not in path_data or not isinstance(path_data["points"], list):
            path_data["points"] = copy.deepcopy(default_path["points"])
            self.repairs.append(f"修复trigger_paths[{path_key}].path.points")
        
        # 检查connections字段
        if "connections" not in path_data or not isinstance(path_data["connections"], list):
            path_data["connections"] = copy.deepcopy(default_path["connections"])
            self.repairs.append(f"修复trigger_paths[{path_key}].path.connections")
        else:
            # 检查连线类型
            valid_types = {"line", "curve", "arc"}  # 允许的连线类型
            for i, connection in enumerate(path_data["connections"]):
                if not isinstance(connection, dict):
                    path_data["connections"][i] = {"from": 0, "to": 1, "type": "line"}
                    self.repairs.append(f"修复trigger_paths[{path_key}].path.connections[{i}]格式")
                    continue
                
                # 检查连线类型
                if "type" not in connection or connection["type"] not in valid_types:
                    connection["type"] = "line"
                    self.repairs.append(f"修复trigger_paths[{path_key}].path.connections[{i}].type")
                
                # 检查from和to字段
                if "from" not in connection or not isinstance(connection["from"], int):
                    connection["from"] = 0
                    self.repairs.append(f"修复trigger_paths[{path_key}].path.connections[{i}].from")
                
                if "to" not in connection or not isinstance(connection["to"], int):
                    connection["to"] = 1
                    self.repairs.append(f"修复trigger_paths[{path_key}].path.connections[{i}].to")
        
        return path_data

    def _repair_execute_actions(self, user_data: Dict, default_data: Dict) -> Dict:
        if "execute_actions" not in default_data or not default_data["execute_actions"]:
            return user_data
        
        default_sample = next(iter(default_data["execute_actions"].values()))
        execute_actions = user_data["execute_actions"]
        
        for action_key, action_data in list(execute_actions.items()):
            # 检查键格式（应为数字字符串）
            if not action_key.isdigit():
                new_key = str(len(execute_actions) + 1)
                execute_actions[new_key] = execute_actions.pop(action_key)
                self.repairs.append(f"修复execute_actions键格式: {action_key} -> {new_key}")
                action_key = new_key
                action_data = execute_actions[action_key]
            
            # 检查必要字段
            if not isinstance(action_data, dict):
                execute_actions[action_key] = copy.deepcopy(default_sample)
                self.repairs.append(f"修复execute_actions[{action_key}]整体格式")
                continue
            
            # 检查各个字段
            required_fields = ["name", "type", "value"]
            for field in required_fields:
                if field not in action_data:
                    action_data[field] = default_sample.get(field, "")
                    self.repairs.append(f"添加execute_actions[{action_key}].{field}")
                elif field == "name" and not isinstance(action_data[field], str):
                    action_data[field] = f"操作{action_key}"
                    self.repairs.append(f"修复execute_actions[{action_key}].{field}类型")
                elif field in ["type", "value"] and not isinstance(action_data[field], str):
                    action_data[field] = str(action_data[field])
                    self.repairs.append(f"修复execute_actions[{action_key}].{field}类型")
        
        return user_data

    def _repair_gesture_mappings(self, user_data: Dict, default_data: Dict) -> Dict:
        if "gesture_mappings" not in default_data or not default_data["gesture_mappings"]:
            return user_data
        
        default_sample = next(iter(default_data["gesture_mappings"].values()))
        gesture_mappings = user_data["gesture_mappings"]
        
        for mapping_key, mapping_data in list(gesture_mappings.items()):
            # 检查键格式（应为数字字符串）
            if not mapping_key.isdigit():
                new_key = str(len(gesture_mappings) + 1)
                gesture_mappings[new_key] = gesture_mappings.pop(mapping_key)
                self.repairs.append(f"修复gesture_mappings键格式: {mapping_key} -> {new_key}")
                mapping_key = new_key
                mapping_data = gesture_mappings[mapping_key]
            
            # 检查必要字段
            if not isinstance(mapping_data, dict):
                gesture_mappings[mapping_key] = copy.deepcopy(default_sample)
                self.repairs.append(f"修复gesture_mappings[{mapping_key}]整体格式")
                continue
            
            # 检查各个字段
            required_fields = ["name", "trigger_path_id", "execute_action_id"]
            for field in required_fields:
                if field not in mapping_data:
                    if field == "name":
                        mapping_data[field] = f"手势{mapping_key}"
                    elif field in ["trigger_path_id", "execute_action_id"]:
                        mapping_data[field] = 1
                    self.repairs.append(f"添加gesture_mappings[{mapping_key}].{field}")
                elif field == "name" and not isinstance(mapping_data[field], str):
                    mapping_data[field] = f"手势{mapping_key}"
                    self.repairs.append(f"修复gesture_mappings[{mapping_key}].{field}类型")
                elif field in ["trigger_path_id", "execute_action_id"] and not isinstance(mapping_data[field], int):
                    try:
                        mapping_data[field] = int(mapping_data[field])
                    except (ValueError, TypeError):
                        mapping_data[field] = 1
                    self.repairs.append(f"修复gesture_mappings[{mapping_key}].{field}类型")
        
        return user_data

    def _repair_reference_integrity(self, user_data: Dict) -> Dict:
        trigger_paths = user_data.get("trigger_paths", {})
        execute_actions = user_data.get("execute_actions", {})
        gesture_mappings = user_data.get("gesture_mappings", {})
        
        # 检查映射中的引用完整性
        for mapping_key, mapping_data in list(gesture_mappings.items()):
            if not isinstance(mapping_data, dict):
                continue
            
            # 检查trigger_path_id引用
            trigger_path_id = mapping_data.get("trigger_path_id")
            if trigger_path_id is not None and str(trigger_path_id) not in trigger_paths:
                # 找一个存在的trigger_path_id，如果没有则删除映射
                if trigger_paths:
                    new_id = int(next(iter(trigger_paths.keys())))
                    mapping_data["trigger_path_id"] = new_id
                    self.repairs.append(f"修复gesture_mappings[{mapping_key}].trigger_path_id引用: {trigger_path_id} -> {new_id}")
                else:
                    del gesture_mappings[mapping_key]
                    self.repairs.append(f"删除无效的gesture_mappings[{mapping_key}]（无可用的trigger_path）")
                    continue
            
            # 检查execute_action_id引用
            execute_action_id = mapping_data.get("execute_action_id")
            if execute_action_id is not None and str(execute_action_id) not in execute_actions:
                # 找一个存在的execute_action_id，如果没有则删除映射
                if execute_actions:
                    new_id = int(next(iter(execute_actions.keys())))
                    mapping_data["execute_action_id"] = new_id
                    self.repairs.append(f"修复gesture_mappings[{mapping_key}].execute_action_id引用: {execute_action_id} -> {new_id}")
                else:
                    del gesture_mappings[mapping_key]
                    self.repairs.append(f"删除无效的gesture_mappings[{mapping_key}]（无可用的execute_action）")
                    continue
        
        return user_data

    def _repair_data_order(self, user_data: Dict) -> Dict:
        # 修复各部分的顺序
        for section_name in ["trigger_paths", "execute_actions", "gesture_mappings"]:
            section_data = user_data.get(section_name, {})
            if not section_data:
                continue
            
            # 获取所有数字键并排序
            numeric_keys = []
            non_numeric_data = {}
            
            for key, value in section_data.items():
                if key.isdigit():
                    numeric_keys.append(int(key))
                else:
                    non_numeric_data[key] = value
            
            # 如果没有数字键，跳过
            if not numeric_keys:
                continue
            
            # 按数字排序
            numeric_keys.sort()
            
            # 创建连续的序号映射
            old_data = copy.deepcopy(section_data)
            section_data.clear()
            key_mapping = {}
            
            # 先处理数字键，按连续序号重新排列
            for i, old_id in enumerate(numeric_keys):
                new_id = i + 1
                old_key = str(old_id)
                new_key = str(new_id)
                
                if old_key in old_data:
                    section_data[new_key] = old_data[old_key]
                    if old_id != new_id:
                        key_mapping[old_id] = new_id
                        self.repairs.append(f"重新排序{section_name}: {old_key} -> {new_key}")
            
            # 如果原来的序号不连续，添加修复日志
            expected_keys = list(range(1, len(numeric_keys) + 1))
            if numeric_keys != expected_keys:
                self.repairs.append(f"修复{section_name}序号连续性")
                
                # 如果是trigger_paths或execute_actions被重新排序，需要更新gesture_mappings中的引用
                if section_name in ["trigger_paths", "execute_actions"] and key_mapping:
                    field_name = f"{section_name[:-1]}_id"  # trigger_path_id 或 execute_action_id
                    
                    for mapping_key, mapping_data in user_data.get("gesture_mappings", {}).items():
                        if isinstance(mapping_data, dict) and field_name in mapping_data:
                            old_id = mapping_data[field_name]
                            if old_id in key_mapping:
                                new_id = key_mapping[old_id]
                                mapping_data[field_name] = new_id
                                self.repairs.append(f"更新gesture_mappings[{mapping_key}].{field_name}: {old_id} -> {new_id}")
        
        return user_data

    def _check_and_repair_settings(self):
        self.logger.info("检查设置...")
        
        default_file = self.settings_dir / "default_settings.json"
        default_data = self._load_default_data(default_file, "设置")
        if not default_data:
            return
        
        settings = get_settings()
        user_file = Path(settings.settings_file)
        
        if not user_file.exists():
            self.logger.debug("用户设置不存在，将使用默认设置")
            return
        
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            repaired_data = self._repair_settings_data(user_data, default_data)
            
            if repaired_data != user_data:
                self._save_repaired_data(user_file, repaired_data, "设置")
                settings.load()
                settings.save()
                self.logger.info("已重新加载并保存设置")
                
        except json.JSONDecodeError as e:
            self.warnings.append(f"用户设置JSON格式错误: {e}")
            self._backup_and_reset(user_file, default_data, "设置")
            settings.load()
            settings.save()
            self.logger.info("已重新加载并保存重置的设置")
        except Exception as e:
            self.warnings.append(f"检查用户设置时出错: {e}")

    def _repair_settings_data(self, user_data: Dict, default_data: Dict) -> Dict:
        repaired = copy.deepcopy(user_data)
        
        def repair_nested(current: Dict, template: Dict, path: str = ""):
            for key, default_value in template.items():
                current_path = f"{path}.{key}" if path else key
                
                if key not in current:
                    current[key] = copy.deepcopy(default_value)
                    self.repairs.append(f"添加缺失的设置键: {current_path}")
                elif isinstance(default_value, dict):
                    if not isinstance(current[key], dict):
                        current[key] = copy.deepcopy(default_value)
                        self.repairs.append(f"修复设置键类型: {current_path}")
                    else:
                        repair_nested(current[key], default_value, current_path)
                elif type(current[key]) != type(default_value):
                    if not (isinstance(current[key], (int, float)) and isinstance(default_value, (int, float))):
                        current[key] = copy.deepcopy(default_value)
                        self.repairs.append(f"修复设置值类型: {current_path}")
            
            for key in list(current.keys()):
                if key not in template:
                    del current[key]
                    current_path = f"{path}.{key}" if path else key
                    self.repairs.append(f"删除无效的设置键: {current_path}")
        
        repair_nested(repaired, default_data)
        return repaired

    def _save_repaired_data(self, file_path: Path, data: Dict, data_type: str):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"已修复{data_type}文件: {file_path}")
            
        except Exception as e:
            self.errors.append(f"保存修复的{data_type}文件失败: {e}")

    def _backup_and_reset(self, file_path: Path, default_data: Dict, data_type: str):
        self._backup_corrupted_file(file_path, data_type.lower())
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
            
            self.logger.warning(f"已重置{data_type}为默认值: {file_path}")
            
        except Exception as e:
            self.errors.append(f"重置{data_type}文件失败: {e}")

    def _backup_corrupted_file(self, file_path: Path, file_type: str):
        try:
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                encoded_content = base64.b64encode(content).decode('utf-8')
                
                self.corrupted_data.append({
                    "type": file_type,
                    "path": str(file_path),
                    "content": encoded_content
                })
                
                self.logger.warning(f"已备份损坏文件: {file_path}")
            
        except Exception as e:
            self.logger.error(f"备份文件失败: {e}")

    def _output_check_results(self):
        if self.errors:
            self.logger.error("=" * 50)
            self.logger.error("发现错误:")
            for i, error in enumerate(self.errors, 1):
                self.logger.error(f"  {i}. {error}")
        
        if self.warnings:
            self.logger.warning("=" * 50)
            self.logger.warning("发现警告:")
            for i, warning in enumerate(self.warnings, 1):
                self.logger.warning(f"  {i}. {warning}")
        
        if self.repairs:
            self.logger.info("=" * 50)
            self.logger.info("执行修复:")
            for i, repair in enumerate(self.repairs, 1):
                self.logger.info(f"  {i}. {repair}")
        
        if self.corrupted_data:
            print("\n" + "=" * 60)
            print("损坏数据备份 (Base64加密):")
            print("=" * 60)
            for i, data in enumerate(self.corrupted_data, 1):
                print(f"\n{i}. 类型: {data['type']}")
                print(f"   路径: {data['path']}")
                print(f"   内容: {data['content']}")
            print("=" * 60)


def run_self_check() -> bool:
    checker = SelfChecker()
    return checker.run_full_check()