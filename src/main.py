import sys
import os
import json
import psutil
import signal
import platform
import ctypes
from ctypes import wintypes
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, QWidget, QVBoxLayout, QSplashScreen, QLabel, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG, QThread, QTimer, QUrl, QByteArray, QPropertyAnimation, QEasingCurve, QSize, QRect, QEvent
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter, QFont, QMovie
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from app.ink_painter import InkPainter
from app.web_server import WebServer
from app.log import log

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.file_name = "splash_screen"
        log(self.file_name, "初始化启动画面")
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 窗口大小
        self.setFixedSize(400, 300)
        
        # 居中显示
        self.center()
        
        # 初始化UI
        self.init_ui()
        
        log(self.file_name, "启动画面初始化完成")
        
    def init_ui(self):
        """初始化UI元素"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 应用图标
        icon_label = QLabel(self)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app/ui/static/img/logo.svg")
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # 应用名称
        title_label = QLabel("GestroKey", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D3748; margin-top: 10px;")
        
        # 加载动画
        self.loading_label = QLabel(self)
        self.loading_label.setFixedSize(40, 40)
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        loading_gif_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app/ui/static/img/loading.gif")
        
        # 检查加载动画文件是否存在，不存在则使用文本替代
        if os.path.exists(loading_gif_path):
            self.loading_movie = QMovie(loading_gif_path)
            self.loading_movie.setScaledSize(QSize(40, 40))
            self.loading_label.setMovie(self.loading_movie)
            self.loading_movie.start()
        else:
            log(self.file_name, f"加载动画文件不存在: {loading_gif_path}", level="warning")
            # 创建动态加载文本效果
            self.loading_text = "正在加载"
            self.dots = 0
            self.loading_timer = QTimer(self)
            self.loading_timer.timeout.connect(self.update_loading_text)
            self.loading_timer.start(500)
            self.loading_label.setText(self.loading_text)
            self.loading_label.setStyleSheet("font-size: 16px; color: #4A5568;")
        
        # 状态标签
        self.status_label = QLabel("正在启动系统...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #4A5568; margin-top: 10px;")
        
        # 水平居中包装容器
        loading_container = QWidget()
        loading_layout = QHBoxLayout(loading_container)
        loading_layout.addStretch()
        loading_layout.addWidget(self.loading_label)
        loading_layout.addStretch()
        
        # 添加到布局
        layout.addStretch()
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addSpacing(15)  # 增加间距
        layout.addWidget(loading_container)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # 设置背景样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #E2E8F0;
            }
        """)
        
    def update_loading_text(self):
        """更新加载文本动画"""
        self.dots = (self.dots + 1) % 4
        dots_text = "." * self.dots
        self.loading_label.setText(f"{self.loading_text}{dots_text}")
        
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.setText(message)
        log(self.file_name, f"更新启动状态: {message}")
        
    def center(self):
        """窗口居中显示"""
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
    def closeEvent(self, event):
        """关闭事件处理"""
        if hasattr(self, "loading_movie") and self.loading_movie:
            self.loading_movie.stop()
        if hasattr(self, "loading_timer") and self.loading_timer:
            self.loading_timer.stop()
        log(self.file_name, "启动画面关闭")

