from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QLineEdit, QGroupBox, QMessageBox, QComboBox
)

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library


class GestureMappingsTab(QWidget):
    """手势映射管理选项卡"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GestureMappingsTab")
        self.gesture_library = get_gesture_library()
        
        self.current_mapping_key = None
        
        self.initUI()
        self._load_mapping_list()
        
    def initUI(self):
        """初始化用户界面"""
        layout = QHBoxLayout(self)
        
        # 左侧映射列表
        left_panel = self._create_mapping_list_panel()
        layout.addWidget(left_panel, 1)
        
        # 右侧映射编辑器
        right_panel = self._create_mapping_editor_panel()
        layout.addWidget(right_panel, 2)
        
    def _create_mapping_list_panel(self):
        """创建映射列表面板"""
        panel = QGroupBox("手势映射列表")
        layout = QVBoxLayout(panel)
        
        # 映射列表
        self.mapping_list = QListWidget()
        self.mapping_list.itemClicked.connect(self._on_mapping_selected)
        layout.addWidget(self.mapping_list)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.btn_add_mapping = QPushButton("添加映射")
        self.btn_add_mapping.clicked.connect(self._add_new_mapping)
        button_layout.addWidget(self.btn_add_mapping)
        
        self.btn_delete_mapping = QPushButton("删除映射")
        self.btn_delete_mapping.clicked.connect(self._delete_mapping)
        self.btn_delete_mapping.setEnabled(False)
        button_layout.addWidget(self.btn_delete_mapping)
        
        layout.addLayout(button_layout)
        
        return panel
        
    def _create_mapping_editor_panel(self):
        """创建映射编辑器面板"""
        panel = QGroupBox("映射编辑器")
        layout = QVBoxLayout(panel)
        
        # 基本信息编辑
        info_layout = QVBoxLayout()
        
        # 手势名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("手势名称:"))
        self.edit_name = QLineEdit()
        self.edit_name.textChanged.connect(self._on_form_changed)
        name_layout.addWidget(self.edit_name)
        info_layout.addLayout(name_layout)
        
        # 触发路径选择
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("触发路径:"))
        self.combo_trigger_path = QComboBox()
        self.combo_trigger_path.currentIndexChanged.connect(self._on_form_changed)
        path_layout.addWidget(self.combo_trigger_path)
        info_layout.addLayout(path_layout)
        
        # 执行操作选择
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("执行操作:"))
        self.combo_execute_action = QComboBox()
        self.combo_execute_action.currentIndexChanged.connect(self._on_form_changed)
        action_layout.addWidget(self.combo_execute_action)
        info_layout.addLayout(action_layout)
        
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
        
    def _load_mapping_list(self):
        """加载映射列表"""
        self.mapping_list.clear()
        
        # 同时加载下拉框选项
        self._load_combo_options()
        
        gesture_mappings = self.gesture_library.gesture_mappings
        
        # 按ID排序显示
        sorted_mappings = sorted(gesture_mappings.items(), key=lambda x: x[1].get('id', 0))
        
        for mapping_key, mapping_data in sorted_mappings:
            mapping_id = mapping_data.get('id', 0)
            mapping_name = mapping_data.get('name', f'手势{mapping_id}')
            
            # 获取触发路径名称
            trigger_path_id = mapping_data.get('trigger_path_id')
            trigger_path_name = self._get_path_name_by_id(trigger_path_id)
            
            # 获取执行操作名称
            execute_action_id = mapping_data.get('execute_action_id')
            execute_action_name = self._get_action_name_by_id(execute_action_id)
            
            item_text = f"{mapping_id}. {mapping_name} ({trigger_path_name} → {execute_action_name})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, mapping_key)
            self.mapping_list.addItem(item)
            
        self.logger.debug(f"已加载 {len(gesture_mappings)} 个手势映射")
        
    def _load_combo_options(self):
        """加载下拉框选项"""
        # 加载触发路径选项
        self.combo_trigger_path.clear()
        self.combo_trigger_path.addItem("请选择触发路径", None)
        
        trigger_paths = self.gesture_library.trigger_paths
        sorted_paths = sorted(trigger_paths.items(), key=lambda x: x[1].get('id', 0))
        
        for path_key, path_data in sorted_paths:
            path_id = path_data.get('id')
            path_name = path_data.get('name', f'路径{path_id}')
            self.combo_trigger_path.addItem(f"{path_id}. {path_name}", path_id)
            
        # 加载执行操作选项
        self.combo_execute_action.clear()
        self.combo_execute_action.addItem("请选择执行操作", None)
        
        execute_actions = self.gesture_library.execute_actions
        sorted_actions = sorted(execute_actions.items(), key=lambda x: x[1].get('id', 0))
        
        for action_key, action_data in sorted_actions:
            action_id = action_data.get('id')
            action_name = action_data.get('name', f'操作{action_id}')
            action_value = action_data.get('value', '')
            display_text = f"{action_id}. {action_name} ({action_value})"
            self.combo_execute_action.addItem(display_text, action_id)
            
    def _get_path_name_by_id(self, path_id):
        """根据ID获取路径名称"""
        for path_data in self.gesture_library.trigger_paths.values():
            if path_data.get('id') == path_id:
                return path_data.get('name', f'路径{path_id}')
        return f'路径{path_id}(未找到)'
        
    def _get_action_name_by_id(self, action_id):
        """根据ID获取操作名称"""
        for action_data in self.gesture_library.execute_actions.values():
            if action_data.get('id') == action_id:
                return action_data.get('name', f'操作{action_id}')
        return f'操作{action_id}(未找到)'
        
    def _on_mapping_selected(self, item):
        """映射选择事件"""
        mapping_key = item.data(Qt.ItemDataRole.UserRole)
        self._load_mapping_to_editor(mapping_key)
        
    def _load_mapping_to_editor(self, mapping_key):
        """将映射数据加载到编辑器"""
        mapping_data = self.gesture_library.gesture_mappings.get(mapping_key)
        if not mapping_data:
            self.logger.error(f"找不到映射: {mapping_key}")
            return
            
        self.logger.debug(f"开始加载映射到编辑器: {mapping_key}")
        
        # 暂时断开信号连接
        self.edit_name.textChanged.disconnect()
        self.combo_trigger_path.currentIndexChanged.disconnect()
        self.combo_execute_action.currentIndexChanged.disconnect()
        
        try:
            # 更新状态
            self.current_mapping_key = mapping_key
            
            # 填充表单
            mapping_name = mapping_data.get('name', '')
            trigger_path_id = mapping_data.get('trigger_path_id')
            execute_action_id = mapping_data.get('execute_action_id')
            
            self.edit_name.setText(mapping_name)
            
            # 设置触发路径下拉框
            for i in range(self.combo_trigger_path.count()):
                if self.combo_trigger_path.itemData(i) == trigger_path_id:
                    self.combo_trigger_path.setCurrentIndex(i)
                    break
                    
            # 设置执行操作下拉框
            for i in range(self.combo_execute_action.count()):
                if self.combo_execute_action.itemData(i) == execute_action_id:
                    self.combo_execute_action.setCurrentIndex(i)
                    break
                    
        finally:
            # 重新连接信号
            self.edit_name.textChanged.connect(self._on_form_changed)
            self.combo_trigger_path.currentIndexChanged.connect(self._on_form_changed)
            self.combo_execute_action.currentIndexChanged.connect(self._on_form_changed)
            
        # 更新按钮状态
        self._update_button_states()
        
        self.logger.debug(f"已加载映射到编辑器: {mapping_key}")
        
    def _on_form_changed(self):
        """表单内容变化事件"""
        self._auto_save_changes()
        
    def _auto_save_changes(self):
        """自动保存变更到手势库变量中"""
        if not self.current_mapping_key:
            return
            
        name = self.edit_name.text().strip()
        trigger_path_id = self.combo_trigger_path.currentData()
        execute_action_id = self.combo_execute_action.currentData()
        
        if not name or trigger_path_id is None or execute_action_id is None:
            return
            
        try:
            # 自动更新到手势库变量中
            mapping_data = self.gesture_library.gesture_mappings[self.current_mapping_key]
            mapping_data['name'] = name
            mapping_data['trigger_path_id'] = trigger_path_id
            mapping_data['execute_action_id'] = execute_action_id
            
            # 刷新列表显示
            self._load_mapping_list()
            self._select_mapping_in_list(self.current_mapping_key)
            
        except Exception as e:
            self.logger.error(f"自动保存映射时出错: {e}")
        
    def _update_button_states(self):
        """更新按钮状态"""
        self.btn_delete_mapping.setEnabled(self.current_mapping_key is not None)
        
    def _add_new_mapping(self):
        """添加新映射"""
        # 刷新下拉框选项（可能有新的路径或操作）
        self._load_combo_options()
        self._clear_form()
        self.logger.info("开始添加新映射")
        
    def _select_mapping_in_list(self, mapping_key):
        """在列表中选择指定映射"""
        for i in range(self.mapping_list.count()):
            item = self.mapping_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == mapping_key:
                self.mapping_list.setCurrentItem(item)
                break
                
    def _delete_mapping(self):
        """删除映射"""
        if not self.current_mapping_key:
            return
            
        mapping_data = self.gesture_library.gesture_mappings.get(self.current_mapping_key)
        if not mapping_data:
            return
            
        mapping_name = mapping_data.get('name', '未命名映射')
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除手势映射 '{mapping_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                del self.gesture_library.gesture_mappings[self.current_mapping_key]
                self.logger.info(f"删除映射: {mapping_name}")
                
                # 清空编辑器
                self._clear_form()
                
                # 刷新列表
                self._load_mapping_list()
                
                QMessageBox.information(self, "成功", "映射已删除")
                
            except Exception as e:
                self.logger.error(f"删除映射时出错: {e}")
                QMessageBox.critical(self, "错误", f"删除映射失败: {str(e)}")
        
    def _clear_form(self):
        """清空表单"""
        self.current_mapping_key = None
        self.edit_name.setText("")
        self.combo_trigger_path.setCurrentIndex(0)
        self.combo_execute_action.setCurrentIndex(0)
        
        # 更新按钮状态
        self.btn_delete_mapping.setEnabled(False)
        
        self.logger.info("已清空表单")
                
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        return False  # 新架构中变更实时保存，无未保存状态
        
    def refresh_list(self):
        """刷新列表"""
        self._load_mapping_list() 