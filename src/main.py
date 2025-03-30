import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMainWindow
from PyQt5.QtCore import Qt

from core.drawer import DrawingManager
from core.logger import get_logger

class GestroKeyApp(QMainWindow):
    """GestroKey应用程序主窗口"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("MainApp")
        self.drawing_manager = None
        self.initUI()
        self.logger.info("GestroKey应用程序已启动")
        
    def initUI(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle('GestroKey')
        self.setGeometry(300, 300, 300, 200)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # 标题标签
        title_label = QLabel("GestroKey")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("font-size: 10pt; margin-bottom: 20px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 开始按钮
        self.start_button = QPushButton("开始监听")
        self.start_button.setFixedSize(150, 40)
        self.start_button.clicked.connect(self.start_drawing)
        layout.addWidget(self.start_button)
        
        # 停止按钮（初始禁用）
        self.stop_button = QPushButton("停止监听")
        self.stop_button.setFixedSize(150, 40)
        self.stop_button.clicked.connect(self.stop_drawing)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        # 退出按钮
        self.exit_button = QPushButton("退出程序")
        self.exit_button.setFixedSize(150, 40)
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)
        
        # 显示窗口
        self.show()
        
    def start_drawing(self):
        """开始绘制功能"""
        self.logger.info("启动绘制管理器")
        self.status_label.setText("监听中 - 使用鼠标右键进行绘制")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # 启动绘制管理器（在新线程中运行）
        if not self.drawing_manager:
            self.drawing_manager = DrawingManager()
            
        self.logger.debug("绘制管理器已启动")
    
    def stop_drawing(self):
        """停止绘制功能"""
        if self.drawing_manager:
            self.logger.info("停止绘制管理器")
            self.drawing_manager.quit()
            self.drawing_manager = None
            
        self.status_label.setText("准备就绪")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    def closeEvent(self, event):
        """关闭窗口事件处理"""
        self.logger.info("程序关闭")
        self.stop_drawing()
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