class MainWindow(QMainWindow):
    def __init__(self):
        # 使用简单的初始化方式
        super().__init__()
        log(__name__, "主窗口初始化")
        
        # 保存窗口大小和位置
        self.saved_geometry = None
        
        # 设置窗口标题
        self.setWindowTitle("GestroKey")
        
        # 初始化painter
        self.painter = None
        
        # 设置窗口大小范围，不再使用固定大小
        self.setMinimumSize(800, 600)  # 最小尺寸
        self.setMaximumSize(1600, 1200)  # 最大尺寸
        self.resize(1000, 700)  # 初始大小
        self.is_maximized = False
        
        # 加载设置
        self.settings = self._load_settings()
        
        # 初始化系统托盘
        self._initTray()
        
        # 初始化Web服务
        self._initWebServer()
        
        # 初始化界面
        self._initUI()
        
        # 加载图标
        icon_path = os.path.join(os.path.dirname(__file__), "app/ui/static/img/logo.svg")
        log(__name__, f"为窗口加载图标: {icon_path}")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            log(__name__, f"窗口图标文件不存在: {icon_path}", level="warning")
        
        # 如果需要窗口置顶
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
        # 确保先销毁旧的托盘图标（如果存在）
        try:
            if hasattr(self, 'tray_icon') and self.tray_icon is not None:
                try:
                    self.tray_icon.activated.disconnect()  # 断开信号连接
                except:
                    pass
                self.tray_icon.hide()
                self.tray_icon.deleteLater()
                # 给QT事件循环一些时间处理删除操作
                QApplication.processEvents()
        except Exception as e:
            log(__name__, f"清理旧托盘图标时出错: {str(e)}", level="warning")
        
        # 创建新的托盘图标实例
        self.tray_icon = QSystemTrayIcon(self)
        
        # 加载托盘图标
        icon_path = os.path.join(os.path.dirname(__file__), "app/ui/static/img/logo.svg")
        log(__name__, f"为托盘加载图标: {icon_path}")
        if os.path.exists(icon_path):
            tray_icon = QIcon(icon_path)
            self.tray_icon.setIcon(tray_icon)
        else:
            log(__name__, f"托盘图标文件不存在: {icon_path}", level="warning")
            # 尝试使用备用图标
            self.tray_icon.setIcon(QIcon.fromTheme("application-x-executable"))
            
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 绘画开关操作 - 添加安全检查
        painter_exists = hasattr(self, 'painter')
        self.toggle_action = QAction("开始绘画" if not painter_exists or self.painter is None else "停止绘画", self)
        self.toggle_action.triggered.connect(self.toggle_painting)
        tray_menu.addAction(self.toggle_action)
        
        # 显示/隐藏主窗口操作
        is_visible = self.isVisible() and not self.isMinimized()
        self.show_action = QAction("隐藏主窗口" if is_visible else "显示主窗口", self)
        self.show_action.triggered.connect(self.show if not is_visible else self.hide)
        tray_menu.addAction(self.show_action)
        
        # 退出操作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.clean_exit)
        tray_menu.addAction(exit_action)
        
        # 设置托盘菜单并显示
        self.tray_icon.setContextMenu(tray_menu)
        
        # 绑定托盘图标的激活信号
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # 设置工具提示
        self.tray_icon.setToolTip("GestroKey")
        
        # 确保托盘图标显示
        self.tray_icon.show()
        
        # 验证托盘图标是否可见
        if not self.tray_icon.isVisible():
            log(__name__, "警告：托盘图标创建后不可见", level="warning")
            # 尝试再次显示
            QTimer.singleShot(500, self.tray_icon.show)
        
        log(__name__, "系统托盘初始化完成，已设置点击事件")
    
    def _on_tray_activated(self, reason):
        """响应托盘图标点击"""
        try:
            # 转换reason为字符串形式以便调试
            reason_str = "未知"
            if reason == QSystemTrayIcon.Trigger:
                reason_str = "左键单击(Trigger)"
            elif reason == QSystemTrayIcon.DoubleClick:
                reason_str = "双击(DoubleClick)"
            elif reason == QSystemTrayIcon.MiddleClick:
                reason_str = "中键点击(MiddleClick)"
            elif reason == QSystemTrayIcon.Context:
                reason_str = "右键菜单(Context)"
            elif reason == QSystemTrayIcon.Unknown:
                reason_str = "未知(Unknown)"

            log(__name__, f"托盘图标激活，原因: {reason} ({reason_str})")
            
            if reason == QSystemTrayIcon.Trigger:  # 左键单击
                log(__name__, "托盘图标左键单击 - 切换绘画状态")
                # 使用try-except包装以避免异常导致托盘失效
                try:
                    # 直接调用而不是使用Timer，可能是Timer导致的问题
                    self.toggle_painting()
                except Exception as e:
                    log(__name__, f"切换绘画状态时出错: {str(e)}", level="error")
                    # 显示错误通知
                    self._show_error_message(f"切换绘画状态时出错: {str(e)}")
            
            elif reason == QSystemTrayIcon.DoubleClick:  # 双击
                log(__name__, "托盘图标双击 - 显示主窗口")
                try:
                    # 直接调用显示窗口方法
                    self._show_and_activate()
                except Exception as e:
                    log(__name__, f"显示窗口时出错: {str(e)}", level="error")
                    self._show_error_message(f"显示窗口时出错: {str(e)}")
            
            elif reason == QSystemTrayIcon.MiddleClick:  # 中键点击
                log(__name__, "托盘图标中键点击 - 显示状态信息")
                try:
                    # 直接显示状态信息
                    self._show_status_message()
                except Exception as e:
                    log(__name__, f"显示状态信息时出错: {str(e)}", level="error")
        
        except Exception as e:
            log(__name__, f"处理托盘图标事件时发生严重错误: {str(e)}", level="error")
            # 尝试重新初始化托盘图标
            QTimer.singleShot(500, self._initTray)
    
    def _show_error_message(self, message):
        """显示错误消息"""
        try:
            self.tray_icon.showMessage(
                "GestroKey错误",
                message,
                QSystemTrayIcon.Critical,
                3000
            )
        except:
            # 如果连通知都不能显示，至少打印到控制台
            print(f"错误: {message}")
            log(__name__, f"无法显示错误通知: {message}", level="error")
    
    def _show_and_activate(self):
        """显示窗口并激活"""
        self.showNormal()
        self.activateWindow()
        self.show_action.setText("隐藏主窗口")
        log(__name__, "显示并激活主窗口")
    
    def _show_status_message(self):
        """显示状态消息"""
        painting_status = "开启" if self.painter is not None else "关闭"
        self.tray_icon.showMessage(
            "GestroKey 状态",
            f"绘画模式: {painting_status}\n应用版本: 1.0.0",
            QSystemTrayIcon.Information,
            2000
        )

    def toggle_painting(self):
        """切换绘画状态"""
        log(__name__, "切换绘画状态")
        try:
            if self.painter is None:
                # 启动绘画
                try:
                    log(__name__, "正在启动绘画...")
                    self.painter = InkPainter()
                    # 确保是最新设置
                    self.painter.load_drawing_settings()
                    start_result = self.painter.start_drawing()
                    log(__name__, f"启动绘画结果: {start_result}")
                    self.toggle_action.setText("停止绘画")
                    
                    # 显示启动成功通知
                    self.tray_icon.showMessage(
                        "GestroKey",
                        "绘画模式已启动",
                        QSystemTrayIcon.Information,
                        2000
                    )
                    log(__name__, "绘画已启动")
                except Exception as e:
                    log(__name__, f"启动绘画失败：{str(e)}", level="error")
                    # 显示错误通知
                    self.tray_icon.showMessage(
                        "GestroKey错误",
                        f"启动绘画失败：{str(e)}",
                        QSystemTrayIcon.Critical,
                        3000
                    )
                    print(f"启动绘画失败：{str(e)}")
            else:
                # 停止绘画
                try:
                    log(__name__, "正在停止绘画...")
                    stop_result = self.painter.stop_drawing()
                    log(__name__, f"停止绘画结果: {stop_result}")
                    self.painter = None
                    self.toggle_action.setText("开始绘画")
                    
                    # 显示停止成功通知
                    self.tray_icon.showMessage(
                        "GestroKey",
                        "绘画模式已停止",
                        QSystemTrayIcon.Information,
                        2000
                    )
                    log(__name__, "绘画已停止")
                except Exception as e:
                    log(__name__, f"停止绘画失败：{str(e)}", level="error")
                    # 显示错误通知
                    self.tray_icon.showMessage(
                        "GestroKey错误",
                        f"停止绘画失败：{str(e)}",
                        QSystemTrayIcon.Critical,
                        3000
                    )
                    print(f"停止绘画失败：{str(e)}")
        except Exception as e:
            log(__name__, f"切换绘画状态时发生错误: {str(e)}", level="error")
            self.tray_icon.showMessage(
                "GestroKey错误",
                f"切换绘画状态失败：{str(e)}",
                QSystemTrayIcon.Critical,
                3000
            )
    
    def show(self):
        """显示主窗口"""
        log(__name__, "准备显示主窗口")
        
        if self.isMinimized():
            # 从最小化状态恢复
            super().showNormal()
        else:
            # 正常显示
            super().show()
        
        self.activateWindow()  # 确保窗口获得焦点
        self.show_action.setText("隐藏主窗口")
        log(__name__, "主窗口已显示")
    
    def hide(self):
        """隐藏主窗口"""
        log(__name__, "隐藏主窗口")
        super().hide()
        self.show_action.setText("显示主窗口")
        # 隐藏窗口后确保托盘图标响应
        QTimer.singleShot(100, self._ensure_tray_responsive)
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 关闭窗口时不直接退出，而是触发网页中的确认对话框
        log(__name__, "窗口关闭请求 - 显示确认对话框")
        event.ignore()  # 忽略关闭事件
        
        # 通过JavaScript执行网页中的确认对话框函数
        js_code = """
        if (typeof showConfirm === 'function') {
            showConfirm('您确定要退出应用程序吗?', function() {
                fetch('/api/exit', { method: 'POST' });
            });
        } else {
            console.error('showConfirm函数未定义');
            fetch('/api/exit', { method: 'POST' });
        }
        """
        self.web_view.page().runJavaScript(js_code)
        log(__name__, "已显示退出确认对话框")

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

    def minimize_window(self):
        """最小化窗口"""
        log(__name__, "窗口最小化")
        # 使用标准的窗口最小化功能
        self.showMinimized()
        return {"success": True}
    
    def _ensure_tray_responsive(self):
        """确保托盘图标保持响应状态"""
        log(__name__, "检查托盘图标状态...")
        try:
            if not hasattr(self, 'tray_icon') or self.tray_icon is None or not self.tray_icon.isVisible():
                log(__name__, "托盘图标状态异常，重新初始化", level="warning")
                self._initTray()
            else:
                # 重新连接信号，确保托盘图标能接收点击事件
                try:
                    self.tray_icon.activated.disconnect()
                except:
                    pass
                self.tray_icon.activated.connect(self._on_tray_activated)
                log(__name__, "托盘图标状态正常")
        except Exception as e:
            log(__name__, f"确保托盘响应时出错: {str(e)}", level="error")
            print(f"托盘图标错误: {str(e)}")
        
    def changeEvent(self, event):
        """处理窗口状态改变事件"""
        try:
            if event.type() == QEvent.WindowStateChange:
                log(__name__, f"窗口状态改变: {self.windowState()}")
                # 如果窗口从最小化状态恢复
                if self.windowState() & Qt.WindowMinimized:
                    log(__name__, "窗口从最小化状态恢复")
                    # 更新托盘菜单显示状态
                    self.show_action.setText("隐藏主窗口")
                elif self.windowState() == Qt.WindowNoState and not self.isVisible():
                    log(__name__, "窗口处于正常状态但不可见")
                    # 如果窗口恢复但不可见，则显示它
                    self.show()
        except Exception as e:
            log(__name__, f"处理窗口状态改变事件出错: {str(e)}", level="error")
        super().changeEvent(event)

    def showEvent(self, event):
        """窗口显示事件处理"""
        super().showEvent(event)
        log(__name__, "窗口显示事件处理完成")

    def nativeEvent(self, eventType, message):
        """处理底层平台事件"""
        # 直接让Qt处理事件，不做额外干预
        return super().nativeEvent(eventType, message)

