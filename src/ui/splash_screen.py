import os
import sys
import math  # 添加math模块导入
from PyQt6.QtWidgets import (QSplashScreen, QProgressBar, QVBoxLayout, 
                             QLabel, QWidget, QApplication, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QTransform, QIcon

try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from version import get_version_string, APP_NAME
    from core.logger import get_logger
except ImportError:
    # 如果找不到模块，尝试调整导入路径
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(parent_dir)
    from version import get_version_string, APP_NAME
    from core.logger import get_logger

class LoadingIcon(QWidget):
    """自定义加载图标组件，显示旋转的图标"""
    
    def __init__(self, parent=None, size=80, color=None, icon_path=None):
        super().__init__(parent)
        self.logger = get_logger("LoadingIcon")
        
        # 设置默认主题颜色
        self.color = QColor(0, 120, 255) if color is None else QColor(color)
        
        # 设置固定大小
        self.setFixedSize(size, size)
        
        # 加载中心图标
        self.icon_pixmap = None
        if icon_path and os.path.exists(icon_path):
            self.icon_pixmap = QPixmap(icon_path)
        
        # 动画参数
        self._rotation_angle = 0
        self._dots_opacity = [1.0, 0.8, 0.6, 0.4, 0.2]
        
        # 设置旋转动画
        self.rotation_animation = QPropertyAnimation(self, b"rotationAngle")
        self.rotation_animation.setDuration(1500)  # 1.5秒旋转一周
        self.rotation_animation.setStartValue(0)
        self.rotation_animation.setEndValue(360)
        self.rotation_animation.setLoopCount(-1)  # 无限循环
        self.rotation_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.rotation_animation.start()
        
        # 设置不透明度动画
        self.dots_timer = QTimer(self)
        self.dots_timer.timeout.connect(self._update_dots_opacity)
        self.dots_timer.start(100)  # 每100毫秒更新一次
        
        self.logger.debug("加载图标初始化完成")
    
    def _update_dots_opacity(self):
        """更新点的不透明度，创建脉动效果"""
        # 循环移动不透明度值，创建旋转效果
        last = self._dots_opacity.pop()
        self._dots_opacity.insert(0, last)
        self.update()  # 重绘组件
    
    def paintEvent(self, event):
        """绘制加载图标"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 计算中心点和半径
        center_x = self.width() / 2
        center_y = self.height() / 2
        outer_radius = min(center_x, center_y) - 5
        inner_radius = outer_radius * 0.7
        
        # 应用旋转变换
        painter.translate(center_x, center_y)
        painter.rotate(self._rotation_angle)
        painter.translate(-center_x, -center_y)
        
        # 绘制外环
        pen = QPen(self.color)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawEllipse(int(center_x - outer_radius), int(center_y - outer_radius), 
                          int(outer_radius * 2), int(outer_radius * 2))
        
        # 绘制内环
        painter.drawEllipse(int(center_x - inner_radius), int(center_y - inner_radius), 
                          int(inner_radius * 2), int(inner_radius * 2))
        
        # 绘制五个点
        dot_radius = outer_radius * 0.12
        for i in range(5):
            angle = i * 72  # 均匀分布在360度上 (360/5 = 72)
            rad = angle * 3.14159 / 180.0
            
            # 设置不同的透明度
            color = QColor(self.color)
            color.setAlphaF(self._dots_opacity[i])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # 计算点的位置（在内外环之间）
            dot_pos_radius = (inner_radius + outer_radius) / 2
            x = center_x + dot_pos_radius * (1.0 if i % 2 == 0 else 0.85) * (1.0 if i % 3 == 0 else 0.9) * round(math.cos(rad), 5)
            y = center_y + dot_pos_radius * (1.0 if i % 2 == 0 else 0.85) * (1.0 if i % 3 == 0 else 0.9) * round(math.sin(rad), 5)
            
            # 绘制点
            painter.drawEllipse(int(x - dot_radius), int(y - dot_radius), 
                              int(dot_radius * 2), int(dot_radius * 2))
        
        # 重置旋转
        painter.resetTransform()
        
        # 绘制中心图标
        if self.icon_pixmap:
            # 计算图标大小（内环直径的60%）
            icon_size = int(inner_radius * 1.2)
            scaled_pixmap = self.icon_pixmap.scaled(
                icon_size, icon_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            # 在中心绘制图标
            icon_x = int(center_x - scaled_pixmap.width() / 2)
            icon_y = int(center_y - scaled_pixmap.height() / 2)
            painter.drawPixmap(icon_x, icon_y, scaled_pixmap)
    
    # 定义旋转角度属性，用于动画
    def _get_rotation_angle(self):
        return self._rotation_angle
        
    def _set_rotation_angle(self, angle):
        self._rotation_angle = angle
        self.update()
        
    rotationAngle = pyqtProperty(float, _get_rotation_angle, _set_rotation_angle)
    
    def set_color(self, color):
        """设置图标颜色"""
        self.color = QColor(color)
        self.update()
    
    def start_animation(self):
        """开始动画"""
        if not self.rotation_animation.state() == QPropertyAnimation.State.Running:
            self.rotation_animation.start()
        if not self.dots_timer.isActive():
            self.dots_timer.start()
            
    def stop_animation(self):
        """停止动画"""
        self.rotation_animation.stop()
        self.dots_timer.stop()


class SplashScreen(QSplashScreen):
    """加载动画页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("SplashScreen")
        
        # 创建加载画面的背景图像
        self._create_pixmap()
        
        # 创建加载页面的内容组件
        self._create_content()
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                          Qt.WindowType.WindowStaysOnTopHint)
        
        # 创建淡入动画
        self.fade_in_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(800)  # 800毫秒淡入
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 淡出动画
        self.fade_out_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(600)  # 600毫秒淡出
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # 创建独立定时器以保持UI响应
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._process_events)
        self.animation_timer.start(50)
        
        self.logger.debug("加载画面初始化完成")
    
    def _process_events(self):
        """处理事件队列，保持UI响应"""
        QApplication.processEvents()
    
    def _create_pixmap(self):
        """创建背景图像"""
        # 创建一个400x400的背景图像
        pixmap = QPixmap(400, 400)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # 创建画家
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆角矩形背景
        painter.setBrush(QColor(30, 30, 30, 230))  # 半透明深色背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 400, 400, 20, 20)
        
        painter.end()
        
        # 设置图像作为背景
        self.setPixmap(pixmap)
    
    def _create_content(self):
        """创建内容组件"""
        # 创建容器组件
        self.content_widget = QWidget(self)
        self.content_widget.setGeometry(self.pixmap().rect())
        
        # 创建不透明度效果 - 初始不透明度为0.0（完全透明）
        self._opacity_effect = QGraphicsOpacityEffect(self.content_widget)
        self._opacity_effect.setOpacity(0.0)  # 初始不透明度为0.0（完全透明）
        self.content_widget.setGraphicsEffect(self._opacity_effect)
        
        # 创建布局
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(20)
        
        # 获取应用图标路径
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'images', 'icon.svg')
        
        # 添加标题标签
        title_label = QLabel(APP_NAME)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title_label)
        
        # 添加版本标签
        version_label = QLabel(f"v{get_version_string().split('v')[1]}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 180);")
        layout.addWidget(version_label)
        
        # 添加间隔
        layout.addSpacing(20)
        
        # 添加带图标的加载动画
        self.loading_icon = LoadingIcon(color=QColor(0, 120, 255), size=120, icon_path=icon_path)
        layout.addWidget(self.loading_icon, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 添加加载状态标签
        self.status_label = QLabel("正在启动...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; color: white;")
        layout.addWidget(self.status_label)
        
        # 添加底部提示
        hint_label = QLabel("请稍后")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 130);")
        layout.addWidget(hint_label)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 创建状态更新定时器
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status_text)
        self.status_timer.start(800)  # 每800毫秒更新一次状态文本
        self.status_index = 0
        self.status_texts = [
            "正在初始化资源...",
            "正在加载组件...",
            "正在准备主界面...",
            "即将完成..."
        ]
    
    def _update_status_text(self):
        """更新状态文本，创建动画效果"""
        self.status_index = (self.status_index + 1) % len(self.status_texts)
        self.status_label.setText(self.status_texts[self.status_index])
    
    def showEvent(self, event):
        """显示事件处理"""
        super().showEvent(event)
        # 确保动画和状态更新定时器正在运行
        if not self.status_timer.isActive():
            self.status_timer.start()
        
        # 启动淡入动画
        self.fade_in_animation.start()
    
    def fade_out_and_close(self):
        """淡出并关闭加载画面"""
        # 停止状态更新和事件处理定时器
        self.status_timer.stop()
        self.animation_timer.stop()
        
        # 开始淡出动画
        self.fade_out_animation.finished.connect(self.close)
        self.fade_out_animation.start()
    
    def drawContents(self, painter):
        """绘制内容，覆盖基类方法"""
        # 不调用基类方法，直接返回
        pass
    
    def mousePressEvent(self, event):
        """鼠标按下事件处理"""
        # 忽略鼠标事件，防止用户点击关闭
        event.ignore()


if __name__ == "__main__":
    """测试代码"""
    app = QApplication(sys.argv)
    
    splash = SplashScreen()
    splash.show()
    
    # 模拟主窗口加载延迟
    def finish_loading():
        splash.fade_out_and_close()
    
    QTimer.singleShot(3000, finish_loading)
    
    sys.exit(app.exec())