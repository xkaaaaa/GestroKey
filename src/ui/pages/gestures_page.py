from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QGroupBox, QFrame, QSpacerItem, QSizePolicy, QGridLayout,
                              QListWidget, QListWidgetItem, QLineEdit, QComboBox, QMessageBox,
                              QScrollArea, QToolButton, QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

import os
import sys

try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

class GestureEditDialog(QDialog):
    """手势编辑对话框"""
    
    def __init__(self, gesture_name="", gesture_directions="", gesture_action="", parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("编辑手势")
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # 名称输入
        self.name_input = QLineEdit(gesture_name)
        self.name_input.setPlaceholderText("请输入手势名称")
        form_layout.addRow("手势名称:", self.name_input)
        
        # 方向输入
        self.direction_input = QLineEdit(gesture_directions)
        self.direction_input.setPlaceholderText("例如: up,down,left,right")
        form_layout.addRow("手势方向:", self.direction_input)
        
        # 操作选择
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "next_window", "prev_window", "maximize_current_window", 
            "minimize_current_window", "minimize_all", "restore_all"
        ])
        
        if gesture_action:
            index = self.action_combo.findText(gesture_action)
            if index >= 0:
                self.action_combo.setCurrentIndex(index)
                
        form_layout.addRow("触发操作:", self.action_combo)
        
        # 添加表单布局
        layout.addLayout(form_layout)
        
        # 对话框按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 设置按钮样式
        for button in button_box.buttons():
            if button_box.buttonRole(button) == QDialogButtonBox.AcceptRole:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #4299E1;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    
                    QPushButton:hover {
                        background-color: #3182CE;
                    }
                    
                    QPushButton:pressed {
                        background-color: #2B6CB0;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #EDF2F7;
                        color: #4A5568;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    
                    QPushButton:hover {
                        background-color: #E2E8F0;
                    }
                    
                    QPushButton:pressed {
                        background-color: #CBD5E0;
                    }
                """)
        
        layout.addWidget(button_box)
        
    def get_gesture_data(self):
        """获取对话框中的手势数据
        
        Returns:
            包含手势数据的字典
        """
        return {
            "name": self.name_input.text().strip(),
            "directions": self.direction_input.text().strip(),
            "action": self.action_combo.currentText()
        }

class GestureItem(QWidget):
    """手势列表项"""
    
    editClicked = pyqtSignal(str)  # 编辑信号，参数为手势键名
    deleteClicked = pyqtSignal(str)  # 删除信号，参数为手势键名
    
    def __init__(self, key, name, directions, action, parent=None):
        super().__init__(parent)
        self.key = key
        
        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 名称和方向容器
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # 名称
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #2D3748;")
        info_layout.addWidget(name_label)
        
        # 方向和操作
        details_label = QLabel(f"方向: {directions} | 操作: {action}")
        details_label.setStyleSheet("font-size: 13px; color: #4A5568;")
        info_layout.addWidget(details_label)
        
        # 添加信息容器到主布局
        layout.addWidget(info_container)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 编辑按钮
        edit_btn = QToolButton()
        edit_btn.setText("编辑")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QToolButton {
                background-color: #4299E1;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 13px;
            }
            
            QToolButton:hover {
                background-color: #3182CE;
            }
            
            QToolButton:pressed {
                background-color: #2B6CB0;
            }
        """)
        edit_btn.clicked.connect(lambda: self.editClicked.emit(self.key))
        
        # 删除按钮
        delete_btn = QToolButton()
        delete_btn.setText("删除")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QToolButton {
                background-color: #F56565;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 13px;
                margin-left: 5px;
            }
            
            QToolButton:hover {
                background-color: #E53E3E;
            }
            
            QToolButton:pressed {
                background-color: #C53030;
            }
        """)
        delete_btn.clicked.connect(lambda: self.deleteClicked.emit(self.key))
        
        # 添加按钮到主布局
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

class GesturesPageHeader(QWidget):
    """手势页头部组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 10)
        
        # 标题
        title = QLabel("手势管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D3748;")
        layout.addWidget(title)
        
        # 描述
        description = QLabel("自定义和管理你的手势及其触发的操作")
        description.setStyleSheet("font-size: 14px; color: #4A5568; margin-top: 5px;")
        layout.addWidget(description)
        
        # 分割线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #E2E8F0;")
        layout.addWidget(divider)