def check_files():
    """检查必要文件是否存在"""
    log(__name__, "开始检查必要文件")
    
    # 检查设置文件
    settings_path = get_settings_path()
    if not os.path.exists(settings_path):
        log(__name__, f"设置文件不存在，需要创建: {settings_path}")
        ensure_settings_file(settings_path)
    else:
        log(__name__, f"设置文件已存在: {settings_path}")
    
    # 检查手势库文件
    gestures_path = get_gestures_path()
    if not os.path.exists(gestures_path):
        log(__name__, f"手势库文件不存在，需要创建: {gestures_path}")
        ensure_gestures_file(gestures_path)
    else:
        log(__name__, f"手势库文件已存在: {gestures_path}")
    
    log(__name__, "文件检查完成")
    return True

def ensure_settings_file(settings_path):
    """确保设置文件存在"""
    try:
        # 确保目录存在
        settings_dir = os.path.dirname(settings_path)
        os.makedirs(settings_dir, exist_ok=True)
        
        # 默认设置
        default_settings = {
            "drawing_settings": {
                "base_width": 6,
                "min_width": 3,
                "max_width": 15,
                "speed_factor": 1.2,
                "fade_duration": 0.5,
                "antialias_layers": 2,
                "min_distance": 20,
                "line_color": "#00BFFF",
                "max_stroke_points": 200,
                "max_stroke_duration": 5,
                "enable_advanced_brush": True,
                "force_topmost": True,
                "enable_auto_smoothing": True,
                "smoothing_factor": 0.6,
                "enable_hardware_acceleration": True
            }
        }
        
        # 写入文件
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, ensure_ascii=False, indent=4)
            
        log(__name__, f"成功创建设置文件: {settings_path}")
        return True
    except Exception as e:
        log(__name__, f"创建设置文件失败: {str(e)}", level="error")
        return False

