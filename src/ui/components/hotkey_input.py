import sys
import os
import ctypes
from PyQt6.QtWidgets import (QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, 
                            QGraphicsDropShadowEffect, QPushButton, QScrollArea, QFrame,
                            QGridLayout, QDialog, QToolButton, QGraphicsOpacityEffect)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty, 
                          pyqtSignal, QRect, QParallelAnimationGroup, QTimer, QEvent, QPointF)
from PyQt6.QtGui import (QColor, QPainter, QFont, QPainterPath, QBrush, QPen, 
                         QKeyEvent, QPalette, QFontMetrics, QIcon)

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

# 平台特定代码
if sys.platform == 'win32':
    try:
        # 获取用户32库
        user32 = ctypes.windll.user32
        # 定义Windows键盘钩子常量
        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        WM_KEYUP = 0x0101
        WM_SYSKEYDOWN = 0x0104
        WM_SYSKEYUP = 0x0105
    except Exception as e:
        print(f"加载Windows库失败: {e}")
elif sys.platform == 'darwin':
    # macOS平台特定代码
    try:
        import Quartz
        # 如果需要其他macOS特定库，在此处导入
    except ImportError:
        print("无法导入macOS特定库，某些功能可能受限")
elif sys.platform.startswith('linux'):
    # Linux平台特定代码
    try:
        import Xlib
        from Xlib import X, XK, display
        # 如果需要其他Linux特定库，在此处导入
    except ImportError:
        print("无法导入Linux特定库，某些功能可能受限")

