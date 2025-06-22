from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QGroupBox, QMessageBox, QComboBox, QDialogButtonBox
)

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library
from ui.gestures.drawing_widget import GestureDrawingWidget


class TriggerPathEditDialog(QDialog):
    """触发路径编辑/添加对话框"""
    
    def __init__(self, path_key=None, parent=None):
        super().__init__(parent)
        self.logger = get_logger("TriggerPathEditDialog")
        self.gesture_library = get_gesture_library()
        
        self.path_key = path_key
        self.current_path = None
        self.is_editing = path_key is not None
        
        self.setWindowTitle("编辑触发路径" if self.is_editing else "添加触发路径")
        self.setFixedSize(600, 500)
        
        self.initUI()
        
        if self.is_editing:
            self._load_path_data()
        
    def initUI(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 基本信息编辑
        info_group = QGroupBox("基本信息")
        info_layout = QVBoxLayout(info_group)
        
        # 路径名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("路径名称:"))
        self.edit_name = QLineEdit()
        name_layout.addWidget(self.edit_name)
        info_layout.addLayout(name_layout)
        
        layout.addWidget(info_group)
        
        # 路径绘制区域
        drawing_group = QGroupBox("路径绘制")
        drawing_layout = QVBoxLayout(drawing_group)
        
        self.drawing_widget = GestureDrawingWidget()
        self.drawing_widget.current_tool = "brush"
        self.drawing_widget.pathCompleted.connect(self._on_path_completed)
        self.drawing_widget.pathUpdated.connect(self._on_path_updated)
        drawing_layout.addWidget(self.drawing_widget)
        
        layout.addWidget(drawing_group)
        
        # 按钮区域
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        
        # 添加清空绘制按钮
        self.btn_clear = QPushButton("清空绘制")
        self.btn_clear.clicked.connect(self._clear_drawing)
        button_box.addButton(self.btn_clear, QDialogButtonBox.ButtonRole.ActionRole)
        
        layout.addWidget(button_box)
        
    def _load_path_data(self):
        """加载路径数据"""
        if not self.path_key:
            return
            
        path_data = self.gesture_library.trigger_paths.get(self.path_key)
        if not path_data:
            self.logger.error(f"找不到路径: {self.path_key}")
            return
            
        # 填充表单
        path_name = path_data.get('name', '')
        self.edit_name.setText(path_name)
        
        # 加载路径到绘制区域
        path = path_data.get('path')
        if path:
            import copy
            self.current_path = copy.deepcopy(path)
            self.drawing_widget.load_path(self.current_path)
            
    def _on_path_completed(self, path):
        """处理路径绘制完成事件"""
        import copy
        self.current_path = copy.deepcopy(path)
        self.logger.info(f"路径绘制完成，关键点数: {len(path.get('points', []))}")
        
    def _on_path_updated(self):
        """处理路径更新事件"""
        if self.drawing_widget.completed_paths:
            import copy
            self.current_path = copy.deepcopy(self.drawing_widget.completed_paths[-1])
            self.logger.info("路径已更新")
            
    def _clear_drawing(self):
        """清空绘制"""
        self.drawing_widget.clear_drawing()
        self.current_path = None
        
    def _save_and_accept(self):
        """保存并关闭对话框"""
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入路径名称")
            return
            
        try:
            if self.is_editing:
                # 编辑现有路径
                path_data = self.gesture_library.trigger_paths[self.path_key]
                path_data['name'] = name
                if self.current_path:
                    path_data['path'] = self.current_path
                self.logger.info(f"更新路径: {name}")
            else:
                # 添加新路径
                path_id = self.gesture_library._get_next_path_id()
                path_key = f"path_{path_id}"
                
                new_path_data = {
                    'id': path_id,
                    'name': name,
                    'path': self.current_path
                }
                
                self.gesture_library.trigger_paths[path_key] = new_path_data
                self.path_key = path_key
                self.logger.info(f"添加新路径: {name}, ID: {path_id}")
                
            # 标记数据已变更
            self.gesture_library.mark_data_changed("trigger_paths")
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"保存路径时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存路径失败: {str(e)}")


class ExecuteActionEditDialog(QDialog):
    """执行操作编辑/添加对话框"""
    
    def __init__(self, action_key=None, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ExecuteActionEditDialog")
        self.gesture_library = get_gesture_library()
        
        self.action_key = action_key
        self.is_editing = action_key is not None
        
        self.setWindowTitle("编辑执行操作" if self.is_editing else "添加执行操作")
        self.setFixedSize(400, 300)
        
        self.initUI()
        
        if self.is_editing:
            self._load_action_data()
        
    def initUI(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 基本信息编辑
        info_group = QGroupBox("操作信息")
        info_layout = QVBoxLayout(info_group)
        
        # 操作名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("操作名称:"))
        self.edit_name = QLineEdit()
        name_layout.addWidget(self.edit_name)
        info_layout.addLayout(name_layout)
        
        # 操作类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("操作类型:"))
        self.combo_type = QComboBox()
        self.combo_type.addItem("快捷键", "shortcut")
        type_layout.addWidget(self.combo_type)
        info_layout.addLayout(type_layout)
        
        # 操作值
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("操作值:"))
        self.edit_value = QLineEdit()
        self.edit_value.setPlaceholderText("例如: Ctrl+C")
        value_layout.addWidget(self.edit_value)
        info_layout.addLayout(value_layout)
        
        layout.addWidget(info_group)
        
        # 添加一些空间
        layout.addStretch()
        
        # 按钮区域
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
    def _load_action_data(self):
        """加载操作数据"""
        if not self.action_key:
            return
            
        action_data = self.gesture_library.execute_actions.get(self.action_key)
        if not action_data:
            self.logger.error(f"找不到操作: {self.action_key}")
            return
            
        # 填充表单
        action_name = action_data.get('name', '')
        action_type = action_data.get('type', 'shortcut')
        action_value = action_data.get('value', '')
        
        self.edit_name.setText(action_name)
        self.edit_value.setText(action_value)
        
        # 设置类型下拉框
        for i in range(self.combo_type.count()):
            if self.combo_type.itemData(i) == action_type:
                self.combo_type.setCurrentIndex(i)
                break
                
    def _save_and_accept(self):
        """保存并关闭对话框"""
        name = self.edit_name.text().strip()
        action_type = self.combo_type.currentData()
        value = self.edit_value.text().strip()
        
        if not name:
            QMessageBox.warning(self, "警告", "请输入操作名称")
            return
            
        if not value:
            QMessageBox.warning(self, "警告", "请输入操作值")
            return
            
        try:
            if self.is_editing:
                # 编辑现有操作
                action_data = self.gesture_library.execute_actions[self.action_key]
                action_data['name'] = name
                action_data['type'] = action_type
                action_data['value'] = value
                self.logger.info(f"更新操作: {name}")
            else:
                # 添加新操作
                action_id = self.gesture_library._get_next_action_id()
                action_key = f"action_{action_id}"
                
                new_action_data = {
                    'id': action_id,
                    'name': name,
                    'type': action_type,
                    'value': value
                }
                
                self.gesture_library.execute_actions[action_key] = new_action_data
                self.action_key = action_key
                self.logger.info(f"添加新操作: {name}, ID: {action_id}")
                
            # 标记数据已变更
            self.gesture_library.mark_data_changed("execute_actions")
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"保存操作时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存操作失败: {str(e)}") 