def ensure_gestures_file(gestures_path):
    """确保手势库文件存在"""
    try:
        # 确保目录存在
        gestures_dir = os.path.dirname(gestures_path)
        os.makedirs(gestures_dir, exist_ok=True)
        
        # 默认手势库
        default_gestures = {
            "gestures": {
                "上": {
                    "directions": "↑",
                    "action": "cGFzc2FwcC5taW5pbWl6ZV9hbGwoKQ=="  # base64编码的"passapp.minimize_all()"
                },
                "下": {
                    "directions": "↓",
                    "action": "cGFzc2FwcC5yZXN0b3JlX2FsbCgp"  # base64编码的"passapp.restore_all()"
                },
                "左": {
                    "directions": "←",
                    "action": "cGFzc2FwcC5wcmV2X3dpbmRvdygp"  # base64编码的"passapp.prev_window()"
                },
                "右": {
                    "directions": "→",
                    "action": "cGFzc2FwcC5uZXh0X3dpbmRvdygp"  # base64编码的"passapp.next_window()"
                }
            }
        }
        
        # 写入文件
        with open(gestures_path, 'w', encoding='utf-8') as f:
            json.dump(default_gestures, f, ensure_ascii=False, indent=4)
            
        log(__name__, f"成功创建手势库文件: {gestures_path}")
        return True
    except Exception as e:
        log(__name__, f"创建手势库文件失败: {str(e)}", level="error")
        return False

