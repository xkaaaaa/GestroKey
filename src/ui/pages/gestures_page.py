from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                      QGroupBox, QFrame, QSpacerItem, QSizePolicy, QGridLayout,
                      QListWidget, QListWidgetItem, QLineEdit, QComboBox, QMessageBox,
                      QScrollArea, QToolButton, QDialog, QDialogButtonBox, QFormLayout,
                      QTextEdit, QPlainTextEdit, QApplication, QToolBar, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon
import os
import sys
import base64
import uuid

try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log


class DirectionButtonGroup(QWidget):
    """方向按钮组，用于可视化地选择手势方向"""
    
    directionChanged = pyqtSignal(list)  # 方向变更信号
    
    def __init__(self, initial_directions=None, parent=None):
        super().__init__(parent)
        
        if initial_directions is None:
            initial_directions = []
            
        self.directions = initial_directions.copy() if isinstance(initial_directions, list) else []
        
        # 布局
        main_layout = QVBoxLayout(self)
        
        # 方向显示
        self.direction_display = QLabel()
        self.direction_display.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                padding: 8px;
                min-height: 20px;
            }
        """)
        main_layout.addWidget(self.direction_display)
        
        # 方向按钮网格
        button_grid = QGridLayout()
        button_grid.setSpacing(5)
        
        # 方向映射
        self.direction_map = {
            "↖": (0, 0), "↑": (0, 1), "↗": (0, 2),
            "←": (1, 0), "·": (1, 1), "→": (1, 2),
            "↙": (2, 0), "↓": (2, 1), "↘": (2, 2)
        }
        
        # 创建方向按钮
        for direction, (row, col) in self.direction_map.items():
            if direction == "·":  # 中心点放删除按钮
                # 创建删除按钮
                delete_btn = QPushButton()
                delete_btn.setFixedSize(40, 40)
                delete_btn.setText("X")  # 使用字母X作为删除图标
                delete_btn.setFont(QFont("Arial", 14, QFont.Normal))
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FF5656;
                        color: white;
                        border: none;
                        border-radius: 20px;
                        font-weight: normal;
                    }
                    QPushButton:hover {
                        background-color: #E53E3E;
                    }
                    QPushButton:pressed {
                        background-color: #C53030;
                    }
                """)
                delete_btn.setToolTip("删除最后一个方向")  # 添加工具提示说明按钮功能
                delete_btn.clicked.connect(self.remove_last_direction)
                button_grid.addWidget(delete_btn, row, col)
                continue
            
            btn = QPushButton(direction)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #E2E8F0;
                    border: none;
                    border-radius: 20px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #CBD5E0;
                }
                QPushButton:pressed {
                    background-color: #4299E1;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, d=direction: self.add_direction(d))
            button_grid.addWidget(btn, row, col)
        
        main_layout.addLayout(button_grid)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        # 清空所有方向
        clear_btn = QPushButton("清空")
        clear_btn.setIcon(QIcon.fromTheme("edit-clear"))
        clear_btn.clicked.connect(self.clear_directions)
        toolbar.addWidget(clear_btn)
        
        main_layout.addLayout(toolbar)
        
        # 更新显示
        self._update_display()
    
    def add_direction(self, direction):
        """添加方向"""
        # 手动记录方向添加，避免重复
        self.directions.append(direction)
        self._update_display()
        # 发出信号通知方向已改变
        self.directionChanged.emit(self.directions.copy())  # 发送副本以避免引用问题
    
    def remove_last_direction(self):
        """删除最后一个方向"""
        if self.directions:
            self.directions.pop()
            self._update_display()
            self.directionChanged.emit(self.directions.copy())  # 发送副本以避免引用问题
    
    def clear_directions(self):
        """清空所有方向"""
        self.directions.clear()
        self._update_display()
        self.directionChanged.emit(self.directions.copy())  # 发送副本以避免引用问题
    
    def get_directions(self):
        """获取当前的方向列表"""
        return self.directions
    
    def set_directions(self, directions):
        """设置方向列表"""
        self.directions = directions.copy() if directions else []
        self._update_display()
    
    def _update_display(self):
        """更新方向显示"""
        if not self.directions:
            self.direction_display.setText("未设置方向")
            log.debug("方向显示更新: 未设置方向")
        else:
            # 确保所有元素都是字符串
            direction_strings = [str(d) for d in self.directions]
            display_text = " - ".join(direction_strings)  # 使用"-"作为方向连接符
            self.direction_display.setText(display_text)
            log.debug(f"方向显示更新: {self.directions} -> {display_text}")


class GestureEditDialog(QDialog):
    """手势编辑对话框"""
    
    def __init__(self, gesture_name="", gesture_directions=None, gesture_action="", parent=None):
        super().__init__(parent)
        
        if gesture_directions is None:
            gesture_directions = []
            
        self.setWindowTitle("编辑手势")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignTop)  # 标签左上对齐
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)   # 字段左上对齐
        
        # 名称输入
        self.name_input = QLineEdit(gesture_name)
        self.name_input.setPlaceholderText("请输入手势名称")
        form_layout.addRow("手势名称:", self.name_input)
        
        # 方向输入（使用按钮组）
        self.direction_buttons = DirectionButtonGroup(gesture_directions)
        form_layout.addRow("手势方向:", self.direction_buttons)
        
        # 添加表单布局
        layout.addLayout(form_layout)
        
        # Python代码编辑
        code_group = QGroupBox("操作代码 (Python)")
        code_layout = QVBoxLayout(code_group)
        
        # 代码编辑器
        self.code_editor = QPlainTextEdit()
        self.code_editor.setStyleSheet("""
            QPlainTextEdit {
                font-family: Consolas, 'Courier New', monospace;
                font-size: 14px;
                background-color: #f8f9fa;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        # 如果有传入的操作代码，尝试从Base64解码
        if gesture_action:
            try:
                decoded_action = base64.b64decode(gesture_action).decode('utf-8')
                self.code_editor.setPlainText(decoded_action)
            except:
                # 如果解码失败，可能是未编码的原始代码
                self.code_editor.setPlainText(gesture_action)
        else:
            # 默认代码模板
            self.code_editor.setPlainText("""# 在此编写Python代码
# 可使用以下模块:
# - os, sys: 系统操作
# - pyautogui: 自动化键鼠操作
# - subprocess: 执行命令
# - time: 时间操作

# 示例 - 模拟Alt+Tab键切换窗口:
pyautogui.hotkey('alt', 'tab')""")
            
        code_layout.addWidget(self.code_editor)
        
        # 提示信息
        help_text = """
        <b>可用模块:</b>
        <ul>
            <li><b>pyautogui</b>: 控制鼠标键盘，如 pyautogui.hotkey('alt', 'tab')</li>
            <li><b>os</b> & <b>sys</b>: 系统操作</li>
            <li><b>subprocess</b>: 执行系统命令</li>
            <li><b>time</b>: 时间操作，如 time.sleep(1)</li>
        </ul>
        """
        help_label = QLabel(help_text)
        help_label.setStyleSheet("color: #4A5568; background-color: #EDF2F7; padding: 10px; border-radius: 5px;")
        help_label.setWordWrap(True)
        code_layout.addWidget(help_label)
        
        layout.addWidget(code_group)
        
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
        # 获取代码文本
        code_text = self.code_editor.toPlainText().strip()
        
        # Base64编码
        try:
            encoded_action = base64.b64encode(code_text.encode('utf-8')).decode('utf-8')
        except:
            encoded_action = ""
            
        return {
            "name": self.name_input.text().strip(),
            "directions": self.direction_buttons.get_directions(),
            "action": encoded_action
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
        
        # 方向信息
        # 将方向列表格式化为文本
        if isinstance(directions, list):
            directions_text = " - ".join([str(d) for d in directions]) if directions else "无"
        else:
            directions_text = directions if directions else "无"
            
        details_label = QLabel(f"方向: {directions_text}")
        details_label.setStyleSheet("font-size: 13px; color: #4A5568;")
        info_layout.addWidget(details_label)
        
        layout.addWidget(info_container, 1)
        
        # 编辑按钮
        edit_btn = QPushButton("编辑")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4299E1;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #3182CE;
            }
        """)
        edit_btn.clicked.connect(lambda: self.editClicked.emit(self.key))
        layout.addWidget(edit_btn)
        
        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F56565;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #E53E3E;
            }
        """)
        delete_btn.clicked.connect(lambda: self.deleteClicked.emit(self.key))
        layout.addWidget(delete_btn)
        
        # 设置项目样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 6px;
                border: 1px solid #E2E8F0;
            }
        """)


