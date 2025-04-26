import os
import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QWidget
from PyQt6.QtGui import QIcon, QAction, QCursor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject, QTimer

try:
    from core.logger import get_logger
    from ui.components.toast_notification import show_info
    from version import get_version_string, APP_NAME
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger
    from ui.components.toast_notification import show_info
    from version import get_version_string, APP_NAME

class SystemTrayIcon(QSystemTrayIcon):
    """系统托盘图标
    
    提供系统托盘图标及其菜单和事件处理功能。
    支持单击、双击、中键点击等操作，以及右键自定义菜单。
    兼容Windows、macOS和Linux平台。
    """
    
    # 自定义信号
    toggle_drawing_signal = pyqtSignal()  # 切换绘制状态
    show_settings_signal = pyqtSignal()   # 显示设置页面
    show_window_signal = pyqtSignal()     # 显示主窗口
    exit_app_signal = pyqtSignal()        # 退出应用程序
    
    def __init__(self, app_icon=None, parent=None):
        # 如果未提供图标，尝试加载默认图标
        if app_icon is None:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    '../../assets/images/icon.svg')
            if os.path.exists(icon_path):
                app_icon = QIcon(icon_path)
            else:
                app_icon = QIcon()
        
        super().__init__(app_icon, parent)
        self.logger = get_logger("SystemTray")
        
        # 初始状态
        self.drawing_active = False
        
        # 单击/双击防抖变量
        self.click_timer = None
        self.is_double_click = False
        
        # 检测操作系统类型
        self.platform = sys.platform
        self.logger.info(f"检测到操作系统平台: {self.platform}")
        
        # 创建右键菜单和设置事件处理
        self._create_menu()
        self._setup_event_handlers()
        
        # 设置工具提示
        self.setToolTip(f"{APP_NAME} 手势控制工具")
        self.logger.info("系统托盘图标初始化完成")
    
    def _create_menu(self):
        """创建托盘图标右键菜单"""
        self.logger.debug("创建托盘图标菜单")
        
        # 创建菜单实例
        self.menu = QMenu()
        
        # 根据不同操作系统应用不同样式
        if self.platform == 'win32':
            self.menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #dddddd;
                    border-radius: 5px;
                    padding: 5px;
                }
                QMenu::item {
                    background-color: transparent;
                    padding: 8px 25px 8px 25px;
                    border-radius: 4px;
                    margin: 2px 5px;
                }
                QMenu::item:selected {
                    background-color: rgba(52, 152, 219, 0.2);
                }
                QMenu::item:pressed {
                    background-color: rgba(52, 152, 219, 0.3);
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #dddddd;
                    margin: 5px 10px;
                }
            """)
        elif self.platform == 'darwin':
            # macOS风格菜单（更简洁，边距较小）
            self.menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    padding: 3px;
                }
                QMenu::item {
                    background-color: transparent;
                    padding: 5px 20px 5px 20px;
                    border-radius: 4px;
                    margin: 1px 3px;
                }
                QMenu::item:selected {
                    background-color: rgba(0, 122, 255, 0.2);
                }
                QMenu::item:pressed {
                    background-color: rgba(0, 122, 255, 0.3);
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #cccccc;
                    margin: 3px 8px;
                }
            """)
        else:
            # Linux风格菜单
            self.menu.setStyleSheet("""
                QMenu {
                    background-color: #f5f5f5;
                    border: 1px solid #d0d0d0;
                    border-radius: 3px;
                    padding: 4px;
                }
                QMenu::item {
                    background-color: transparent;
                    padding: 6px 22px 6px 22px;
                    margin: 1px 4px;
                }
                QMenu::item:selected {
                    background-color: rgba(61, 174, 233, 0.2);
                }
                QMenu::item:pressed {
                    background-color: rgba(61, 174, 233, 0.3);
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #d0d0d0;
                    margin: 4px 8px;
                }
            """)
        
        # 创建菜单项 - 开始/停止监听
        self.toggle_action = QAction("开始监听", self)
        self.toggle_action.triggered.connect(self._on_toggle_action)
        
        # 创建菜单项 - 显示主窗口
        show_window_action = QAction("显示主窗口", self)
        show_window_action.triggered.connect(self.show_window_signal.emit)
        
        # 创建菜单项 - 设置
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings_signal.emit)
        
        # 创建菜单项 - 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        
        # 创建菜单项 - 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exit_app_signal.emit)
        
        # 添加菜单项到菜单
        self.menu.addAction(self.toggle_action)
        self.menu.addAction(show_window_action)
        self.menu.addAction(settings_action)
        self.menu.addSeparator()
        self.menu.addAction(about_action)
        self.menu.addSeparator()
        self.menu.addAction(exit_action)
        
        # 设置右键菜单
        self.setContextMenu(self.menu)
    
    def _setup_event_handlers(self):
        """设置托盘图标事件处理"""
        self.logger.debug("设置托盘图标事件处理器")
        
        # 连接激活信号（单击、双击等）
        self.activated.connect(self._on_tray_activated)
    
    def _on_tray_activated(self, reason):
        """处理托盘图标激活事件"""
        # ActivationReason枚举值:
        # 1: 上下文菜单 (Trigger)
        # 2: 左键双击 (DoubleClick)
        # 3: 左键单击 (Trigger)
        # 4: 中键单击 (MiddleClick)
        
        self.logger.debug(f"托盘图标被激活，原因: {reason}")
        
        # macOS系统托盘行为特殊处理
        if self.platform == 'darwin':
            # macOS上单击通常显示菜单，我们将双击/单击都处理为显示窗口
            if reason in [QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick]:
                self.show_window_signal.emit()
                self.logger.debug("macOS托盘事件：显示主窗口")
                return
        
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 双击 - 显示主窗口
            self.is_double_click = True
            if self.click_timer:
                self.click_timer.stop()
            self.show_window_signal.emit()
            self.logger.debug("双击事件：显示主窗口")
            
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Linux上可能不响应单击，使用单独的处理
            if self.platform.startswith('linux'):
                # 在Linux上直接处理单击，无需延迟
                self.toggle_drawing_signal.emit()
                self.logger.debug("Linux单击事件：切换绘制状态")
                return
            
            # 左键单击 - 使用定时器延迟处理，避免与双击冲突
            self.is_double_click = False
            if self.click_timer:
                self.click_timer.stop()
            
            # 创建定时器延迟处理单击事件
            self.click_timer = QTimer()
            self.click_timer.setSingleShot(True)
            self.click_timer.timeout.connect(self._handle_single_click)
            
            # Windows上使用较短的延迟
            delay = 250 if self.platform == 'win32' else 300
            self.click_timer.start(delay)
            
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            # 中键点击 - 显示设置页面
            self.show_settings_signal.emit()
            self.logger.debug("中键事件：显示设置页面")
    
    def _handle_single_click(self):
        """处理延迟的单击事件"""
        if not self.is_double_click:
            # 如果不是双击的一部分，则执行单击操作
            self.toggle_drawing_signal.emit()
            self.logger.debug("单击事件：切换绘制状态")
    
    def _on_toggle_action(self):
        """处理开始/停止监听动作"""
        self.toggle_drawing_signal.emit()
    
    def _show_about(self):
        """显示关于信息"""
        show_info(None, f"关于 {APP_NAME}\n\n{get_version_string()}\n\n一款鼠标手势工具")
    
    def update_drawing_state(self, is_active):
        """更新绘制状态，同步更新菜单项文本"""
        self.drawing_active = is_active
        self.toggle_action.setText("停止监听" if is_active else "开始监听")
        
        # 更新工具提示
        # 根据不同系统设置不同的状态显示格式
        if self.platform == 'darwin':
            # macOS通常对通知文本更简洁
            self.setToolTip(f"{APP_NAME} {is_active and '●' or '○'}")
        elif self.platform == 'win32':
            # Windows上使用括号提示
            self.setToolTip(f"{APP_NAME} {'(监听中)' if is_active else '(已停止)'}")
        else:
            # Linux等其他系统
            self.setToolTip(f"{APP_NAME} - {'监听中' if is_active else '已停止'}")
            
        self.logger.debug(f"更新托盘图标状态: {'监听中' if is_active else '已停止'}")

