"""
主界面模块
功能：
- 启动/停止绘画窗口
- 系统托盘图标
- 状态提示
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from app.ink_painter import InkPainter

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.painter = None
        self._init_ui()

    def _init_ui(self):
        """初始化界面组件"""
        self.setWindowTitle("隐绘助手")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # 状态标签
        self.label = QLabel("点击按钮开始或停止绘画", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # 切换按钮
        self.toggle_btn = QPushButton("开始绘画", self)
        self.toggle_btn.clicked.connect(self.toggle_painting)
        self._set_button_style(self.toggle_btn, "#1F6AA5", "#144870")
        layout.addWidget(self.toggle_btn)

        # 退出按钮
        self.exit_btn = QPushButton("退出", self)
        self.exit_btn.clicked.connect(self.close)
        self._set_button_style(self.exit_btn, "#D32F2F", "#9A0000")
        layout.addWidget(self.exit_btn)

        self.setLayout(layout)

    def _set_button_style(self, button, normal_color, hover_color):
        """统一设置按钮样式"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {normal_color};
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 120px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

    def toggle_painting(self):
        """切换绘画状态"""
        if not self.painter:
            self.start_painting()
            self.toggle_btn.setText("停止绘画")
            self.label.setText("绘画已启动")
        else:
            self.stop_painting()
            self.toggle_btn.setText("开始绘画")
            self.label.setText("绘画已停止")

    def start_painting(self):
        """创建并显示绘画窗口"""
        self.painter = InkPainter()
        # 原逻辑中有 closed 信号连接，但新版 InkPainter 使用 root 窗口展示，所以此处省略该信号
        self.painter.root.show()

    def stop_painting(self):
        """关闭绘画窗口"""
        if self.painter:
            self.painter.shutdown()
            self.painter = None

    def on_painter_closed(self):
        """处理绘画窗口关闭信号"""
        self.painter = None
        self.toggle_btn.setText("开始绘画")
        self.label.setText("绘画已停止")
"""
主界面模块（PyQt5 实现）
功能：
- 启动/停止绘画窗口
- 系统托盘图标
- 状态提示
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from app.ink_painter import InkPainter

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.painter = None
        self._init_ui()

    def _init_ui(self):
        """初始化界面组件"""
        self.setWindowTitle("隐绘助手")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # 状态标签
        self.label = QLabel("点击按钮开始或停止绘画", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # 切换按钮
        self.toggle_btn = QPushButton("开始绘画", self)
        self.toggle_btn.clicked.connect(self.toggle_painting)
        self._set_button_style(self.toggle_btn, "#1F6AA5", "#144870")
        layout.addWidget(self.toggle_btn)

        # 退出按钮
        self.exit_btn = QPushButton("退出", self)
        self.exit_btn.clicked.connect(self.close)
        self._set_button_style(self.exit_btn, "#D32F2F", "#9A0000")
        layout.addWidget(self.exit_btn)

        self.setLayout(layout)

    def _set_button_style(self, button, normal_color, hover_color):
        """统一设置按钮样式"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {normal_color};
                color: white;
                border-radius: 5px;
                padding: 10px;
                min-width: 120px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

    def toggle_painting(self):
        """切换绘画状态"""
        if not self.painter:
            self.start_painting()
            self.toggle_btn.setText("停止绘画")
            self.label.setText("绘画已启动")
        else:
            self.stop_painting()
            self.toggle_btn.setText("开始绘画")
            self.label.setText("绘画已停止")

    def start_painting(self):
        """创建并显示绘画窗口"""
        self.painter = InkPainter()
        # 原逻辑中有 closed 信号连接，但新版 InkPainter 使用 root 窗口展示，所以此处省略该信号
        self.painter.root.show()

    def stop_painting(self):
        """关闭绘画窗口"""
        if self.painter:
            self.painter.shutdown()
            self.painter = None

    def on_painter_closed(self):
        """处理绘画窗口关闭信号"""
        self.painter = None
        self.toggle_btn.setText("开始绘画")
        self.label.setText("绘画已停止")

    def closeEvent(self, event):
        """重写关闭事件确保资源释放"""
        if self.painter:
            self.painter.shutdown()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 统一控件风格
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

    def closeEvent(self, event):
        """重写关闭事件确保资源释放"""
        if self.painter:
            self.painter.shutdown()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 统一控件风格
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
