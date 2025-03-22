import os
import sys
import time
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                              QStackedWidget, QLabel, QSizePolicy, QGraphicsDropShadowEffect,
                              QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QColor, QFont, QPalette

# 导入自定义组件
from ui.sidebar import Sidebar
from ui.pages.console_page import ConsolePage
from ui.pages.settings_page import SettingsPage
from ui.pages.gestures_page import GesturesPage

# 导入手势管理器
from ui.utils.gesture_manager import GestureManager

# 导入日志模块
from app.log import log

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
        
        # 窗口基本设置
        self.setWindowTitle("GestroKey")
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("ui/assets/icons/app_icon.png"))
        
        # 初始化系统托盘
        self.setup_tray_icon()
        
        # 初始化UI
        self.init_ui()
        
        # 应用样式
        self.apply_styles()
        
        # 状态变量
        self.drawing_active = False
        
        # 连接信号
        self.connect_signals()
        
        # 记录启动时间
        self.start_time = time.time()
        
        log.info("主窗口初始化完成")
        
    def init_ui(self):
        """初始化UI组件"""
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建侧边栏
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # 创建内容区容器
        self.content_container = QWidget()
        content_layout = QHBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 创建堆叠窗口部件用于页面切换
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # 添加内容区到主布局
        main_layout.addWidget(self.content_container)
        
        # 设置布局的拉伸因子，使内容区自动填充
        main_layout.setStretch(0, 0)  # 侧边栏不拉伸
        main_layout.setStretch(1, 1)  # 内容区填充剩余空间
        
        # 创建各个页面
        self.init_pages()
        
        # 连接侧边栏的页面切换信号
        self.sidebar.pageChanged.connect(self.change_page)
        
        # 默认显示控制台页面
        self.sidebar.navigate_to("console")
        
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
        
    def connect_signals(self):
        """连接信号与槽"""
        # 控制台页面的操作按钮信号
        self.console_page.start_drawing_button.clicked.connect(self.toggle_drawing)
        self.console_page.stop_drawing_button.clicked.connect(self.toggle_drawing)
        self.console_page.minimize_button.clicked.connect(self.hide)
        self.console_page.exit_button.clicked.connect(self.close)
        
        # 设置页面的保存按钮信号
        self.settings_page.save_button.clicked.connect(self.save_settings)
        self.settings_page.reset_button.clicked.connect(self.reset_settings)
        
        # 将应用控制器的信号转发到控制台页面
        self.app_controller.sigStatusUpdate.connect(self.on_status_update)
        
    def change_page(self, page_name):
        """切换页面
        
        Args:
            page_name: 页面名称
        """
        if page_name in self.pages:
            self.content_stack.setCurrentIndex(self.pages[page_name])
            log.info(f"切换到页面: {page_name}")
        else:
            log.warning(f"未知页面: {page_name}")
            
    def toggle_drawing(self):
        """切换绘制状态"""
        self.drawing_active = not self.drawing_active
        
        # 更新控制台页面UI
        self.console_page.update_drawing_state(self.drawing_active)
        
        # 发出绘制状态变化信号
        self.sigDrawingStateChange.emit(self.drawing_active)
        
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
            # 重置设置
            if self.settings_manager.reset_to_defaults():
                log.info("设置已重置为默认值")
                
                # 重新加载设置页面
                default_settings = self.settings_manager.get_settings()
                self.settings_page.load_settings(default_settings)
                
                QMessageBox.information(self, "重置成功", "设置已重置为默认值。")
                
                # 应用设置到应用控制器
                if self.app_controller:
                    self.app_controller.apply_settings(default_settings)
            else:
                log.error("重置设置失败")
                QMessageBox.warning(self, "重置失败", "重置设置时发生错误。")
                
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
        
    def setup_tray_icon(self):
        """设置系统托盘图标"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("ui/assets/icons/app_icon.png"))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 显示主窗口
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        # 分隔线
        tray_menu.addSeparator()
        
        # 启动/停止手势识别
        self.toggle_drawing_action = QAction("启动手势识别", self)
        self.toggle_drawing_action.triggered.connect(self.toggle_drawing)
        tray_menu.addAction(self.toggle_drawing_action)
        
        # 分隔线
        tray_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(tray_menu)
        
        # 显示托盘图标
        self.tray_icon.show()
        
        # 连接托盘图标的点击信号
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
    def on_tray_icon_activated(self, reason):
        """托盘图标激活处理
        
        Args:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.DoubleClick:
            # 双击托盘图标显示主窗口
            self.show()
            
    def apply_styles(self):
        """应用样式"""
        # 设置全局字体
        font = QFont("Microsoft YaHei", 10)
        self.app.setFont(font)
        
        # 设置应用程序级别的样式表
        self.app.setStyleSheet("""
            QMainWindow {
                background-color: #F9FAFB;
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
        """)
        
    def closeEvent(self, event):
        """窗口关闭事件处理
        
        Args:
            event: 关闭事件
        """
        reply = QMessageBox.question(
            self, "确认退出", 
            "确定要退出应用程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 关闭应用前停止手势识别
            if self.drawing_active and self.app_controller:
                self.app_controller.stop_gesture_recognition()
                
            # 保存设置
            current_settings = self.settings_page.get_current_settings()
            self.settings_manager.save_settings(current_settings)
            
            # 关闭系统托盘图标
            self.tray_icon.hide()
            
            # 记录日志
            log.info("应用程序关闭")
            
            # 接受关闭事件
            event.accept()
        else:
            # 忽略关闭事件
            event.ignore()
            
    def hideEvent(self, event):
        """窗口隐藏事件处理
        
        Args:
            event: 隐藏事件
        """
        # 显示通知
        self.tray_icon.showMessage(
            "GestroKey", 
            "应用程序已最小化到系统托盘。双击图标以恢复窗口。",
            QSystemTrayIcon.Information,
            2000
        )
        
    def showEvent(self, event):
        """窗口显示事件处理
        
        Args:
            event: 显示事件
        """
        # 更新托盘菜单的状态
        action_text = "停止手势识别" if self.drawing_active else "启动手势识别"
        self.toggle_drawing_action.setText(action_text)

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