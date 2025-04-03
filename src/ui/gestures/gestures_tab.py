import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QApplication, QLineEdit, QComboBox,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QGroupBox, QMessageBox, QPushButton, QAbstractItemView)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

try:
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
    from ui.components.button import AnimatedButton
except ImportError:
    sys.path.append('../../')
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
    from ui.components.button import AnimatedButton

class GesturesTab(QWidget):
    """手势管理选项卡，提供手势库管理功能"""
    
    # 定义方向选项
    DIRECTIONS = [
        "上", "下", "左", "右", 
        "上-下", "下-上", "左-右", "右-左",
        "上-左", "上-右", "下-左", "下-右",
        "左-上", "左-下", "右-上", "右-下"
    ]
    
    # 定义动作类型
    ACTION_TYPES = ["shortcut"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GesturesTab")
        self.gestures = get_gesture_library()
        
        self.initUI()
        self.logger.debug("手势管理选项卡初始化完成")
    
    def initUI(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        
        # 标题标签
        title_label = QLabel("手势管理")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建手势列表
        self.createGestureList(main_layout)
        
        # 创建手势编辑区域
        self.createGestureEditor(main_layout)
        
        # 创建操作按钮区域
        self.createActionButtons(main_layout)
        
        # 设置布局
        self.setLayout(main_layout)
        
        # 更新手势列表
        self.updateGestureList()
    
    def createGestureList(self, parent_layout):
        """创建手势列表区域"""
        # 手势列表组
        list_group = QGroupBox("当前手势库")
        list_layout = QVBoxLayout()
        
        # 创建表格
        self.gesture_table = QTableWidget()
        self.gesture_table.setColumnCount(4)
        self.gesture_table.setHorizontalHeaderLabels(["名称", "方向", "动作类型", "动作值"])
        self.gesture_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.gesture_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.gesture_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # 设置列宽
        header = self.gesture_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        # 选择行时触发编辑
        self.gesture_table.itemSelectionChanged.connect(self.onGestureSelected)
        
        list_layout.addWidget(self.gesture_table)
        list_group.setLayout(list_layout)
        parent_layout.addWidget(list_group)
    
    def createGestureEditor(self, parent_layout):
        """创建手势编辑区域"""
        # 手势编辑组
        edit_group = QGroupBox("编辑手势")
        edit_layout = QVBoxLayout()
        
        # 名称输入
        name_layout = QHBoxLayout()
        name_label = QLabel("名称:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        edit_layout.addLayout(name_layout)
        
        # 方向选择
        direction_layout = QHBoxLayout()
        direction_label = QLabel("方向:")
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(self.DIRECTIONS)
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.direction_combo)
        edit_layout.addLayout(direction_layout)
        
        # 动作类型选择
        action_type_layout = QHBoxLayout()
        action_type_label = QLabel("动作类型:")
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(self.ACTION_TYPES)
        action_type_layout.addWidget(action_type_label)
        action_type_layout.addWidget(self.action_type_combo)
        edit_layout.addLayout(action_type_layout)
        
        # 动作值输入
        action_value_layout = QHBoxLayout()
        action_value_label = QLabel("动作值:")
        self.action_value_input = QLineEdit()
        self.action_value_input.setPlaceholderText("例如: ctrl+c")
        action_value_layout.addWidget(action_value_label)
        action_value_layout.addWidget(self.action_value_input)
        edit_layout.addLayout(action_value_layout)
        
        # 编辑区域按钮
        edit_buttons_layout = QHBoxLayout()
        
        # 清空按钮 - 使用标准按钮
        self.clear_button = QPushButton("清空")
        self.clear_button.clicked.connect(self.clearEditor)
        
        # 保存按钮 - 使用自定义动画按钮
        self.save_gesture_button = AnimatedButton("保存手势", primary_color=[41, 128, 185])
        self.save_gesture_button.clicked.connect(self.saveGesture)
        
        edit_buttons_layout.addWidget(self.clear_button)
        edit_buttons_layout.addWidget(self.save_gesture_button)
        
        edit_layout.addLayout(edit_buttons_layout)
        edit_group.setLayout(edit_layout)
        parent_layout.addWidget(edit_group)
    
    def createActionButtons(self, parent_layout):
        """创建操作按钮区域"""
        buttons_layout = QHBoxLayout()
        
        # 删除按钮
        self.delete_button = AnimatedButton("删除选中手势", primary_color=[231, 76, 60])
        self.delete_button.clicked.connect(self.deleteGesture)
        
        # 重置按钮
        self.reset_button = AnimatedButton("重置为默认手势库", primary_color=[108, 117, 125])
        self.reset_button.clicked.connect(self.resetGestures)
        
        # 保存按钮
        self.save_button = AnimatedButton("保存手势库", primary_color=[41, 128, 185])
        self.save_button.clicked.connect(self.saveGestureLibrary)
        
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.save_button)
        
        parent_layout.addLayout(buttons_layout)
        parent_layout.addStretch()
    
    def updateGestureList(self):
        """更新手势列表"""
        self.gesture_table.setRowCount(0)  # 清空表格
        
        all_gestures = self.gestures.get_all_gestures()
        for i, (name, gesture) in enumerate(all_gestures.items()):
            self.gesture_table.insertRow(i)
            
            # 添加名称
            name_item = QTableWidgetItem(name)
            self.gesture_table.setItem(i, 0, name_item)
            
            # 添加方向
            direction_item = QTableWidgetItem(gesture.get("direction", ""))
            self.gesture_table.setItem(i, 1, direction_item)
            
            # 添加动作类型
            action = gesture.get("action", {})
            action_type_item = QTableWidgetItem(action.get("type", ""))
            self.gesture_table.setItem(i, 2, action_type_item)
            
            # 添加动作值
            action_value_item = QTableWidgetItem(action.get("value", ""))
            self.gesture_table.setItem(i, 3, action_value_item)
    
    def onGestureSelected(self):
        """当选择手势时，更新编辑区域"""
        selected_rows = self.gesture_table.selectionModel().selectedRows()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        
        # 获取选中行的数据
        name = self.gesture_table.item(row, 0).text()
        direction = self.gesture_table.item(row, 1).text()
        action_type = self.gesture_table.item(row, 2).text()
        action_value = self.gesture_table.item(row, 3).text()
        
        # 更新编辑区域
        self.name_input.setText(name)
        
        # 查找并设置方向下拉框
        direction_index = self.direction_combo.findText(direction)
        if direction_index != -1:
            self.direction_combo.setCurrentIndex(direction_index)
        
        # 查找并设置动作类型下拉框
        action_type_index = self.action_type_combo.findText(action_type)
        if action_type_index != -1:
            self.action_type_combo.setCurrentIndex(action_type_index)
        
        # 设置动作值
        self.action_value_input.setText(action_value)
    
    def clearEditor(self):
        """清空编辑区域"""
        self.name_input.clear()
        self.direction_combo.setCurrentIndex(0)
        self.action_type_combo.setCurrentIndex(0)
        self.action_value_input.clear()
        self.gesture_table.clearSelection()
    
    def saveGesture(self):
        """保存当前编辑的手势"""
        # 获取输入
        name = self.name_input.text().strip()
        direction = self.direction_combo.currentText()
        action_type = self.action_type_combo.currentText()
        action_value = self.action_value_input.text().strip()
        
        # 验证输入
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入手势名称")
            return
        
        if not action_value:
            QMessageBox.warning(self, "输入错误", "请输入动作值")
            return
        
        # 添加或更新手势
        self.gestures.add_gesture(name, direction, action_type, action_value)
        
        # 更新列表
        self.updateGestureList()
        
        # 清空编辑区域
        self.clearEditor()
        
        # 显示成功消息
        QMessageBox.information(self, "保存成功", f"手势 '{name}' 已保存")
    
    def deleteGesture(self):
        """删除选中的手势"""
        selected_rows = self.gesture_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "选择错误", "请先选择要删除的手势")
            return
            
        row = selected_rows[0].row()
        name = self.gesture_table.item(row, 0).text()
        
        # 确认对话框
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除手势 '{name}' 吗？",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 删除手势
            self.gestures.remove_gesture(name)
            
            # 更新列表
            self.updateGestureList()
            
            # 清空编辑区域
            self.clearEditor()
    
    def resetGestures(self):
        """重置为默认手势库"""
        # 确认对话框
        reply = QMessageBox.question(
            self, 
            "确认重置", 
            "确定要重置为默认手势库吗？这将删除所有自定义手势！",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 重置手势库
            self.gestures.reset_to_default()
            
            # 更新列表
            self.updateGestureList()
            
            # 清空编辑区域
            self.clearEditor()
    
    def saveGestureLibrary(self):
        """保存手势库到文件"""
        result = self.gestures.save()
        if result:
            QMessageBox.information(self, "保存成功", "手势库已成功保存")
        else:
            QMessageBox.warning(self, "保存失败", "保存手势库时发生错误，请查看日志获取更多信息")


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = GesturesTab()
    window.setWindowTitle("手势管理")
    window.setGeometry(100, 100, 600, 700)
    window.show()
    sys.exit(app.exec_()) 