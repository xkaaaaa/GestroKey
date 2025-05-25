import os
import sys
import time

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
)

# 导入PyQtWidgetForge库中的按钮组件
from PyQtWidgetForge.widgets import ForgeButton

from core.drawer import DrawingManager
from core.logger import get_logger
from ui.components.dialog import show_dialog  # 导入自定义对话框组件
from ui.components.navigation_menu import SideNavigationMenu  # 导入导航菜单组件
from ui.components.system_tray import get_system_tray  # 导入系统托盘图标
from ui.components.toast_notification import (  # 导入Toast通知组件
    get_toast_manager,
    show_error,
    show_info,
    show_warning,
)
from ui.console import ConsolePage
from ui.gestures.gestures import get_gesture_library  # 导入手势库
from ui.gestures.gestures_tab import GesturesPage  # 导入手势管理页面
from ui.settings.settings import get_settings
from ui.settings.settings_tab import SettingsPage
from ui.splash_screen import SplashScreen  # 导入加载动画页面
from version import APP_NAME, get_version_string  # 导入版本信息


class GestroKeyApp(QMainWindow):
    """GestroKey应用程序主窗口"""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("MainApp")
        self.drawing_manager = None
        self.is_drawing_active = False

        # 在程序启动时初始化设置和手势库
        self.init_global_resources()

        # 初始化UI
        self.initUI()

        # 初始化系统托盘图标
        self.init_system_tray()

        # 初始化Toast管理器并设置主窗口引用
        toast_manager = get_toast_manager()
        toast_manager.set_main_window(self)
        self.logger.debug("初始化Toast管理器并设置主窗口引用")

        self.logger.info("GestroKey应用程序已启动")

    def init_global_resources(self):
        """初始化全局资源 - 设置和手势库"""
        try:
            # 初始化设置管理器
            settings = get_settings()
            self.logger.info("设置管理器初始化完成")

            # 初始化手势库管理器
            gestures = get_gesture_library()
            self.logger.info("手势库管理器初始化完成")
        except Exception as e:
            self.logger.error(f"初始化全局资源失败: {e}")
            raise

    def init_system_tray(self):
        """初始化系统托盘图标"""
        try:
            # 获取托盘图标实例
            self.tray_icon = get_system_tray(self)

            # 连接托盘图标信号
            self.tray_icon.toggle_drawing_signal.connect(self.toggle_drawing)
            self.tray_icon.show_window_signal.connect(self.show_and_activate)
            self.tray_icon.show_settings_signal.connect(self.show_settings_page)
            self.tray_icon.exit_app_signal.connect(self.close)

            # 显示托盘图标
            self.tray_icon.show()
            self.logger.info("系统托盘图标初始化完成")
        except Exception as e:
            self.logger.error(f"初始化系统托盘图标失败: {e}")

    def toggle_drawing(self):
        """切换绘制状态 - 托盘图标调用"""
        self.logger.info("从托盘图标切换绘制状态")
        if hasattr(self, "console_page"):
            if self.is_drawing_active:
                self.stop_drawing()
            else:
                self.start_drawing()
        else:
            self.logger.warning("找不到控制台页面，无法切换绘制状态")

    def start_drawing(self):
        """开始绘制 - 托盘图标调用"""
        if not self.is_drawing_active and hasattr(self, "console_page"):
            self.console_page.start_drawing()
            self.is_drawing_active = True
            # 更新托盘图标状态
            if hasattr(self, "tray_icon"):
                self.tray_icon.update_drawing_state(True)
            self.logger.info("已启动绘制功能")

    def stop_drawing(self):
        """停止绘制 - 托盘图标调用"""
        if self.is_drawing_active and hasattr(self, "console_page"):
            self.console_page.stop_drawing()
            self.is_drawing_active = False
            # 更新托盘图标状态
            if hasattr(self, "tray_icon"):
                self.tray_icon.update_drawing_state(False)
            self.logger.info("已停止绘制功能")

    def show_and_activate(self):
        """显示并激活主窗口"""
        # 先显示窗口
        self.show()

        # 根据不同操作系统处理窗口激活方式
        import sys

        if sys.platform == "win32":
            # Windows平台 - 增强版激活方法
            # 首先确保窗口不是最小化状态
            if self.isMinimized():
                self.setWindowState(
                    self.windowState() & ~Qt.WindowState.WindowMinimized
                )

            # 使用多种窗口标志组合来激活窗口
            self.setWindowState(
                self.windowState() & ~Qt.WindowState.WindowMinimized
                | Qt.WindowState.WindowActive
            )

            # 提高窗口显示的优先级
            self.raise_()
            self.activateWindow()

            # 使用Win32 API确保窗口激活（在某些Windows版本上更可靠）
            try:
                import ctypes
                from ctypes import wintypes

                # 获取窗口句柄
                hwnd = int(self.winId())

                # 在前台显示窗口并激活
                user32 = ctypes.WinDLL("user32", use_last_error=True)

                # SetForegroundWindow函数使窗口置于前台
                user32.SetForegroundWindow.argtypes = [wintypes.HWND]
                user32.SetForegroundWindow.restype = wintypes.BOOL
                user32.SetForegroundWindow(hwnd)

                # 确保不是最小化
                user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
                user32.ShowWindow.restype = wintypes.BOOL

                # SW_RESTORE = 9, SW_SHOW = 5, SW_SHOWNA = 8 (显示窗口但不激活)
                user32.ShowWindow(hwnd, 9)  # 如果窗口最小化则还原

                # BringWindowToTop函数将窗口带到Z序顶部
                user32.BringWindowToTop.argtypes = [wintypes.HWND]
                user32.BringWindowToTop.restype = wintypes.BOOL
                user32.BringWindowToTop(hwnd)

                self.logger.debug("成功使用Win32 API激活窗口")
            except Exception as e:
                # 如果Win32 API调用失败，使用Qt方法作为备选
                self.logger.warning(f"Win32 API窗口激活失败: {e}，使用Qt方法作为备选")
                # 继续使用Qt方法

            # 添加延迟处理，确保窗口被激活
            QTimer.singleShot(
                50,
                lambda: [
                    self.activateWindow(),
                    self.raise_(),
                    QApplication.processEvents(),
                ],
            )

            # 再次尝试，有些Windows版本需要多次尝试才能激活
            QTimer.singleShot(
                150,
                lambda: [
                    self.activateWindow(),
                    self.raise_(),
                    QApplication.processEvents(),
                ],
            )

        elif sys.platform == "darwin":
            # macOS平台 - 使用不同顺序可以提高可靠性
            # 先还原窗口（如果最小化）
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
            # 延迟一点再激活窗口，让系统有时间处理窗口状态
            QTimer.singleShot(10, self.raise_)
            QTimer.singleShot(20, self.activateWindow)

            # 对于macOS，使用两步操作提高可靠性
            QTimer.singleShot(
                50,
                lambda: [
                    self.raise_(),
                    QApplication.processEvents(),
                    self.activateWindow(),
                ],
            )
        else:
            # Linux平台 - 不同窗口管理器的处理方式可能不同
            # 先还原窗口（如果最小化）
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)

            # 在Linux上，多次尝试激活窗口，并处理事件循环
            def try_activate():
                self.raise_()
                self.activateWindow()
                QApplication.processEvents()

            # 立即尝试一次
            try_activate()
            # 然后延迟再尝试几次
            QTimer.singleShot(50, try_activate)
            QTimer.singleShot(150, try_activate)

        self.logger.info(f"在{sys.platform}平台上显示并激活主窗口")

    def show_settings_page(self):
        """显示设置页面"""
        self.show_and_activate()
        # 切换到设置页面
        if hasattr(self, "navigation_menu"):
            # 查找设置页面的索引（默认为1）
            settings_index = 1
            # 由于SideNavigationMenu没有count方法，直接使用我们知道的页面信息
            # 控制台页面索引为0，手势管理页面索引为1，设置页面索引为2
            for i in range(3):  # 假设有3个页面
                if self.navigation_menu.widget(i) == self.settings_page:
                    settings_index = i
                    break

            self.navigation_menu.setCurrentPage(settings_index)
            self.logger.info(f"切换到设置页面，索引: {settings_index}")
        else:
            self.logger.warning("找不到导航菜单，无法切换到设置页面")

    def initUI(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle(APP_NAME)
        self.setGeometry(300, 300, 1000, 680)  # 增大默认窗口大小，宽度从850增加到1000，高度从650增加到680
        self.setMinimumSize(800, 500)  # 增加最小窗口大小，宽度从640增加到800，高度从480增加到500

        # 设置应用图标
        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "images", "icon.svg"
        )
        if os.path.exists(icon_path):
            self.logger.info(f"加载窗口图标: {icon_path}")
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            # 同时设置应用程序图标
            QApplication.setWindowIcon(app_icon)
        else:
            self.logger.warning(f"窗口图标文件不存在: {icon_path}")

        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 去除边距以获得更好的视觉效果
        main_layout.setSpacing(0)  # 减少布局间距

        # 创建页面内容
        self.logger.debug("创建控制台页面")
        self.console_page = ConsolePage()

        # 连接控制台页面的绘制状态变化信号
        self.console_page.drawing_state_changed.connect(self.on_drawing_state_changed)

        self.logger.debug("创建设置页面")
        self.settings_page = SettingsPage()

        self.logger.debug("创建手势管理页面")
        self.gestures_page = GesturesPage()

        # 创建侧边栏导航菜单
        self.logger.debug("创建侧边栏导航菜单")
        self.navigation_menu = SideNavigationMenu()
        self.navigation_menu.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # 创建页面图标
        # 尝试使用存在的图标文件，而不是依赖系统主题
        icons_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "images"
        )
        console_icon_path = os.path.join(icons_dir, "console.svg")
        settings_icon_path = os.path.join(icons_dir, "settings.svg")
        gestures_icon_path = os.path.join(icons_dir, "gestures.svg")

        # 如果图标文件存在则使用，否则使用空图标
        console_icon = (
            QIcon(console_icon_path) if os.path.exists(console_icon_path) else QIcon()
        )
        settings_icon = (
            QIcon(settings_icon_path) if os.path.exists(settings_icon_path) else QIcon()
        )
        gestures_icon = (
            QIcon(gestures_icon_path) if os.path.exists(gestures_icon_path) else QIcon()
        )

        # 添加页面到侧边栏导航菜单
        self.logger.debug("添加页面到侧边栏导航菜单")
        # 控制台页面放在顶部
        console_index = self.navigation_menu.addPage(
            self.console_page, "控制台", console_icon, self.navigation_menu.POSITION_TOP
        )
        # 手势管理页面也放在顶部
        gestures_index = self.navigation_menu.addPage(
            self.gestures_page, "手势管理", gestures_icon, self.navigation_menu.POSITION_TOP
        )
        # 设置页面放在底部
        settings_index = self.navigation_menu.addPage(
            self.settings_page,
            "设置",
            settings_icon,
            self.navigation_menu.POSITION_BOTTOM,
        )

        # 页面切换事件连接
        self.navigation_menu.currentChanged.connect(self.onPageChanged)

        # 将导航菜单添加到主布局
        self.logger.debug("将导航菜单添加到主布局")
        main_layout.addWidget(self.navigation_menu, 1)  # 设置1的拉伸系数，让导航菜单占据大部分空间

        # 添加底部状态栏
        status_widget = QWidget()
        status_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)  # 设置适当的边距

        # 使用自定义动画按钮替换标准按钮
        self.exit_button = ForgeButton("退出程序", level="danger")
        self.exit_button.clicked.connect(self.close)

        self.version_label = QLabel(get_version_string())
        self.version_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.version_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        status_layout.addWidget(self.exit_button)
        status_layout.addStretch(1)
        status_layout.addWidget(self.version_label)

        # 设置状态栏布局
        status_widget.setLayout(status_layout)
        main_layout.addWidget(status_widget)

        # 显示窗口
        self.show()

        # 初始化后确保选择控制台页面
        self.logger.debug("设置初始页面为控制台")
        QApplication.processEvents()  # 处理待处理的事件

        # 使用单次计时器延迟设置初始页面，确保UI完全准备好
        QTimer.singleShot(100, lambda: self._select_initial_page())

    def _select_initial_page(self):
        """选择初始页面（延迟执行）"""
        try:
            if hasattr(self, "navigation_menu") and self.navigation_menu:
                self.logger.debug("设置初始页面索引为0（控制台）")
                self.navigation_menu.setCurrentPage(0)  # 确保控制台页面被选中
                QApplication.processEvents()  # 再次处理事件，确保UI更新
        except Exception as e:
            self.logger.error(f"设置初始页面时出错: {e}")

    def onPageChanged(self, index):
        """页面切换事件处理"""
        page_name = (
            "控制台"
            if index == 0
            else "设置"
            if index == 1
            else "手势管理"
            if index == 2
            else f"未知({index})"
        )
        self.logger.debug(f"切换到页面: {index} ({page_name})")

    def resizeEvent(self, event):
        """窗口尺寸变化事件处理"""
        super().resizeEvent(event)
        self.logger.debug(f"主窗口大小已调整: {self.width()}x{self.height()}")

        # 更新全局通知的位置
        toast_manager = get_toast_manager()
        toast_manager.update_positions_on_resize()

    def closeEvent(self, event):
        """关闭窗口事件处理"""
        self.logger.info("程序准备关闭")

        # 如果已经在关闭过程中，不再询问
        if hasattr(self, "_closing") and self._closing:
            self.logger.info("已在关闭过程中，直接接受关闭事件")
            event.accept()
            return

        # 如果有活动的对话框，忽略此次关闭事件
        if hasattr(self, "current_dialog") and self.current_dialog:
            self.logger.info("检测到活动对话框，忽略此次关闭事件")
            event.ignore()
            return

        # 如果控制台页面存在，停止绘制
        if hasattr(self, "console_page"):
            self.console_page.stop_drawing()

        # 确保释放所有可能的按键状态
        from core.gesture_executor import get_gesture_executor

        try:
            executor = get_gesture_executor()
            executor.release_all_keys()
            self.logger.info("已释放所有可能的按键状态")
        except Exception as e:
            self.logger.error(f"释放按键状态时出错: {e}")

        # 检查是否有未保存的更改
        unsaved_settings = False
        unsaved_gestures = False

        # 检查设置是否有未保存的更改
        if hasattr(self, "settings_page") and self.settings_page.has_unsaved_changes():
            unsaved_settings = True

        # 检查手势库是否有未保存的更改
        if hasattr(self, "gestures_page") and self.gestures_page.has_unsaved_changes():
            unsaved_gestures = True

        # 如果存在未保存的更改，询问用户
        if unsaved_settings or unsaved_gestures:
            self.logger.info("检测到未保存的更改")
            # 使用全局对话框方法
            self.show_global_dialog(
                message_type="question",
                title_text="保存更改",
                message="检测到未保存的更改，是否保存后退出？",
                custom_buttons=["是", "否", "取消"],
                callback=self._handle_save_changes_response,
            )
            # 暂时阻止关闭窗口，等待对话框结果
            event.ignore()
            return

        # 记录日志
        self.logger.info("程序正常关闭")
        # 接受事件，关闭窗口
        event.accept()

    def _handle_save_changes_response(self, button_text):
        """处理保存更改对话框的响应"""
        self.logger.info(f"用户选择: {button_text}")

        # 设置关闭标志，防止重复弹出对话框
        self._closing = True

        # 跟踪保存操作是否成功
        save_success = True

        if button_text == "是":
            unsaved_settings = False
            unsaved_gestures = False

            # 检查设置是否有未保存的更改
            if (
                hasattr(self, "settings_page")
                and self.settings_page.has_unsaved_changes()
            ):
                unsaved_settings = True

            # 检查手势库是否有未保存的更改
            if (
                hasattr(self, "gestures_page")
                and self.gestures_page.has_unsaved_changes()
            ):
                unsaved_gestures = True

            try:
                # 保存设置
                if unsaved_settings:
                    self.logger.info("正在保存设置...")
                    if self.settings_page.save_settings():
                        self.logger.info("设置已保存")
                    else:
                        self.logger.error("保存设置失败")
                        save_success = False
                        show_error(self, "保存设置失败，取消退出")
            except Exception as e:
                self.logger.error(f"保存设置时出现异常: {e}")
                save_success = False
                show_error(self, f"保存设置时出错: {str(e)}，取消退出")

            try:
                # 保存手势库
                if unsaved_gestures and save_success:  # 只有前面的保存成功才继续保存手势库
                    self.logger.info("正在保存手势库...")
                    if self.gestures_page.saveGestureLibrary():
                        self.logger.info("手势库已保存")
                    else:
                        self.logger.error("保存手势库失败")
                        save_success = False
                        show_error(self, "保存手势库失败，取消退出")
            except Exception as e:
                self.logger.error(f"保存手势库时出现异常: {e}")
                save_success = False
                show_error(self, f"保存手势库时出错: {str(e)}，取消退出")

            # 如果保存失败，重置关闭标志
            if not save_success:
                self._closing = False
                self.logger.info("保存失败，取消退出")
                return

        # 只有选择"是"并且保存成功，或选择"否"才退出程序
        if (button_text == "是" and save_success) or button_text == "否":
            self.logger.info("准备退出程序")
            # 使用sys.exit强制退出，避免使用QApplication.quit
            import sys

            sys.exit(0)
        else:
            # 用户选择取消关闭，或保存失败，重置关闭标志
            self._closing = False
            self.logger.info("取消关闭窗口")

    def show_global_dialog(
        self,
        parent=None,
        message_type="warning",
        title_text=None,
        message="",
        content_widget=None,
        custom_icon=None,
        custom_buttons=None,
        custom_button_colors=None,
        callback=None,
    ):
        """全局对话框创建方法，确保阴影覆盖整个主窗口

        Args:
            parent: 父窗口 (会被忽略，总是使用主窗口作为父窗口)
            message_type: 对话框类型
            title_text: 标题文本
            message: 消息内容
            content_widget: 自定义内容组件
            custom_icon: 自定义图标
            custom_buttons: 自定义按钮列表
            custom_button_colors: 自定义按钮颜色字典
            callback: 按钮点击回调函数

        Returns:
            dialog: 对话框实例
        """
        # 始终记录对话框的创建
        self.logger.info(f"创建全局对话框: 类型={message_type}, 标题={title_text}")

        try:
            # 始终使用主窗口作为父窗口，确保阴影覆盖整个应用窗口
            dialog = show_dialog(
                parent=self,  # 使用主窗口作为父窗口
                message_type=message_type,
                title_text=title_text,
                message=message,
                content_widget=content_widget,
                custom_icon=custom_icon,
                custom_buttons=custom_buttons,
                custom_button_colors=custom_button_colors,
                callback=callback,
            )

            # 记录对话框创建成功
            self.logger.debug("全局对话框创建成功")

            # 将主窗口置为活动窗口以确保对话框显示在最前面
            self.activateWindow()
            self.raise_()

            # 保存当前对话框引用，避免被垃圾回收
            self.current_dialog = dialog

            return dialog
        except Exception as e:
            self.logger.error(f"创建全局对话框时出错: {e}")
            # 返回None表示创建失败
            return None

    def handle_dialog_close(self, dialog):
        """处理对话框关闭事件"""
        self.logger.debug("处理对话框关闭")
        if hasattr(self, "current_dialog") and self.current_dialog == dialog:
            self.current_dialog = None
            self.logger.debug("已清除当前对话框引用")

    def on_drawing_state_changed(self, is_active):
        """响应控制台页面的绘制状态变化"""
        self.is_drawing_active = is_active
        # 更新托盘图标状态
        if hasattr(self, "tray_icon"):
            self.tray_icon.update_drawing_state(is_active)
            self.logger.debug(f"托盘图标状态已更新: {'监听中' if is_active else '已停止'}")


if __name__ == "__main__":
    # 创建应用程序实例
    app = QApplication(sys.argv)

    # 解决高DPI显示问题
    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # 创建日志记录器
    logger = get_logger("Main")
    logger.info("启动GestroKey应用程序")

    # 显示加载画面
    splash = SplashScreen()
    splash.show()

    # 强制处理事件，确保加载画面立即显示
    for i in range(5):  # 多次处理事件，确保UI更新
        app.processEvents()

    # 延迟一会儿，给加载动画一些显示时间
    start_time = time.time()

    # 创建主窗口（但不显示）
    window = GestroKeyApp()

    # 确保加载画面至少显示1.5秒
    elapsed = time.time() - start_time
    if elapsed < 1.5:
        time.sleep(1.5 - elapsed)

    # 显示主窗口并关闭加载画面
    window.show()
    splash.fade_out_and_close()

    # 启动应用程序主循环
    sys.exit(app.exec())
