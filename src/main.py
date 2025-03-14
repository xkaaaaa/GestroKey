import sys
import os
import json
import psutil
import signal
import platform
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, QWidget, QVBoxLayout, QSplashScreen
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG, QThread, QTimer, QUrl, QByteArray
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from app.ink_painter import InkPainter
from app.web_server import WebServer
from app.log import log

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        log(__name__, "主窗口初始化")
        
        # 初始化系统托盘
        self._initTray()
        
        # 先初始化Web服务
        self._initWebServer()
        
        # 再初始化界面
        self._initUI()
        
        # 设置窗口属性
        self.painter = None
        self.setWindowTitle("GestroKey")
        
        # 加载图标
        icon_path = os.path.join(os.path.dirname(__file__), "app/ui/static/img/logo.svg")
        log(__name__, f"为窗口加载图标: {icon_path}")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            log(__name__, f"窗口图标文件不存在: {icon_path}", level="warning")
        
        self.setMinimumSize(900, 600)
        
        # 禁用窗口关闭按钮，改为最小化到托盘
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        
        # 设置窗口置顶
        self.settings = self._load_settings()
        if self.settings.get('force_topmost', True):
            self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        log(__name__, "主窗口初始化完成")
    
    def _initUI(self):
        """初始化用户界面"""
        log(__name__, "初始化用户界面")
        
        # 主布局
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建Web视图
        self.web_view = QWebEngineView()
        
        # 配置Web引擎设置
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        
        # 添加Web视图到布局
        self.layout.addWidget(self.web_view)
        
        # 先加载loading页面，等待Web服务器就绪
        self.web_view.load(QUrl("http://127.0.0.1:5000/"))
        
        # 页面加载完成后再跳转到控制台
        self.web_view.loadFinished.connect(self._on_first_load_finished)
        
        log(__name__, "用户界面初始化完成")
    
    def _on_first_load_finished(self, success):
        """首次页面加载完成的回调"""
        # 取消连接，避免多次触发
        self.web_view.loadFinished.disconnect(self._on_first_load_finished)
        
        # 稍等片刻，确保Web服务器完全就绪，然后跳转到控制台页面
        QTimer.singleShot(200, lambda: self.web_view.load(QUrl("http://127.0.0.1:5000/console")))
    
    def _initWebServer(self):
        """初始化Web服务器"""
        log(__name__, "初始化Web服务器")
        self.web_server = WebServer(self)
        self.web_server.start()
        log(__name__, "Web服务器初始化完成")
    
    def _initTray(self):
        """初始化系统托盘"""
        log(__name__, "初始化系统托盘")
        self.tray_icon = QSystemTrayIcon(self)
        
        # 加载托盘图标
        icon_path = os.path.join(os.path.dirname(__file__), "app/ui/static/img/logo.svg")
        log(__name__, f"为托盘加载图标: {icon_path}")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            log(__name__, f"托盘图标文件不存在: {icon_path}", level="warning")
            
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 绘画开关操作
        self.toggle_action = QAction("开始绘画", self)
        self.toggle_action.triggered.connect(self.toggle_painting)
        tray_menu.addAction(self.toggle_action)
        
        # 显示/隐藏主窗口操作
        self.show_action = QAction("显示主窗口", self)
        self.show_action.triggered.connect(self.show)
        tray_menu.addAction(self.show_action)
        
        # 退出操作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.clean_exit)
        tray_menu.addAction(exit_action)
        
        # 设置托盘菜单并显示
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
        
        log(__name__, "系统托盘初始化完成")
    
    def _on_tray_activated(self, reason):
        """响应托盘图标点击"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()
    
    def toggle_painting(self):
        """切换绘画状态"""
        log(__name__, "切换绘画状态")
        if self.painter is None:
            # 启动绘画
            try:
                log(__name__, "启动绘画")
                self.painter = InkPainter()
                self.painter.start_drawing()
                self.toggle_action.setText("停止绘画")
                log(__name__, "绘画已启动")
            except Exception as e:
                log(__name__, f"启动绘画失败：{str(e)}", level="error")
                print(f"启动绘画失败：{str(e)}")
        else:
            # 停止绘画
            try:
                log(__name__, "停止绘画")
                self.painter.stop_drawing()
                self.painter = None
                self.toggle_action.setText("开始绘画")
                log(__name__, "绘画已停止")
            except Exception as e:
                log(__name__, f"停止绘画失败：{str(e)}", level="error")
                print(f"停止绘画失败：{str(e)}")
    
    def show(self):
        """显示主窗口"""
        super().show()
        self.show_action.setText("隐藏主窗口")
        log(__name__, "显示主窗口")
        
        # 更新显示状态
        # QMetaObject调用可能不存在的方法会导致错误，暂时注释掉
        # QMetaObject.invokeMethod(
        #     self, 
        #     "activate", 
        #     Qt.QueuedConnection
        # )
    
    def hide(self):
        """隐藏主窗口"""
        super().hide()
        self.show_action.setText("显示主窗口")
        log(__name__, "隐藏主窗口")
        
        # 更新显示状态
        # QMetaObject调用可能不存在的方法会导致错误，暂时注释掉
        # QMetaObject.invokeMethod(
        #     self, 
        #     "deactivate", 
        #     Qt.QueuedConnection
        # )
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 关闭窗口时最小化到托盘而不是退出
        event.ignore()
        self.hide()
        log(__name__, "窗口关闭请求 - 已最小化到托盘")
    
    def clean_exit(self):
        """干净地退出应用程序"""
        log(__name__, "应用程序退出")
        if self.painter is not None:
            try:
                self.painter.stop_drawing()
                self.painter = None
                log(__name__, "绘画已停止")
            except Exception as e:
                log(__name__, f"停止绘画失败：{str(e)}", level="error")
        
        # 停止Web服务器
        if hasattr(self, "web_server"):
            self.web_server.stop()
            log(__name__, "Web服务器已停止")
        
        # 退出应用
        QApplication.quit()
    
    def _load_settings(self):
        """加载设置"""
        log(__name__, "加载设置")
        settings_path = self._get_settings_path()
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                log(__name__, "设置加载成功")
                return config['drawing_settings']
        except Exception as e:
            log(__name__, f"加载设置失败: {str(e)}", level="error")
            print(f"加载设置失败: {str(e)}")
            # 返回默认设置
            return {
                'force_topmost': True,
                'enable_hardware_acceleration': True,
            }
    
    def _get_settings_path(self):
        """获取设置文件路径"""
        # 与ink_painter中相同的逻辑
        import sys
        if getattr(sys, 'frozen', False):
            # 打包后使用exe所在目录的上二级目录
            return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'settings.json')
        else:
            # 开发时使用当前文件的上一级目录（src → 根目录）
            return os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'settings.json'
            )

def main():
    """主函数"""
    log(__name__, "程序启动")
    
    # 设置应用程序ID (Windows)
    if platform.system() == 'Windows':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GestroKey")
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 显示启动画面
    splash_pixmap = QPixmap(400, 300)
    splash_pixmap.fill(Qt.white)
    painter = QPainter(splash_pixmap)
    painter.setPen(QColor(0, 0, 0))
    painter.setFont(QFont('Arial', 14))
    
    # 绘制图标
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app/ui/static/img/logo.svg")
    log(__name__, f"加载图标: {icon_path}")
    
    # 检查文件是否存在
    if not os.path.exists(icon_path):
        log(__name__, f"图标文件不存在: {icon_path}", level="error")
        # 使用空白图标
        icon = QIcon()
    else:
        icon = QIcon(icon_path)
    
    icon_pixmap = icon.pixmap(64, 64)
    painter.drawPixmap(168, 80, icon_pixmap)
    
    # 绘制文本
    painter.drawText(120, 180, "GestroKey 正在启动...")
    painter.end()
    
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()
    
    # 创建主窗口
    window = MainWindow()
    
    # 显示主窗口
    window.show()
    
    # 关闭启动画面
    splash.finish(window)
    
    log(__name__, "主窗口已显示，程序初始化完成")
    
    # 设置中断处理
    def signal_handler(sig, frame):
        window.clean_exit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()