class GesturesPage(QWidget):
    """手势管理页面"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("手势管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D3748; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 描述
        description = QLabel("创建和管理自定义手势，为每个手势分配自动化操作。")
        description.setStyleSheet("font-size: 14px; color: #4A5568; margin-bottom: 15px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # 手势列表容器
        list_container = QWidget()
        list_container.setStyleSheet("background-color: #F7FAFC; border-radius: 8px; padding: 10px;")
        list_layout = QVBoxLayout(list_container)
        
        # 列表标题和添加按钮行
        header_layout = QHBoxLayout()
        header_label = QLabel("已定义手势")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2D3748;")
        header_layout.addWidget(header_label)
        
        # 添加手势按钮
        add_button = QPushButton("添加手势")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #48BB78;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #38A169;
            }
        """)
        add_button.setMinimumWidth(120)
        add_button.clicked.connect(self.add_gesture)
        header_layout.addWidget(add_button)
        
        list_layout.addLayout(header_layout)
        
        # 手势列表滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #EDF2F7;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E0;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # 创建手势列表的容器
        self.gestures_list = QWidget()
        self.gestures_layout = QVBoxLayout(self.gestures_list)
        self.gestures_layout.setContentsMargins(0, 0, 0, 0)
        self.gestures_layout.setSpacing(10)
        self.gestures_layout.addStretch()
        
        scroll_area.setWidget(self.gestures_list)
        list_layout.addWidget(scroll_area)
        
        layout.addWidget(list_container)
        
        # 提示信息
        tips_text = """
        <b>提示:</b><br>
        • 手势由一系列方向组成，如"上-右-下-左"<br>
        • 每个手势可以执行一段Python代码<br>
        • 手势识别时自动运行相应的代码<br>
        • 可以使用各种Python库进行自动化操作
        """
        tips_label = QLabel(tips_text)
        tips_label.setStyleSheet("color: #4A5568; background-color: #EDF2F7; padding: 15px; border-radius: 8px;")
        tips_label.setWordWrap(True)
        layout.addWidget(tips_label)
        
        # 加载手势列表
        self.load_gestures()
    
    def load_gestures(self):
        """加载手势列表"""
        log.debug("加载手势列表")
        
        # 清除现有的手势项
        for i in reversed(range(self.gestures_layout.count() - 1)):  # -1 因为有一个 stretch
            widget = self.gestures_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # 获取所有手势
        all_gestures = self.controller.get_all_gestures()
        
        # 处理可能存在的新版格式
        gestures = {}
        if isinstance(all_gestures, dict):
            if 'gestures' in all_gestures:
                # 新版格式，从gestures字段中获取
                gestures = all_gestures.get('gestures', {})
            else:
                # 旧版格式，直接使用
                gestures = {k: v for k, v in all_gestures.items() if k != 'version'}
        
        if not gestures:
            # 如果没有手势，显示一个空状态
            empty_label = QLabel('还没有添加任何手势。点击"添加手势"创建你的第一个手势。')
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #718096; font-size: 14px; padding: 20px;")
            empty_label.setWordWrap(True)
            self.gestures_layout.insertWidget(0, empty_label)
        else:
            # 添加手势项
            for key, gesture in gestures.items():
                # 检查gesture的类型并相应处理
                if isinstance(gesture, dict):
                    name = gesture.get("name", "")
                    directions = gesture.get("directions", [])
                    action = gesture.get("action", "")
                else:
                    # 如果gesture不是字典，则尝试将其转换为字符串
                    name = str(gesture)
                    directions = []
                    action = ""
                    log.warning(f"手势数据格式不正确: {key} -> {gesture}")
                
                item = GestureItem(
                    key=key,
                    name=name,
                    directions=directions,
                    action=action
                )
                item.editClicked.connect(self.edit_gesture)
                item.deleteClicked.connect(self.delete_gesture)
                self.gestures_layout.insertWidget(0, item)
        
        log.debug(f"手势列表加载完成，共 {len(gestures)} 个手势")
    
    def add_gesture(self):
        """添加新手势"""
        log.debug("打开添加手势对话框")
        
        dialog = GestureEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            gesture_data = dialog.get_gesture_data()
            name = gesture_data["name"]
            directions = gesture_data["directions"]
            
            if not name:
                QMessageBox.warning(self, "错误", "手势名称不能为空。")
                return
            
            if not directions:
                QMessageBox.warning(self, "错误", "请至少添加一个方向。")
                return
            
            # 生成唯一键名
            key = f"gesture_{uuid.uuid4().hex[:8]}"
            
            # 添加手势
            if self.controller.add_gesture(key, name, directions, gesture_data["action"]):
                log.debug(f"添加手势成功: {key} -> {name}")
                self.load_gestures()
            else:
                QMessageBox.warning(self, "错误", "添加手势失败。")
    
    def edit_gesture(self, key):
        """编辑现有手势
        
        Args:
            key: 手势的键名
        """
        log.debug(f"编辑手势: {key}")
        
        gesture = self.controller.get_gesture(key)
        if not gesture:
            QMessageBox.warning(self, "错误", f"找不到手势: {key}")
            return
        
        dialog = GestureEditDialog(
            gesture_name=gesture.get("name", ""),
            gesture_directions=gesture.get("directions", []),
            gesture_action=gesture.get("action", ""),
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            gesture_data = dialog.get_gesture_data()
            name = gesture_data["name"]
            directions = gesture_data["directions"]
            
            if not name:
                QMessageBox.warning(self, "错误", "手势名称不能为空。")
                return
            
            if not directions:
                QMessageBox.warning(self, "错误", "请至少添加一个方向。")
                return
            
            # 更新手势
            if self.controller.update_gesture(key, key, name, directions, gesture_data["action"]):
                log.debug(f"更新手势成功: {key} -> {name}")
                self.load_gestures()
            else:
                QMessageBox.warning(self, "错误", "更新手势失败。")
    
    def delete_gesture(self, key):
        """删除手势
        
        Args:
            key: 手势的键名
        """
        log.debug(f"请求删除手势: {key}")
        
        # 获取手势名称
        gesture = self.controller.get_gesture(key)
        if not gesture:
            return
        
        name = gesture.get("name", key)
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f'确定要删除手势 "{name}" 吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.controller.delete_gesture(key):
                log.debug(f"删除手势成功: {key}")
                self.load_gestures()
            else:
                QMessageBox.warning(self, "错误", "删除手势失败。")


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