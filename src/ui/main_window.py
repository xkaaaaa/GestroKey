import os
import sys
import time
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                              QStackedWidget, QLabel, QSizePolicy, QGraphicsDropShadowEffect,
                              QSystemTrayIcon, QMenu, QAction, QMessageBox, QPushButton,
                              QFrame, QToolButton, QApplication, QStyleFactory)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QIcon, QColor, QFont, QPalette, QPixmap, QCursor, QPainter, QPen, QBrush

# 导入自定义组件
from ui.sidebar import Sidebar
from ui.pages.console_page import ConsolePage
from ui.pages.settings_page import SettingsPage
from ui.pages.gestures_page import GesturesPage
from ui.utils.icon_utils import svg_to_ico

# 导入手势管理器
from ui.utils.gesture_manager import GestureManager

# 导入日志模块
from app.log import log

# 导入版本信息
try:
    from version import __version__, __title__, __copyright__, get_about_text
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from version import __version__, __title__, __copyright__, get_about_text

# 设置日志
log = logging.getLogger(__name__)

class TitleBar(QFrame):
    """自定义标题栏"""
    
    # 定义信号
    windowClose = pyqtSignal()  # 窗口关闭信号
    windowMinimize = pyqtSignal()  # 窗口最小化信号
    windowMaximize = pyqtSignal()  # 窗口最大化信号
    
    def __init__(self, parent=None):
        """初始化标题栏
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # 设置固定高度
        self.setFixedHeight(48)
        
        # 设置标题栏样式
        self.setStyleSheet("""
            TitleBar {
                background-color: #F8F9FA;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid #E0E4E8;
            }
            
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2D3748;
            }
            
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            
            QToolButton:pressed {
                background-color: rgba(0, 0, 0, 0.1);
            }
            
            #closeButton:hover {
                background-color: #FD5D5D;
                color: white;
            }
            
            #closeButton:pressed {
                background-color: #CF4545;
            }
        """)
        
        # 初始化UI
        self.init_ui()
        
        # 鼠标跟踪标志
        self._is_tracking = False
        self._start_pos = QPoint(0, 0)
        self._window_pos = QPoint(0, 0)
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        log.debug("自定义标题栏初始化完成")
        
    def init_ui(self):
        """初始化UI组件"""
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)
        
        # 应用图标
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/logo.svg")
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            log.warning(f"找不到应用图标: {icon_path}")
        
        # 版本标签
        try:
            version_text = f"v{__version__}"
            self.version_label = QLabel(version_text)
            self.version_label.setStyleSheet("color: #718096; font-size: 12px; font-weight: normal;")
        except:
            self.version_label = QLabel()
            
        # 添加图标和版本号
        layout.addWidget(self.icon_label)
        layout.addSpacing(8)
        layout.addWidget(self.version_label)
        
        # 弹性空间
        layout.addStretch()
        
        # 窗口控制按钮
        btn_size = QSize(32, 32)
        
        # 获取图标路径
        minimize_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/minimize.svg")
        maximize_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/maximize.svg")
        restore_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/restore.svg")
        close_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/close.svg")
        
        # 最小化按钮
        self.minimize_button = QToolButton()
        self.minimize_button.setFixedSize(btn_size)
        if os.path.exists(minimize_icon_path):
            self.minimize_button.setIcon(QIcon(minimize_icon_path))
        else:
            self.minimize_button.setIcon(self.style().standardIcon(self.style().SP_TitleBarMinButton))
            log.warning(f"找不到最小化图标: {minimize_icon_path}，使用系统默认图标")
        self.minimize_button.setIconSize(QSize(16, 16))
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setToolTip("最小化")
        self.minimize_button.clicked.connect(self.windowMinimize.emit)
        
        # 最大化/还原按钮
        self.maximize_button = QToolButton()
        self.maximize_button.setFixedSize(btn_size)
        if os.path.exists(maximize_icon_path):
            self.maximize_icon = QIcon(maximize_icon_path)
            self.restore_icon = QIcon(restore_icon_path) if os.path.exists(restore_icon_path) else self.style().standardIcon(self.style().SP_TitleBarNormalButton)
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.maximize_icon = self.style().standardIcon(self.style().SP_TitleBarMaxButton)
            self.restore_icon = self.style().standardIcon(self.style().SP_TitleBarNormalButton)
            self.maximize_button.setIcon(self.maximize_icon)
            log.warning(f"找不到最大化图标: {maximize_icon_path}，使用系统默认图标")
        self.maximize_button.setIconSize(QSize(16, 16))
        self.maximize_button.setCursor(Qt.PointingHandCursor)
        self.maximize_button.setToolTip("最大化")
        self.maximize_button.clicked.connect(self.windowMaximize.emit)
        
        # 关闭按钮
        self.close_button = QToolButton()
        self.close_button.setFixedSize(btn_size)
        if os.path.exists(close_icon_path):
            self.close_button.setIcon(QIcon(close_icon_path))
        else:
            self.close_button.setIcon(self.style().standardIcon(self.style().SP_TitleBarCloseButton))
            log.warning(f"找不到关闭图标: {close_icon_path}，使用系统默认图标")
        self.close_button.setIconSize(QSize(16, 16))
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setToolTip("关闭")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.windowClose.emit)
        
        # 添加控制按钮
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)
        
    def update_maximized_state(self, is_maximized):
        """更新最大化状态
        
        Args:
            is_maximized: 是否最大化
        """
        if is_maximized:
            # 使用还原图标
            if hasattr(self, 'restore_icon'):
                self.maximize_button.setIcon(self.restore_icon)
            else:
                self.maximize_button.setIcon(self.style().standardIcon(self.style().SP_TitleBarNormalButton))
                log.debug("使用系统默认还原图标")
            self.maximize_button.setToolTip("还原")
            self.setStyleSheet(self.styleSheet().replace("border-top-left-radius: 10px;", "border-top-left-radius: 0px;")
                               .replace("border-top-right-radius: 10px;", "border-top-right-radius: 0px;"))
        else:
            # 使用最大化图标
            if hasattr(self, 'maximize_icon'):
                self.maximize_button.setIcon(self.maximize_icon)
            else:
                self.maximize_button.setIcon(self.style().standardIcon(self.style().SP_TitleBarMaxButton))
                log.debug("使用系统默认最大化图标")
            self.maximize_button.setToolTip("最大化")
            self.setStyleSheet(self.styleSheet().replace("border-top-left-radius: 0px;", "border-top-left-radius: 10px;")
                               .replace("border-top-right-radius: 0px;", "border-top-right-radius: 10px;"))
        
        # 确保样式更新
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
        log.debug(f"标题栏最大化状态已更新: {is_maximized}")
            
    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self.windowMaximize.emit()
            log.debug("标题栏双击: 触发最大化/还原")
        
    def mousePressEvent(self, event):
        """处理鼠标按下事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self._is_tracking = True
            self._start_pos = event.globalPos()
            self._window_pos = self.window().pos()
            
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件
        
        Args:
            event: 鼠标事件
        """
        if self._is_tracking and (event.buttons() == Qt.LeftButton):
            # 如果窗口最大化，移动时先恢复正常大小
            if self.window().isMaximized():
                # 恢复正常大小后，根据鼠标点击位置计算新的窗口位置
                relative_pos = event.pos()
                width_ratio = relative_pos.x() / self.width()
                
                log.debug("窗口从最大化状态拖动: 正在还原")
                self.windowMaximize.emit()  # 还原窗口
                
                # 计算新的起始位置，使鼠标保持在点击的相对位置
                new_width = self.window().width()
                new_x = event.globalPos().x() - (new_width * width_ratio)
                new_y = event.globalPos().y() - (relative_pos.y())
                
                self.window().move(int(new_x), int(new_y))
                self._window_pos = self.window().pos()
                self._start_pos = event.globalPos()
            else:
                # 计算移动距离
                delta = event.globalPos() - self._start_pos
                # 移动窗口
                self.window().move(self._window_pos + delta)
                
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self._is_tracking = False
            
    def update_title(self, title):
        """更新标题文本
        
        Args:
            title: 新标题
        """
        # 直接返回，不再更新标题（因为标题标签已移除）
        log.debug(f"标题更新请求被忽略: {title}")
        return

class MainWindow(QMainWindow):
    """主窗口类，包含侧边栏和主要内容区域"""
    
    # 信号定义
    sigStatusChange = pyqtSignal(str, str)  # 状态变化信号：状态名称、状态值
    sigDrawingStateChange = pyqtSignal(bool)  # 绘制状态变化信号
    
    def __init__(self, app, settings_manager, app_controller):
        """初始化主窗口
        
        Args:
            app: QApplication实例
            settings_manager: 设置管理器实例
            app_controller: 应用控制器实例
        """
        super().__init__()
        
        # 保存实例变量
        self.app = app
        self.settings_manager = settings_manager
        self.app_controller = app_controller
        
        # 初始化手势管理器
        self.gesture_manager = GestureManager()
        
        # 状态变量 - 移动到这里，确保在setup_tray_icon之前初始化
        self.drawing_active = False
        
        # 标记是否正在处理页面切换
        self.is_handling_page_change = False
        
        # 保存窗口原始几何信息（用于从最大化状态恢复）
        self.normal_geometry = None
        
        # 窗口调整大小相关变量
        self.resizing = False
        self.resize_direction = None
        self.drag_position = None
        self.border_width = 5  # 边框宽度，用于调整大小
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
        
        # 窗口基本设置
        self.setWindowTitle("GestroKey")
        self.setMinimumSize(1000, 600)
        
        # 设置应用图标
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons", "logo.svg")
        ico_path = svg_to_ico(logo_path)
        if ico_path and os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        else:
            log.warning(f"找不到应用图标: {logo_path}")
        
        # 初始化系统托盘
        self.setup_tray_icon()
        
        # 初始化UI
        self.init_ui()
        
        # 应用样式
        self.apply_styles()
        
        # 连接信号
        self.connect_signals()
        
        # 恢复窗口状态
        self.restore_window_state()
        
        # 记录启动时间
        self.start_time = time.time()
        
        log.info("主窗口初始化完成")
        
    def init_ui(self):
        """初始化UI组件"""
        # 创建中央窗口部件
        central_widget = QWidget()
        central_widget.setObjectName("mainContainer")
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建标题栏
        self.title_bar = TitleBar()
        self.title_bar.windowClose.connect(self.close)
        self.title_bar.windowMinimize.connect(self.showMinimized)
        self.title_bar.windowMaximize.connect(self.toggle_maximize)
        main_layout.addWidget(self.title_bar)
        
        log.debug("添加标题栏到主布局")
        
        # 创建内容容器
        content_container = QWidget()
        content_container.setObjectName("contentContainer")
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 创建侧边栏
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)
        
        log.debug("添加侧边栏到内容布局")
        
        # 创建内容区容器
        self.content_container = QWidget()
        inner_content_layout = QHBoxLayout(self.content_container)
        inner_content_layout.setContentsMargins(0, 0, 0, 0)
        inner_content_layout.setSpacing(0)
        
        # 创建堆叠窗口部件用于页面切换
        self.content_stack = QStackedWidget()
        inner_content_layout.addWidget(self.content_stack)
        
        # 添加内容区到主布局
        content_layout.addWidget(self.content_container)
        
        # 设置布局的拉伸因子，使内容区自动填充
        content_layout.setStretch(0, 0)  # 侧边栏不拉伸
        content_layout.setStretch(1, 1)  # 内容区填充剩余空间
        
        # 添加内容容器到主布局
        main_layout.addWidget(content_container)
        
        # 创建各个页面
        self.init_pages()
        
        # 连接侧边栏的页面切换信号
        self.sidebar.pageChanged.connect(self.handle_page_change_request)
        
        # 默认显示控制台页面
        self.sidebar.navigate_to("console")
        
        # 设置阴影效果
        self.apply_shadow()
        
        log.debug("UI组件初始化完成")
        
    def apply_shadow(self):
        """应用阴影效果"""
        if not self.isMaximized():
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 0)
            self.centralWidget().setGraphicsEffect(shadow)
            log.debug("应用阴影效果")
        else:
            self.centralWidget().setGraphicsEffect(None)
            log.debug("移除阴影效果")
            
    def toggle_maximize(self):
        """切换窗口最大化状态"""
        if self.isMaximized():
            # 先取消最大化
            self.showNormal()
            # 恢复窗口置顶
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            # 恢复到之前保存的窗口大小
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
                log.debug(f"还原到保存的窗口几何信息: {self.normal_geometry}")
            self.show()
            log.debug("窗口已还原并恢复置顶")
        else:
            # 保存当前窗口几何信息
            self.normal_geometry = self.geometry()
            log.debug(f"保存窗口几何信息: {self.normal_geometry}")
            # 最大化窗口并取消置顶
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.showMaximized()
            log.debug("窗口已最大化并取消置顶")
            
        # 更新标题栏状态
        self.title_bar.update_maximized_state(self.isMaximized())
        
        # 保存窗口状态
        self.save_window_state()
        
        # 确保窗口在屏幕上
        self.ensure_on_screen()
        
    def paintEvent(self, event):
        """绘制窗口背景
        
        Args:
            event: 绘制事件
        """
        # 只在非最大化状态下绘制圆角
        if not self.isMaximized():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 设置背景色
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            
            # 绘制圆角矩形
            rect = self.rect()
            painter.drawRoundedRect(rect, 10, 10)
            
    def changeEvent(self, event):
        """处理窗口状态变化事件
        
        Args:
            event: 状态变化事件
        """
        if event.type() == event.WindowStateChange:
            is_maximized = self.isMaximized()
            self.title_bar.update_maximized_state(is_maximized)
            
            if is_maximized:
                # 最大化时移除阴影效果
                self.centralWidget().setGraphicsEffect(None)
                log.debug("窗口状态改变：最大化")
            else:
                # 非最大化时恢复阴影效果
                self.apply_shadow()
                # 强制重绘以恢复圆角
                self.update()
                log.debug("窗口状态改变：非最大化")
                
        super().changeEvent(event)
        
    def resizeEvent(self, event):
        """处理窗口调整大小事件
        
        Args:
            event: 调整大小事件
        """
        super().resizeEvent(event)
            
        # 只在非最大化状态下应用阴影
        if not self.isMaximized() and hasattr(self, 'centralWidget'):
            self.apply_shadow()
        
    def init_pages(self):
        """初始化各个页面"""
        # 创建控制台页面
        self.console_page = ConsolePage()
        self.content_stack.addWidget(self.console_page)
        
        # 创建设置页面
        self.settings_page = SettingsPage(self.settings_manager)
        self.content_stack.addWidget(self.settings_page)
        
        # 创建手势管理页面
        self.gestures_page = GesturesPage(self.gesture_manager)
        self.content_stack.addWidget(self.gestures_page)
        
        # 页面映射字典
        self.pages = {
            "console": 0,
            "settings": 1,
            "gestures": 2
        }
        
        # 当前页面
        self.current_page = "console"
        
    def connect_signals(self):
        """连接信号与槽"""
        # 控制台页面的切换按钮信号
        self.console_page.toggle_button.clicked.connect(self.toggle_drawing)
        
        # 设置页面的信号
        self.settings_page.save_button.clicked.connect(self.save_settings)
        self.settings_page.reset_button.clicked.connect(self.reset_settings)
        
        # 连接设置页面的未保存更改信号
        self.settings_page.hasUnsavedChanges.connect(self.on_settings_changed)
        
        # 将应用控制器的信号转发到控制台页面
        self.app_controller.sigStatusUpdate.connect(self.on_status_update)
        
        # 完全断开并重连侧边栏信号
        self.sidebar.pageChanged.disconnect()  # 断开所有现有连接
        self.sidebar.pageChanged.connect(self.handle_page_change_request)  # 使用新的处理方法
        
    def handle_page_change_request(self, page_name):
        """处理页面切换请求
        
        Args:
            page_name: 请求切换到的页面名称
        """
        log.debug(f"收到页面切换请求: {self.current_page} -> {page_name}")
        
        # 如果是相同页面，忽略请求
        if page_name == self.current_page:
            return
            
        # 防止重复请求
        if hasattr(self, '_changing_page') and self._changing_page:
            log.debug("正在处理另一个页面切换请求，忽略此请求")
            return
            
        self._changing_page = True
        
        # 判断是否可以切换页面
        can_change = True
        
        try:
            # 检查设置页面是否有未保存更改
            if self.current_page == "settings" and hasattr(self, 'settings_page'):
                if self.settings_page.has_pending_changes():
                    # 创建消息框
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("未保存的更改")
                    msg_box.setText("您有未保存的设置更改。是否保存这些更改？")
                    msg_box.setIcon(QMessageBox.Question)
                    
                    # 添加自定义按钮
                    save_btn = msg_box.addButton("保存", QMessageBox.AcceptRole)
                    discard_btn = msg_box.addButton("放弃", QMessageBox.DestructiveRole)
                    cancel_btn = msg_box.addButton("取消", QMessageBox.RejectRole)
                    
                    # 显示对话框
                    msg_box.exec_()
                    
                    clicked_button = msg_box.clickedButton()
                    
                    if clicked_button == save_btn:
                        # 保存设置
                        if not self.save_settings():
                            can_change = False  # 保存失败，不切换
                    elif clicked_button == cancel_btn:
                        can_change = False  # 用户取消，不切换
                    else:  # discard_btn
                        # 放弃更改
                        current_settings = self.settings_manager.get_settings()
                        self.settings_page.update_settings(current_settings)
                        self.settings_page.hasUnsavedChanges.emit(False)
            
            # 如果可以切换，执行切换
            if can_change:
                self._actually_change_page(page_name)
            else:
                log.debug(f"页面切换被取消，保持当前页面: {self.current_page}")
                
                # 临时禁用信号，确保不会再次触发切换
                self.sidebar.blockSignals(True)
                
                try:
                    # 调用侧边栏的方法，直接设置正确的选中状态
                    self.sidebar.set_active_page(self.current_page)
                finally:
                    # 恢复信号处理
                    self.sidebar.blockSignals(False)
                    
                # 强制刷新UI，确保视觉状态更新
                self.sidebar.repaint()
                    
        finally:
            self._changing_page = False
            
    def _actually_change_page(self, page_name):
        """实际执行页面切换
        
        Args:
            page_name: 页面名称
        """
        if page_name in self.pages:
            page_index = self.pages[page_name]
            self.content_stack.setCurrentIndex(page_index)
            self.current_page = page_name
            log.info(f"已切换到页面: {page_name}")
        else:
            log.warning(f"未知页面: {page_name}")
            
    def toggle_drawing(self):
        """切换绘制状态"""
        self.drawing_active = not self.drawing_active
        
        # 更新控制台页面UI
        self.console_page.update_drawing_state(self.drawing_active)
        
        # 发出绘制状态变化信号
        self.sigDrawingStateChange.emit(self.drawing_active)
        
        # 更新托盘菜单
        self.update_tray_menu()
        
        # 记录日志
        state_text = "启动" if self.drawing_active else "停止"
        log.info(f"{state_text}手势识别")
        
        # 通知应用控制器
        if self.app_controller:
            if self.drawing_active:
                self.app_controller.start_gesture_recognition()
            else:
                self.app_controller.stop_gesture_recognition()
                
    def save_settings(self):
        """保存设置"""
        # 从设置页面获取当前设置
        current_settings = self.settings_page.get_current_settings()
        
        # 保存到设置管理器
        if self.settings_manager.save_settings(current_settings):
            log.info("设置已保存")
            
            # 重新加载保存后的设置
            saved_settings = self.settings_manager.get_settings()
            
            # 先加载设置以确保内部状态一致
            self.settings_page.load_settings(saved_settings)
            
            # 再更新UI显示
            self.settings_page.update_settings(saved_settings)
            
            # 更新UI以表示设置已保存
            self.settings_page.hasUnsavedChanges.emit(False)
            log.debug("重置设置页面的未保存更改状态")
            
            QMessageBox.information(self, "保存成功", "设置已成功保存。")
            
            # 应用设置到应用控制器
            if self.app_controller:
                self.app_controller.apply_settings(current_settings)
        else:
            log.error("保存设置失败")
            QMessageBox.warning(self, "保存失败", "保存设置时发生错误。")
            
    def reset_settings(self):
        """重置设置为默认值"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要将所有设置重置为默认值吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.settings_manager.reset_to_defaults():
                log.info("设置已重置为默认值")
                
                # 获取默认设置
                default_settings = self.settings_manager.get_settings()
                
                # 先加载设置以确保内部状态一致
                self.settings_page.load_settings(default_settings)
                
                # 然后更新UI显示
                self.settings_page.update_settings(default_settings)
                
                # 确保设置页面的未保存更改状态被重置
                self.settings_page.hasUnsavedChanges.emit(False)
                log.debug("重置设置页面的未保存更改状态")
                
                # 应用设置到应用控制器
                if self.app_controller:
                    self.app_controller.apply_settings(default_settings)
                    
                QMessageBox.information(self, "重置成功", "所有设置已重置为默认值。")
            else:
                log.error("重置设置失败")
                QMessageBox.warning(self, "重置失败", "重置设置时发生错误。")
                
    def apply_single_setting(self, key, value):
        """处理单个设置变更
        
        注意: 此方法不再用于实时应用设置，仅在兼容旧代码或
        特殊场景下使用。设置通常在save_settings方法中批量应用。
        
        Args:
            key: 设置键名
            value: 设置值
        """
        log.debug(f"单次设置更新请求: {key} = {value} (未立即应用)")
        
        # 不再立即应用设置，仅在保存按钮点击时应用
        # 保留此方法仅用于兼容或特殊需求
                
    def on_status_update(self, status_type, status_value):
        """状态更新处理
        
        Args:
            status_type: 状态类型
            status_value: 状态值
        """
        # 更新控制台页面的状态指示器
        self.console_page.update_status(status_type, status_value)
        
        # 发出状态变化信号
        self.sigStatusChange.emit(status_type, status_value)
        
    def on_settings_changed(self, has_changes):
        """处理设置页面未保存更改的状态变化
        
        Args:
            has_changes: 是否有未保存的更改
        """
        # 可以在这里更新UI以指示有未保存的更改
        # 例如修改保存按钮的样式或显示提示图标
        if has_changes:
            self.settings_page.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #F59E0B;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #D97706;
                }
                
                QPushButton:pressed {
                    background-color: #B45309;
                }
            """)
        else:
            self.settings_page.save_button.setStyleSheet("""
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
        
    def setup_tray_icon(self):
        """设置系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置托盘图标
        if hasattr(self, 'app_icon_path') and os.path.exists(self.app_icon_path):
            self.tray_icon.setIcon(QIcon(self.app_icon_path))
        else:
            # 如果找不到图标，使用默认图标
            self.tray_icon.setIcon(self.windowIcon())
        
        try:
            # 设置托盘图标的工具提示
            from version import __title__, __version__
            self.tray_icon.setToolTip(f"{__title__} v{__version__}")
        except ImportError:
            self.tray_icon.setToolTip("GestroKey")
        
        # 创建托盘菜单
        self.tray_menu = QMenu()
        
        # 添加显示/隐藏动作
        self.toggle_visibility_action = QAction("显示窗口" if not self.isVisible() else "隐藏窗口", self)
        self.toggle_visibility_action.triggered.connect(self.toggle_visibility)
        self.tray_menu.addAction(self.toggle_visibility_action)
        
        # 添加开始/停止绘制动作
        action_text = "停止手势识别" if self.drawing_active else "启动手势识别"
        self.toggle_drawing_action = QAction(action_text, self)
        self.toggle_drawing_action.triggered.connect(self.toggle_drawing)
        self.tray_menu.addAction(self.toggle_drawing_action)
        
        # 添加分隔线
        self.tray_menu.addSeparator()
        
        # 添加设置操作
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings_page)
        self.tray_menu.addAction(settings_action)
        
        # 添加关于操作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about_dialog)
        self.tray_menu.addAction(about_action)
        
        # 添加分隔线
        self.tray_menu.addSeparator()
        
        # 添加退出动作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.force_exit)
        self.tray_menu.addAction(exit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # 设置托盘图标双击事件
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        
        log.debug("系统托盘图标已设置")
        
    def update_tray_menu(self):
        """更新托盘菜单项文本"""
        if hasattr(self, 'toggle_visibility_action'):
            self.toggle_visibility_action.setText("显示窗口" if not self.isVisible() else "隐藏窗口")
            
        if hasattr(self, 'toggle_drawing_action'):
            action_text = "停止手势识别" if self.drawing_active else "启动手势识别"
            self.toggle_drawing_action.setText(action_text)
            
    def toggle_visibility(self):
        """切换窗口显示/隐藏状态"""
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.showNormal()  # 使用showNormal替代show以确保从最小化状态恢复
            self.activateWindow()  # 确保窗口被激活（在前台显示）
            self.raise_()  # 确保窗口置于最前
            
        # 更新菜单文本
        self.update_tray_menu()
        
    def _tray_icon_activated(self, reason):
        """托盘图标激活事件处理
        
        Args:
            reason: 激活原因，例如单击、双击等
        """
        # QSystemTrayIcon.Trigger是单击，DoubleClick是双击
        if reason == QSystemTrayIcon.DoubleClick or reason == QSystemTrayIcon.Trigger:
            # 如果窗口已最小化，恢复窗口
            if self.isMinimized():
                self.showNormal()
                self.activateWindow()
                self.raise_()
            else:
                self.toggle_visibility()
                
    def show_about_dialog(self):
        """显示关于对话框"""
        try:
            from version import get_about_text
            about_text = get_about_text()
        except ImportError:
            about_text = f"GestroKey\n版本：1.0.0\n© 2023 All Rights Reserved"
        
        # 强制显示主窗口(但保持最小化状态)，确保应用程序不会因为缺少可见窗口而退出
        was_visible = self.isVisible()
        if not was_visible:
            self.setVisible(True)
            self.setWindowState(Qt.WindowMinimized)
            log.debug("临时显示最小化窗口以确保应用不会退出")
            
        # 使用QMessageBox显示关于信息
        about_box = QMessageBox(self)  # 使用self作为父窗口
        about_box.setWindowTitle("关于")
        about_box.setText(about_text)
        about_box.setIconPixmap(self.windowIcon().pixmap(64, 64))
        about_box.setStandardButtons(QMessageBox.Ok)
        
        # 自定义按钮文本
        about_box.button(QMessageBox.Ok).setText("确定")
        
        # 设置对话框样式，确保窗口保持在前台
        about_box.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        
        log.debug("显示关于对话框")
        # 使用模态对话框显示
        about_box.exec_()
        
        # 如果窗口之前是隐藏的，恢复隐藏状态
        if not was_visible:
            self.setVisible(False)
            log.debug("恢复窗口隐藏状态")
            
    def apply_styles(self):
        """应用样式"""
        # 设置全局字体
        font = QFont("Microsoft YaHei", 10)
        self.app.setFont(font)
        
        # 尝试使用Fusion风格
        if 'Fusion' in QStyleFactory.keys():
            self.app.setStyle(QStyleFactory.create('Fusion'))
            log.debug("应用Fusion风格")
        
        # 设置应用程序级别的样式表
        self.app.setStyleSheet("""
            QMainWindow {
                background-color: transparent;
                border: none;
            }
            
            #mainContainer {
                background-color: transparent;
                border: none;
            }
            
            #contentContainer {
                background-color: #F9FAFB;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            
            QLabel {
                color: #1A202C;
            }
            
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
            
            QPushButton:disabled {
                background-color: #CBD5E0;
                color: #A0AEC0;
            }
            
            QLineEdit, QComboBox {
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                padding: 8px;
                background-color: white;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4299E1;
            }
            
            QSlider::groove:horizontal {
                height: 8px;
                background: #E2E8F0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #4299E1;
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #3182CE;
            }
            
            QSlider::add-page:horizontal {
                background: #E2E8F0;
                border-radius: 4px;
            }
            
            QSlider::sub-page:horizontal {
                background: #4299E1;
                border-radius: 4px;
            }
            
            QCheckBox {
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #CBD5E0;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:unchecked {
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4299E1;
                border: 1px solid #4299E1;
                image: url(ui/assets/icons/check.png);
            }
            
            QMessageBox {
                background-color: #FFFFFF;
                border-radius: 10px;
            }
            
            QMessageBox QLabel {
                font-size: 14px;
                color: #1A202C;
            }
            
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 30px;
                font-size: 13px;
            }
            
            QToolTip {
                background-color: #F8F9FA;
                color: #1A202C;
                border: 1px solid #E2E8F0;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        
        log.debug("应用样式表完成")
        
    def has_unsaved_changes(self):
        """检查是否有未保存的更改
        
        Returns:
            bool: 是否有未保存的更改
        """
        # 检查设置页面是否有未保存的更改
        if hasattr(self, 'settings_page') and self.settings_page.has_pending_changes():
            log.debug("设置页面有未保存的更改")
            return True
            
        # 检查手势页面是否有未保存的更改
        if hasattr(self, 'gestures_page') and hasattr(self.gestures_page, 'has_unsaved_changes') and self.gestures_page.has_unsaved_changes:
            log.debug("手势页面有未保存的更改")
            return True
        
        # 检查其他可能有未保存更改的页面
        # 根据需要添加其他页面的检查
        
        return False
        
    def closeEvent(self, event):
        """窗口关闭事件处理
        
        Args:
            event: 关闭事件对象
        """
        # 保存窗口状态
        self.save_window_state()
        
        # 在窗口关闭前移除透明背景和阴影效果，避免UpdateLayeredWindowIndirect失败
        self.centralWidget().setGraphicsEffect(None)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # 判断是否是真正的退出操作
        from PyQt5.QtWidgets import QSystemTrayIcon
        if not hasattr(self, 'tray_icon') or not self.tray_icon or not QSystemTrayIcon.isSystemTrayAvailable():
            # 如果没有系统托盘或托盘不可用，执行正常关闭
            log.info("系统托盘不可用，执行正常关闭流程")
            self._handle_real_close(event)
            return
            
        # 如果是普通的关闭操作，则只是最小化到托盘
        if not self.app.property("force_exit"):
            log.info("最小化到系统托盘而不是关闭")
            event.ignore()
            self.hide()
            
            # 不使用系统通知，仅更新托盘菜单状态
            self.update_tray_menu()
            return
        
        # 如果已设置force_exit属性，执行真正的关闭
        self._handle_real_close(event)
        
    def _handle_real_close(self, event):
        """处理真正的窗口关闭逻辑
        
        Args:
            event: 关闭事件对象
        """
        # 检查是否有未保存的更改
        if self.has_unsaved_changes():
            # 创建确认对话框
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("确认退出")
            msg_box.setText("有未保存的更改，确定要退出吗？")
            msg_box.setIcon(QMessageBox.Question)
            
            # 添加自定义按钮
            save_btn = msg_box.addButton("保存", QMessageBox.AcceptRole)
            discard_btn = msg_box.addButton("不保存", QMessageBox.DestructiveRole)
            cancel_btn = msg_box.addButton("取消", QMessageBox.RejectRole)
            
            # 设置对话框样式
            msg_box.setWindowFlags(msg_box.windowFlags() | Qt.FramelessWindowHint)
            
            # 显示对话框
            msg_box.exec_()
            
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == save_btn:
                # 保存更改
                saved = False
                
                # 根据当前页面保存相应的内容
                if self.current_page == "settings" and self.settings_page.has_pending_changes():
                    saved = self.settings_page.save_settings()
                elif self.current_page == "gestures" and hasattr(self.gestures_page, 'save_gestures'):
                    saved = self.gestures_page.save_gestures()
                
                # 如果保存失败，取消关闭
                if not saved:
                    event.ignore()
                    return
            elif clicked_button == cancel_btn:
                # 取消关闭
                event.ignore()
                return
            # 如果选择丢弃更改，则继续关闭
            
        # 处理关闭前的清理工作
        try:
            # 停止手势识别
            if self.drawing_active and self.app_controller:
                self.app_controller.stop_gesture_recognition()
                log.info("已停止手势识别")
            
            # 如果有系统托盘图标，隐藏它
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.hide()
                
            # 记录应用程序关闭
            log.info("应用程序正在关闭")
            
        except Exception as e:
            # 记录异常但不阻止关闭
            log.error(f"关闭时发生错误: {str(e)}")
            
        # 允许关闭窗口
        event.accept()

    def show_settings_page(self):
        """显示设置页面"""
        # 切换到设置页面
        self.handle_page_change_request("settings")
        # 如果窗口是隐藏的，显示窗口
        if not self.isVisible():
            self.show()
            self.activateWindow()
            
    def force_exit(self):
        """强制退出应用程序"""
        # 设置force_exit属性，使closeEvent知道这是真正的退出请求
        self.app.setProperty("force_exit", True)
        # 调用close方法来触发closeEvent
        self.close()

    def restore_window_state(self):
        """恢复窗口状态"""
        try:
            # 尝试从设置中恢复窗口位置和大小
            if self.settings_manager and hasattr(self.settings_manager, 'get_ui_settings'):
                ui_settings = self.settings_manager.get_ui_settings()
                if ui_settings and 'window_geometry' in ui_settings:
                    self.restoreGeometry(ui_settings['window_geometry'])
                    log.debug("已恢复窗口几何信息")
                if ui_settings and 'window_state' in ui_settings:
                    self.restoreState(ui_settings['window_state'])
                    log.debug("已恢复窗口状态")
                # 确保窗口不会超出屏幕范围
                self.ensure_on_screen()
            else:
                # 如果没有保存的状态，居中显示窗口
                self.center_window()
        except Exception as e:
            log.error(f"恢复窗口状态失败: {str(e)}")
            # 出错时居中显示窗口
            self.center_window()
            
    def ensure_on_screen(self):
        """确保窗口在屏幕范围内"""
        desktop = QApplication.desktop()
        screen_rect = desktop.availableGeometry(self)
        window_rect = self.frameGeometry()
        
        # 如果窗口完全在屏幕外，将其移至屏幕中央
        if not screen_rect.intersects(window_rect):
            self.center_window()
        else:
            # 如果窗口部分超出屏幕，调整位置
            if window_rect.left() < screen_rect.left():
                self.move(screen_rect.left(), self.y())
            if window_rect.top() < screen_rect.top():
                self.move(self.x(), screen_rect.top())
            if window_rect.right() > screen_rect.right():
                self.move(screen_rect.right() - window_rect.width(), self.y())
            if window_rect.bottom() > screen_rect.bottom():
                self.move(self.x(), screen_rect.bottom() - window_rect.height())
                
        log.debug("已确保窗口在屏幕范围内")
            
    def center_window(self):
        """将窗口居中显示"""
        frame_geo = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geo.moveCenter(center_point)
        self.move(frame_geo.topLeft())
        log.debug("窗口已居中显示")
        
    def save_window_state(self):
        """保存窗口状态"""
        try:
            if self.settings_manager and hasattr(self.settings_manager, 'save_ui_settings'):
                ui_settings = {
                    'window_geometry': self.saveGeometry(),
                    'window_state': self.saveState()
                }
                self.settings_manager.save_ui_settings(ui_settings)
                log.debug("已保存窗口状态")
        except Exception as e:
            log.error(f"保存窗口状态失败: {str(e)}")

    def mousePressEvent(self, event):
        """处理鼠标按下事件
        
        Args:
            event: 鼠标事件
        """
        if self.isMaximized():
            return super().mousePressEvent(event)
            
        # 如果鼠标在边框区域，开始调整大小
        if self._is_resize_area(event.pos()):
            self.resizing = True
            self.resize_direction = self._get_resize_direction(event.pos())
            self.setCursor(self._get_resize_cursor(self.resize_direction))
            event.accept()
        # 如果点击在标题栏区域外，则将事件传递给父类
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件
        
        Args:
            event: 鼠标事件
        """
        if self.isMaximized():
            self.setCursor(Qt.ArrowCursor)
            return super().mouseMoveEvent(event)
            
        # 如果正在调整大小，调整窗口大小
        if self.resizing:
            self._resize_window(event.globalPos())
            event.accept()
        # 如果鼠标在边框区域，更改光标形状
        elif self._is_resize_area(event.pos()):
            direction = self._get_resize_direction(event.pos())
            self.setCursor(self._get_resize_cursor(direction))
            event.accept()
        # 否则恢复默认光标
        else:
            self.setCursor(Qt.ArrowCursor)
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件
        
        Args:
            event: 鼠标事件
        """
        # 结束调整大小
        if self.resizing:
            self.resizing = False
            self.resize_direction = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def _is_resize_area(self, pos):
        """判断位置是否在调整大小的区域内
        
        Args:
            pos: 鼠标位置
            
        Returns:
            bool: 是否在调整大小区域
        """
        return (self._is_top_edge(pos) or self._is_bottom_edge(pos) or 
                self._is_left_edge(pos) or self._is_right_edge(pos))
    
    def _is_top_edge(self, pos):
        """判断位置是否在顶部边缘
        
        Args:
            pos: 鼠标位置
            
        Returns:
            bool: 是否在顶部边缘
        """
        return 0 <= pos.y() <= self.border_width
    
    def _is_bottom_edge(self, pos):
        """判断位置是否在底部边缘
        
        Args:
            pos: 鼠标位置
            
        Returns:
            bool: 是否在底部边缘
        """
        return self.height() - self.border_width <= pos.y() <= self.height()
    
    def _is_left_edge(self, pos):
        """判断位置是否在左侧边缘
        
        Args:
            pos: 鼠标位置
            
        Returns:
            bool: 是否在左侧边缘
        """
        return 0 <= pos.x() <= self.border_width
    
    def _is_right_edge(self, pos):
        """判断位置是否在右侧边缘
        
        Args:
            pos: 鼠标位置
            
        Returns:
            bool: 是否在右侧边缘
        """
        return self.width() - self.border_width <= pos.x() <= self.width()
    
    def _get_resize_direction(self, pos):
        """获取调整大小的方向
        
        Args:
            pos: 鼠标位置
            
        Returns:
            tuple: 水平和垂直方向的调整
        """
        horizontal = 0  # -1 左, 0 中间, 1 右
        vertical = 0    # -1 上, 0 中间, 1 下
        
        if self._is_left_edge(pos):
            horizontal = -1
        elif self._is_right_edge(pos):
            horizontal = 1
            
        if self._is_top_edge(pos):
            vertical = -1
        elif self._is_bottom_edge(pos):
            vertical = 1
            
        return (horizontal, vertical)
    
    def _get_resize_cursor(self, direction):
        """获取调整大小方向对应的光标
        
        Args:
            direction: 调整方向元组
            
        Returns:
            QCursor: 对应的光标
        """
        horizontal, vertical = direction
        
        if horizontal == -1 and vertical == -1:
            return Qt.SizeFDiagCursor
        elif horizontal == 1 and vertical == -1:
            return Qt.SizeBDiagCursor
        elif horizontal == -1 and vertical == 1:
            return Qt.SizeBDiagCursor
        elif horizontal == 1 and vertical == 1:
            return Qt.SizeFDiagCursor
        elif horizontal == 0 and vertical == -1:
            return Qt.SizeVerCursor
        elif horizontal == 0 and vertical == 1:
            return Qt.SizeVerCursor
        elif horizontal == -1 and vertical == 0:
            return Qt.SizeHorCursor
        elif horizontal == 1 and vertical == 0:
            return Qt.SizeHorCursor
        else:
            return Qt.ArrowCursor
    
    def _resize_window(self, global_pos):
        """调整窗口大小
        
        Args:
            global_pos: 全局鼠标位置
        """
        if not self.resize_direction:
            return
            
        horizontal, vertical = self.resize_direction
        current_rect = self.geometry()
        
        left = current_rect.left()
        top = current_rect.top()
        right = current_rect.right()
        bottom = current_rect.bottom()
        
        min_width = self.minimumWidth()
        min_height = self.minimumHeight()
        
        if horizontal == -1:  # 左边
            left = min(global_pos.x(), right - min_width)
        elif horizontal == 1:  # 右边
            right = max(global_pos.x(), left + min_width)
            
        if vertical == -1:  # 上边
            top = min(global_pos.y(), bottom - min_height)
        elif vertical == 1:  # 下边
            bottom = max(global_pos.y(), top + min_height)
            
        self.setGeometry(left, top, right - left, bottom - top)

    def showMinimized(self):
        """重写showMinimized方法，确保最小化的窗口可以被恢复"""
        super().showMinimized()
        log.debug("窗口已最小化")
        # 更新托盘菜单文本
        self.update_tray_menu()

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 导入测试用的设置管理器
    from ui.utils.settings_manager import SettingsManager
    
    # 创建临时设置文件
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
        temp_path = temp.name
    
    # 初始化设置管理器
    settings_manager = SettingsManager(temp_path)
    
    # 创建简单的应用控制器用于测试
    class MockAppController:
        sigStatusUpdate = pyqtSignal(str, str)
        
        def __init__(self):
            self.gesture_recognition_active = False
            
        def start_gesture_recognition(self):
            self.gesture_recognition_active = True
            print("开始手势识别")
            
        def stop_gesture_recognition(self):
            self.gesture_recognition_active = False
            print("停止手势识别")
            
        def apply_settings(self, settings):
            print(f"应用设置: {settings}")
    
    # 创建应用控制器实例
    app_controller = MockAppController()
    
    # 创建并显示主窗口
    window = MainWindow(app, settings_manager, app_controller)
    window.show()
    
    # 运行应用程序
    ret = app.exec_()
    
    # 清理临时文件
    os.unlink(temp_path)
    
    sys.exit(ret) 