def get_system_tray(parent=None):
    """获取系统托盘图标单例实例"""
    if not hasattr(get_system_tray, "_instance") or get_system_tray._instance is None:
        # 尝试加载不同平台适合的图标格式
        icon_found = False
        app_icon = QIcon()
        
        # 图标查找顺序（根据平台优先级）
        icon_formats = []
        
        if sys.platform == 'win32':
            # Windows优先查找ICO格式
            icon_formats = ['icon.ico', 'icon.svg', 'icon.png']
        elif sys.platform == 'darwin':
            # macOS优先查找高分辨率图标
            icon_formats = ['icon.svg', 'icon@2x.png', 'icon.png', 'icon.icns']
        else:
            # Linux和其他系统
            icon_formats = ['icon.svg', 'icon.png']
        
        # 尝试按优先级加载图标
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../assets/images'))
        for icon_name in icon_formats:
            icon_path = os.path.join(assets_dir, icon_name)
            if os.path.exists(icon_path):
                app_icon = QIcon(icon_path)
                icon_found = True
                break
        
        if not icon_found:
            # 最后尝试加载默认SVG图标
            default_icon_path = os.path.join(assets_dir, 'icon.svg')
            if os.path.exists(default_icon_path):
                app_icon = QIcon(default_icon_path)
        
        get_system_tray._instance = SystemTrayIcon(app_icon, parent)
    
    return get_system_tray._instance

# 示例代码
if __name__ == "__main__":
    # 示例用法
    import sys
    app = QApplication(sys.argv)
    
    # 创建系统托盘图标
    tray_icon = get_system_tray()
    
    # 定义简单的处理函数
    def toggle_action():
        print("切换绘制状态")
        # 切换托盘图标状态（仅用于演示）
        is_active = not getattr(toggle_action, 'is_active', False)
        toggle_action.is_active = is_active
        tray_icon.update_drawing_state(is_active)
        print(f"当前状态: {'监听中' if is_active else '已停止'}")
    
    def show_window():
        print("显示主窗口")
    
    def show_settings():
        print("显示设置页面")
    
    def exit_app():
        print("退出应用")
        app.quit()
    
    # 连接信号
    tray_icon.toggle_drawing_signal.connect(toggle_action)
    tray_icon.show_window_signal.connect(show_window)
    tray_icon.show_settings_signal.connect(show_settings)
    tray_icon.exit_app_signal.connect(exit_app)
    
    # 显示托盘图标
    tray_icon.show()
    
    print(f"系统托盘示例已启动 (平台: {sys.platform})")
    print("- 左键单击: 切换开始/停止监听")
    print("- 双击: 显示主窗口")
    print("- 中键点击: 显示设置页面")
    print("- 右键: 显示菜单")
    
    sys.exit(app.exec())