import argparse
import ctypes
import os
import sys
from ctypes import wintypes
from datetime import datetime

from version import QT_API
os.environ['QT_API'] = QT_API

from qtpy.QtCore import Qt, QTimer, QSize
from qtpy.QtGui import QIcon, QAction
from qtpy.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
    QSizePolicy, QStackedWidget, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu,
    QDialog, QCheckBox, QRadioButton, QButtonGroup
)

from core.logger import get_logger
from core.self_check import run_self_check
from ui.console import ConsolePage
from ui.gestures.gestures import get_gesture_library
from ui.gestures.gestures_tab import GesturesPage
from ui.settings.settings import get_settings
from ui.settings.settings_tab import SettingsPage
from version import APP_NAME, get_version_string


def show_dialog(parent, message_type="warning", title_text=None, message="", 
                content_widget=None, custom_icon=None, custom_buttons=None, 
                custom_button_colors=None, callback=None):
    title = title_text or "提示"
    
    if message_type == "question" and custom_buttons:
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        buttons = []
        for btn_text in custom_buttons:
            btn = msg_box.addButton(btn_text, QMessageBox.ButtonRole.ActionRole)
            buttons.append(btn)
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        if callback and clicked_button:
            for i, btn in enumerate(buttons):
                if btn == clicked_button:
                    callback(custom_buttons[i])
                    break
            
    elif message_type == "question":
        result = QMessageBox.question(
            parent, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if callback:
            callback("是" if result == QMessageBox.StandardButton.Yes else "否")
    elif message_type == "warning":
        QMessageBox.warning(parent, title, message)
    elif message_type == "error":
        QMessageBox.critical(parent, title, message)
    else:
        QMessageBox.information(parent, title, message)
    
    return None


def get_system_tray(parent):
    if not QSystemTrayIcon.isSystemTrayAvailable():
        return None
    
    def _get_icon_path(icon_name):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if icon_name.startswith("app/"):
            return os.path.join(base_dir, "assets", "images", icon_name)
        else:
            return os.path.join(base_dir, "assets", "images", "ui", icon_name)
    
    def _set_action_icon(action, icon_name):
        icon_path = _get_icon_path(icon_name)
        if os.path.exists(icon_path):
            action.setIcon(QIcon(icon_path))
    
    tray_icon = QSystemTrayIcon(parent)
    icon_path = _get_icon_path("app/icon.svg")
    if os.path.exists(icon_path):
        tray_icon.setIcon(QIcon(icon_path))
    else:
        tray_icon.setIcon(parent.style().standardIcon(parent.style().StandardPixmap.SP_ComputerIcon))
    
    menu = QMenu()
    
    show_action = QAction("显示窗口", parent)
    _set_action_icon(show_action, "tray-show.svg")
    show_action.triggered.connect(parent.show_and_activate)
    menu.addAction(show_action)
    
    menu.addSeparator()
    
    toggle_action = QAction("启动/停止监听", parent)
    toggle_action.triggered.connect(parent.toggle_drawing)
    menu.addAction(toggle_action)
    
    settings_action = QAction("设置", parent)
    _set_action_icon(settings_action, "settings.svg")
    settings_action.triggered.connect(parent.show_settings_page)
    menu.addAction(settings_action)
    
    menu.addSeparator()
    
    exit_action = QAction("退出", parent)
    _set_action_icon(exit_action, "exit.svg")
    exit_action.triggered.connect(parent._exit_application)
    menu.addAction(exit_action)
    
    tray_icon.setContextMenu(menu)
    
    def on_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            parent.show_and_activate()
    
    tray_icon.activated.connect(on_activated)
    
    def update_drawing_state(is_active):
        status = "监听中" if is_active else "已停止"
        tray_icon.setToolTip(f"GestroKey - {status}")
        toggle_action.setText(f"{'停止' if is_active else '启动'}监听")
        
        icon_name = "tray-stop.svg" if is_active else "tray-start.svg"
        _set_action_icon(toggle_action, icon_name)
    
    tray_icon.update_drawing_state = update_drawing_state
    tray_icon.update_drawing_state(False)
    
    return tray_icon





class GestroKeyApp(QMainWindow):
    def __init__(self, silent_start=False):
        super().__init__()
        self.logger = get_logger("MainApp")
        self.is_drawing_active = False
        self.silent_start = silent_start

        self.init_global_resources()
        self.initUI()
        self.init_system_tray()



        if self.silent_start:
            self.logger.info("GestroKey应用程序已静默启动")
            QTimer.singleShot(100, self._silent_start_drawing)
        else:
            self.logger.info("GestroKey应用程序已启动")

    def init_global_resources(self):
        try:
            self.logger.info("运行程序自检...")
            
            if not run_self_check():
                self.logger.warning("自检发现问题，但程序继续启动")
            else:
                self.logger.info("程序自检通过")
        except Exception as e:
            self.logger.error(f"运行自检时发生异常: {e}")
        
        try:
            settings = get_settings()
            self.logger.info("设置管理器初始化完成")

            gestures = get_gesture_library()
            self.logger.info("手势库管理器初始化完成")
        except Exception as e:
            self.logger.error(f"初始化全局资源失败: {e}")
            raise

    def init_system_tray(self):
        try:
            self.tray_icon = get_system_tray(self)
            
            if self.tray_icon:
                self.tray_icon.show()
                self.logger.info("系统托盘图标初始化完成")
            else:
                self.logger.info("系统托盘功能不可用")
        except Exception as e:
            self.logger.error(f"初始化系统托盘图标失败: {e}")

    def toggle_drawing(self):
        self.logger.info("从托盘图标切换绘制状态")
        if hasattr(self, "console_page"):
            if self.is_drawing_active:
                self.stop_drawing()
            else:
                self.start_drawing()
        else:
            self.logger.warning("找不到控制台页面，无法切换绘制状态")

    def _silent_start_drawing(self):
        """静默启动时的绘制启动方法"""
        if hasattr(self, "console_page"):
            self.start_drawing()
        else:
            # 如果console_page还未初始化，再延迟一点时间
            self.logger.warning("console_page尚未初始化，延迟启动监听")
            QTimer.singleShot(200, self._silent_start_drawing)

    def start_drawing(self):
        if not self.is_drawing_active and hasattr(self, "console_page"):
            self.console_page.start_drawing()
            self.is_drawing_active = True
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.update_drawing_state(True)
            self.logger.info("已启动绘制功能")

    def stop_drawing(self):
        if self.is_drawing_active and hasattr(self, "console_page"):
            self.console_page.stop_drawing()
            self.is_drawing_active = False
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.update_drawing_state(False)
            self.logger.info("已停止绘制功能")

    def show_and_activate(self):
        self.show()

        if sys.platform == "win32":
            if self.isMinimized():
                self.setWindowState(
                    self.windowState() & ~Qt.WindowState.WindowMinimized
                )

            self.setWindowState(
                self.windowState() & ~Qt.WindowState.WindowMinimized
                | Qt.WindowState.WindowActive
            )

            self.raise_()
            self.activateWindow()

            try:
                hwnd = int(self.winId())
                user32 = ctypes.WinDLL("user32", use_last_error=True)

                user32.SetForegroundWindow.argtypes = [wintypes.HWND]
                user32.SetForegroundWindow.restype = wintypes.BOOL
                user32.SetForegroundWindow(hwnd)

                user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
                user32.ShowWindow.restype = wintypes.BOOL
                user32.ShowWindow(hwnd, 9)

                user32.BringWindowToTop.argtypes = [wintypes.HWND]
                user32.BringWindowToTop.restype = wintypes.BOOL
                user32.BringWindowToTop(hwnd)

                self.logger.debug("成功使用Win32 API激活窗口")
            except Exception as e:
                self.logger.warning(f"Win32 API窗口激活失败: {e}，使用Qt方法作为备选")

            QTimer.singleShot(
                50,
                lambda: [
                    self.activateWindow(),
                    self.raise_(),
                    QApplication.processEvents(),
                ],
            )

            QTimer.singleShot(
                150,
                lambda: [
                    self.activateWindow(),
                    self.raise_(),
                    QApplication.processEvents(),
                ],
            )

        elif sys.platform == "darwin":
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
            QTimer.singleShot(10, self.raise_)
            QTimer.singleShot(20, self.activateWindow)

            QTimer.singleShot(
                50,
                lambda: [
                    self.raise_(),
                    QApplication.processEvents(),
                    self.activateWindow(),
                ],
            )
        else:
            self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)

            def try_activate():
                self.raise_()
                self.activateWindow()

                QApplication.processEvents()

            try_activate()
            QTimer.singleShot(50, try_activate)
            QTimer.singleShot(150, try_activate)

        self.logger.info(f"在{sys.platform}平台上显示并激活主窗口")

    def show_settings_page(self):
        """显示设置页面"""
        self.show_and_activate()
        # 切换到设置页面
        if hasattr(self, "stacked_widget"):
            self.switch_page(2)  # 设置页面的索引是2
            self.logger.info("切换到设置页面")
        else:
            self.logger.warning("找不到页面堆栈，无法切换到设置页面")

    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(300, 300, 1000, 680)
        self.setMinimumSize(800, 500)

        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "images", "app", "icon.svg"
        )
        if os.path.exists(icon_path):
            self.logger.info(f"加载窗口图标: {icon_path}")
            app_icon = QIcon(icon_path)
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)
        else:
            self.logger.warning(f"窗口图标文件不存在: {icon_path}")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.console_page = ConsolePage()
        self.console_page.drawing_state_changed.connect(self.on_drawing_state_changed)

        self.settings_page = SettingsPage()
        self.gestures_page = GesturesPage()
        
        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
        
        def _create_tab_button(text, icon_name, page_index):
            button = QPushButton(text)
            icon_path = os.path.join(assets_dir, "ui", icon_name)
            if os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
            button.clicked.connect(lambda: self.switch_page(page_index))
            button.setMinimumHeight(40)
            button.setIconSize(QSize(20, 20))
            return button
        
        self.console_btn = _create_tab_button("控制台", "console.svg", 0)
        self.gestures_btn = _create_tab_button("手势管理", "gestures.svg", 1)
        self.settings_btn = _create_tab_button("设置", "settings.svg", 2)
        
        tab_layout.addWidget(self.console_btn)
        tab_layout.addWidget(self.gestures_btn)
        tab_layout.addWidget(self.settings_btn)
        tab_layout.addStretch()
        
        main_layout.addWidget(tab_widget)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        
        self.stacked_widget.addWidget(self.console_page)
        self.stacked_widget.addWidget(self.gestures_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        main_layout.addWidget(self.stacked_widget, 1)

        status_widget = QWidget()
        status_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)

        self.exit_button = QPushButton("退出程序")
        self.exit_button.setMinimumSize(120, 36)
        self.exit_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.exit_button.clicked.connect(self._exit_application)
        exit_icon_path = os.path.join(assets_dir, "ui", "exit.svg")
        if os.path.exists(exit_icon_path):
            self.exit_button.setIcon(QIcon(exit_icon_path))
            self.exit_button.setIconSize(QSize(18, 18))

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

        status_widget.setLayout(status_layout)
        main_layout.addWidget(status_widget)

        if not self.silent_start:
            self.show()

        QApplication.processEvents()
        QTimer.singleShot(100, lambda: self._select_initial_page())

    def switch_page(self, index):
        try:
            self.stacked_widget.setCurrentIndex(index)
            self.onPageChanged(index)
            
            buttons = [self.console_btn, self.gestures_btn, self.settings_btn]
            for i, btn in enumerate(buttons):
                btn.setStyleSheet("font-weight: bold;" if i == index else "")
        except Exception as e:
            self.logger.error(f"切换页面时出错: {e}")

    def _select_initial_page(self):
        try:
            if hasattr(self, "stacked_widget") and self.stacked_widget:
                self.switch_page(0)
                QApplication.processEvents()
        except Exception as e:
            self.logger.error(f"设置初始页面时出错: {e}")

    def onPageChanged(self, index):
        page_name = (
            "控制台"
            if index == 0
            else "手势管理"
            if index == 1
            else "设置"
            if index == 2
            else f"未知({index})"
        )
        self.logger.debug(f"切换到页面: {index} ({page_name})")

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.logger.info("检测到窗口关闭事件")
        self._handle_close_request(is_window_close=True)
        event.ignore()

    def _show_exit_dialog(self):
        class ExitDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("退出程序")
                self.setFixedSize(350, 130)
                self.setModal(True)
                
                self.settings = get_settings()
                
                layout = QVBoxLayout(self)
                
                question_label = QLabel("是否退出程序？")
                question_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0;")
                layout.addWidget(question_label)
                
                self.dont_show_checkbox = QCheckBox("不再显示此对话框")
                layout.addWidget(self.dont_show_checkbox)
                
                button_layout = QHBoxLayout()
                
                self.minimize_btn = QPushButton("最小化到托盘")
                self.exit_btn = QPushButton("退出程序")
                self.cancel_btn = QPushButton("取消")
                
                self.minimize_btn.clicked.connect(self._on_minimize_clicked)
                self.exit_btn.clicked.connect(self._on_exit_clicked)
                self.cancel_btn.clicked.connect(self.reject)
                
                button_layout.addWidget(self.minimize_btn)
                button_layout.addWidget(self.exit_btn)
                button_layout.addWidget(self.cancel_btn)
                
                layout.addLayout(button_layout)
            
            def _on_minimize_clicked(self):
                if self.dont_show_checkbox.isChecked():
                    self.settings.set("app.show_exit_dialog", False)
                    self.settings.set("app.default_close_action", "minimize")
                    self.settings.save()
                    self.parent()._notify_settings_changed()
                
                self.accept()
                self.parent()._minimize_to_tray()
            
            def _on_exit_clicked(self):
                if self.dont_show_checkbox.isChecked():
                    self.settings.set("app.show_exit_dialog", False)
                    self.settings.set("app.default_close_action", "exit")
                    self.settings.save()
                    self.parent()._notify_settings_changed()
                
                self.accept()
                self.parent()._exit_with_save_check()
        
        dialog = ExitDialog(self)
        dialog.exec()

    def _handle_close_request(self, is_window_close=False):
        """统一的关闭请求处理"""
        self.logger.info(f"处理关闭请求，窗口关闭: {is_window_close}")
        
        # 检查是否有活动对话框
        if hasattr(self, "current_dialog") and self.current_dialog:
            self.logger.info("检测到活动对话框，忽略关闭请求")
            return
        
        # 停止绘制和释放按键
        self._prepare_for_close()
        
        settings = get_settings()
        
        if is_window_close:
            show_exit_dialog = settings.get("app.show_exit_dialog", True)
            if show_exit_dialog:
                self._show_exit_dialog()
                return
            
            default_action = settings.get("app.default_close_action", "minimize")
            if default_action == "minimize":
                self._minimize_to_tray()
                return
        
        # 强制退出或者默认行为是退出
        self._exit_with_save_check()
    
    def _prepare_for_close(self):
        """准备关闭：停止绘制和释放按键"""
        if hasattr(self, "console_page"):
            self.console_page.stop_drawing()
        
        from core.gesture_executor import get_gesture_executor
        try:
            executor = get_gesture_executor()
            executor.release_all_keys()
            self.logger.info("已释放所有可能的按键状态")
        except Exception as e:
            self.logger.error(f"释放按键状态时出错: {e}")

    def _notify_settings_changed(self):
        """通知设置已更改，需要更新内存和UI"""
        # 重新加载设置到内存
        settings = get_settings()
        settings.load()
        self.logger.info("已重新加载设置到内存")
        
        # 刷新设置页面UI
        if hasattr(self, "settings_page"):
            self.settings_page._load_settings()
            self.logger.info("已刷新设置页面UI")

    def _minimize_to_tray(self):
        """最小化到托盘"""
        self.hide()
        self.logger.info("程序已最小化到托盘")

    def _exit_application(self):
        """退出应用程序入口（强制退出）"""
        self.logger.info("强制退出应用程序")
        self._prepare_for_close()
        self._exit_with_save_check()
    
    def _exit_with_save_check(self):
        """退出程序并检查未保存项目"""
        self.logger.info("准备退出程序，检查未保存项目")
        try:
            self.logger.debug("即将调用_check_unsaved_and_exit方法")
            self._check_unsaved_and_exit()
        except Exception as e:
            self.logger.error(f"调用_check_unsaved_and_exit时出错: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self._force_exit()

    def _check_unsaved_and_exit(self):
        try:
            unsaved_settings = False
            unsaved_gestures = False
            
            try:
                if hasattr(self, "settings_page"):
                    frontend_changes = self.settings_page.has_unsaved_changes()
                    if frontend_changes:
                        unsaved_settings = True
                else:
                    settings = get_settings()
                    settings_has_changes = settings.has_changes()
                    if settings_has_changes:
                        unsaved_settings = True
            except Exception as e:
                self.logger.error(f"检查设置变更时出错: {e}")

            try:
                gesture_library = get_gesture_library()
                gestures_has_changes = gesture_library.has_changes()
                if gestures_has_changes:
                    unsaved_gestures = True
            except Exception as e:
                self.logger.error(f"检查手势库变更时出错: {e}")

            if unsaved_settings or unsaved_gestures:
                self.logger.info("检测到未保存的更改")
                self.show_global_dialog(
                    message_type="question",
                    title_text="保存更改",
                    message="检测到未保存的更改，是否保存后退出？",
                    custom_buttons=["是", "否", "取消"],
                    callback=self._handle_save_changes_response,
                )
                return

            self._force_exit()
            
        except Exception as e:
            self.logger.error(f"检查未保存更改时发生严重错误: {e}")
            self._force_exit()
    
    def _force_exit(self):
        """强制退出程序"""
        self.logger.info("程序正常关闭")
        import sys
        sys.exit(0)

    def _handle_save_changes_response(self, button_text):
        self.logger.info(f"用户选择: {button_text}")

        self._closing = True
        save_success = True

        if button_text == "是":
            try:
                # 保存设置（如果设置页面有未保存的更改）
                if hasattr(self, "settings_page") and self.settings_page.has_unsaved_changes():
                    self.logger.info("正在保存设置...")
                    self.settings_page._apply_settings()
                    if self.settings_page.settings.save():
                        self.logger.info("设置已保存")
                    else:
                        self.logger.error("保存设置失败")
                        save_success = False
                        QMessageBox.critical(self, "错误", "保存设置失败，取消退出")
            except Exception as e:
                self.logger.error(f"保存设置时出现异常: {e}")
                save_success = False
                QMessageBox.critical(self, "错误", f"保存设置时出错: {str(e)}，取消退出")

            try:
                gesture_library = get_gesture_library()
                if save_success and gesture_library.has_changes():
                    self.logger.info("正在保存手势库...")
                    if gesture_library.save():
                        self.logger.info("手势库已保存")
                    else:
                        self.logger.error("保存手势库失败")
                        save_success = False
                        QMessageBox.critical(self, "错误", "保存手势库失败，取消退出")
            except Exception as e:
                self.logger.error(f"保存手势库时出现异常: {e}")
                save_success = False
                QMessageBox.critical(self, "错误", f"保存手势库时出错: {str(e)}，取消退出")

            if not save_success:
                self._closing = False
                self.logger.info("保存失败，取消退出")
                return

        if (button_text == "是" and save_success) or button_text == "否":
            self._force_exit()
        else:
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
        self.logger.info(f"创建全局对话框: 类型={message_type}, 标题={title_text}")

        try:
            dialog = show_dialog(
                parent=self,
                message_type=message_type,
                title_text=title_text,
                message=message,
                content_widget=content_widget,
                custom_icon=custom_icon,
                custom_buttons=custom_buttons,
                custom_button_colors=custom_button_colors,
                callback=callback,
            )

            self.logger.debug("全局对话框创建成功")

            self.activateWindow()
            self.raise_()

            self.current_dialog = dialog

            return dialog
        except Exception as e:
            self.logger.error(f"创建全局对话框时出错: {e}")
            return None

    def handle_dialog_close(self, dialog):
        self.logger.debug("处理对话框关闭")
        if hasattr(self, "current_dialog") and self.current_dialog == dialog:
            self.current_dialog = None
            self.logger.debug("已清除当前对话框引用")

    def on_drawing_state_changed(self, is_active):
        self.is_drawing_active = is_active
        if hasattr(self, "tray_icon") and self.tray_icon:
            self.tray_icon.update_drawing_state(is_active)
            self.logger.debug(f"托盘图标状态已更新: {'监听中' if is_active else '已停止'}")
        else:
            self.logger.debug(f"托盘图标未初始化，跳过状态更新: {'监听中' if is_active else '已停止'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GestroKey - 手势控制应用程序')
    parser.add_argument('--silent', '-s', action='store_true', 
                       help='静默启动：自动开始监听并最小化到托盘')
    args = parser.parse_args()

    app = QApplication(sys.argv)

    logger = get_logger("Main")
    if args.silent:
        logger.info("静默启动GestroKey应用程序")
    else:
        logger.info("启动GestroKey应用程序")

    window = GestroKeyApp(silent_start=args.silent)
    
    if not args.silent:
        window.show()

    sys.exit(app.exec())