# 虚拟键盘对话框类
class VirtualKeyboardDialog(QDialog):
    """虚拟键盘对话框，允许用户通过点击选择按键"""
    
    # 自定义信号
    keySelected = pyqtSignal(str)  # 当用户选择了一个按键时发出的信号
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setWindowTitle("虚拟键盘")
        
        # 保存修饰键状态
        self.modifier_states = {
            "Ctrl": False,
            "Alt": False,
            "Shift": False,
            "Win": False
        }
        
        # 保存所有按键状态，用于实时同步
        self.key_states = {}
        
        # 按钮大小配置
        self.key_size = QSize(36, 30)  # 默认按键尺寸
        
        # 当前主题颜色
        self.theme_colors = {
            "background": QColor("#f8f9fa"),
            "key_bg": QColor("#ffffff"),
            "key_text": QColor("#212529"),
            "key_border": QColor("#dee2e6"),
            "key_pressed": QColor("#0d6efd"),
            "key_pressed_text": QColor("#ffffff"),
            "modifier_active": QColor("#0d6efd")
        }
        
        # 当前按键动画状态
        self.key_animations = {}
        
        # 设置无边框和透明背景
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 设置窗口背景透明
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 设置对话框样式，不再需要背景色和边框
        self.setStyleSheet("""
            QDialog {
                background-color: transparent;
            }
            QPushButton {
                background-color: #ffffff;
                color: #212529;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 1px;
                margin: 1px;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border: 1px solid #c1c9d0;
            }
            QPushButton:pressed, QPushButton:checked {
                background-color: #0d6efd;
                color: white;
                border: 1px solid #0a58ca;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        # 创建背景内容面板（带有圆角背景）
        self.content_panel = QWidget(self)
        self.content_panel.setObjectName("contentPanel")
        self.content_panel.setStyleSheet("""
            QWidget#contentPanel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 12px;
            }
        """)
        
        panel_layout = QVBoxLayout(self.content_panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(0)
        
        # 创建键盘面板容器
        keyboard_widget = QWidget()
        keyboard_layout = QHBoxLayout(keyboard_widget)
        keyboard_layout.setContentsMargins(0, 0, 0, 0)
        keyboard_layout.setSpacing(8)
        
        # 主键盘部分 (左侧)
        main_keyboard = QWidget()
        main_keyboard_layout = QVBoxLayout(main_keyboard)
        main_keyboard_layout.setContentsMargins(0, 0, 0, 0)
        main_keyboard_layout.setSpacing(4)
        
        # 顶部功能键行 (Esc, F1-F12)
        function_row = QWidget()
        function_layout = QHBoxLayout(function_row)
        function_layout.setContentsMargins(0, 0, 0, 0)
        function_layout.setSpacing(4)
        
        # Esc键
        esc_btn = QPushButton("ESC")
        esc_btn.setFixedSize(42, 30)
        esc_btn.clicked.connect(lambda: self.on_key_selected("Esc"))
        self.key_states[Qt.Key.Key_Escape] = esc_btn
        function_layout.addWidget(esc_btn)
        
        function_layout.addSpacing(10)
        
        # F1-F12功能键
        f_keys = [
            ("F1", Qt.Key.Key_F1), ("F2", Qt.Key.Key_F2), 
            ("F3", Qt.Key.Key_F3), ("F4", Qt.Key.Key_F4), 
            ("F5", Qt.Key.Key_F5), ("F6", Qt.Key.Key_F6), 
            ("F7", Qt.Key.Key_F7), ("F8", Qt.Key.Key_F8), 
            ("F9", Qt.Key.Key_F9), ("F10", Qt.Key.Key_F10), 
            ("F11", Qt.Key.Key_F11), ("F12", Qt.Key.Key_F12)
        ]
        
        # 按照分组添加功能键
        for i, (text, key) in enumerate(f_keys):
            btn = QPushButton(text)
            btn.setFixedSize(42, 30)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            self.key_states[key] = btn
            function_layout.addWidget(btn)
            
            # 每4个键添加间隔
            if i in [3, 7] and i < 11:
                function_layout.addSpacing(10)
        
        main_keyboard_layout.addWidget(function_row)
        
        # 数字键行
        number_row = QWidget()
        number_layout = QHBoxLayout(number_row)
        number_layout.setContentsMargins(0, 0, 0, 0)
        number_layout.setSpacing(4)
        
        # 添加数字键和符号键
        num_keys = [
            ("`", Qt.Key.Key_QuoteLeft), ("1", Qt.Key.Key_1), 
            ("2", Qt.Key.Key_2), ("3", Qt.Key.Key_3), 
            ("4", Qt.Key.Key_4), ("5", Qt.Key.Key_5), 
            ("6", Qt.Key.Key_6), ("7", Qt.Key.Key_7), 
            ("8", Qt.Key.Key_8), ("9", Qt.Key.Key_9), 
            ("0", Qt.Key.Key_0), ("-", Qt.Key.Key_Minus), 
            ("=", Qt.Key.Key_Equal), ("Backspace", Qt.Key.Key_Backspace)
        ]
        
        # 特殊宽度的键
        key_widths = [42] * 13 + [84]
        
        for i, (text, key) in enumerate(num_keys):
            btn = QPushButton(text)
            btn.setFixedSize(key_widths[i], 30)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            self.key_states[key] = btn
            number_layout.addWidget(btn)
        
        main_keyboard_layout.addWidget(number_row)
        
        # Tab键行
        tab_row = QWidget()
        tab_layout = QHBoxLayout(tab_row)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(4)
        
        # Tab键
        tab_btn = QPushButton("Tab")
        tab_btn.setFixedSize(63, 30)
        tab_btn.clicked.connect(lambda: self.on_key_selected("Tab"))
        self.key_states[Qt.Key.Key_Tab] = tab_btn
        tab_layout.addWidget(tab_btn)
        
        # 第一行字母 Q-P 和符号
        qwerty_row1 = [
            ("Q", Qt.Key.Key_Q), ("W", Qt.Key.Key_W), 
            ("E", Qt.Key.Key_E), ("R", Qt.Key.Key_R), 
            ("T", Qt.Key.Key_T), ("Y", Qt.Key.Key_Y), 
            ("U", Qt.Key.Key_U), ("I", Qt.Key.Key_I), 
            ("O", Qt.Key.Key_O), ("P", Qt.Key.Key_P), 
            ("[", Qt.Key.Key_BracketLeft), ("]", Qt.Key.Key_BracketRight), 
            ("\\", Qt.Key.Key_Backslash)
        ]
        
        for text, key in qwerty_row1:
            btn = QPushButton(text)
            # 右侧反斜杠键宽度稍大
            if text == "\\":
                btn.setFixedSize(52, 30)
            else:
                btn.setFixedSize(42, 30)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            self.key_states[key] = btn
            tab_layout.addWidget(btn)
        
        main_keyboard_layout.addWidget(tab_row)
        
        # Caps Lock行
        caps_row = QWidget()
        caps_layout = QHBoxLayout(caps_row)
        caps_layout.setContentsMargins(0, 0, 0, 0)
        caps_layout.setSpacing(4)
        
        # Caps Lock键
        caps_btn = QPushButton("Caps")
        caps_btn.setFixedSize(73, 30)
        caps_btn.setCheckable(True)
        caps_btn.clicked.connect(lambda: self.on_key_selected("CapsLock"))
        self.key_states[Qt.Key.Key_CapsLock] = caps_btn
        caps_layout.addWidget(caps_btn)
        
        # 第二行字母 A-L 和符号
        qwerty_row2 = [
            ("A", Qt.Key.Key_A), ("S", Qt.Key.Key_S), 
            ("D", Qt.Key.Key_D), ("F", Qt.Key.Key_F), 
            ("G", Qt.Key.Key_G), ("H", Qt.Key.Key_H), 
            ("J", Qt.Key.Key_J), ("K", Qt.Key.Key_K), 
            ("L", Qt.Key.Key_L), (";", Qt.Key.Key_Semicolon), 
            ("'", Qt.Key.Key_Apostrophe)
        ]
        
        for text, key in qwerty_row2:
            btn = QPushButton(text)
            btn.setFixedSize(42, 30)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            self.key_states[key] = btn
            caps_layout.addWidget(btn)
        
        # Enter键
        enter_btn = QPushButton("Enter")
        enter_btn.setFixedSize(84, 30)
        enter_btn.clicked.connect(lambda: self.on_key_selected("Enter"))
        self.key_states[Qt.Key.Key_Return] = enter_btn
        caps_layout.addWidget(enter_btn)
        
        main_keyboard_layout.addWidget(caps_row)
        
        # Shift行
        shift_row = QWidget()
        shift_layout = QHBoxLayout(shift_row)
        shift_layout.setContentsMargins(0, 0, 0, 0)
        shift_layout.setSpacing(4)
        
        # 左Shift键
        left_shift_btn = QPushButton("Shift")
        left_shift_btn.setFixedSize(95, 30)
        left_shift_btn.setCheckable(True)
        left_shift_btn.clicked.connect(self.on_shift_clicked)
        self.key_states[Qt.Key.Key_Shift] = left_shift_btn
        shift_layout.addWidget(left_shift_btn)
        
        # 第三行字母 Z-M 和符号
        qwerty_row3 = [
            ("Z", Qt.Key.Key_Z), ("X", Qt.Key.Key_X), 
            ("C", Qt.Key.Key_C), ("V", Qt.Key.Key_V), 
            ("B", Qt.Key.Key_B), ("N", Qt.Key.Key_N), 
            ("M", Qt.Key.Key_M), (",", Qt.Key.Key_Comma), 
            (".", Qt.Key.Key_Period), ("/", Qt.Key.Key_Slash)
        ]
        
        for text, key in qwerty_row3:
            btn = QPushButton(text)
            btn.setFixedSize(42, 30)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            self.key_states[key] = btn
            shift_layout.addWidget(btn)
        
        # 右Shift键
        right_shift_btn = QPushButton("Shift")
        right_shift_btn.setFixedSize(95, 30)
        right_shift_btn.setCheckable(True)
        right_shift_btn.clicked.connect(self.on_shift_clicked)
        shift_layout.addWidget(right_shift_btn)
        
        main_keyboard_layout.addWidget(shift_row)
        
        # 底部控制键行
        ctrl_row = QWidget()
        ctrl_layout = QHBoxLayout(ctrl_row)
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        ctrl_layout.setSpacing(4)
        
        # 添加控制键
        control_keys = [
            ("Ctrl", Qt.Key.Key_Control, 60),
            ("Win", Qt.Key.Key_Meta, 60),
            ("Alt", Qt.Key.Key_Alt, 60),
            ("Space", Qt.Key.Key_Space, 230),
            ("Alt", Qt.Key.Key_Alt, 60),
            ("Win", Qt.Key.Key_Meta, 60),
            ("Ctrl", Qt.Key.Key_Control, 60)
        ]
        
        for i, (text, key, width) in enumerate(control_keys):
            btn = QPushButton(text)
            btn.setFixedSize(width, 30)
            
            # 修饰键是可切换的
            if text in ["Ctrl", "Alt", "Win"]:
                btn.setCheckable(True)
                if text == "Ctrl":
                    btn.clicked.connect(self.on_ctrl_clicked)
                elif text == "Alt":
                    btn.clicked.connect(self.on_alt_clicked)
                elif text == "Win":
                    btn.clicked.connect(self.on_win_clicked)
            else:
                btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            
            # 第一次出现的键保存状态映射
            if i in [0, 1, 2, 3]:
                self.key_states[key] = btn
                
            ctrl_layout.addWidget(btn)
        
        main_keyboard_layout.addWidget(ctrl_row)
        
        # 右侧面板部分
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(10, 0, 0, 0)
        right_panel_layout.setSpacing(4)
        
        # 顶部附加功能键 (PrtSc, ScrLk, Pause)
        top_func_row = QWidget()
        top_func_layout = QHBoxLayout(top_func_row)
        top_func_layout.setContentsMargins(0, 0, 0, 0)
        top_func_layout.setSpacing(4)
        
        # 顶部附加功能键
        extra_f_keys = [
            ("Prt Sc", Qt.Key.Key_Print),
            ("Scr Lk", Qt.Key.Key_ScrollLock),
            ("Pause", Qt.Key.Key_Pause)
        ]
        
        for text, key in extra_f_keys:
            btn = QPushButton(text)
            btn.setFixedSize(42, 30)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            self.key_states[key] = btn
            top_func_layout.addWidget(btn)
        
        right_panel_layout.addWidget(top_func_row)
        
        # 导航键部分 (Insert, Home, PgUp, etc.)
        nav_section = QWidget()
        nav_layout = QVBoxLayout(nav_section)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(4)
        
        # 上排导航键 (Insert, Home, PgUp)
        top_nav_row = QWidget()
        top_nav_layout = QHBoxLayout(top_nav_row)
        top_nav_layout.setContentsMargins(0, 0, 0, 0)
        top_nav_layout.setSpacing(4)
        
        top_nav_keys = [
            ("Insert", Qt.Key.Key_Insert),
            ("Home", Qt.Key.Key_Home),
            ("Pg Up", Qt.Key.Key_PageUp)
        ]
        
        for text, key in top_nav_keys:
            btn = QPushButton(text)
            btn.setFixedSize(42, 30)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            self.key_states[key] = btn
            top_nav_layout.addWidget(btn)
        
        nav_layout.addWidget(top_nav_row)
        
        # 下排导航键 (Delete, End, PgDn)
        bottom_nav_row = QWidget()
        bottom_nav_layout = QHBoxLayout(bottom_nav_row)
        bottom_nav_layout.setContentsMargins(0, 0, 0, 0)
        bottom_nav_layout.setSpacing(4)
        
        bottom_nav_keys = [
            ("Delete", Qt.Key.Key_Delete),
            ("End", Qt.Key.Key_End),
            ("Pg Dn", Qt.Key.Key_PageDown)
        ]
        
        for text, key in bottom_nav_keys:
            btn = QPushButton(text)
            btn.setFixedSize(42, 30)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(t))
            self.key_states[key] = btn
            bottom_nav_layout.addWidget(btn)
        
        nav_layout.addWidget(bottom_nav_row)
        
        # 添加弹性空间使导航键与主键盘的布局对齐
        nav_layout.addStretch()
        
        # 方向键部分 - 调整布局使其与左侧键盘的倒数两行对齐
        arrow_section = QWidget()
        arrow_layout = QGridLayout(arrow_section)
        arrow_layout.setContentsMargins(0, 0, 0, 0)
        arrow_layout.setSpacing(4)
        
        # 上箭头
        up_btn = QPushButton("↑")
        up_btn.setFixedSize(42, 30)
        up_btn.clicked.connect(lambda: self.on_key_selected("Up"))
        self.key_states[Qt.Key.Key_Up] = up_btn
        arrow_layout.addWidget(up_btn, 0, 1)
        
        # 左箭头
        left_btn = QPushButton("←")
        left_btn.setFixedSize(42, 30)
        left_btn.clicked.connect(lambda: self.on_key_selected("Left"))
        self.key_states[Qt.Key.Key_Left] = left_btn
        arrow_layout.addWidget(left_btn, 1, 0)
        
        # 下箭头
        down_btn = QPushButton("↓")
        down_btn.setFixedSize(42, 30)
        down_btn.clicked.connect(lambda: self.on_key_selected("Down"))
        self.key_states[Qt.Key.Key_Down] = down_btn
        arrow_layout.addWidget(down_btn, 1, 1)
        
        # 右箭头
        right_btn = QPushButton("→")
        right_btn.setFixedSize(42, 30)
        right_btn.clicked.connect(lambda: self.on_key_selected("Right"))
        self.key_states[Qt.Key.Key_Right] = right_btn
        arrow_layout.addWidget(right_btn, 1, 2)
        
        # 不再使用nav_layout添加arrow_section，而是直接添加到right_panel_layout
        right_panel_layout.addWidget(nav_section)
        
        # 方向键部分与左侧主键盘的倒数两行对齐
        # 这里我们添加一个占位弹性空间
        right_panel_layout.addStretch(1)
        right_panel_layout.addWidget(arrow_section)  # 方向键放在倒数第二行位置
        
        # 添加空间使其排列在合适位置
        right_panel_layout.addWidget(QWidget())  # 与底部控制键行对齐的空白widget
        
        # 数字小键盘部分
        numpad_section = QWidget()
        numpad_layout = QVBoxLayout(numpad_section)
        numpad_layout.setContentsMargins(10, 0, 0, 0)
        numpad_layout.setSpacing(4)
        
        # 数字键盘状态行 (NumLk / * -)
        numpad_top_row = QWidget()
        numpad_top_layout = QHBoxLayout(numpad_top_row)
        numpad_top_layout.setContentsMargins(0, 35, 0, 0)
        numpad_top_layout.setSpacing(4)
        
        numpad_top_keys = [
            ("NumLk", Qt.Key.Key_NumLock),
            ("/", Qt.Key.Key_Slash + 1000),
            ("*", Qt.Key.Key_Asterisk + 1000),
            ("-", Qt.Key.Key_Minus + 1000)
        ]
        
        for text, key in numpad_top_keys:
            btn = QPushButton(text)
            btn.setFixedSize(42, 30)
            if text == "NumLk":
                btn.setCheckable(True)
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(f"Num+{t}" if t not in ["NumLk"] else t))
            self.key_states[key] = btn
            numpad_top_layout.addWidget(btn)
        
        numpad_layout.addWidget(numpad_top_row)
        
        # 数字键盘主体部分 (7-9, 4-6, 1-3, 0.)
        numpad_main = QWidget()
        numpad_main_layout = QGridLayout(numpad_main)
        numpad_main_layout.setContentsMargins(0, 0, 0, 0)
        numpad_main_layout.setSpacing(4)
        
        # 数字键盘按钮 (7-9, 4-6, 1-3, 0.)
        numpad_keys = [
            ("7", Qt.Key.Key_7 + 1000, 0, 0), ("8", Qt.Key.Key_8 + 1000, 0, 1), ("9", Qt.Key.Key_9 + 1000, 0, 2),
            ("4", Qt.Key.Key_4 + 1000, 1, 0), ("5", Qt.Key.Key_5 + 1000, 1, 1), ("6", Qt.Key.Key_6 + 1000, 1, 2),
            ("1", Qt.Key.Key_1 + 1000, 2, 0), ("2", Qt.Key.Key_2 + 1000, 2, 1), ("3", Qt.Key.Key_3 + 1000, 2, 2),
            ("0", Qt.Key.Key_0 + 1000, 3, 0, 1, 2), (".", Qt.Key.Key_Period + 1000, 3, 2)
        ]
        
        for key_data in numpad_keys:
            if len(key_data) > 5:  # 扩展按键 (0)
                text, key_code, row, col, rowspan, colspan = key_data
            else:  # 标准按键
                text, key_code, row, col = key_data
                rowspan, colspan = 1, 1
            
            btn = QPushButton(text)
            if text == "0":
                btn.setFixedSize(84, 30)
            else:
                btn.setFixedSize(42, 30)
            
            btn.clicked.connect(lambda checked, t=text: self.on_key_selected(f"Num+{t}"))
            self.key_states[key_code] = btn
            numpad_main_layout.addWidget(btn, row, col, rowspan, colspan)
        
        # 添加 + 和 Enter 键
        plus_btn = QPushButton("+")
        plus_btn.setFixedSize(42, 60)  # 跨两行
        plus_btn.clicked.connect(lambda: self.on_key_selected("Num++"))
        self.key_states[Qt.Key.Key_Plus + 1000] = plus_btn
        numpad_main_layout.addWidget(plus_btn, 0, 3, 2, 1)
        
        enter_btn = QPushButton("Enter")
        enter_btn.setFixedSize(42, 60)  # 跨两行
        enter_btn.clicked.connect(lambda: self.on_key_selected("Num+Enter"))
        self.key_states[Qt.Key.Key_Enter] = enter_btn
        numpad_main_layout.addWidget(enter_btn, 2, 3, 2, 1)
        
        numpad_layout.addWidget(numpad_main)
        
        # 组合左侧和右侧布局
        keyboard_layout.addWidget(main_keyboard)
        keyboard_layout.addWidget(right_panel)
        keyboard_layout.addWidget(numpad_section)
        
        # 将键盘容器添加到主布局
        panel_layout.addWidget(keyboard_widget)
        
        # 将面板添加到主布局
        main_layout.addWidget(self.content_panel)
        
        # 为所有按钮添加鼠标悬停效果
        for btn in self.findChildren(QPushButton):
            btn.setProperty("class", "keyboard-key")
            # 确保按钮可见
            btn.setVisible(True)
        
        # 调整窗口大小
        self.resize(780, 240)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def on_shift_clicked(self):
        """处理Shift按钮点击事件"""
        sender = self.sender()
        self.modifier_states["Shift"] = sender.isChecked()
        
        # 如果一个Shift按钮被点击，另一个也应该同步状态
        for btn in self.findChildren(QPushButton):
            if btn != sender and btn.text() == "Shift":
                btn.setChecked(sender.isChecked())
    
    def on_ctrl_clicked(self):
        """处理Ctrl按钮点击事件"""
        sender = self.sender()
        self.modifier_states["Ctrl"] = sender.isChecked()
        
        # 如果一个Ctrl按钮被点击，另一个也应该同步状态
        for btn in self.findChildren(QPushButton):
            if btn != sender and btn.text() == "Ctrl":
                btn.setChecked(sender.isChecked())
    
    def on_alt_clicked(self):
        """处理Alt按钮点击事件"""
        sender = self.sender()
        self.modifier_states["Alt"] = sender.isChecked()
        
        # 如果一个Alt按钮被点击，另一个也应该同步状态
        for btn in self.findChildren(QPushButton):
            if btn != sender and btn.text() == "Alt":
                btn.setChecked(sender.isChecked())
    
    def on_win_clicked(self):
        """处理Win按钮点击事件"""
        sender = self.sender()
        
        # 获取当前操作系统对应的Win键名称
        # 这里需要一致使用HotkeyInput中的命名
        import sys
        if sys.platform == 'darwin':  # macOS
            win_key_name = "⌘"
        elif sys.platform == 'win32':  # Windows
            win_key_name = "Win"
        else:  # Linux和其他
            win_key_name = "Super"
        
        self.modifier_states[win_key_name] = sender.isChecked()
        
        # 如果一个Win按钮被点击，另一个也应该同步状态
        for btn in self.findChildren(QPushButton):
            if btn != sender and (btn.text() == "Win" or btn.text() == "⌘" or btn.text() == "Super"):
                btn.setChecked(sender.isChecked())
    
    def on_key_selected(self, key):
        """当用户选择一个非修饰键时触发"""
        # 获取选中的修饰键
        modifiers = []
        
        # 获取操作系统相关的修饰键名称
        import sys
        if sys.platform == 'darwin':  # macOS
            ctrl_name, alt_name, shift_name, meta_name = "⌃", "⌥", "⇧", "⌘"
        elif sys.platform == 'win32':  # Windows
            ctrl_name, alt_name, shift_name, meta_name = "Ctrl", "Alt", "Shift", "Win"
        else:  # Linux和其他
            ctrl_name, alt_name, shift_name, meta_name = "Ctrl", "Alt", "Shift", "Super"
            
        # 检查每个修饰键的状态
        if self.modifier_states.get("Ctrl", False):
            modifiers.append(ctrl_name)
        if self.modifier_states.get("Alt", False):
            modifiers.append(alt_name)
        if self.modifier_states.get("Shift", False):
            modifiers.append(shift_name)
            
        # 针对不同系统检查Win/Command/Super键
        if sys.platform == 'darwin':
            if self.modifier_states.get("⌘", False):
                modifiers.append(meta_name)
        elif sys.platform == 'win32':
            if self.modifier_states.get("Win", False):
                modifiers.append(meta_name)
        else:
            if self.modifier_states.get("Super", False):
                modifiers.append(meta_name)
        
        # 组合修饰键和主键
        if modifiers:
            hotkey = "+".join(modifiers + [key])
        else:
            hotkey = key
        
        # 发出信号
        self.keySelected.emit(hotkey)
        self.close()
    
    def update_modifier_state(self, key, state):
        """根据物理键盘的按键状态更新虚拟键盘的按键状态"""
        # 修饰键状态更新
        if key == Qt.Key.Key_Control:
            self.modifier_states["Ctrl"] = state
            # 更新所有Ctrl按钮
            for btn in self.findChildren(QPushButton):
                if btn.text() in ["Ctrl", "⌃"]:  # 支持macOS的Control键符号
                    btn.setChecked(state)
        
        elif key == Qt.Key.Key_Alt:
            self.modifier_states["Alt"] = state
            # 更新所有Alt按钮
            for btn in self.findChildren(QPushButton):
                if btn.text() in ["Alt", "⌥"]:  # 支持macOS的Option键符号
                    btn.setChecked(state)
        
        elif key == Qt.Key.Key_Shift:
            self.modifier_states["Shift"] = state
            # 更新所有Shift按钮
            for btn in self.findChildren(QPushButton):
                if btn.text() in ["Shift", "⇧"]:  # 支持macOS的Shift键符号
                    btn.setChecked(state)
        
        elif key == Qt.Key.Key_Meta:
            # 处理各个系统的Win/Command/Super键
            import sys
            if sys.platform == 'darwin':
                self.modifier_states["⌘"] = state  # macOS中的Command
                for btn in self.findChildren(QPushButton):
                    if btn.text() == "⌘":
                        btn.setChecked(state)
            elif sys.platform == 'win32':
                self.modifier_states["Win"] = state  # Windows中的Win键
                for btn in self.findChildren(QPushButton):
                    if btn.text() == "Win":
                        btn.setChecked(state)
            else:
                self.modifier_states["Super"] = state  # Linux中的Super键
                for btn in self.findChildren(QPushButton):
                    if btn.text() == "Super":
                        btn.setChecked(state)
        
        # 更新其他按键状态
        if key in self.key_states:
            btn = self.key_states[key]
            if btn.isCheckable():
                btn.setChecked(state)
            else:
                if state:
                    # 应用高亮样式
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #0d6efd;
                            color: white;
                            border: 1px solid #0a58ca;
                            border-radius: 6px;
                            padding: 1px;
                            margin: 1px;
                            font-weight: bold;
                            font-size: 9pt;
                        }
                    """)
                else:
                    # 恢复原始样式，此处需确保移除所有高亮风格
                    btn.setStyleSheet("")
                    # 确保按钮可见
                    btn.setVisible(True)
    
    def keyPressEvent(self, event):
        """处理键盘按键按下事件"""
        key = event.key()
        self.update_modifier_state(key, True)
        
        # 如果按下的是非修饰键，尝试生成快捷键组合
        if key not in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
            key_name = self._get_key_name(key)
            if key_name:
                # 调用on_key_selected处理组合键
                self.on_key_selected(key_name)
        
        event.accept()
    
    def keyReleaseEvent(self, event):
        """处理键盘按键释放事件"""
        key = event.key()
        self.update_modifier_state(key, False)
        event.accept()
    
    def showEvent(self, event):
        """对话框显示时，居中显示并重置状态"""
        super().showEvent(event)
        # 重置修饰键状态
        for key in self.modifier_states:
            self.modifier_states[key] = False
        
        # 重置所有可选择的按钮状态
        for btn in self.findChildren(QPushButton):
            if btn.isCheckable():
                btn.setChecked(False)
            else:
                btn.setStyleSheet("")
    
    def paintEvent(self, event):
        """自定义绘制事件，用于绘制圆角背景"""
        # 不调用父类的方法，完全自定义绘制
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿
        
        # 内容区域不需要额外绘制，由内容面板提供
        # 这里只处理整体窗口的透明度

    def _get_key_name(self, key):
        """获取按键名称"""
        # 特殊键映射
        key_mapping = {
            Qt.Key.Key_Escape: "Esc",
            Qt.Key.Key_Tab: "Tab",
            Qt.Key.Key_Backtab: "Tab",
            Qt.Key.Key_Backspace: "Backspace",
            Qt.Key.Key_Return: "Enter",
            Qt.Key.Key_Enter: "Enter",
            Qt.Key.Key_Insert: "Insert",
            Qt.Key.Key_Delete: "Delete",
            Qt.Key.Key_Pause: "Pause",
            Qt.Key.Key_Print: "Print",
            Qt.Key.Key_Home: "Home",
            Qt.Key.Key_End: "End",
            Qt.Key.Key_Left: "Left",
            Qt.Key.Key_Up: "Up",
            Qt.Key.Key_Right: "Right",
            Qt.Key.Key_Down: "Down",
            Qt.Key.Key_PageUp: "PageUp",
            Qt.Key.Key_PageDown: "PageDown",
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_F1: "F1",
            Qt.Key.Key_F2: "F2",
            Qt.Key.Key_F3: "F3",
            Qt.Key.Key_F4: "F4",
            Qt.Key.Key_F5: "F5",
            Qt.Key.Key_F6: "F6",
            Qt.Key.Key_F7: "F7",
            Qt.Key.Key_F8: "F8",
            Qt.Key.Key_F9: "F9",
            Qt.Key.Key_F10: "F10",
            Qt.Key.Key_F11: "F11",
            Qt.Key.Key_F12: "F12",
            Qt.Key.Key_CapsLock: "CapsLock",
            Qt.Key.Key_NumLock: "NumLock",
            Qt.Key.Key_ScrollLock: "ScrollLock",
            # 添加修饰键映射 - 现在使用platform相关的名称
            Qt.Key.Key_Control: self._modifier_keys["ctrl"]["name"],
            Qt.Key.Key_Shift: self._modifier_keys["shift"]["name"],
            Qt.Key.Key_Alt: self._modifier_keys["alt"]["name"],
            Qt.Key.Key_Meta: self._modifier_keys["meta"]["name"],
            # 字母键
            Qt.Key.Key_A: "A",
            Qt.Key.Key_B: "B",
            Qt.Key.Key_C: "C",
            Qt.Key.Key_D: "D",
            Qt.Key.Key_E: "E",
            Qt.Key.Key_F: "F",
            Qt.Key.Key_G: "G",
            Qt.Key.Key_H: "H",
            Qt.Key.Key_I: "I",
            Qt.Key.Key_J: "J",
            Qt.Key.Key_K: "K",
            Qt.Key.Key_L: "L",
            Qt.Key.Key_M: "M",
            Qt.Key.Key_N: "N",
            Qt.Key.Key_O: "O",
            Qt.Key.Key_P: "P",
            Qt.Key.Key_Q: "Q",
            Qt.Key.Key_R: "R",
            Qt.Key.Key_S: "S",
            Qt.Key.Key_T: "T",
            Qt.Key.Key_U: "U",
            Qt.Key.Key_V: "V",
            Qt.Key.Key_W: "W",
            Qt.Key.Key_X: "X",
            Qt.Key.Key_Y: "Y",
            Qt.Key.Key_Z: "Z",
            # 数字键
            Qt.Key.Key_0: "0",
            Qt.Key.Key_1: "1",
            Qt.Key.Key_2: "2",
            Qt.Key.Key_3: "3",
            Qt.Key.Key_4: "4",
            Qt.Key.Key_5: "5",
            Qt.Key.Key_6: "6",
            Qt.Key.Key_7: "7",
            Qt.Key.Key_8: "8",
            Qt.Key.Key_9: "9",
            # 符号键
            Qt.Key.Key_Minus: "-",
            Qt.Key.Key_Equal: "=",
            Qt.Key.Key_BracketLeft: "[",
            Qt.Key.Key_BracketRight: "]",
            Qt.Key.Key_Backslash: "\\",
            Qt.Key.Key_Semicolon: ";",
            Qt.Key.Key_Apostrophe: "'",
            Qt.Key.Key_Comma: ",",
            Qt.Key.Key_Period: ".",
            Qt.Key.Key_Slash: "/",
            Qt.Key.Key_QuoteLeft: "`"
        }
        
        # 检查是否是特殊键
        if key in key_mapping:
            return key_mapping[key]
        
        # 检查是否是基本按键 (字母、数字等)
        if 32 <= key <= 126:  # 可打印ASCII字符
            return chr(key).upper()
        
        # 小键盘按键
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            return str(key - Qt.Key.Key_0)
            
        # 如果是其他键，返回为空
        return ""


