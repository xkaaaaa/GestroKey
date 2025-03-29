import os
import sys
import time
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QStackedWidget, QLabel, QSizePolicy, QGraphicsDropShadowEffect,
                             QMessageBox, QPushButton, QFrame, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QBrush

# 导入自定义组件
from ui.sidebar import Sidebar
from ui.pages.console_page import ConsolePage
from ui.pages.settings_page import SettingsPage
from ui.pages.gestures_page import GesturesPage
from ui.utils.icon_utils import svg_to_ico

# 导入拆分出的组件和工具
from ui.components.title_bar import TitleBar
from ui.components.tray_icon_manager import TrayIconManager
from ui.components.window_resize_handler import WindowResizeHandler
from ui.utils.style_manager import StyleManager
from ui.utils.window_manager import WindowManager

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
        
        # 创建窗口大小调整处理器
        self.resize_handler = WindowResizeHandler(self)
        
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
        
        # 初始化UI
        self.init_ui()
        
        # 应用样式
        StyleManager.apply_styles(self.app)
        
        # 初始化系统托盘
        self.init_tray_icon()
        
        # 连接信号
        self.connect_signals()
        
        # 恢复窗口状态
        WindowManager.restore_window_state(self, self.settings_manager)
        
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
            shadow = StyleManager.get_shadow_effect()
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
        WindowManager.save_window_state(self, self.settings_manager)
        
        # 确保窗口在屏幕上
        WindowManager.ensure_on_screen(self)
        
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
                    # 显示未保存更改对话框
                    result = WindowManager.show_unsaved_changes_dialog(self)
                    
                    if result == 'save':
                        # 保存设置
                        if not self.save_settings():
                            can_change = False  # 保存失败，不切换
                    elif result == 'cancel':
                        can_change = False  # 用户取消，不切换
                    else:  # discard
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
        if hasattr(self, 'tray_manager'):
            self.tray_manager.update_menu(self.drawing_active)
        
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
                
            return True
        else:
            log.error("保存设置失败")
            QMessageBox.warning(self, "保存失败", "保存设置时发生错误。")
            return False
            
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
                return True
            else:
                log.error("重置设置失败")
                QMessageBox.warning(self, "重置失败", "重置设置时发生错误。")
                return False
        return False
                
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
        # 使用样式管理器更新保存按钮的样式
        StyleManager.update_button_style_for_unsaved_changes(self.settings_page.save_button, has_changes)
        
    def init_tray_icon(self):
        """初始化系统托盘图标"""
        # 使用托盘图标管理器
        self.tray_manager = TrayIconManager(self, self.windowIcon())
        
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
            
    def closeEvent(self, event):
        """窗口关闭事件处理
        
        Args:
            event: 关闭事件对象
        """
        # 保存窗口状态
        WindowManager.save_window_state(self, self.settings_manager)
        
        # 在窗口关闭前移除透明背景和阴影效果，避免UpdateLayeredWindowIndirect失败
        self.centralWidget().setGraphicsEffect(None)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # 判断是否是真正的退出操作
        from PyQt5.QtWidgets import QSystemTrayIcon
        if not hasattr(self, 'tray_manager') or not self.tray_manager.tray_icon or not QSystemTrayIcon.isSystemTrayAvailable():
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
            self.tray_manager.update_menu(self.drawing_active)
            return
        
        # 如果已设置force_exit属性，执行真正的关闭
        self._handle_real_close(event)
        
    def _handle_real_close(self, event):
        """处理真正的窗口关闭逻辑
        
        Args:
            event: 关闭事件对象
        """
        # 检查是否有未保存的更改
        if WindowManager.check_unsaved_changes(self):
            # 显示未保存更改对话框
            result = WindowManager.show_unsaved_changes_dialog(self)
            
            if result == 'save':
                # 保存更改
                saved = False
                
                # 根据当前页面保存相应的内容
                if self.current_page == "settings" and self.settings_page.has_pending_changes():
                    saved = self.save_settings()
                elif self.current_page == "gestures" and hasattr(self.gestures_page, 'save_gestures'):
                    saved = self.gestures_page.save_gestures()
                
                # 如果保存失败，取消关闭
                if not saved:
                    event.ignore()
                    return
            elif result == 'cancel':
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
            if hasattr(self, 'tray_manager'):
                self.tray_manager.hide()
                
            # 记录应用程序关闭
            log.info("应用程序正在关闭")
            
        except Exception as e:
            # 记录异常但不阻止关闭
            log.error(f"关闭时发生错误: {str(e)}")
            
        # 允许关闭窗口
        event.accept()
        
    def showMinimized(self):
        """重写showMinimized方法，确保最小化的窗口可以被恢复"""
        super().showMinimized()
        log.debug("窗口已最小化")
        # 更新托盘菜单文本
        if hasattr(self, 'tray_manager'):
            self.tray_manager.update_menu(self.drawing_active)
           
    def mousePressEvent(self, event):
        """处理鼠标按下事件
        
        Args:
            event: 鼠标事件
        """
        # 使用窗口调整大小处理器
        if not self.resize_handler.handle_mouse_press(event, self.isMaximized()):
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件
        
        Args:
            event: 鼠标事件
        """
        # 使用窗口调整大小处理器
        if not self.resize_handler.handle_mouse_move(event, self.isMaximized()):
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件
        
        Args:
            event: 鼠标事件
        """
        # 使用窗口调整大小处理器
        if not self.resize_handler.handle_mouse_release(event):
            super().mouseReleaseEvent(event) 