def get_settings_path():
    """获取设置文件路径"""
    if getattr(sys, 'frozen', False):
        # 打包后使用exe所在目录的上二级目录
        return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'settings.json')
    else:
        # 开发时使用当前文件的上一级目录（src → 根目录）
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'settings.json'
        )

def get_gestures_path():
    """获取手势库文件路径"""
    if getattr(sys, 'frozen', False):
        # 打包后使用exe所在目录的上二级目录
        return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'gestures.json')
    else:
        # 开发时使用当前文件的上一级目录（src → 根目录）
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'gestures.json'
        )

def main():
    """主函数"""
    log(__name__, "程序启动")
    
    # 设置应用程序ID (Windows)
    if platform.system() == 'Windows':
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GestroKey")
        except Exception as e:
            log(__name__, f"设置应用程序ID失败: {str(e)}", level="warning")
    
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 检查是否是开机自启
    is_autostart = '--autostart' in sys.argv
    
    # 执行必要的文件检查
    log(__name__, "检查必要文件")
    check_files()
    
    # 创建主窗口
    log(__name__, "创建主窗口")
    window = MainWindow()
    
    # 如果是开机自启，则自动启动绘画并最小化到托盘
    if is_autostart:
        log(__name__, "检测到自动启动参数，自动启动绘画并最小化到托盘")
        # 使用QTimer延迟执行，确保窗口和托盘已完全初始化
        QTimer.singleShot(1000, lambda: window.toggle_painting())
        QTimer.singleShot(1500, lambda: window.hide())
    else:
        # 正常显示主窗口
        window.show()
    
    log(__name__, "程序初始化完成，进入事件循环")
    
    # 设置中断处理
    def signal_handler(sig, frame):
        window.clean_exit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()