class GesturesPage(QWidget):
    """手势管理页面"""
    
    def __init__(self, gesture_manager, parent=None):
        super().__init__(parent)
        self.gesture_manager = gesture_manager
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 页头
        self.header = GesturesPageHeader()
        main_layout.addWidget(self.header)
        
        # 内容容器
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # 操作按钮
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加手势按钮
        add_btn = QPushButton("添加手势")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4299E1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #3182CE;
            }
            
            QPushButton:pressed {
                background-color: #2B6CB0;
            }
        """)
        add_btn.clicked.connect(self.on_add_gesture)
        actions_layout.addWidget(add_btn)
        
        # 添加弹性空间
        actions_layout.addStretch()
        
        # 添加操作按钮到内容布局
        content_layout.addWidget(actions_container)
        
        # 手势列表
        self.gesture_list = QListWidget()
        self.gesture_list.setFrameShape(QFrame.NoFrame)
        self.gesture_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #E2E8F0;
            }
            
            QListWidget::item:hover {
                background-color: #F7FAFC;
            }
        """)
        self.gesture_list.setSpacing(5)
        
        # 添加手势列表到内容布局
        content_layout.addWidget(self.gesture_list)
        
        # 添加内容容器到主布局
        main_layout.addWidget(content_container)
        
        # 加载手势数据
        self.load_gestures()
        
        # 监听手势管理器的信号
        self.gesture_manager.gesturesChanged.connect(self.on_gestures_changed)
        
    def load_gestures(self):
        """加载手势数据到列表"""
        # 清空列表
        self.gesture_list.clear()
        
        # 获取所有手势
        gestures = self.gesture_manager.get_all_gestures()
        
        # 添加到列表
        for key, gesture in gestures.items():
            item = QListWidgetItem()
            
            # 创建自定义部件
            widget = GestureItem(
                key, 
                gesture.get('name', '未命名'),
                gesture.get('directions', ''),
                gesture.get('action', '')
            )
            
            # 连接信号
            widget.editClicked.connect(self.on_edit_gesture)
            widget.deleteClicked.connect(self.on_delete_gesture)
            
            # 设置大小
            item.setSizeHint(widget.sizeHint())
            
            # 添加到列表
            self.gesture_list.addItem(item)
            self.gesture_list.setItemWidget(item, widget)
        
    def on_gestures_changed(self, gestures):
        """手势变更处理"""
        self.load_gestures()
        
    def on_add_gesture(self):
        """添加手势"""
        dialog = GestureEditDialog(parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # 获取手势数据
            gesture_data = dialog.get_gesture_data()
            
            # 验证输入
            if not gesture_data['name'] or not gesture_data['directions']:
                QMessageBox.warning(self, "输入错误", "手势名称和方向不能为空")
                return
                
            # 生成键名（使用名称的首字母或整个名称）
            key = gesture_data['name']
            if len(key) > 5:  # 太长就截断
                key = key[:5]
                
            # 添加手势
            success = self.gesture_manager.add_gesture(
                key, 
                gesture_data['name'],
                gesture_data['directions'],
                gesture_data['action']
            )
            
            if not success:
                QMessageBox.warning(self, "添加失败", "手势添加失败，可能存在名称或方向冲突")
        
    def on_edit_gesture(self, key):
        """编辑手势
        
        Args:
            key: 手势键名
        """
        # 获取手势数据
        gesture = self.gesture_manager.get_gesture(key)
        if not gesture:
            QMessageBox.warning(self, "编辑失败", f"找不到键名为 {key} 的手势")
            return
            
        dialog = GestureEditDialog(
            gesture.get('name', ''),
            gesture.get('directions', ''),
            gesture.get('action', ''),
            parent=self
        )
        
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # 获取新的手势数据
            new_gesture = dialog.get_gesture_data()
            
            # 验证输入
            if not new_gesture['name'] or not new_gesture['directions']:
                QMessageBox.warning(self, "输入错误", "手势名称和方向不能为空")
                return
                
            # 生成新键名
            new_key = new_gesture['name']
            if len(new_key) > 5:  # 太长就截断
                new_key = new_key[:5]
                
            # 更新手势
            success = self.gesture_manager.update_gesture(
                key,
                new_key,
                new_gesture['name'],
                new_gesture['directions'],
                new_gesture['action']
            )
            
            if not success:
                QMessageBox.warning(self, "更新失败", "手势更新失败，可能存在名称或方向冲突")
        
    def on_delete_gesture(self, key):
        """删除手势
        
        Args:
            key: 手势键名
        """
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除此手势吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.gesture_manager.delete_gesture(key)
            
            if not success:
                QMessageBox.warning(self, "删除失败", f"删除手势 {key} 失败")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from ui.utils.gesture_manager import GestureManager
    import tempfile
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
        temp_path = temp.name
        
    app = QApplication(sys.argv)
    
    # 初始化手势管理器
    gesture_manager = GestureManager(temp_path)
    
    # 创建手势页面
    gestures_page = GesturesPage(gesture_manager)
    gestures_page.show()
    
    # 运行应用
    ret = app.exec_()
    
    # 清理
    os.unlink(temp_path)
    
    sys.exit(ret) 