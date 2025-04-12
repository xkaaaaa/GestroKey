import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                            QLabel, QMainWindow, QHBoxLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from core.drawer import DrawingManager
from core.logger import get_logger
from version import get_version_string, APP_NAME  # 导入版本信息

# 导入页面模块
try:
    from ui.console import ConsolePage
    from ui.settings.settings import get_settings
    from ui.settings.settings_tab import SettingsPage
    from ui.gestures.gestures import get_gesture_library  # 导入手势库
    from ui.gestures.gestures_tab import GesturesPage  # 导入手势管理页面
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.side_tab import SideNavigationMenu  # 导入侧边栏导航菜单组件
    from ui.components.toast_notification import show_info, show_warning, show_error, get_toast_manager  # 导入Toast通知组件
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ui.console import ConsolePage
    from ui.settings.settings import get_settings
    from ui.settings.settings_tab import SettingsPage
    from ui.gestures.gestures import get_gesture_library  # 导入手势库
    from ui.gestures.gestures_tab import GesturesPage  # 导入手势管理页面
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.side_tab import SideNavigationMenu  # 导入侧边栏导航菜单组件
    from ui.components.toast_notification import show_info, show_warning, show_error, get_toast_manager  # 导入Toast通知组件

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
        
    def initUI(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle(APP_NAME)
        self.setGeometry(300, 300, 1000, 680)  # 增大默认窗口大小，宽度从850增加到1000，高度从650增加到680
        self.setMinimumSize(800, 500)  # 增加最小窗口大小，宽度从640增加到800，高度从480增加到500
        
        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'images', 'icon.svg')
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
        
        self.logger.debug("创建设置页面")
        self.settings_page = SettingsPage()
        
        self.logger.debug("创建手势管理页面")
        self.gestures_page = GesturesPage()
        
        # 创建侧边栏导航菜单
        self.logger.debug("创建侧边栏导航菜单")
        self.navigation_menu = SideNavigationMenu()
        self.navigation_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 创建页面图标
        # 尝试使用存在的图标文件，而不是依赖系统主题
        icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'images')
        console_icon_path = os.path.join(icons_dir, 'console.svg')
        settings_icon_path = os.path.join(icons_dir, 'settings.svg')
        gestures_icon_path = os.path.join(icons_dir, 'gestures.svg')

        # 如果图标文件存在则使用，否则使用空图标
        console_icon = QIcon(console_icon_path) if os.path.exists(console_icon_path) else QIcon()
        settings_icon = QIcon(settings_icon_path) if os.path.exists(settings_icon_path) else QIcon()
        gestures_icon = QIcon(gestures_icon_path) if os.path.exists(gestures_icon_path) else QIcon()
        
        # 添加页面到侧边栏导航菜单
        self.logger.debug("添加页面到侧边栏导航菜单")
        # 控制台页面放在顶部
        console_index = self.navigation_menu.addPage(self.console_page, "控制台", console_icon, 
                                             self.navigation_menu.POSITION_TOP)
        # 手势管理页面也放在顶部
        gestures_index = self.navigation_menu.addPage(self.gestures_page, "手势管理", gestures_icon, 
                                              self.navigation_menu.POSITION_TOP)
        # 设置页面放在底部
        settings_index = self.navigation_menu.addPage(self.settings_page, "设置", settings_icon, 
                                              self.navigation_menu.POSITION_BOTTOM)

        # 记录初始添加的页面索引
        self.logger.debug(f"控制台索引: {console_index}, 设置索引: {settings_index}, 手势索引: {gestures_index}")
        
        # 页面切换事件连接
        self.navigation_menu.currentChanged.connect(self.onPageChanged)
        
        # 将导航菜单添加到主布局
        self.logger.debug("将导航菜单添加到主布局")
        main_layout.addWidget(self.navigation_menu, 1)  # 设置1的拉伸系数，让导航菜单占据大部分空间
        
        # 添加底部状态栏
        status_widget = QWidget()
        status_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)  # 设置适当的边距
        
        # 使用自定义动画按钮替换标准按钮
        self.exit_button = AnimatedButton("退出程序", primary_color=[220, 53, 69])  # 红色按钮
        self.exit_button.setMinimumSize(120, 36)  # 设置最小尺寸，而不是固定尺寸
        self.exit_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.exit_button.clicked.connect(self.close)
        
        self.version_label = QLabel(get_version_string())
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.version_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
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
            if hasattr(self, 'navigation_menu') and self.navigation_menu:
                self.logger.debug("设置初始页面索引为0（控制台）")
                self.navigation_menu.setCurrentPage(0)  # 确保控制台页面被选中
                QApplication.processEvents()  # 再次处理事件，确保UI更新
        except Exception as e:
            self.logger.error(f"设置初始页面时出错: {e}")
    
    def onPageChanged(self, index):
        """页面切换事件处理"""
        page_name = "控制台" if index == 0 else "设置" if index == 1 else "手势管理" if index == 2 else f"未知({index})"
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
        
        # 如果控制台页面存在，停止绘制
        if hasattr(self, 'console_page'):
            self.console_page.stop_drawing()
            
        # 检查是否有未保存的更改
        unsaved_settings = False
        unsaved_gestures = False
        
        # 检查设置是否有未保存的更改
        if hasattr(self, 'settings_page') and self.settings_page.has_unsaved_changes():
            unsaved_settings = True
        
        # 检查手势库是否有未保存的更改
        if hasattr(self, 'gestures_page') and self.gestures_page.has_unsaved_changes():
            unsaved_gestures = True
        
        # 如果存在未保存的更改，询问用户
        if unsaved_settings or unsaved_gestures:
            self.logger.info("检测到未保存的更改")
            # 使用自定义对话框而不是QMessageBox
            is_saved = False
            
            # 这里我们还是需要使用确认对话框，因为需要用户做选择
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, '保存更改',
                                         '检测到未保存的更改，是否保存后退出？',
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                                         QMessageBox.StandardButton.Save)
            
            if reply == QMessageBox.StandardButton.Save:
                try:
                    # 保存设置
                    if unsaved_settings:
                        self.logger.info("正在保存设置...")
                        if self.settings_page.save_settings():
                            self.logger.info("设置已保存")
                            is_saved = True
                        else:
                            self.logger.error("保存设置失败")
                            show_warning(self, "错误", "保存设置失败")
                            event.ignore()
                            return
                except Exception as e:
                    self.logger.error(f"保存设置时出现异常: {e}")
                    show_warning(self, f"保存设置失败: {str(e)}")
                    event.ignore()
                    return
                
                try:
                    # 保存手势库
                    if unsaved_gestures:
                        self.logger.info("正在保存手势库...")
                        if self.gestures_page.save_gestures():
                            self.logger.info("手势库已保存")
                            is_saved = True
                        else:
                            self.logger.error("保存手势库失败")
                            show_warning(self, f"保存手势库失败: {str(e)}")
                            event.ignore()
                            return
                except Exception as e:
                    self.logger.error(f"保存手势库时出现异常: {e}")
                    show_warning(self, f"保存手势库失败: {str(e)}")
                    event.ignore()
                    return
                
            elif reply == QMessageBox.StandardButton.Discard:
                self.logger.info("放弃未保存的更改")
                # 用户选择放弃更改，不需要做任何事情
            else:
                # 用户选择取消关闭，取消事件
                self.logger.info("取消关闭窗口")
                event.ignore()
                return
        
        # 记录日志
        self.logger.info("程序正常关闭")
        # 接受事件，关闭窗口
        event.accept()


if __name__ == "__main__":
    # 设置高DPI缩放 - PyQt6中处理方式不同
    app = QApplication(sys.argv)
    # 在PyQt6中，高DPI缩放是自动处理的，不再需要显式设置这些属性
    
    window = GestroKeyApp()
    sys.exit(app.exec()) 