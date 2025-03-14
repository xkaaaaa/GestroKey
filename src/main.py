import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                            QSystemTrayIcon, QMenu, QAction, QPushButton)
from PyQt5.QtGui import QCloseEvent, QIcon

# 绘画模块
from app.ink_painter import InkPainter

class MainWindow(QWidget):
    """主窗口类（简易版本，支持一键启动和托盘功能）"""
    
    def __init__(self):
        super().__init__()
        self.painter = None  # 绘画实例
        self.tray = None     # 托盘实例
        self._initUI()       # 构建界面
        self._initTray()     # 初始化托盘

    def _initUI(self):
        """构建简易布局界面"""
        self.setWindowTitle("GestroKey 隐绘助手")
        self.setWindowIcon(QIcon("img/icon/icon.ico"))  # 设置窗口图标
        self.setMinimumSize(300, 200)  # 最小尺寸限制

        # 使用弹性布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # 状态指示
        self.statusLabel = QWidget(self)
        self.statusLabel.setMinimumHeight(20)
        layout.addWidget(self.statusLabel)

        # 核心功能按钮组
        self._createControlButtons(layout)

    def _createControlButtons(self, layout):
        """创建操作按钮组"""
        # 绘画控制
        self.toggleBtn = QPushButton('开始绘画', self)
        self.toggleBtn.clicked.connect(self.toggle_painting)
        layout.addWidget(self.toggleBtn)

        # 系统功能
        self.exitBtn = QPushButton('退出程序', self)
        self.exitBtn.clicked.connect(self.clean_exit)
        layout.addWidget(self.exitBtn)

    def _initTray(self):
        """初始化托盘系统"""
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon("img/icon/icon.ico"))
        
        # 托盘菜单
        trayMenu = QMenu()
        trayMenu.addAction(QAction('显示主窗口', triggered=self.showNormal))
        trayMenu.addAction(QAction('开始/停止绘画', triggered=self.toggle_painting))
        trayMenu.addSeparator()
        trayMenu.addAction(QAction('退出', triggered=self.clean_exit))
        self.tray.setContextMenu(trayMenu)
        self.tray.show()

    def toggle_painting(self):
        """绘画状态切换（保留核心逻辑）"""
        if not self.painter:
            self.start_painting()
            self.toggleBtn.setText("停止绘画")
        else:
            self.stop_painting()
            self.toggleBtn.setText("开始绘画")

    def start_painting(self):
        """启动绘画窗口"""
        try:
            self.painter = InkPainter()
            self.painter.root.show()
        except Exception as e:
            print(f"启动失败：{str(e)}")

    def stop_painting(self):
        """安全停止绘画"""
        if self.painter:
            self.painter.shutdown()
            self.painter = None

    def clean_exit(self):
        """系统级退出"""
        self.stop_painting()
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent):
        """窗口关闭事件重写（实现最小化到托盘）"""
        if event.spontaneous():  # 系统关闭事件
            event.ignore()
            self.hide()
            self.tray.showMessage(
                "程序已最小化",
                "点击托盘图标恢复窗口",
                QSystemTrayIcon.Information,
                2000
            )

    def changeEvent(self, event):
        """窗口状态变更处理"""
        if event.type() == event.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()  # 最小化时隐藏窗口

if __name__ == "__main__":
    # 高DPI适配
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())