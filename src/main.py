import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                            QLabel, QMainWindow, QTabWidget, QHBoxLayout)
from PyQt5.QtCore import Qt

from core.drawer import DrawingManager
from core.logger import get_logger

# 导入选项卡模块
try:
    from ui.console import ConsoleTab
    from ui.settings.settings_tab import SettingsTab
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ui.console import ConsoleTab
    from ui.settings.settings_tab import SettingsTab
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮

class GestroKeyApp(QMainWindow):
    """GestroKey应用程序主窗口"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("MainApp")
        self.drawing_manager = None
        self.is_drawing_active = False
        self.initUI()
        self.logger.info("GestroKey应用程序已启动")
        
    def initUI(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle('GestroKey')
        self.setGeometry(300, 300, 400, 400)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建选项卡小部件
        self.tab_widget = QTabWidget()
        
        # 创建控制台选项卡
        self.console_tab = ConsoleTab()
        self.tab_widget.addTab(self.console_tab, "控制台")
        
        # 创建设置选项卡
        self.settings_tab = SettingsTab()
        self.tab_widget.addTab(self.settings_tab, "设置")
        
        # 将选项卡添加到主布局
        main_layout.addWidget(self.tab_widget)
        
        # 添加底部状态栏
        status_layout = QHBoxLayout()
        
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