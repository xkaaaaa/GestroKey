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
)

try:
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library


class GesturesPage(QWidget):
    """手势管理页面 - 重新设计版本
    
    功能：
    1. 左侧显示手势列表
    2. 右侧显示手势编辑器
    3. 支持添加、编辑、删除、重置手势
    4. 清晰的状态管理和错误处理
    """

    # 支持的方向
    DIRECTIONS = [
        "上", "下", "左", "右",
        "上-下", "下-上", "左-右", "右-左",
        "上-左", "上-右", "下-左", "下-右",
        "左-上", "左-下", "右-上", "右-下",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GesturesPage")
        self.gesture_library = get_gesture_library()
        
        # 状态变量
        self.current_gesture_name = None  # 当前选中的手势名称
        self.is_editing = False  # 是否正在编辑状态
        
        self._init_ui()
        self._load_gesture_list()
        self.logger.info("手势管理页面初始化完成")

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

        # 手势方向
        self.combo_direction = QComboBox()
        self.combo_direction.addItems(self.DIRECTIONS)
        self.combo_direction.currentTextChanged.connect(self._on_form_changed)
        form_layout.addRow("方向:", self.combo_direction)

        # 快捷键
        self.edit_shortcut = QLineEdit()
        self.edit_shortcut.setPlaceholderText("例如: Ctrl+C")
        self.edit_shortcut.textChanged.connect(self._on_form_changed)
        form_layout.addRow("快捷键:", self.edit_shortcut)

        layout.addWidget(form_group)

        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_new = QPushButton("新建")
        self.btn_new.clicked.connect(self._new_gesture)
        button_layout.addWidget(self.btn_new)

        self.btn_save_current = QPushButton("保存修改")
        self.btn_save_current.clicked.connect(self._save_current_gesture)
        self.btn_save_current.setEnabled(False)
        button_layout.addWidget(self.btn_save_current)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self._cancel_edit)
        self.btn_cancel.setEnabled(False)
        button_layout.addWidget(self.btn_cancel)

        layout.addLayout(button_layout)
        layout.addStretch()

        return panel

    def _load_gesture_list(self):
        """加载手势列表"""
        self.gesture_list.clear()
        gestures = self.gesture_library.get_all_gestures()

        # 按ID排序显示
        sorted_gestures = sorted(gestures.items(), key=lambda x: x[1].get('id', 0))

        for name, data in sorted_gestures:
            direction = data.get('direction', '')
            action = data.get('action', {})
            shortcut = action.get('value', '')
            
            # 创建列表项
            item_text = f"{name} ({direction}) → {shortcut}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, name)  # 存储手势名称
            self.gesture_list.addItem(item)

        self.logger.debug(f"已加载 {len(gestures)} 个手势")

    def _on_gesture_selected(self, item):
        """手势被选中时的处理"""
        gesture_name = item.data(Qt.ItemDataRole.UserRole)
        if not gesture_name:
            return

        # 如果正在编辑，询问是否保存
        if self.is_editing:
            result = QMessageBox.question(
                self, "确认", "当前有未保存的更改，是否先保存？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if result == QMessageBox.StandardButton.Yes:
                if not self._save_current_gesture():
                    return  # 保存失败，不切换
            elif result == QMessageBox.StandardButton.Cancel:
                return  # 取消切换

        # 加载手势数据到编辑器
        self._load_gesture_to_editor(gesture_name)

    def _load_gesture_to_editor(self, gesture_name):
        """将手势数据加载到编辑器"""
        gesture_data = self.gesture_library.get_gesture(gesture_name)
        if not gesture_data:
            self.logger.error(f"找不到手势: {gesture_name}")
            return

        # 更新状态
        self.current_gesture_name = gesture_name
        self.is_editing = False

        # 填充表单
        self.edit_name.setText(gesture_name)
        
        direction = gesture_data.get('direction', '')
        if direction in self.DIRECTIONS:
            self.combo_direction.setCurrentText(direction)
        else:
            self.combo_direction.setCurrentIndex(0)

        action = gesture_data.get('action', {})
        shortcut = action.get('value', '')
        self.edit_shortcut.setText(shortcut)

        # 更新按钮状态
        self._update_button_states()
        self.btn_delete.setEnabled(True)

        self.logger.debug(f"已加载手势到编辑器: {gesture_name}")

    def _on_form_changed(self):
        """表单内容发生变化"""
        if self.current_gesture_name and not self.is_editing:
            self.is_editing = True
            self._update_button_states()

    def _update_button_states(self):
        """更新按钮状态"""
        has_selection = self.current_gesture_name is not None
        
        self.btn_save_current.setEnabled(self.is_editing and has_selection)
        self.btn_cancel.setEnabled(self.is_editing)

    def _new_gesture(self):
        """创建新手势"""
        # 如果正在编辑，询问是否保存
        if self.is_editing:
            result = QMessageBox.question(
                self, "确认", "当前有未保存的更改，是否先保存？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if result == QMessageBox.StandardButton.Yes:
                if not self._save_current_gesture():
                    return
            elif result == QMessageBox.StandardButton.Cancel:
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
        self.combo_direction.setCurrentIndex(0)
        self.edit_shortcut.setText("Ctrl+C")

        # 设置状态
        self.current_gesture_name = None
        self.is_editing = True
        self._update_button_states()
        
        self.logger.debug(f"开始创建新手势: {new_name}")

    def _save_current_gesture(self):
        """保存当前手势"""
        name = self.edit_name.text().strip()
        direction = self.combo_direction.currentText()
        shortcut = self.edit_shortcut.text().strip()

        # 验证输入
        if not name:
            QMessageBox.warning(self, "错误", "手势名称不能为空")
            return False

        if not shortcut:
            QMessageBox.warning(self, "错误", "快捷键不能为空")
            return False

        try:
            # 如果是新手势或改名了
            if not self.current_gesture_name or name != self.current_gesture_name:
                # 检查名称是否已存在
                if self.gesture_library.get_gesture(name):
                    QMessageBox.warning(self, "错误", f"手势名称 '{name}' 已存在")
                    return False

                # 如果是改名，删除旧的
                if self.current_gesture_name:
                    self.gesture_library.remove_gesture(self.current_gesture_name)

            # 添加或更新手势
            success = self.gesture_library.add_gesture(name, direction, 'shortcut', shortcut)
            
            if success:
                # 更新状态
                self.current_gesture_name = name
                self.is_editing = False
                
                # 刷新列表
                self._load_gesture_list()
                
                # 重新选中当前手势
                self._select_gesture_in_list(name)
                
                self._update_button_states()
                QMessageBox.information(self, "成功", "手势已保存")
                self.logger.info(f"手势已保存: {name}")
                return True
            else:
                QMessageBox.critical(self, "错误", "保存手势失败")
                return False

        except Exception as e:
            self.logger.error(f"保存手势时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存手势时出错: {str(e)}")
            return False

    def _select_gesture_in_list(self, name):
        """在列表中选中指定手势"""
        for i in range(self.gesture_list.count()):
            item = self.gesture_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == name:
                self.gesture_list.setCurrentItem(item)
                break

    def _cancel_edit(self):
        """取消编辑"""
        if self.current_gesture_name:
            # 重新加载当前手势数据
            self._load_gesture_to_editor(self.current_gesture_name)
        else:
            # 清空编辑器
            self._clear_editor()

    def _clear_editor(self):
        """清空编辑器"""
        self.edit_name.clear()
        self.combo_direction.setCurrentIndex(0)
        self.edit_shortcut.clear()
        
        self.current_gesture_name = None
        self.is_editing = False
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
                    QMessageBox.information(self, "成功", "手势库已重置为默认设置")
                    self.logger.info("手势库已重置为默认")
                else:
                    QMessageBox.critical(self, "错误", "重置手势库失败")
            except Exception as e:
                self.logger.error(f"重置手势库时出错: {e}")
                QMessageBox.critical(self, "错误", f"重置手势库时出错: {str(e)}")

    def _save_gestures(self):
        """保存手势库到文件"""
        # 如果正在编辑，先询问是否保存当前修改
        if self.is_editing:
            result = QMessageBox.question(
                self, "确认", "当前有未保存的更改，是否先保存？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if result == QMessageBox.StandardButton.Yes:
                if not self._save_current_gesture():
                    return
            elif result == QMessageBox.StandardButton.Cancel:
                return

        try:
            success = self.gesture_library.save()
            if success:
                QMessageBox.information(self, "成功", "手势库已保存")
                self.logger.info("手势库已保存到文件")
            else:
                QMessageBox.critical(self, "错误", "保存手势库失败")
        except Exception as e:
            self.logger.error(f"保存手势库时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存手势库时出错: {str(e)}")

    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        return self.is_editing or self.gesture_library.has_changes()


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    widget = GesturesPage()
    widget.show()
    sys.exit(app.exec()) 