import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                            QLabel, QMainWindow, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from core.drawer import DrawingManager
from core.logger import get_logger

# 导入选项卡模块
try:
    from ui.console import ConsoleTab
    from ui.settings.settings import get_settings
    from ui.settings.settings_tab import SettingsTab
    from ui.gestures.gestures import get_gesture_library  # 导入手势库
    from ui.gestures.gestures_tab import GesturesTab  # 导入手势管理选项卡
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.side_tab import SideTabWidget  # 导入左侧选项卡组件
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ui.console import ConsoleTab
    from ui.settings.settings import get_settings
    from ui.settings.settings_tab import SettingsTab
    from ui.gestures.gestures import get_gesture_library  # 导入手势库
    from ui.gestures.gestures_tab import GesturesTab  # 导入手势管理选项卡
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.side_tab import SideTabWidget  # 导入左侧选项卡组件

class GestroKeyApp(QMainWindow):
    """GestroKey应用程序主窗口"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("MainApp")
        self.drawing_manager = None
        self.is_drawing_active = False
        
        # 在程序启动时初始化设置和手势库
        self.init_global_resources()
        
        self.initUI()
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
        self.setWindowTitle('GestroKey')
        self.setGeometry(300, 300, 750, 550)  # 调整窗口大小以适应左侧选项卡
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 去除边距以获得更好的视觉效果
        
        # 创建选项卡内容
        self.logger.debug("创建控制台选项卡")
        self.console_tab = ConsoleTab()
        
        self.logger.debug("创建设置选项卡")
        self.settings_tab = SettingsTab()
        
        self.logger.debug("创建手势管理选项卡")
        self.gestures_tab = GesturesTab()
        
        # 创建左侧选项卡小部件
        self.logger.debug("创建左侧选项卡组件")
        self.tab_widget = SideTabWidget()
        
        # 创建选项卡图标
        console_icon = QIcon.fromTheme("utilities-terminal", QIcon())  # 使用系统图标或默认的空图标
        settings_icon = QIcon.fromTheme("preferences-system", QIcon())
        gestures_icon = QIcon.fromTheme("input-mouse", QIcon())
        
        # 添加选项卡到左侧选项卡组件
        self.logger.debug("添加选项卡到左侧选项卡组件")
        console_index = self.tab_widget.addTab(self.console_tab, "控制台", console_icon)
        settings_index = self.tab_widget.addTab(self.settings_tab, "设置", settings_icon)
        gestures_index = self.tab_widget.addTab(self.gestures_tab, "手势管理", gestures_icon)
        
        # 记录初始添加的选项卡索引
        self.logger.debug(f"控制台索引: {console_index}, 设置索引: {settings_index}, 手势索引: {gestures_index}")
        
        # 选项卡切换事件连接
        self.tab_widget.currentChanged.connect(self.onTabChanged)
        
        # 将选项卡添加到主布局
        self.logger.debug("将选项卡添加到主布局")
        main_layout.addWidget(self.tab_widget)
        
        # 添加底部状态栏
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(10, 5, 10, 5)  # 设置适当的边距
        
        # 使用自定义动画按钮替换标准按钮
        self.exit_button = AnimatedButton("退出程序", primary_color=[220, 53, 69])  # 红色按钮
        self.exit_button.setFixedSize(120, 36)
        self.exit_button.clicked.connect(self.close)
        
        self.version_label = QLabel("v1.0.0")
        self.version_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        status_layout.addWidget(self.exit_button)
        status_layout.addStretch(1)
        status_layout.addWidget(self.version_label)
        
        main_layout.addLayout(status_layout)
        
        # 显示窗口
        self.show()
        
        # 初始化后确保选择控制台选项卡
        self.logger.debug("设置初始选项卡为控制台")
        QApplication.processEvents()  # 处理待处理的事件
        
        # 使用单次计时器延迟设置初始选项卡，确保UI完全准备好
        QTimer.singleShot(100, lambda: self._select_initial_tab())
    
    def _select_initial_tab(self):
        """选择初始选项卡（延迟执行）"""
        try:
            if hasattr(self, 'tab_widget') and self.tab_widget:
                self.logger.debug("设置初始选项卡索引为0（控制台）")
                self.tab_widget.setCurrentIndex(0)  # 确保控制台选项卡被选中
                QApplication.processEvents()  # 再次处理事件，确保UI更新
        except Exception as e:
            self.logger.error(f"设置初始选项卡时出错: {e}")
    
    def onTabChanged(self, index):
        """选项卡切换事件处理"""
        tab_name = "控制台" if index == 0 else "设置" if index == 1 else "手势管理" if index == 2 else f"未知({index})"
        self.logger.debug(f"切换到选项卡: {index} ({tab_name})")
    
    def closeEvent(self, event):
        """关闭窗口事件处理"""
        self.logger.info("程序关闭")
        # 如果控制台标签页存在，停止绘制
        if hasattr(self, 'console_tab'):
            self.console_tab.stop_drawing()
        # 如果设置标签页存在，保存设置
        if hasattr(self, 'settings_tab'):
            try:
                self.settings_tab.save_settings()
            except Exception as e:
                self.logger.warning(f"关闭时保存设置失败: {e}")
        # 如果手势管理标签页存在，保存手势库
        if hasattr(self, 'gestures_tab'):
            try:
                self.gestures_tab.saveGestureLibrary()
            except Exception as e:
                self.logger.warning(f"关闭时保存手势库失败: {e}")
        event.accept()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # 使用Fusion样式，在所有平台上看起来一致
        main_window = GestroKeyApp()
        sys.exit(app.exec_())
    except Exception as e:
        error_logger = get_logger("MainError")
        error_logger.exception(f"主程序发生未捕获的异常: {e}")
        # 显示错误消息框
        from PyQt5.QtWidgets import QMessageBox
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("错误")
        error_box.setText("程序启动失败")
        error_box.setDetailedText(f"错误详情: {str(e)}")
        error_box.exec_() 