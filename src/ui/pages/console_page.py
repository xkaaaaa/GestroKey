from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QGroupBox, QFrame, QSpacerItem, QSizePolicy, QGridLayout, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

import os
import sys
import time
import psutil
from datetime import datetime

try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

class StatusCard(QFrame):
    """状态卡片组件"""
    
    def __init__(self, title, value="", icon_path=None, parent=None):
        """初始化状态卡片
        
        Args:
            title: 标题
            value: 值
            icon_path: 图标路径
            parent: 父部件
        """
        super().__init__(parent)
        
        # 设置样式
        self.setStyleSheet("""
            StatusCard {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
        """)
        
        # 设置阴影效果
        self.setGraphicsEffect(None)  # 使用CSS实现更好的阴影效果
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # 创建标题布局
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        # 添加图标（如果提供）
        if icon_path and os.path.exists(icon_path):
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(16, 16))
            title_layout.addWidget(icon_label)
        
        # 添加标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #4A5568; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        # 添加弹性空间
        title_layout.addStretch()
        
        # 添加标题布局到主布局
        layout.addLayout(title_layout)
        
        # 添加值
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("font-size: 24px; color: #2D3748; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # 添加弹性空间
        layout.addStretch()
        
    def update_value(self, value):
        """更新值
        
        Args:
            value: 新值
        """
        self.value_label.setText(str(value))

class ConsolePageHeader(QWidget):
    """控制台页面头部组件"""
    
    def __init__(self, parent=None):
        """初始化控制台页面头部
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 10)
        
        # 标题
        title = QLabel("控制台")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D3748;")
        layout.addWidget(title)
        
        # 描述
        description = QLabel("查看系统状态和控制手势识别")
        description.setStyleSheet("font-size: 14px; color: #4A5568; margin-top: 5px;")
        layout.addWidget(description)
        
        # 分割线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #E2E8F0;")
        layout.addWidget(divider)

class SystemInfoPanel(QGroupBox):
    """系统信息面板"""
    
    def __init__(self, parent=None):
        super().__init__("系统信息", parent)
        
        # 设置样式
        self.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QLabel {
                font-size: 14px;
                color: #4A5568;
            }
            
            QLabel.value {
                font-weight: bold;
                color: #2D3748;
            }
        """)
        
        # 创建布局
        layout = QGridLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(10)
        
        # 运行时间
        layout.addWidget(QLabel("运行时间:"), 0, 0)
        self.runtime_label = QLabel("0时0分0秒")
        self.runtime_label.setStyleSheet("font-weight: bold; color: #2D3748;")
        layout.addWidget(self.runtime_label, 0, 1)
        
        # 内存使用量
        layout.addWidget(QLabel("内存使用:"), 1, 0)
        self.memory_label = QLabel("0 MB")
        self.memory_label.setStyleSheet("font-weight: bold; color: #2D3748;")
        layout.addWidget(self.memory_label, 1, 1)
        
        # CPU使用率
        layout.addWidget(QLabel("CPU使用:"), 2, 0)
        self.cpu_label = QLabel("0%")
        self.cpu_label.setStyleSheet("font-weight: bold; color: #2D3748;")
        layout.addWidget(self.cpu_label, 2, 1)
        
        # 操作系统
        layout.addWidget(QLabel("操作系统:"), 3, 0)
        import platform
        os_info = f"{platform.system()} {platform.version()}"
        os_label = QLabel(os_info)
        os_label.setStyleSheet("font-weight: bold; color: #2D3748;")
        layout.addWidget(os_label, 3, 1)
        
        # 启动更新定时器
        self.start_time = datetime.now()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(1000)  # 每秒更新一次
        
        # 初始更新
        self.update_info()
        
    def update_info(self):
        """更新系统信息"""
        # 更新运行时间
        runtime = datetime.now() - self.start_time
        hours, remainder = divmod(runtime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        days = runtime.days
        
        if days > 0:
            runtime_text = f"{days}天{hours}时{minutes}分"
        else:
            runtime_text = f"{hours}时{minutes}分{seconds}秒"
            
        self.runtime_label.setText(runtime_text)
        
        # 更新内存使用
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        self.memory_label.setText(f"{memory_mb:.1f} MB")
        
        # 更新CPU使用
        try:
            cpu_percent = process.cpu_percent(interval=None)
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
        except Exception as e:
            log.warning(f"获取CPU使用率失败: {str(e)}")
        
    def closeEvent(self, event):
        """关闭事件处理"""
        self.update_timer.stop()
        super().closeEvent(event)

class ControlPanel(QGroupBox):
    """控制面板"""
    
    # 定义信号
    togglePaintingSignal = pyqtSignal()  # 切换绘画状态信号
    minimizeSignal = pyqtSignal()  # 最小化信号
    exitSignal = pyqtSignal()  # 退出信号
    
    def __init__(self, parent=None):
        super().__init__("控制面板", parent)
        
        # 设置样式
        self.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QPushButton {
                background-color: #EDF2F7;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                color: #2D3748;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #E2E8F0;
            }
            
            QPushButton:pressed {
                background-color: #CBD5E0;
            }
            
            QPushButton.primary {
                background-color: #4299E1;
                color: white;
            }
            
            QPushButton.primary:hover {
                background-color: #3182CE;
            }
            
            QPushButton.primary:pressed {
                background-color: #2B6CB0;
            }
            
            QPushButton.danger {
                background-color: #F56565;
                color: white;
            }
            
            QPushButton.danger:hover {
                background-color: #E53E3E;
            }
            
            QPushButton.danger:pressed {
                background-color: #C53030;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(15)
        
        # 状态容器
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        # 状态指示器 - 使用标签替代进度条
        self.status_indicator = QLabel("就绪")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setFixedHeight(30)
        self.status_indicator.setStyleSheet("""
            QLabel {
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                background-color: #EDF2F7;
                padding: 5px 15px;
                font-size: 14px;
                font-weight: bold;
                color: #4A5568;
            }
        """)
        status_layout.addWidget(self.status_indicator)
        
        # 状态标签
        self.status_label = QLabel("已停止")
        self.status_label.setStyleSheet("font-size: 14px; color: #4A5568; margin-left: 5px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # 添加状态容器到主布局
        layout.addWidget(status_container)
        
        # 绘画按钮
        self.toggle_btn = QPushButton("开始")
        self.toggle_btn.setObjectName("toggle_btn")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setProperty("class", "primary")  # 使用属性设置样式类
        self.toggle_btn.setStyleSheet("background-color: #4299E1; color: white;")
        self.toggle_btn.clicked.connect(self.toggle_painting)
        layout.addWidget(self.toggle_btn)
        
    def toggle_painting(self):
        """切换绘画状态"""
        self.togglePaintingSignal.emit()
        
    def minimize(self):
        """最小化到托盘"""
        self.minimizeSignal.emit()
        
    def exit_app(self):
        """退出应用"""
        self.exitSignal.emit()
        
    def update_painting_status(self, is_running):
        """更新绘画状态
        
        Args:
            is_running: 是否正在运行
        """
        self.status_indicator.setText("运行中" if is_running else "已停止")
        
        # 更新按钮文本
        if is_running:
            self.toggle_btn.setText("关闭")
            self.toggle_btn.setStyleSheet("background-color: #F56565; color: white;")
        else:
            self.toggle_btn.setText("开始")
            self.toggle_btn.setStyleSheet("background-color: #4299E1; color: white;")

class ConsolePage(QWidget):
    """控制台页面"""
    
    # 定义信号
    togglePaintingSignal = pyqtSignal()  # 切换绘画状态信号
    minimizeSignal = pyqtSignal()  # 最小化信号
    exitSignal = pyqtSignal()  # 退出信号
    
    def __init__(self, parent=None):
        """初始化控制台页面
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # 状态变量
        self.drawing_active = False
        self.start_time = time.time()
        
        # 初始化UI
        self.init_ui()
        
        # 启动定时器更新状态
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status_display)
        self.timer.start(1000)  # 每秒更新一次
        
    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 页头
        self.header = ConsolePageHeader()
        main_layout.addWidget(self.header)
        
        # 内容容器
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # 状态卡片组
        status_group = QGroupBox("系统状态")
        status_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
                border: none;
            }
        """)
        
        status_layout = QGridLayout(status_group)
        status_layout.setContentsMargins(0, 20, 0, 0)
        status_layout.setSpacing(15)
        
        # 创建状态卡片
        self.cpu_card = StatusCard("CPU使用率", "0%")
        self.memory_card = StatusCard("内存使用率", "0%")
        self.runtime_card = StatusCard("运行时间", "0:00:00")
        self.os_card = StatusCard("操作系统", sys.platform)
        
        # 添加状态卡片到网格布局
        status_layout.addWidget(self.cpu_card, 0, 0)
        status_layout.addWidget(self.memory_card, 0, 1)
        status_layout.addWidget(self.runtime_card, 1, 0)
        status_layout.addWidget(self.os_card, 1, 1)
        
        # 添加状态组到内容布局
        content_layout.addWidget(status_group)
        
        # 操作按钮组
        actions_group = QGroupBox("手势控制")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
                border: none;
            }
        """)
        
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setContentsMargins(0, 20, 0, 0)
        actions_layout.setSpacing(15)
        
        # 状态指示器 - 使用标签替代进度条
        self.status_indicator = QLabel("就绪")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setFixedHeight(30)
        self.status_indicator.setStyleSheet("""
            QLabel {
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                background-color: #EDF2F7;
                padding: 5px 15px;
                font-size: 14px;
                font-weight: bold;
                color: #4A5568;
            }
        """)
        actions_layout.addWidget(self.status_indicator)
        
        # 按钮布局
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # 切换按钮（开始/关闭）
        self.toggle_button = QPushButton("开始")
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #4299E1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #3182CE;
            }
            
            QPushButton:pressed {
                background-color: #2B6CB0;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_drawing)
        buttons_layout.addWidget(self.toggle_button)
        
        # 添加按钮布局到操作布局
        actions_layout.addLayout(buttons_layout)
        
        # 添加操作组到内容布局
        content_layout.addWidget(actions_group)
        
        # 添加内容容器到主布局
        main_layout.addWidget(content_container)
        
        # 更新初始状态
        self.update_status_display()
        
    def toggle_drawing(self):
        """切换绘图状态"""
        # 发出信号，通知应用切换绘图状态
        self.togglePaintingSignal.emit()
        
    def update_drawing_state(self, active):
        """更新绘制状态
        
        Args:
            active: 是否激活
        """
        self.drawing_active = active
        
        # 更新按钮文本和样式
        if active:
            self.toggle_button.setText("关闭")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #F56565;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #E53E3E;
                }
                
                QPushButton:pressed {
                    background-color: #C53030;
                }
            """)
        else:
            self.toggle_button.setText("开始")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #4299E1;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #3182CE;
                }
                
                QPushButton:pressed {
                    background-color: #2B6CB0;
                }
            """)
        
        # 更新状态指示器
        if active:
            self.status_indicator.setText("正在运行")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    border: 1px solid #E2E8F0;
                    border-radius: 5px;
                    background-color: #EDF2F7;
                    padding: 5px 15px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #48BB78;
                }
            """)
        else:
            self.status_indicator.setText("已停止")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    border: 1px solid #E2E8F0;
                    border-radius: 5px;
                    background-color: #EDF2F7;
                    padding: 5px 15px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #F56565;
                }
            """)
    
    def update_status(self, status_type, status_value):
        """更新状态
        
        Args:
            status_type: 状态类型
            status_value: 状态值
        """
        if status_type == "cpu_usage":
            self.cpu_card.update_value(f"{status_value}%")
        elif status_type == "memory_usage":
            self.memory_card.update_value(f"{status_value}%")
        elif status_type == "runtime":
            # 格式化为 小时:分钟:秒
            hours, remainder = divmod(int(float(status_value)), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.runtime_card.update_value(f"{hours}:{minutes:02d}:{seconds:02d}")
        elif status_type == "os_name":
            self.os_card.update_value(status_value)
        elif status_type == "status":
            if status_value == "running":
                self.update_drawing_state(True)
            elif status_value == "stopped":
                self.update_drawing_state(False)
            elif status_value == "ready":
                self.status_indicator.setText("就绪")
                self.status_indicator.setStyleSheet("""
                    QLabel {
                        border: 1px solid #E2E8F0;
                        border-radius: 5px;
                        background-color: #EDF2F7;
                        padding: 5px 15px;
                        font-size: 14px;
                        font-weight: bold;
                        color: #4299E1;
                    }
                """)
    
    def update_status_display(self):
        """更新状态显示"""
        # 更新CPU使用率
        cpu_percent = psutil.cpu_percent()
        self.cpu_card.update_value(f"{cpu_percent}%")
        
        # 更新内存使用率
        memory_percent = psutil.virtual_memory().percent
        self.memory_card.update_value(f"{memory_percent}%")
        
        # 更新运行时间
        runtime = time.time() - self.start_time
        hours, remainder = divmod(int(runtime), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.runtime_card.update_value(f"{hours}:{minutes:02d}:{seconds:02d}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    console_page = ConsolePage()
    console_page.show()
    
    # 测试状态更新
    QTimer.singleShot(2000, lambda: console_page.update_status("status", "running"))
    QTimer.singleShot(4000, lambda: console_page.update_status("status", "stopped"))
    
    sys.exit(app.exec_()) 