from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QLineEdit, QGroupBox, QMessageBox, QFrame
)

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library


class TriggerPathsTab(QWidget):
    """触发路径管理选项卡"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("TriggerPathsTab")
        self.gesture_library = get_gesture_library()
        
        self.current_path_key = None
        self.current_path = None
        
        self.initUI()
        self._load_path_list()
        
    def initUI(self):
        """初始化用户界面"""
        layout = QHBoxLayout(self)
        
        # 左侧路径列表
        left_panel = self._create_path_list_panel()
        layout.addWidget(left_panel, 1)
        
        # 右侧路径编辑器
        right_panel = self._create_path_editor_panel()
        layout.addWidget(right_panel, 2)
        
    def _create_path_list_panel(self):
        """创建路径列表面板"""
        panel = QGroupBox("触发路径列表")
        layout = QVBoxLayout(panel)
        
        # 路径列表
        self.path_list = QListWidget()
        self.path_list.itemClicked.connect(self._on_path_selected)
        layout.addWidget(self.path_list)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.btn_add_path = QPushButton("添加路径")
        self.btn_add_path.clicked.connect(self._add_new_path)
        button_layout.addWidget(self.btn_add_path)
        
        self.btn_delete_path = QPushButton("删除路径")
        self.btn_delete_path.clicked.connect(self._delete_path)
        self.btn_delete_path.setEnabled(False)
        button_layout.addWidget(self.btn_delete_path)
        
        layout.addLayout(button_layout)
        
        return panel
        
    def _create_path_editor_panel(self):
        """创建路径编辑器面板"""
        panel = QGroupBox("路径编辑器")
        layout = QVBoxLayout(panel)
        
        # 基本信息编辑
        info_layout = QVBoxLayout()
        
        # 路径名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("路径名称:"))
        self.edit_name = QLineEdit()
        self.edit_name.textChanged.connect(self._on_form_changed)
        name_layout.addWidget(self.edit_name)
        info_layout.addLayout(name_layout)
        
        layout.addLayout(info_layout)
        
        # 路径绘制区域（导入绘制控件）
        from ui.gestures.drawing_widget import GestureDrawingWidget
        self.drawing_widget = GestureDrawingWidget()
        self.drawing_widget.current_tool = "brush"
        self.drawing_widget.pathCompleted.connect(self._on_path_completed)
        self.drawing_widget.testSimilarity.connect(self._on_test_similarity)
        layout.addWidget(self.drawing_widget)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self._clear_form)
        button_layout.addWidget(self.btn_clear)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return panel
        
    def _load_path_list(self):
        """加载路径列表"""
        self.path_list.clear()
        trigger_paths = self.gesture_library.trigger_paths
        
        # 按ID排序显示
        sorted_paths = sorted(trigger_paths.items(), key=lambda x: x[1].get('id', 0))
        
        for path_key, path_data in sorted_paths:
            path_id = path_data.get('id', 0)
            path_name = path_data.get('name', f'路径{path_id}')
            path_points = path_data.get('path', {}).get('points', [])
            
            item_text = f"{path_id}. {path_name} ({len(path_points)}点)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, path_key)
            self.path_list.addItem(item)
            
        self.logger.debug(f"已加载 {len(trigger_paths)} 个触发路径")
        
    def _on_path_selected(self, item):
        """路径选择事件"""
        path_key = item.data(Qt.ItemDataRole.UserRole)
        self._load_path_to_editor(path_key)
        
    def _load_path_to_editor(self, path_key):
        """将路径数据加载到编辑器"""
        path_data = self.gesture_library.trigger_paths.get(path_key)
        if not path_data:
            self.logger.error(f"找不到路径: {path_key}")
            return
            
        self.logger.debug(f"开始加载路径到编辑器: {path_key}")
        
        # 暂时断开信号连接
        self.edit_name.textChanged.disconnect()
        
        try:
            # 更新状态
            self.current_path_key = path_key
            
            # 填充表单
            path_name = path_data.get('name', '')
            self.edit_name.setText(path_name)
            
            # 加载路径到绘制区域
            path = path_data.get('path')
            if path:
                import copy
                self.current_path = copy.deepcopy(path)
                self.drawing_widget.load_path(self.current_path)
            else:
                self.drawing_widget.clear_drawing()
                self.current_path = None
                
        finally:
            # 重新连接信号
            self.edit_name.textChanged.connect(self._on_form_changed)
            
        # 更新按钮状态
        self.btn_delete_path.setEnabled(True)
        
        self.logger.debug(f"已加载路径到编辑器: {path_key}")
        
    def _on_form_changed(self):
        """表单内容变化事件"""
        self._auto_save_changes()
        
    def _auto_save_changes(self):
        """自动保存变更到手势库变量中"""
        if not self.current_path_key:
            return
            
        name = self.edit_name.text().strip()
        if not name or not self.current_path:
            return
            
        try:
            # 自动更新到手势库变量中
            path_data = self.gesture_library.trigger_paths[self.current_path_key]
            path_data['name'] = name
            path_data['path'] = self.current_path
            
            # 刷新列表显示
            self._load_path_list()
            self._select_path_in_list(self.current_path_key)
            
        except Exception as e:
            self.logger.error(f"自动保存路径时出错: {e}")
        
    def _has_form_changes(self):
        """检查表单是否有未保存的更改"""
        if not self.current_path_key:
            # 新路径，检查表单是否为空
            name = self.edit_name.text().strip()
            return bool(name or self.current_path)
            
        # 现有路径，比较表单内容与原数据
        current_data = self.gesture_library.trigger_paths.get(self.current_path_key)
        if not current_data:
            return False
            
        form_name = self.edit_name.text().strip()
        saved_name = current_data.get('name', '')
        saved_path = current_data.get('path')
        
        name_changed = form_name != saved_name
        path_changed = self._paths_different(self.current_path, saved_path)
        
        return name_changed or path_changed
        
    def _paths_different(self, path1, path2):
        """比较两个路径是否不同"""
        if path1 is None and path2 is None:
            return False
        if path1 is None or path2 is None:
            return True
            
        import json
        try:
            return json.dumps(path1, sort_keys=True) != json.dumps(path2, sort_keys=True)
        except:
            return True
            
    def _on_path_completed(self, path):
        """处理路径绘制完成事件"""
        import copy
        self.current_path = copy.deepcopy(path)
        
        # 如果是新路径，自动创建
        if not self.current_path_key:
            self._create_new_path_from_drawing()
        else:
            # 现有路径，触发自动保存
            self._auto_save_changes()
            
        self.logger.info(f"路径绘制完成，关键点数: {len(path.get('points', []))}")
        
    def _create_new_path_from_drawing(self):
        """从绘制创建新路径"""
        if not self.current_path:
            return
            
        try:
            # 添加新路径
            path_id = self.gesture_library._get_next_path_id()
            path_key = f"path_{path_id}"
            default_name = f"路径{path_id}"
            
            self.gesture_library.trigger_paths[path_key] = {
                'id': path_id,
                'name': default_name,
                'path': self.current_path
            }
            
            self.current_path_key = path_key
            
            # 断开信号避免递归
            self.edit_name.textChanged.disconnect()
            self.edit_name.setText(default_name)
            self.edit_name.textChanged.connect(self._on_form_changed)
            
            # 刷新列表
            self._load_path_list()
            self._select_path_in_list(self.current_path_key)
            
            # 更新按钮状态
            self.btn_delete_path.setEnabled(True)
            
            self.logger.info(f"自动创建新路径: {default_name}, ID: {path_id}")
            
        except Exception as e:
            self.logger.error(f"自动创建路径时出错: {e}")
        
    def _add_new_path(self):
        """添加新路径"""
        self.current_path_key = None
        self.current_path = None
        
        # 清空表单
        self.edit_name.setText("")
        self.drawing_widget.clear_drawing()
        
        # 更新按钮状态
        self.btn_delete_path.setEnabled(False)
        
        self.logger.info("开始添加新路径")
        
    def _clear_form(self):
        """清空表单"""
        self.current_path_key = None
        self.current_path = None
        
        # 清空表单
        self.edit_name.setText("")
        self.drawing_widget.clear_drawing()
        
        # 更新按钮状态
        self.btn_delete_path.setEnabled(False)
        
        self.logger.info("已清空表单")
            
    def _select_path_in_list(self, path_key):
        """在列表中选择指定路径"""
        for i in range(self.path_list.count()):
            item = self.path_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == path_key:
                self.path_list.setCurrentItem(item)
                break
                
    def _delete_path(self):
        """删除路径"""
        if not self.current_path_key:
            return
            
        path_data = self.gesture_library.trigger_paths.get(self.current_path_key)
        if not path_data:
            return
            
        path_name = path_data.get('name', '未命名路径')
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除路径 '{path_name}' 吗？\n\n注意：删除路径可能会影响使用此路径的手势映射。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                del self.gesture_library.trigger_paths[self.current_path_key]
                self.logger.info(f"删除路径: {path_name}")
                
                # 清空编辑器
                self.current_path_key = None
                self.current_path = None
                self.edit_name.setText("")
                self.drawing_widget.clear_drawing()
                
                # 刷新列表
                self._load_path_list()
                
                # 更新按钮状态
                self.btn_delete_path.setEnabled(False)
                
                QMessageBox.information(self, "成功", "路径已删除")
                
            except Exception as e:
                self.logger.error(f"删除路径时出错: {e}")
                QMessageBox.critical(self, "错误", f"删除路径失败: {str(e)}")
                
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        return False  # 新架构中变更实时保存，无未保存状态
        
    def refresh_list(self):
        """刷新列表"""
        self._load_path_list()
        
    def _on_test_similarity(self):
        """处理测试相似度事件"""
        # 检查是否有当前编辑的路径
        if not self.current_path:
            QMessageBox.information(self, "提示", "请先选择或绘制一个路径")
            return
            
        try:
            # 使用原有的相似度测试对话框
            from ui.gestures.gestures_tab import SimilarityTestDialog
            
            # 传入当前编辑的路径作为参考路径
            dialog = SimilarityTestDialog(self.current_path, self)
            dialog.exec()
            
        except Exception as e:
            self.logger.error(f"打开相似度测试对话框时出错: {e}")
            QMessageBox.critical(self, "错误", f"无法打开相似度测试对话框: {str(e)}")
            
    def _show_similarity_results(self, test_path, results):
        """显示相似度测试结果"""
        # 这个方法已不再需要，因为使用原有的对话框
        pass 