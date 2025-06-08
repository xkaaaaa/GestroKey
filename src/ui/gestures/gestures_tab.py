import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QTabWidget,
    QDoubleSpinBox,
    QTabWidget,
)

try:
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
    from ui.gestures.drawing_widget import GestureDrawingWidget
    from ui.settings.settings import get_settings
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
    from ui.gestures.drawing_widget import GestureDrawingWidget
    from ui.settings.settings import get_settings


class GesturesPage(QWidget):
    """手势管理页面 - 重新设计版本
    
    功能：
    1. 左侧显示手势列表
    2. 右侧显示手势编辑器
    3. 支持添加、编辑、删除、重置手势
    4. 清晰的状态管理和错误处理
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GesturesPage")
        
        # 获取手势库实例
        self.gesture_library = get_gesture_library()
        
        # 当前选中的手势
        self.current_gesture_name = None
        
        # 当前绘制的路径
        self.current_path = None
        
        # 初始化UI
        self._init_ui()
        
        # 加载手势列表
        self._load_gesture_list()
        
        # 初始化按钮状态
        self._update_button_states()
        
        self.logger.info("手势管理页面初始化完成")

    def showEvent(self, event):
        """页面显示时刷新按钮状态"""
        super().showEvent(event)
        self._update_button_states()

    def _init_ui(self):
        """初始化用户界面"""
        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # 左侧：手势列表
        left_panel = self._create_gesture_list_panel()
        splitter.addWidget(left_panel)

        # 右侧：手势编辑器
        right_panel = self._create_gesture_editor_panel()
        splitter.addWidget(right_panel)

        # 设置分割器比例
        splitter.setSizes([350, 450])
        main_layout.addWidget(splitter)

    def _create_gesture_list_panel(self):
        """创建手势列表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 标题
        title = QLabel("手势库")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 手势列表
        self.gesture_list = QListWidget()
        self.gesture_list.setMinimumWidth(300)
        self.gesture_list.itemClicked.connect(self._on_gesture_selected)
        layout.addWidget(self.gesture_list)

        # 按钮区域
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)

        self.btn_add = QPushButton("添加新手势")
        self.btn_add.clicked.connect(self._add_new_gesture)
        button_layout.addWidget(self.btn_add)

        self.btn_delete = QPushButton("删除手势")
        self.btn_delete.clicked.connect(self._delete_gesture)
        self.btn_delete.setEnabled(False)
        button_layout.addWidget(self.btn_delete)

        self.btn_reset = QPushButton("重置为默认")
        self.btn_reset.clicked.connect(self._reset_gestures)
        button_layout.addWidget(self.btn_reset)

        self.btn_save = QPushButton("保存手势库")
        self.btn_save.clicked.connect(self._save_gestures)
        button_layout.addWidget(self.btn_save)

        layout.addLayout(button_layout)
        return panel

    def _create_gesture_editor_panel(self):
        """创建手势编辑器面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 标题
        title = QLabel("手势编辑器")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 编辑表单
        form_group = QGroupBox("手势信息")
        form_layout = QFormLayout(form_group)

        # 手势名称
        self.edit_name = QLineEdit()
        self.edit_name.textChanged.connect(self._on_form_changed)
        form_layout.addRow("名称:", self.edit_name)

        # 快捷键
        self.edit_shortcut = QLineEdit()
        self.edit_shortcut.setPlaceholderText("例如: Ctrl+C")
        self.edit_shortcut.textChanged.connect(self._on_form_changed)
        form_layout.addRow("快捷键:", self.edit_shortcut)

        layout.addWidget(form_group)

        # 路径绘制组件
        path_group = QGroupBox("手势路径绘制")
        path_layout = QVBoxLayout(path_group)
        
        self.drawing_widget = GestureDrawingWidget()
        self.drawing_widget.pathCompleted.connect(self._on_path_completed)
        path_layout.addWidget(self.drawing_widget)
        
        layout.addWidget(path_group)

        # 相似度阈值设置
        threshold_group = QGroupBox("相似度设置")
        threshold_layout = QFormLayout(threshold_group)
        
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.0, 1.0)
        self.threshold_spinbox.setSingleStep(0.05)
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setValue(0.7)
        self.threshold_spinbox.valueChanged.connect(self._on_threshold_changed)
        threshold_layout.addRow("相似度阈值:", self.threshold_spinbox)
        
        layout.addWidget(threshold_group)

        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_new = QPushButton("新建")
        self.btn_new.clicked.connect(self._new_gesture)
        button_layout.addWidget(self.btn_new)

        self.btn_clear_form = QPushButton("清空表单")
        self.btn_clear_form.clicked.connect(self._clear_editor)
        button_layout.addWidget(self.btn_clear_form)

        self.btn_undo = QPushButton("撤销")
        self.btn_undo.clicked.connect(self._undo_changes)
        self.btn_undo.setEnabled(False)
        button_layout.addWidget(self.btn_undo)

        layout.addLayout(button_layout)

        # 初始化相似度阈值
        self._load_similarity_threshold()

        return panel

    def _load_gesture_list(self):
        """加载手势列表"""
        self.gesture_list.clear()
        gestures = self.gesture_library.get_all_gestures()

        # 按ID排序显示
        sorted_gestures = sorted(gestures.items(), key=lambda x: x[1].get('id', 0))

        for name, data in sorted_gestures:
            gesture_id = data.get('id', 0)
            direction = data.get('direction', '')
            path = data.get('path')
            action = data.get('action', {})
            shortcut = action.get('value', '')
            
            # 确定显示的手势类型
            if path:
                gesture_type = f"路径({len(path.get('points', []))}点)"
            else:
                gesture_type = f"方向({direction})"
            
            # 创建列表项，显示编号
            item_text = f"{gesture_id}. {name} ({gesture_type}) → {shortcut}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, name)  # 存储手势名称
            self.gesture_list.addItem(item)

        self.logger.debug(f"已加载 {len(gestures)} 个手势")

    def _on_gesture_selected(self, item):
        """手势被选中时的处理"""
        gesture_name = item.data(Qt.ItemDataRole.UserRole)
        if not gesture_name:
            return

        self.logger.info(f"选择手势: {gesture_name}")
        
        # 如果有未保存的更改，询问是否继续
        if self._has_form_changes():
            self.logger.info("检测到未保存的更改，显示确认对话框")
            result = QMessageBox.question(
                self, "确认", "当前有未保存的更改，是否继续切换？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.No:
                return  # 取消切换
        else:
            self.logger.info("没有检测到未保存的更改，直接切换")

        # 加载手势数据到编辑器
        self._load_gesture_to_editor(gesture_name)

    def _load_gesture_to_editor(self, gesture_name):
        """将手势数据加载到编辑器"""
        gesture_data = self.gesture_library.get_gesture(gesture_name)
        if not gesture_data:
            self.logger.error(f"找不到手势: {gesture_name}")
            return

        self.logger.debug(f"开始加载手势到编辑器: {gesture_name}")

        # 暂时断开信号连接，避免在加载数据时触发变更检测
        self.edit_name.textChanged.disconnect()
        self.edit_shortcut.textChanged.disconnect()

        try:
            # 更新状态
            self.current_gesture_name = gesture_name

            # 填充表单
            self.edit_name.setText(gesture_name)
            
            # 加载路径（新格式）
            path = gesture_data.get('path')
            if path:
                # 深度复制路径数据，避免引用问题
                import copy
                self.current_path = copy.deepcopy(path)
                self.drawing_widget.load_path(self.current_path)
            else:
                self.drawing_widget.clear_drawing()
                self.current_path = None

            action = gesture_data.get('action', {})
            shortcut = action.get('value', '')
            self.edit_shortcut.setText(shortcut)

        finally:
            # 重新连接信号
            self.edit_name.textChanged.connect(self._on_form_changed)
            self.edit_shortcut.textChanged.connect(self._on_form_changed)

        # 更新按钮状态
        self._update_button_states()
        self.btn_delete.setEnabled(True)

        self.logger.debug(f"已加载手势到编辑器: {gesture_name}")

    def _has_form_changes(self):
        """检查当前表单是否有未保存的更改"""
        if not self.current_gesture_name:
            # 新手势，检查表单是否为空
            name = self.edit_name.text().strip()
            shortcut = self.edit_shortcut.text().strip()
            
            # 只有当名称或快捷键不为空，或者有路径时，才认为有更改
            # 方向的默认值不算作更改
            result = bool(name or shortcut or self.current_path)
            self.logger.info(f"新手势变更检测: 名称='{name}', 快捷键='{shortcut}', 路径={bool(self.current_path)}, 结果={result}")
            return result
        
        # 现有手势，比较表单内容与手势库中的数据
        current_gesture = self.gesture_library.get_gesture(self.current_gesture_name)
        if not current_gesture:
            self.logger.debug(f"找不到当前手势: {self.current_gesture_name}")
            return False
        
        # 获取表单当前值
        form_name = self.edit_name.text().strip()
        form_shortcut = self.edit_shortcut.text().strip()
        
        # 获取手势库中的值
        saved_name = self.current_gesture_name
        saved_action = current_gesture.get('action', {})
        saved_shortcut = saved_action.get('value', '')
        
        # 检查路径是否有变化（深度比较）
        saved_path = current_gesture.get('path')
        path_changed = self._paths_different(self.current_path, saved_path)
        
        # 详细比较每个字段
        name_changed = form_name != saved_name
        shortcut_changed = form_shortcut != saved_shortcut
        
        # 比较是否有差异
        has_changes = (name_changed or shortcut_changed or path_changed)
        
        self.logger.info(f"现有手势变更检测 '{self.current_gesture_name}':")
        self.logger.info(f"  名称: '{form_name}' vs '{saved_name}' = {name_changed}")
        self.logger.info(f"  快捷键: '{form_shortcut}' vs '{saved_shortcut}' = {shortcut_changed}")
        self.logger.info(f"  路径变化: {path_changed}")
        self.logger.info(f"  最终结果: {has_changes}")
        
        return has_changes

    def _paths_different(self, path1, path2):
        """比较两个路径是否不同（深度比较）"""
        self.logger.debug(f"路径比较: path1={bool(path1)}, path2={bool(path2)}")
        
        # 如果都为空，则相同
        if not path1 and not path2:
            self.logger.debug("两个路径都为空，相同")
            return False
        
        # 如果一个为空一个不为空，则不同
        if bool(path1) != bool(path2):
            self.logger.debug("一个路径为空一个不为空，不同")
            return True
        
        # 都不为空，比较内容
        if path1 and path2:
            # 比较点数量
            points1 = path1.get('points', [])
            points2 = path2.get('points', [])
            self.logger.debug(f"点数量比较: {len(points1)} vs {len(points2)}")
            if len(points1) != len(points2):
                self.logger.debug("点数量不同")
                return True
            
            # 比较每个点
            for i, (p1, p2) in enumerate(zip(points1, points2)):
                if p1 != p2:
                    self.logger.debug(f"点{i}不同: {p1} vs {p2}")
                    return True
            
            # 比较连接数量
            conn1 = path1.get('connections', [])
            conn2 = path2.get('connections', [])
            self.logger.debug(f"连接数量比较: {len(conn1)} vs {len(conn2)}")
            if len(conn1) != len(conn2):
                self.logger.debug("连接数量不同")
                return True
            
            # 比较每个连接
            for i, (c1, c2) in enumerate(zip(conn1, conn2)):
                if c1 != c2:
                    self.logger.debug(f"连接{i}不同: {c1} vs {c2}")
                    return True
        
        self.logger.debug("路径完全相同")
        return False

    def _on_form_changed(self):
        """表单内容发生变化"""
        # 自动应用修改到手势库（不保存到文件）
        self._auto_apply_changes()
        # 更新按钮状态
        self._update_button_states()

    def _auto_apply_changes(self):
        """自动应用表单变更到手势库（不保存到文件）"""
        name = self.edit_name.text().strip()
        shortcut = self.edit_shortcut.text().strip()
        
        # 验证基本输入
        if not name or not shortcut or not self.current_path:
            return
            
        try:
            if not self.current_gesture_name:
                # 新手势：检查名称是否已存在
                if self.gesture_library.get_gesture(name):
                    return  # 名称已存在，不自动创建
                
                # 创建新手势
                success = self.gesture_library.add_gesture(name, self.current_path, 'shortcut', shortcut)
                if success:
                    self.current_gesture_name = name
                    # 刷新列表显示
                    self._load_gesture_list()
                    self._select_gesture_in_list(name)
                    self.logger.info(f"自动创建新手势: {name}")
                    # 更新按钮状态（新手势创建后手势库有变更）
                    self._update_button_states()
            else:
                # 现有手势：更新
                current_gesture = self.gesture_library.get_gesture(self.current_gesture_name)
                if not current_gesture:
                    return
                    
                gesture_id = current_gesture.get('id')
                if gesture_id is None:
                    return
                    
                # 使用当前路径或保持原有路径
                gesture_data = self.current_path if self.current_path else current_gesture.get('path')
                
                # 自动更新手势（不保存到文件）
                self.gesture_library.update_gesture_by_id(
                    gesture_id, name, gesture_data, 'shortcut', shortcut
                )
                
                # 更新当前手势名称
                old_name = self.current_gesture_name
                self.current_gesture_name = name
                
                # 刷新列表显示（无论名称是否变化都要刷新，因为其他信息可能变化）
                self._load_gesture_list()
                self._select_gesture_in_list(name)
                
                self.logger.info(f"自动更新手势: {old_name} -> {name}")
                # 更新按钮状态（手势更新后手势库有变更）
                self._update_button_states()
                    
        except Exception as e:
            self.logger.error(f"自动应用变更时出错: {e}")

    def _update_button_states(self):
        """更新按钮状态"""
        has_form_changes = self._has_form_changes()
        has_library_changes = self.gesture_library.has_changes()
        
        # 撤销按钮：有表单变更时启用
        self.btn_undo.setEnabled(has_form_changes)
        
        # 保存手势库按钮：有手势库变更时启用
        self.btn_save.setEnabled(has_library_changes)

    def _new_gesture(self):
        """创建新手势"""
        # 如果有未保存的更改，询问是否继续
        if self._has_form_changes():
            result = QMessageBox.question(
                self, "确认", "当前有未保存的更改，是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.No:
                return

        # 清空编辑器
        self._clear_editor()
        
        # 生成新手势名称
        base_name = "新手势"
        counter = 1
        while self.gesture_library.get_gesture(f"{base_name}_{counter}"):
            counter += 1
        
        new_name = f"{base_name}_{counter}"
        self.edit_name.setText(new_name)
        self.edit_shortcut.setText("Ctrl+C")

        # 设置状态
        self.current_gesture_name = None
        self._update_button_states()
        
        self.logger.debug(f"开始创建新手势: {new_name}")



    def _select_gesture_in_list(self, name):
        """在列表中选中指定手势"""
        for i in range(self.gesture_list.count()):
            item = self.gesture_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == name:
                self.gesture_list.setCurrentItem(item)
                break

    def _undo_changes(self):
        """撤销当前的修改"""
        if self.current_gesture_name:
            # 重新加载当前手势数据，撤销所有修改
            self._load_gesture_to_editor(self.current_gesture_name)
        else:
            # 清空编辑器
            self._clear_editor()

    def _clear_editor(self):
        """清空编辑器"""
        self.edit_name.clear()
        self.edit_shortcut.clear()
        
        # 清空路径
        self.drawing_widget.clear_drawing()
        self.current_path = None
        
        self.current_gesture_name = None
        self.btn_delete.setEnabled(False)
        self._update_button_states()

    def _add_new_gesture(self):
        """添加新手势（快捷方式）"""
        self._new_gesture()

    def _delete_gesture(self):
        """删除当前手势"""
        if not self.current_gesture_name:
            return

        result = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除手势 '{self.current_gesture_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            try:
                success = self.gesture_library.remove_gesture(self.current_gesture_name)
                if success:
                    self.logger.info(f"已删除手势: {self.current_gesture_name}")
                    self._clear_editor()
                    self._load_gesture_list()
                    self._update_button_states()  # 更新按钮状态
                    QMessageBox.information(self, "成功", "手势已删除")
                else:
                    QMessageBox.critical(self, "错误", "删除手势失败")
            except Exception as e:
                self.logger.error(f"删除手势时出错: {e}")
                QMessageBox.critical(self, "错误", f"删除手势时出错: {str(e)}")

    def _reset_gestures(self):
        """重置手势库"""
        result = QMessageBox.question(
            self, "确认重置", 
            "确定要重置手势库为默认设置吗？这将删除所有自定义手势。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if result == QMessageBox.StandardButton.Yes:
            try:
                success = self.gesture_library.reset_to_default()
                if success:
                    self._clear_editor()
                    self._load_gesture_list()
                    self._update_button_states()  # 更新按钮状态
                    QMessageBox.information(self, "成功", "手势库已重置为默认设置")
                    self.logger.info("手势库已重置为默认")
                else:
                    QMessageBox.critical(self, "错误", "重置手势库失败")
            except Exception as e:
                self.logger.error(f"重置手势库时出错: {e}")
                QMessageBox.critical(self, "错误", f"重置手势库时出错: {str(e)}")

    def _save_gestures(self):
        """保存手势库到文件"""
        try:
            success = self.gesture_library.save()
            if success:
                self._update_button_states()  # 更新按钮状态
                QMessageBox.information(self, "成功", "手势库已保存")
                self.logger.info("手势库已保存到文件")
            else:
                QMessageBox.critical(self, "错误", "保存手势库失败")
        except Exception as e:
            self.logger.error(f"保存手势库时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存手势库时出错: {str(e)}")

    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        form_has_changes = self._has_form_changes()
        library_has_changes = self.gesture_library.has_changes()
        result = form_has_changes or library_has_changes
        self.logger.debug(f"手势页面检查未保存更改: 表单变化={form_has_changes}, 库有变更={library_has_changes}, 结果={result}")
        return result
    
    def _on_path_completed(self, path):
        """处理路径绘制完成事件"""
        import copy
        self.current_path = copy.deepcopy(path)
        self._on_form_changed()  # 触发表单变更检测
        self.logger.info(f"路径绘制完成，关键点数: {len(path.get('points', []))}")
    
    def _on_threshold_changed(self, value):
        """处理相似度阈值变更"""
        try:
            settings = get_settings()
            settings.set("gesture.similarity_threshold", value)
            self.logger.info(f"相似度阈值已更新为: {value}")
        except Exception as e:
            self.logger.error(f"保存相似度阈值失败: {e}")
    
    def _load_similarity_threshold(self):
        """加载相似度阈值设置"""
        try:
            settings = get_settings()
            threshold = settings.get("gesture.similarity_threshold", 0.70)
            self.threshold_spinbox.setValue(threshold)
        except Exception as e:
            self.logger.error(f"加载相似度阈值失败: {e}")
            self.threshold_spinbox.setValue(0.70)


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    widget = GesturesPage()
    widget.show()
    sys.exit(app.exec()) 