import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QMovie

try:
    from app.log import log
except ImportError:
    # 如果直接运行此文件，可能需要调整导入路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.log import log

class SplashScreen(QWidget):
    """启动画面类"""
    
    def __init__(self):
        super().__init__()
        self.file_name = "splash_screen"
        log(self.file_name, "初始化启动画面")
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 窗口大小
        self.setFixedSize(400, 300)
        
        # 居中显示
        self.center()
        
        # 初始化UI
        self.init_ui()
        
        log(self.file_name, "启动画面初始化完成")
        
    def init_ui(self):
        """初始化UI元素"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 应用图标
        icon_label = QLabel(self)
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/logo.svg")
        if os.path.exists(icon_path):
            icon_pixmap = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        else:
            # 如果找不到图标，使用文本替代
            icon_label.setText("G")
            icon_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #4A90E2;")
            log.warning(f"找不到启动画面图标: {icon_path}")
        
        icon_label.setAlignment(Qt.AlignCenter)
        
        # 应用名称
        title_label = QLabel("GestroKey", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D3748; margin-top: 10px;")
        
        # 加载动画
        self.loading_label = QLabel(self)
        self.loading_label.setFixedSize(40, 40)
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        loading_gif_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets/icons/loading.gif")
        
        # 检查加载动画文件是否存在，不存在则使用文本替代
        if os.path.exists(loading_gif_path):
            self.loading_movie = QMovie(loading_gif_path)
            self.loading_movie.setScaledSize(QSize(40, 40))
            self.loading_label.setMovie(self.loading_movie)
            self.loading_movie.start()
        else:
            log(self.file_name, f"加载动画文件不存在，使用文本替代", level="warning")
            # 创建动态加载文本效果
            self.loading_text = "正在加载"
            self.dots = 0
            self.loading_timer = QTimer(self)
            self.loading_timer.timeout.connect(self.update_loading_text)
            self.loading_timer.start(500)
            self.loading_label.setText(self.loading_text)
            self.loading_label.setStyleSheet("font-size: 16px; color: #4A5568;")
        
        # 状态标签
        self.status_label = QLabel("正在启动系统...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: #4A5568; margin-top: 10px;")
        
        # 水平居中包装容器
        loading_container = QWidget()
        loading_layout = QHBoxLayout(loading_container)
        loading_layout.addStretch()
        loading_layout.addWidget(self.loading_label)
        loading_layout.addStretch()
        
        # 添加到布局
        layout.addStretch()
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addSpacing(15)  # 增加间距
        layout.addWidget(loading_container)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        # 设置背景样式
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #E2E8F0;
            }
        """)
        
    def update_loading_text(self):
        """更新加载文本动画"""
        self.dots = (self.dots + 1) % 4
        dots_text = "." * self.dots
        self.loading_label.setText(f"{self.loading_text}{dots_text}")
        
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.setText(message)
        log(self.file_name, f"更新启动状态: {message}")
        
    def center(self):
        """窗口居中显示"""
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
    def closeEvent(self, event):
        """关闭事件处理"""
        if hasattr(self, "loading_movie") and self.loading_movie:
            self.loading_movie.stop()
        if hasattr(self, "loading_timer") and self.loading_timer:
            self.loading_timer.stop()
        log(self.file_name, "启动画面关闭")
        super().closeEvent(event)

if __name__ == "__main__":
    # 测试启动画面
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    
    # 模拟加载过程
    def update():
        splash.update_status("测试状态更新...")
    
    QTimer.singleShot(2000, update)
    QTimer.singleShot(4000, app.quit)
    
    sys.exit(app.exec_()) 