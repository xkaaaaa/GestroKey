from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QLineEdit, QGroupBox, QMessageBox, QComboBox
)

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library


class ExecuteActionsTab(QWidget):
    """执行操作管理选项卡"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ExecuteActionsTab")
        self.gesture_library = get_gesture_library()
        
        self.current_action_key = None
        
        self.initUI()
        self._load_action_list()
        
    def initUI(self):
        """初始化用户界面"""
        layout = QHBoxLayout(self)
        
        # 左侧操作列表
        left_panel = self._create_action_list_panel()
        layout.addWidget(left_panel, 1)
        
        # 右侧操作编辑器
        right_panel = self._create_action_editor_panel()
        layout.addWidget(right_panel, 2)
        
    def _create_action_list_panel(self):
        """创建操作列表面板"""
        panel = QGroupBox("执行操作列表")
        layout = QVBoxLayout(panel)
        
        # 操作列表
        self.action_list = QListWidget()
        self.action_list.itemClicked.connect(self._on_action_selected)
        layout.addWidget(self.action_list)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.btn_add_action = QPushButton("添加操作")
        self.btn_add_action.clicked.connect(self._add_new_action)
        button_layout.addWidget(self.btn_add_action)
        
        self.btn_delete_action = QPushButton("删除操作")
        self.btn_delete_action.clicked.connect(self._delete_action)
        self.btn_delete_action.setEnabled(False)
        button_layout.addWidget(self.btn_delete_action)
        
        layout.addLayout(button_layout)
        
        return panel
        
    def _create_action_editor_panel(self):
        """创建操作编辑器面板"""
        panel = QGroupBox("操作编辑器")
        layout = QVBoxLayout(panel)
        
        # 基本信息编辑
        info_layout = QVBoxLayout()
        
        # 操作名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("操作名称:"))
        self.edit_name = QLineEdit()
        self.edit_name.textChanged.connect(self._on_form_changed)
        name_layout.addWidget(self.edit_name)
        info_layout.addLayout(name_layout)
        
        # 操作类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("操作类型:"))
        self.combo_type = QComboBox()
        self.combo_type.addItem("快捷键", "shortcut")
        self.combo_type.currentTextChanged.connect(self._on_form_changed)
        type_layout.addWidget(self.combo_type)
        info_layout.addLayout(type_layout)
        
        # 操作值
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("操作值:"))
        self.edit_value = QLineEdit()
        self.edit_value.setPlaceholderText("例如: Ctrl+C")
        self.edit_value.textChanged.connect(self._on_form_changed)
        value_layout.addWidget(self.edit_value)
        info_layout.addLayout(value_layout)
        
        layout.addLayout(info_layout)
        
        # 添加一些空间
        layout.addStretch()
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self._clear_form)
        button_layout.addWidget(self.btn_clear)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return panel
        
    def _load_action_list(self):
        """加载操作列表"""
        self.action_list.clear()
        execute_actions = self.gesture_library.execute_actions
        
        # 按ID排序显示
        sorted_actions = sorted(execute_actions.items(), key=lambda x: x[1].get('id', 0))
        
        for action_key, action_data in sorted_actions:
            action_id = action_data.get('id', 0)
            action_name = action_data.get('name', f'操作{action_id}')
            action_type = action_data.get('type', 'shortcut')
            action_value = action_data.get('value', '')
            
            item_text = f"{action_id}. {action_name} ({action_type}: {action_value})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, action_key)
            self.action_list.addItem(item)
            
        self.logger.debug(f"已加载 {len(execute_actions)} 个执行操作")
        
    def _on_action_selected(self, item):
        """操作选择事件"""
        action_key = item.data(Qt.ItemDataRole.UserRole)
        self._load_action_to_editor(action_key)
        
    def _load_action_to_editor(self, action_key):
        """将操作数据加载到编辑器"""
        action_data = self.gesture_library.execute_actions.get(action_key)
        if not action_data:
            self.logger.error(f"找不到操作: {action_key}")
            return
            
        self.logger.debug(f"开始加载操作到编辑器: {action_key}")
        
        # 暂时断开信号连接
        self.edit_name.textChanged.disconnect()
        self.combo_type.currentTextChanged.disconnect()
        self.edit_value.textChanged.disconnect()
        
        try:
            # 更新状态
            self.current_action_key = action_key
            
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
                    
        finally:
            # 重新连接信号
            self.edit_name.textChanged.connect(self._on_form_changed)
            self.combo_type.currentTextChanged.connect(self._on_form_changed)
            self.edit_value.textChanged.connect(self._on_form_changed)
            
        # 更新按钮状态
        self.btn_delete_action.setEnabled(True)
        
        self.logger.debug(f"已加载操作到编辑器: {action_key}")
        
    def _on_form_changed(self):
        """表单内容变化事件"""
        self._auto_save_changes()
        
    def _auto_save_changes(self):
        """自动保存变更到手势库变量中"""
        if not self.current_action_key:
            return
            
        name = self.edit_name.text().strip()
        action_type = self.combo_type.currentData()
        value = self.edit_value.text().strip()
        
        if not name or not action_type or not value:
            return
            
        try:
            # 自动更新到手势库变量中
            action_data = self.gesture_library.execute_actions[self.current_action_key]
            action_data['name'] = name
            action_data['type'] = action_type
            action_data['value'] = value
            
            # 标记数据已变更
            self.gesture_library.mark_data_changed("execute_actions")
            
            # 刷新列表显示
            self._load_action_list()
            self._select_action_in_list(self.current_action_key)
            
        except Exception as e:
            self.logger.error(f"自动保存操作时出错: {e}")
        

        
    def _clear_form(self):
        """清空表单"""
        self.current_action_key = None
        
        # 清空表单
        self.edit_name.setText("")
        self.edit_value.setText("")
        self.combo_type.setCurrentIndex(0)  # 默认为快捷键
        
        # 更新按钮状态
        self.btn_delete_action.setEnabled(False)
        
        self.logger.info("已清空表单")
        
    def _add_new_action(self):
        """添加新操作"""
        try:
            # 获取表单中的当前内容
            current_name = self.edit_name.text().strip()
            current_type = self.combo_type.currentData()
            current_value = self.edit_value.text().strip()
            
            # 生成新操作ID和默认名称
            action_id = self.gesture_library._get_next_action_id()
            action_key = f"action_{action_id}"
            
            # 使用用户填写的内容，如果为空则使用默认值
            if not current_name:
                current_name = f"操作{action_id}"
            if not current_type:
                current_type = "shortcut"  # 默认为快捷键
            if not current_value:
                current_value = ""  # 默认为空值
            
            # 创建新操作数据
            new_action_data = {
                'id': action_id,
                'name': current_name,
                'type': current_type,
                'value': current_value
            }
            
            # 添加到手势库
            self.gesture_library.execute_actions[action_key] = new_action_data
            
            # 标记数据已变更
            self.gesture_library.mark_data_changed("execute_actions")
            
            # 更新当前编辑状态
            self.current_action_key = action_key
            
            # 断开信号避免递归
            self.edit_name.textChanged.disconnect()
            self.combo_type.currentTextChanged.disconnect()
            self.edit_value.textChanged.disconnect()
            
            # 更新表单内容
            self.edit_name.setText(current_name)
            # 设置类型下拉框
            for i in range(self.combo_type.count()):
                if self.combo_type.itemData(i) == current_type:
                    self.combo_type.setCurrentIndex(i)
                    break
            self.edit_value.setText(current_value)
            
            # 重新连接信号
            self.edit_name.textChanged.connect(self._on_form_changed)
            self.combo_type.currentTextChanged.connect(self._on_form_changed)
            self.edit_value.textChanged.connect(self._on_form_changed)
            
            # 刷新列表并选中新添加的项
            self._load_action_list()
            self._select_action_in_list(action_key)
            
            # 更新按钮状态
            self.btn_delete_action.setEnabled(True)
            
            self.logger.info(f"添加新操作: {current_name}, ID: {action_id}")
            
        except Exception as e:
            self.logger.error(f"添加新操作时出错: {e}")
            QMessageBox.critical(self, "错误", f"添加新操作失败: {str(e)}")
        
    def _select_action_in_list(self, action_key):
        """在列表中选择指定操作"""
        for i in range(self.action_list.count()):
            item = self.action_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == action_key:
                self.action_list.setCurrentItem(item)
                break
                
    def _delete_action(self):
        """删除操作"""
        if not self.current_action_key:
            return
            
        action_data = self.gesture_library.execute_actions.get(self.current_action_key)
        if not action_data:
            return
            
        action_name = action_data.get('name', '未命名操作')
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除操作 '{action_name}' 吗？\n\n注意：删除操作可能会影响使用此操作的手势映射。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                del self.gesture_library.execute_actions[self.current_action_key]
                self.logger.info(f"删除操作: {action_name}")
                
                # 标记数据已变更
                self.gesture_library.mark_data_changed("execute_actions")
                
                # 清空编辑器
                self._clear_form()
                
                # 刷新列表
                self._load_action_list()
                
                QMessageBox.information(self, "成功", "操作已删除")
                
            except Exception as e:
                self.logger.error(f"删除操作时出错: {e}")
                QMessageBox.critical(self, "错误", f"删除操作失败: {str(e)}")
                

        
    def refresh_list(self):
        """刷新列表"""
        self._load_action_list() 