class HotkeyInput(QWidget):
    """自定义快捷键输入组件"""
    
    # 定义自定义信号
    hotkeyChanged = pyqtSignal(str)  # 当快捷键值改变时发出信号
    
    def __init__(self, parent=None, placeholder="请输入快捷键", 
                 primary_color=None, focus_color=None, bg_color=None,
                 enable_virtual_keyboard=True):
        super().__init__(parent)
        
        # 初始化属性
        self._hotkey = ""
        self._placeholder = placeholder
        self._is_focused = False
        self._enable_virtual_keyboard = enable_virtual_keyboard
        self._virtual_keyboard = None
        self._keyboard_animation_group = None
        self._pressed_keys = set()
        self._pressed_modifiers = set()
        
        # 初始化修饰键状态
        self._modifier_keys = {
            "ctrl": {"pressed": False, "name": "Ctrl"},
            "alt": {"pressed": False, "name": "Alt"},
            "shift": {"pressed": False, "name": "Shift"},
            "meta": {"pressed": False, "name": "Win"}
        }
        
        # 根据操作系统设置修饰键名称
        if sys.platform == 'darwin':  # macOS
            self._modifier_keys["ctrl"]["name"] = "⌃"  # Control symbol
            self._modifier_keys["alt"]["name"] = "⌥"   # Option symbol
            self._modifier_keys["shift"]["name"] = "⇧"  # Shift symbol
            self._modifier_keys["meta"]["name"] = "⌘"   # Command symbol
        elif sys.platform == 'win32':  # Windows
            self._modifier_keys["ctrl"]["name"] = "Ctrl"
            self._modifier_keys["alt"]["name"] = "Alt"
            self._modifier_keys["shift"]["name"] = "Shift"
            self._modifier_keys["meta"]["name"] = "Win"
        else:  # Linux 和其他
            self._modifier_keys["ctrl"]["name"] = "Ctrl"
            self._modifier_keys["alt"]["name"] = "Alt"
            self._modifier_keys["shift"]["name"] = "Shift"
            self._modifier_keys["meta"]["name"] = "Super"
            
            # 在某些Linux发行版中可能使用不同名称
            try:
                # 尝试检测常见的Linux发行版
                import platform
                distro = platform.linux_distribution()[0].lower() if hasattr(platform, 'linux_distribution') else ''
                
                # 基于发行版调整按键名称
                if 'ubuntu' in distro or 'debian' in distro:
                    self._modifier_keys["meta"]["name"] = "Super"
                elif 'fedora' in distro or 'redhat' in distro:
                    self._modifier_keys["meta"]["name"] = "Super"
                elif 'arch' in distro or 'manjaro' in distro:
                    self._modifier_keys["meta"]["name"] = "Super"
            except Exception:
                # 如果检测失败，保持默认值
                pass
        
        # 波纹动画属性
        self._ripple_position = QPointF()
        self._ripple_radius = 0
        self._ripple_opacity = 0.0
        
        # 样式属性
        self._primary_color = QColor(*primary_color) if primary_color else QColor(13, 110, 253)  # 默认蓝色
        self._focus_color = QColor(*focus_color) if focus_color else QColor(13, 110, 253).lighter(115)
        self._bg_color = QColor(*bg_color) if bg_color else QColor(248, 249, 250)
        self._text_color = QColor(33, 37, 41)
        self._placeholder_color = QColor(173, 181, 189)
        
        # 边框相关属性
        self._border_width = 1.0
        self._border_radius = 6
        self._current_border_color = self._primary_color
        
        # 设置阴影属性
        self._shadow_strength = 4.0
        
        # 下拉按钮透明度属性
        self._dropdown_opacity = 0.0
        
        # 设置UI组件
        self._setup_ui()
        
        # 设置动画效果
        self._setup_animations()
        
        # 设置样式
        self._update_styles()
        
        # 设置为可接受焦点
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    # 属性动画支持
    def _get_border_width(self):
        return self._border_width
    
    def _set_border_width(self, width):
        self._border_width = width
        self._update_styles()
    
    def _get_border_color(self):
        return self._current_border_color
    
    def _set_border_color(self, color):
        self._current_border_color = color
        self._update_styles()
    
    def _get_shadow_strength(self):
        return self._shadow_strength
    
    def _set_shadow_strength(self, strength):
        self._shadow_strength = strength
        self._update_styles()
    
    def _get_ripple_radius(self):
        return self._ripple_radius
    
    def _set_ripple_radius(self, radius):
        self._ripple_radius = radius
        self.update()
    
    def _get_ripple_opacity(self):
        return self._ripple_opacity
    
    def _set_ripple_opacity(self, opacity):
        self._ripple_opacity = opacity
        self.update()
    
    def _get_dropdown_opacity(self):
        return self._dropdown_opacity
    
    def _set_dropdown_opacity(self, opacity):
        self._dropdown_opacity = opacity
        if hasattr(self, '_dropdown_btn'):
            effect = self._dropdown_btn.graphicsEffect()
            if effect:
                effect.setOpacity(opacity)
    
    # 定义属性以支持动画
    border_width = pyqtProperty(float, _get_border_width, _set_border_width)
    border_color = pyqtProperty(QColor, _get_border_color, _set_border_color)
    shadow_strength = pyqtProperty(float, _get_shadow_strength, _set_shadow_strength)
    ripple_radius = pyqtProperty(int, _get_ripple_radius, _set_ripple_radius)
    ripple_opacity = pyqtProperty(float, _get_ripple_opacity, _set_ripple_opacity)
    dropdown_opacity = pyqtProperty(float, _get_dropdown_opacity, _set_dropdown_opacity)
    
    def focusInEvent(self, event):
        """获取焦点时的处理"""
        self._is_focused = True
        self._animate_focus(True)
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """失去焦点时的处理"""
        self._is_focused = False
        self._animate_focus(False)
        super().focusOutEvent(event)
    
    def paintEvent(self, event):
        """自定义绘制事件"""
        super().paintEvent(event)
        
        # 绘制波纹效果
        if self._ripple_radius > 0 and self._ripple_opacity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 创建一个透明的QColor，带有不透明度
            ripple_color = QColor(self._focus_color)
            ripple_color.setAlphaF(self._ripple_opacity)
            
            # 设置画笔
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(ripple_color))
            
            # 绘制圆形波纹
            painter.drawEllipse(self._ripple_position, self._ripple_radius, self._ripple_radius)
    
    def resizeEvent(self, event):
        """大小变化事件"""
        super().resizeEvent(event)
        
        # 调整容器和波纹容器尺寸
        if hasattr(self, '_container'):
            self._container.resize(self.size())
        if hasattr(self, '_ripple_container'):
            self._ripple_container.resize(self.size())
        
        # 调整下拉按钮位置
        if hasattr(self, '_dropdown_btn'):
            self._position_dropdown_button()
    
    def _position_dropdown_button(self):
        """调整下拉按钮位置"""
        btn_size = self._dropdown_btn.size()
        pos_y = (self.height() - btn_size.height()) // 2
        pos_x = self.width() - btn_size.width() - 5  # 5像素的右边距
        self._dropdown_btn.move(pos_x, pos_y)
    
    def _setup_ui(self):
        """设置UI组件"""
        # 设置固定高度
        self.setFixedHeight(36)
        
        # 设置最小宽度
        self.setMinimumWidth(150)
        
        # 创建主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建容器窗口（用于样式和圆角）
        self._container = QWidget(self)
        self._container.setObjectName("HotkeyContainer")
        self._container.setGeometry(0, 0, self.width(), self.height())
        
        # 容器内布局
        container_layout = QHBoxLayout(self._container)
        container_layout.setContentsMargins(8, 0, 8, 0)  # 左右各8像素的内边距
        
        # 标签文本
        self._label = QLabel(self._placeholder, self._container)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self._label.font()
        font.setPointSize(10)
        self._label.setFont(font)
        
        # 设置文本颜色为占位符色
        self._label.setStyleSheet(f"color: {self._placeholder_color.name()}; background-color: transparent;")
        
        # 将标签添加到容器布局
        container_layout.addWidget(self._label)
        
        # 创建下拉按钮（绝对定位，不影响布局）
        self._dropdown_btn = QPushButton(self)
        self._dropdown_btn.setFixedSize(16, 16)
        self._dropdown_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 设置下拉箭头图标或使用Unicode字符
        self._dropdown_btn.setText("▼")
        self._dropdown_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #6c757d;
                font-size: 8pt;
            }
            QPushButton:hover {
                color: #495057;
            }
        """)
        
        # 初始化时隐藏下拉按钮
        self._dropdown_btn.setVisible(False)
        
        # 添加图形效果来控制透明度
        opacity_effect = QGraphicsOpacityEffect(self._dropdown_btn)
        opacity_effect.setOpacity(0.0)  # 初始透明度
        self._dropdown_btn.setGraphicsEffect(opacity_effect)
        
        # 绝对定位下拉按钮
        self._position_dropdown_button()
        
        # 连接下拉按钮的点击事件
        self._dropdown_btn.clicked.connect(self._dropdown_btn_clicked)
        
        # 添加容器到主布局
        main_layout.addWidget(self._container)
        
        # 创建波纹容器
        self._ripple_container = QWidget(self)
        self._ripple_container.setObjectName("RippleContainer")
        self._ripple_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # 鼠标事件穿透
        self._ripple_container.setStyleSheet("background: transparent;")
        self._ripple_container.setVisible(True)
        self._ripple_container.raise_()  # 确保在最上层
        
        # 调整大小和位置
        self._ripple_container.resize(self.size())
        self._ripple_container.move(0, 0)
    
    def _dropdown_btn_clicked(self):
        """处理下拉按钮的点击事件"""
        # 确保不失去输入框焦点
        self.setFocus()
        
        # 显示虚拟键盘
        self._show_virtual_keyboard()
    
    def _show_virtual_keyboard(self):
        """显示虚拟键盘"""
        if not self._virtual_keyboard:
            self._virtual_keyboard = VirtualKeyboardDialog(self)
            self._virtual_keyboard.keySelected.connect(self.set_hotkey)
            
            # 设置初始大小为0，以便动画展开
            self._virtual_keyboard.resize(0, 0)
        
        # 直接根据当前输入框显示的快捷键来设置虚拟键盘的状态
        self._sync_keyboard_state_from_hotkey()
        
        # 计算虚拟键盘显示位置
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self._virtual_keyboard.move(pos)
        
        # 首先显示虚拟键盘
        self._virtual_keyboard.show()
        
        # 保存目标尺寸
        target_size = QSize(780, 240)
        
        # 创建大小动画
        size_animation = QPropertyAnimation(self._virtual_keyboard, b"size")
        size_animation.setDuration(300)
        size_animation.setStartValue(QSize(0, 0))
        size_animation.setEndValue(target_size)
        size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 创建透明度动画
        opacity_effect = QGraphicsOpacityEffect(self._virtual_keyboard)
        self._virtual_keyboard.setGraphicsEffect(opacity_effect)
        opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
        opacity_animation.setDuration(300)
        opacity_animation.setStartValue(0.0)
        opacity_animation.setEndValue(1.0)
        opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 创建动画组
        self._keyboard_animation_group = QParallelAnimationGroup()
        self._keyboard_animation_group.addAnimation(size_animation)
        self._keyboard_animation_group.addAnimation(opacity_animation)
        
        # 启动动画
        self._keyboard_animation_group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)
    
    def _sync_keyboard_state_from_hotkey(self):
        """基于当前快捷键文本同步虚拟键盘状态"""
        if not self._virtual_keyboard or not self._hotkey:
            return
        
        # 先重置所有状态
        for key in self._virtual_keyboard.key_states:
            self._virtual_keyboard.update_modifier_state(key, False)
        
        # 根据当前输入框显示的快捷键解析按键状态
        key_parts = self._hotkey.split('+')
        
        # 获取当前系统的修饰键名称
        import sys
        if sys.platform == 'darwin':  # macOS
            ctrl_name, alt_name, shift_name, meta_name = "⌃", "⌥", "⇧", "⌘"
        elif sys.platform == 'win32':  # Windows
            ctrl_name, alt_name, shift_name, meta_name = "Ctrl", "Alt", "Shift", "Win"
        else:  # Linux 和其他
            ctrl_name, alt_name, shift_name, meta_name = "Ctrl", "Alt", "Shift", "Super"
        
        # 检查并设置所有修饰键状态
        for part in key_parts:
            part = part.strip()
            if part in [ctrl_name, "Ctrl"]:
                self._virtual_keyboard.update_modifier_state(Qt.Key.Key_Control, True)
            elif part in [alt_name, "Alt"]:
                self._virtual_keyboard.update_modifier_state(Qt.Key.Key_Alt, True)
            elif part in [shift_name, "Shift"]:
                self._virtual_keyboard.update_modifier_state(Qt.Key.Key_Shift, True)
            elif part in [meta_name, "Win", "Command", "Super", "⌘"]:
                self._virtual_keyboard.update_modifier_state(Qt.Key.Key_Meta, True)
            else:
                # 尝试找到对应的非修饰键并高亮
                self._highlight_key_by_name(part)
    
    def _highlight_key_by_name(self, key_name):
        """根据按键名称在虚拟键盘上高亮对应按键"""
        if not self._virtual_keyboard:
            return
            
        # 键名到Qt.Key的映射
        key_mapping = {
            # 功能键
            "Esc": Qt.Key.Key_Escape,
            "Tab": Qt.Key.Key_Tab,
            "Backspace": Qt.Key.Key_Backspace,
            "Enter": Qt.Key.Key_Return,
            "Insert": Qt.Key.Key_Insert,
            "Delete": Qt.Key.Key_Delete,
            "Home": Qt.Key.Key_Home,
            "End": Qt.Key.Key_End,
            "PageUp": Qt.Key.Key_PageUp, "Pg Up": Qt.Key.Key_PageUp,
            "PageDown": Qt.Key.Key_PageDown, "Pg Dn": Qt.Key.Key_PageDown,
            "Space": Qt.Key.Key_Space,
            "CapsLock": Qt.Key.Key_CapsLock, "Caps": Qt.Key.Key_CapsLock,
            "NumLock": Qt.Key.Key_NumLock, "NumLk": Qt.Key.Key_NumLock,
            "ScrollLock": Qt.Key.Key_ScrollLock, "Scr Lk": Qt.Key.Key_ScrollLock,
            "Print": Qt.Key.Key_Print, "Prt Sc": Qt.Key.Key_Print,
            "Pause": Qt.Key.Key_Pause,
            
            # 方向键
            "Up": Qt.Key.Key_Up, "↑": Qt.Key.Key_Up,
            "Down": Qt.Key.Key_Down, "↓": Qt.Key.Key_Down,
            "Left": Qt.Key.Key_Left, "←": Qt.Key.Key_Left,
            "Right": Qt.Key.Key_Right, "→": Qt.Key.Key_Right,
            
            # F1-F12
            "F1": Qt.Key.Key_F1, "F2": Qt.Key.Key_F2, "F3": Qt.Key.Key_F3, "F4": Qt.Key.Key_F4,
            "F5": Qt.Key.Key_F5, "F6": Qt.Key.Key_F6, "F7": Qt.Key.Key_F7, "F8": Qt.Key.Key_F8,
            "F9": Qt.Key.Key_F9, "F10": Qt.Key.Key_F10, "F11": Qt.Key.Key_F11, "F12": Qt.Key.Key_F12,
        }
        
        # 单个字母和数字映射
        if len(key_name) == 1:
            if 'A' <= key_name <= 'Z':
                key_code = getattr(Qt.Key, f"Key_{key_name}")
                self._virtual_keyboard.update_modifier_state(key_code, True)
                return
            elif '0' <= key_name <= '9':
                key_code = getattr(Qt.Key, f"Key_{key_name}")
                self._virtual_keyboard.update_modifier_state(key_code, True)
                return
        
        # 使用映射查找键码
        if key_name in key_mapping:
            self._virtual_keyboard.update_modifier_state(key_mapping[key_name], True)
    
    def _setup_animations(self):
        """设置动画效果"""
        # 边框宽度动画
        self._border_width_animation = QPropertyAnimation(self, b"border_width")
        self._border_width_animation.setDuration(200)
        self._border_width_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 边框颜色动画
        self._border_color_animation = QPropertyAnimation(self, b"border_color")
        self._border_color_animation.setDuration(200)
        self._border_color_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 阴影强度动画
        self._shadow_animation = QPropertyAnimation(self, b"shadow_strength")
        self._shadow_animation.setDuration(200)
        self._shadow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 下拉按钮透明度动画
        self._dropdown_opacity_animation = QPropertyAnimation(self, b"dropdown_opacity")
        self._dropdown_opacity_animation.setDuration(200)
        self._dropdown_opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 创建动画组
        self._animation_group = QParallelAnimationGroup(self)
        self._animation_group.addAnimation(self._border_width_animation)
        self._animation_group.addAnimation(self._border_color_animation)
        self._animation_group.addAnimation(self._shadow_animation)
        self._animation_group.addAnimation(self._dropdown_opacity_animation)
    
    def _update_styles(self):
        """更新样式"""
        # 设置容器样式
        self._container.setStyleSheet(f"""
            QWidget#HotkeyContainer {{
                background-color: {self._bg_color.name()};
                border: {self._border_width}px solid {self._current_border_color.name()};
                border-radius: {self._border_radius}px;
            }}
        """)
        
        # 设置标签样式
        color = self._text_color if self._hotkey else self._placeholder_color
        self._label.setStyleSheet(f"""
            QLabel {{
                color: {color.name()};
                background-color: transparent;
                padding: 6px;
            }}
        """)
        
        # 应用阴影效果
        self._apply_shadow()
    
    def _apply_shadow(self):
        """应用阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(self._shadow_strength)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self._container.setGraphicsEffect(shadow)
    
    def _animate_focus(self, focused):
        """动画聚焦/失焦效果"""
        # 停止正在进行的动画
        self._animation_group.stop()
        
        # 设置边框宽度动画
        self._border_width_animation.setStartValue(self._border_width)
        self._border_width_animation.setEndValue(2.0 if focused else 1.0)
        
        # 设置边框颜色动画
        current_color = self._current_border_color
        target_color = self._focus_color if focused else self._primary_color
        self._border_color_animation.setStartValue(current_color)
        self._border_color_animation.setEndValue(target_color)
        
        # 设置阴影动画
        self._shadow_animation.setStartValue(self._shadow_strength)
        self._shadow_animation.setEndValue(8.0 if focused else 4.0)
        
        # 设置下拉按钮透明度动画
        self._dropdown_opacity_animation.setStartValue(self._dropdown_opacity)
        self._dropdown_opacity_animation.setEndValue(1.0 if focused else 0.0)
        
        # 启动动画组
        self._animation_group.start()
        
        # 显示下拉按钮（动画会控制透明度）
        self._dropdown_btn.setVisible(True)
    
    def _start_ripple_animation(self, position):
        """开始波纹动画"""
        # 保存波纹中心位置
        self._ripple_position = position
        
        # 计算最大半径（对角线长度）
        max_radius = int(((self.width() ** 2) + (self.height() ** 2)) ** 0.5)
        
        # 创建波纹动画
        ripple_animation = QPropertyAnimation(self, b"ripple_radius")
        ripple_animation.setStartValue(0)
        ripple_animation.setEndValue(max_radius)
        ripple_animation.setDuration(400)
        ripple_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 创建不透明度动画
        opacity_animation = QPropertyAnimation(self, b"ripple_opacity")
        opacity_animation.setStartValue(0.35)
        opacity_animation.setEndValue(0.0)
        opacity_animation.setDuration(400)
        opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 创建动画组
        ripple_group = QParallelAnimationGroup(self)
        ripple_group.addAnimation(ripple_animation)
        ripple_group.addAnimation(opacity_animation)
        
        # 连接动画完成信号
        ripple_group.finished.connect(self._on_ripple_finished)
        
        # 启动动画
        ripple_group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)
        
        # 触发重绘
        self.update()
    
    def _on_ripple_finished(self):
        """波纹动画完成处理"""
        self._ripple_radius = 0
        self._ripple_opacity = 0.0
        self.update()
    
    def _format_hotkey(self, modifiers, key):
        """格式化快捷键显示"""
        hotkey_parts = []
        
        # 添加修饰键
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            hotkey_parts.append(self._modifier_keys["ctrl"]["name"])
        if modifiers & Qt.KeyboardModifier.AltModifier:
            hotkey_parts.append(self._modifier_keys["alt"]["name"])
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            hotkey_parts.append(self._modifier_keys["shift"]["name"])
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            hotkey_parts.append(self._modifier_keys["meta"]["name"])
        
        # 添加键名（如果不是修饰键）
        key_name = self._get_key_name(key)
        if key_name and key not in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
            hotkey_parts.append(key_name)
        
        # 针对macOS，使用特殊连接符
        import sys
        if sys.platform == 'darwin':
            # macOS通常使用符号而不是+号
            return " ".join(hotkey_parts)
        else:
            # 其他系统使用+连接
            return "+".join(hotkey_parts)
    
    def set_hotkey(self, hotkey):
        """设置快捷键"""
        self._hotkey = hotkey
        
        if hotkey:
            self._label.setText(hotkey)
            self._label.setStyleSheet(f"color: {self._text_color.name()}; background: transparent;")
        else:
            self._label.setText(self._placeholder)
            self._label.setStyleSheet(f"color: {self._placeholder_color.name()}; background: transparent;")
        
        # 发射信号
        self.hotkeyChanged.emit(hotkey)
    
    def get_hotkey(self):
        """获取快捷键"""
        return self._hotkey
    
    def clear(self):
        """清除快捷键"""
        self.set_hotkey("")
    
    def set_placeholder(self, text):
        """设置占位符文本"""
        self._placeholder = text
        if not self._hotkey:
            self._label.setText(text)
    
    def keyPressEvent(self, event):
        """键盘按下事件"""
        if self._is_focused:
            # 获取按键和修饰键信息
            key = event.key()
            modifiers = event.modifiers()
            
            # 跟踪所有按下的键
            self._pressed_keys.add(key)
            
            # 处理修饰键
            if key in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
                self._pressed_modifiers.add(key)
                key_name = self._get_key_name(key)
                if key_name:
                    self.set_hotkey(key_name)
                
                # 如果虚拟键盘已显示，同步更新其状态
                if self._virtual_keyboard and self._virtual_keyboard.isVisible():
                    self._sync_keyboard_state_from_hotkey()
            else:
                # 格式化快捷键
                hotkey = self._format_hotkey(modifiers, key)
                if hotkey:
                    self.set_hotkey(hotkey)
            
            # 如果虚拟键盘已显示，同步更新所有按键状态
            if self._virtual_keyboard and self._virtual_keyboard.isVisible():
                self._sync_keyboard_state_from_hotkey()
            
            # 阻止事件继续传播
            event.accept()
        else:
            # 若组件未获取焦点，继续传播事件
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """键盘释放事件"""
        if self._is_focused:
            # 获取按键信息
            key = event.key()
            
            # 移除释放的键
            if key in self._pressed_keys:
                self._pressed_keys.remove(key)
            
            # 修饰键释放
            if key in self._pressed_modifiers:
                self._pressed_modifiers.remove(key)
            
            # 如果虚拟键盘已显示，同步更新所有按键状态
            if self._virtual_keyboard and self._virtual_keyboard.isVisible():
                self._sync_keyboard_state_from_hotkey()
            
            # 阻止事件继续传播
            event.accept()
        else:
            super().keyReleaseEvent(event)
    
    def event(self, event):
        """处理所有事件"""
        # 对于键盘事件特殊处理
        if event.type() in [QEvent.Type.KeyPress, QEvent.Type.KeyRelease, 
                          QEvent.Type.ShortcutOverride] and self._is_focused:
            # 显式接受快捷键覆盖事件以阻止系统快捷键
            if event.type() == QEvent.Type.ShortcutOverride:
                event.accept()
                return True
        
        return super().event(event)
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获各种事件"""
        # 处理鼠标事件
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                # 开始波纹动画
                self._start_ripple_animation(event.position().toPoint())
                # 获取焦点
                self.setFocus()
                event.accept()  # 明确接受事件
                return True
        
        # 在捕获各类键盘事件时，不让它们继续传播
        if self._is_focused and event.type() in [QEvent.Type.KeyPress, QEvent.Type.KeyRelease, 
                                               QEvent.Type.ShortcutOverride]:
            # 在函数开始就明确标记了事件被处理
            event.accept()
            
            if event.type() == QEvent.Type.KeyPress:
                # 处理键盘按下事件
                key = event.key()
                modifiers = event.modifiers()
                
                # 跟踪所有按下的键
                self._pressed_keys.add(key)
                
                # 特殊处理Win键 (Meta键)
                if key == Qt.Key.Key_Meta:
                    self._pressed_modifiers.add(key)
                    # 根据不同操作系统设置相应的名称
                    import sys
                    if sys.platform == 'darwin':
                        self.set_hotkey("⌘")  # macOS中的Command
                    elif sys.platform == 'win32':
                        self.set_hotkey("Win")  # Windows中的Win键
                    else:
                        self.set_hotkey("Super")  # Linux中的Super键
                    return True
                
                # 处理其他修饰键
                if key in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt]:
                    self._pressed_modifiers.add(key)
                    key_name = self._get_key_name(key)
                    if key_name:
                        self.set_hotkey(key_name)
                    return True
                
                # 处理组合键
                hotkey = self._format_hotkey(modifiers, key)
                if hotkey:
                    self.set_hotkey(hotkey)
                
                return True
            
            elif event.type() == QEvent.Type.KeyRelease:
                # 处理键盘释放事件
                key = event.key()
                
                # 移除释放的键
                if key in self._pressed_keys:
                    self._pressed_keys.remove(key)
                
                # 修饰键释放
                if key in self._pressed_modifiers:
                    self._pressed_modifiers.remove(key)
                
                return True
        
        return super().eventFilter(obj, event)
    
    def _get_key_name(self, key):
        """获取按键名称"""
        # 特殊键映射
        key_mapping = {
            Qt.Key.Key_Escape: "Esc",
            Qt.Key.Key_Tab: "Tab",
            Qt.Key.Key_Backtab: "Tab",
            Qt.Key.Key_Backspace: "Backspace",
            Qt.Key.Key_Return: "Enter",
            Qt.Key.Key_Enter: "Enter",
            Qt.Key.Key_Insert: "Insert",
            Qt.Key.Key_Delete: "Delete",
            Qt.Key.Key_Pause: "Pause",
            Qt.Key.Key_Print: "Print",
            Qt.Key.Key_Home: "Home",
            Qt.Key.Key_End: "End",
            Qt.Key.Key_Left: "Left",
            Qt.Key.Key_Up: "Up",
            Qt.Key.Key_Right: "Right",
            Qt.Key.Key_Down: "Down",
            Qt.Key.Key_PageUp: "PageUp",
            Qt.Key.Key_PageDown: "PageDown",
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_F1: "F1",
            Qt.Key.Key_F2: "F2",
            Qt.Key.Key_F3: "F3",
            Qt.Key.Key_F4: "F4",
            Qt.Key.Key_F5: "F5",
            Qt.Key.Key_F6: "F6",
            Qt.Key.Key_F7: "F7",
            Qt.Key.Key_F8: "F8",
            Qt.Key.Key_F9: "F9",
            Qt.Key.Key_F10: "F10",
            Qt.Key.Key_F11: "F11",
            Qt.Key.Key_F12: "F12",
            Qt.Key.Key_CapsLock: "CapsLock",
            Qt.Key.Key_NumLock: "NumLock",
            Qt.Key.Key_ScrollLock: "ScrollLock",
            # 添加修饰键映射 - 现在使用platform相关的名称
            Qt.Key.Key_Control: self._modifier_keys["ctrl"]["name"],
            Qt.Key.Key_Shift: self._modifier_keys["shift"]["name"],
            Qt.Key.Key_Alt: self._modifier_keys["alt"]["name"],
            Qt.Key.Key_Meta: self._modifier_keys["meta"]["name"],
            # ... 保留其他键映射 ...
        }
        
        # 检查是否是特殊键
        if key in key_mapping:
            return key_mapping[key]
        
        # 检查是否是基本按键 (字母、数字等)
        if 32 <= key <= 126:  # 可打印ASCII字符
            return chr(key).upper()
        
        # 小键盘按键
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            return str(key - Qt.Key.Key_0)
            
        # 如果是其他键，返回为空
        return ""


class HotkeyDemo(QWidget):
    """快捷键输入组件演示程序"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle("快捷键输入组件演示")
        self.setMinimumSize(600, 500)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 添加标题
        title_label = QLabel("快捷键输入组件演示", self)
        title_font = title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 添加说明文本
        desc_label = QLabel("点击输入框并按下快捷键组合，支持Ctrl、Alt、Shift和Win等修饰键", self)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # 添加描述
        virtual_desc = QLabel("点击输入框会显示一个下拉三角形，点击可打开虚拟键盘", self)
        virtual_desc.setStyleSheet("color: #0366d6")
        virtual_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(virtual_desc)
        
        # 创建滚动区域来容纳演示内容
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # 创建滚动区域的内容窗口
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # 添加按钮行
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 清空按钮
        clear_btn = QPushButton("清空所有快捷键", self)
        clear_btn.clicked.connect(self.clear_all_hotkeys)
        button_layout.addWidget(clear_btn)
        
        # 添加测试数据按钮
        test_btn = QPushButton("添加测试快捷键", self)
        test_btn.clicked.connect(self.add_test_hotkeys)
        button_layout.addWidget(test_btn)
        
        # 将按钮行添加到布局
        scroll_layout.addLayout(button_layout)
        
        # 保存所有快捷键输入组件的引用
        self.hotkey_inputs = []
        
        # 添加默认风格的快捷键输入组件
        scroll_layout.addWidget(QLabel("<b>默认风格</b>"))
        hotkey1, result1 = self.create_hotkey_section("点击此处输入快捷键")
        scroll_layout.addLayout(hotkey1)
        self.hotkey_inputs.append(result1)
        
        # 添加蓝色风格的快捷键输入组件
        scroll_layout.addWidget(QLabel("<b>蓝色风格</b>"))
        hotkey2, result2 = self.create_hotkey_section(
            "按下组合键...", 
            primary_color=[41, 128, 185], 
            focus_color=[52, 152, 219]
        )
        scroll_layout.addLayout(hotkey2)
        self.hotkey_inputs.append(result2)
        
        # 添加绿色风格的快捷键输入组件
        scroll_layout.addWidget(QLabel("<b>绿色风格</b>"))
        hotkey3, result3 = self.create_hotkey_section(
            "设置媒体播放快捷键", 
            primary_color=[46, 204, 113], 
            focus_color=[39, 174, 96]
        )
        scroll_layout.addLayout(hotkey3)
        self.hotkey_inputs.append(result3)
        
        # 添加红色风格的快捷键输入组件
        scroll_layout.addWidget(QLabel("<b>红色风格</b>"))
        hotkey4, result4 = self.create_hotkey_section(
            "录制新快捷键", 
            primary_color=[231, 76, 60], 
            focus_color=[192, 57, 43]
        )
        scroll_layout.addLayout(hotkey4)
        self.hotkey_inputs.append(result4)
        
        # 添加暗色风格的快捷键输入组件
        scroll_layout.addWidget(QLabel("<b>暗色风格</b>"))
        hotkey5, result5 = self.create_hotkey_section(
            "触发手势动作的快捷键", 
            primary_color=[52, 73, 94], 
            focus_color=[44, 62, 80],
            bg_color=[245, 245, 245]
        )
        scroll_layout.addLayout(hotkey5)
        self.hotkey_inputs.append(result5)
        
        # 设置滚动区域内容
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def create_hotkey_section(self, placeholder, primary_color=None, focus_color=None, bg_color=None):
        """创建一个快捷键输入区域"""
        # 创建水平布局
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # 创建快捷键输入组件
        hotkey_input = HotkeyInput(
            placeholder=placeholder,
            primary_color=primary_color,
            focus_color=focus_color,
            bg_color=bg_color
        )
        layout.addWidget(hotkey_input)
        
        # 创建结果标签
        result_label = QLabel("未设置", self)
        result_label.setMinimumWidth(150)
        result_label.setStyleSheet("background-color: #f8f9fa; padding: 8px; border-radius: 4px;")
        layout.addWidget(result_label)
        
        # 连接信号
        hotkey_input.hotkeyChanged.connect(
            lambda hotkey: result_label.setText(hotkey if hotkey else "未设置")
        )
        
        return layout, hotkey_input
    
    def clear_all_hotkeys(self):
        """清空所有快捷键输入组件"""
        for hotkey_input in self.hotkey_inputs:
            hotkey_input.clear()
    
    def add_test_hotkeys(self):
        """添加测试快捷键"""
        test_hotkeys = [
            "Ctrl",  # 现在可以显示单独的修饰键
            "Ctrl+Alt+Del",
            "Shift+F10",
            "Win",   # 现在可以显示单独的修饰键
            "Ctrl+Shift+Esc"
        ]
        
        for i, hotkey_input in enumerate(self.hotkey_inputs):
            if i < len(test_hotkeys):
                hotkey_input.set_hotkey(test_hotkeys[i])


# 测试代码，直接运行该文件时执行
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 创建演示窗口
    demo = HotkeyDemo()
    demo.show()
    
    sys.exit(app.exec()) 
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # 创建演示窗口
    demo = HotkeyDemo()
    demo.show()
    
    sys.exit(app.exec()) 