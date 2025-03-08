# 文件路径: main.py
"""
主界面模块（基于 PyQt5 实现）

功能：
- 启动/停止绘画窗口（InkPainter）
- 系统托盘图标（可扩展）
- 状态提示

本示例通过 qfluentwidgets 实现全局美化效果，
只需导入并调用 setTheme(Theme.LIGHT)（或 Theme.DARK）即可生效。
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

# 使用 qfluentwidgets 美化控件
from qfluentwidgets import setTheme, Theme

# 假设 InkPainter 实现于 app.ink_painter 模块中
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
        layout.addWidget(self.toggle_btn)

        # 退出按钮
        self.exit_btn = QPushButton("退出", self)
        self.exit_btn.clicked.connect(self.close)
        layout.addWidget(self.exit_btn)

        self.setLayout(layout)

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
        # InkPainter 内部使用 root 窗口展示
        self.painter.root.show()

    def stop_painting(self):
        """关闭绘画窗口"""
        if self.painter:
            self.painter.shutdown()
            self.painter = None

    def closeEvent(self, event):
        """重写关闭事件确保资源释放"""
        if self.painter:
            self.painter.shutdown()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 应用 qfluentwidgets 全局主题（仅需1行代码）
    setTheme(Theme.DARK)  # 也可以选择 Theme.DARK
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
