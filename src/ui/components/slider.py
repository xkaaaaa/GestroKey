import sys
import math
import os
from PyQt6.QtWidgets import (QWidget, QSlider, QHBoxLayout, QVBoxLayout, 
                             QLabel, QApplication, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QLinearGradient, QPen, QBrush, QFont, QFontMetrics, QRadialGradient

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

class GesturePattern(QWidget):
    """自定义SVG样式手势图案，用于滑块的滑块部分"""
    
    def __init__(self, parent=None, size=24, primary_color=None):
        super().__init__(parent)
        self.logger = get_logger("GesturePattern")
        
        # 默认颜色 - 蓝色系
        self.primary_color = primary_color or [52, 152, 219]
        self.secondary_color = [41, 128, 185]
        self.highlight_color = [79, 195, 247]
        
        # 设置固定大小
        self.setFixedSize(size, size)
        
        # 圆形图案参数
        self.dot_radius = size * 0.08
        self.orbit_radius = size * 0.35
        self.animation_offset = 0
        
        # 设置动画
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20fps
        
        # 透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 值显示
        self.show_value = False
        self.value = 0
        
    def set_value(self, value):
        """设置要显示的值"""
        self.value = value
        self.update()
        
    def set_show_value(self, show):
        """设置是否显示值"""
        self.show_value = show
        self.update()
        
    def update_animation(self):
        """更新动画参数"""
        self.animation_offset = (self.animation_offset + 0.1) % (2 * math.pi)
        self.update()  # 触发重绘
        
    def set_primary_color(self, color):
        """设置主要颜色"""
        if isinstance(color, list) and len(color) >= 3:
            self.primary_color = color
            # 自动计算次要颜色和高亮颜色
            self.secondary_color = [max(0, int(c * 0.8)) for c in color]
            self.highlight_color = [min(255, int(c * 1.2)) for c in color]
            self.update()
        
    def paintEvent(self, event):
        """绘制自定义SVG样式手势图案"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # 获取组件尺寸
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # 绘制内部填充
        gradient = QRadialGradient(center_x, center_y, width/2)
        gradient.setColorAt(0, QColor(int(self.highlight_color[0]), int(self.highlight_color[1]), int(self.highlight_color[2]), 150))
        gradient.setColorAt(0.7, QColor(int(self.primary_color[0]), int(self.primary_color[1]), int(self.primary_color[2]), 100))
        gradient.setColorAt(1, QColor(int(self.secondary_color[0]), int(self.secondary_color[1]), int(self.secondary_color[2]), 50))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(2, 2, width-4, height-4))
        
        # 如果显示值，绘制带值的视图
        if self.show_value:
            # 绘制半透明背景
            background_brush = QBrush(QColor(0, 0, 0, 180))
            painter.setBrush(background_brush)
            painter.drawEllipse(QRectF(2, 2, width-4, height-4))
            
            # 绘制值文本
            painter.setPen(QColor(255, 255, 255))
            font = QFont()
            font.setBold(True)
            painter.setFont(font)
            value_text = str(self.value)
            painter.drawText(QRectF(0, 0, width, height), Qt.AlignmentFlag.AlignCenter, value_text)
            
            return  # 显示值时不显示图案
            
        # 绘制轨迹线
        pen = QPen(QColor(int(self.primary_color[0]), int(self.primary_color[1]), int(self.primary_color[2]), 180))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawEllipse(QRectF(center_x - self.orbit_radius, center_y - self.orbit_radius,
                                  self.orbit_radius*2, self.orbit_radius*2))
        
        # 绘制运动点
        for i in range(3):
            # 计算点位置，每个点间隔120度，并且随时间动态旋转
            angle = self.animation_offset + i * (2 * math.pi / 3)
            x = center_x + math.cos(angle) * self.orbit_radius
            y = center_y + math.sin(angle) * self.orbit_radius
            
            # 绘制发光效果
            radial = QRadialGradient(x, y, self.dot_radius*2)
            radial.setColorAt(0, QColor(255, 255, 255, 150))
            radial.setColorAt(0.5, QColor(int(self.primary_color[0]), int(self.primary_color[1]), int(self.primary_color[2]), 100))
            radial.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(radial))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(x - self.dot_radius*2, y - self.dot_radius*2, 
                                     self.dot_radius*4, self.dot_radius*4))
            
            # 绘制实心点
            painter.setBrush(QBrush(QColor(int(self.highlight_color[0]), int(self.highlight_color[1]), int(self.highlight_color[2]))))
            painter.drawEllipse(QRectF(x - self.dot_radius, y - self.dot_radius, 
                                     self.dot_radius*2, self.dot_radius*2))
        
        # 绘制中心图案
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.drawEllipse(QRectF(center_x - self.dot_radius*1.5, center_y - self.dot_radius*1.5, 
                                 self.dot_radius*3, self.dot_radius*3))
        
        # 绘制连接线
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(1)
        pen.setColor(QColor(int(self.secondary_color[0]), int(self.secondary_color[1]), int(self.secondary_color[2]), 120))
        painter.setPen(pen)
        
        # 连接所有运动点
        points = []
        for i in range(3):
            angle = self.animation_offset + i * (2 * math.pi / 3)
            x = center_x + math.cos(angle) * self.orbit_radius
            y = center_y + math.sin(angle) * self.orbit_radius
            points.append(QPoint(int(x), int(y)))
        
        # 绘制三角形连接
        painter.drawLine(points[0], points[1])
        painter.drawLine(points[1], points[2])
        painter.drawLine(points[2], points[0])
        
        # 连接到中心
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setColor(QColor(int(self.highlight_color[0]), int(self.highlight_color[1]), int(self.highlight_color[2]), 100))
        painter.setPen(pen)
        for point in points:
            painter.drawLine(QPoint(int(center_x), int(center_y)), point)

class SliderTrack(QWidget):
    """滑块轨道组件，绘制背景和进度"""
    
    def __init__(self, parent=None, orientation=Qt.Orientation.Horizontal, color=None):
        super().__init__(parent)
        
        # 基本属性
        self._orientation = orientation
        self._progress = 0.0  # 0.0 到 1.0
        self._hovered = False
        self._hover_factor = 0.0  # 悬停动画因子(0.0-1.0)，用于平滑过渡
        
        # 配置颜色
        self._track_color = color or [52, 152, 219]  # 默认蓝色
        
        # 配置尺寸
        self.setMinimumSize(100, 6)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding if orientation == Qt.Orientation.Horizontal else QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed if orientation == Qt.Orientation.Horizontal else QSizePolicy.Policy.Expanding
        )
        
        # 启用鼠标追踪以接收悬停事件
        self.setMouseTracking(True)
        
        # 设置悬停动画
        self._hover_animation = QPropertyAnimation(self, b"hover_factor")
        self._hover_animation.setDuration(350) # 动画持续时间350毫秒
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic) # 使用缓出曲线
    
    # 定义hover_factor属性
    @pyqtProperty(float)
    def hover_factor(self):
        return self._hover_factor
    
    @hover_factor.setter
    def hover_factor(self, value):
        self._hover_factor = value
        self.update()  # 当动画值改变时触发重绘
    
    def set_track_color(self, color):
        """设置轨道颜色"""
        self._track_color = color
        self.update()
    
    def set_progress(self, progress):
        """设置进度值 (0.0 到 1.0)"""
        self._progress = max(0.0, min(1.0, progress))
        self.update()
    
    def get_progress(self):
        """获取当前进度值"""
        return self._progress
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self._hovered = True
        
        # 启动悬停动画
        self._hover_animation.setStartValue(self._hover_factor)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._hovered = False
        
        # 启动悬停动画
        self._hover_animation.setStartValue(self._hover_factor)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """绘制轨道和进度"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取尺寸
        width = self.width()
        height = self.height()
        
        # 计算轨道区域
        if self._orientation == Qt.Orientation.Horizontal:
            track_height = 6
            track_rect = QRectF(0, (height - track_height) / 2, width, track_height)
        else:
            track_width = 6
            track_rect = QRectF((width - track_width) / 2, 0, track_width, height)
        
        # 计算进度区域
        if self._orientation == Qt.Orientation.Horizontal:
            progress_width = width * self._progress
            progress_rect = QRectF(0, (height - track_height) / 2, progress_width, track_height)
        else:
            progress_height = height * self._progress
            progress_rect = QRectF(
                (width - track_width) / 2,
                height - progress_height,
                track_width,
                progress_height
            )
        
        # 根据悬停状态调整不透明度
        base_opacity = 0.5
        hover_opacity = 0.7
        current_opacity = base_opacity + (hover_opacity - base_opacity) * self._hover_factor
        
        # 绘制轨道背景
        track_color = QColor(*self._track_color, int(current_opacity * 80))
        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, 3, 3)
        
        # 绘制进度
        progress_color = QColor(*self._track_color, int(current_opacity * 255))
        painter.setBrush(QBrush(progress_color))
        painter.drawRoundedRect(progress_rect, 3, 3)
        
        # 悬停时添加轨道发光效果
        if self._hover_factor > 0:
            # 为轨道添加发光效果
            glow_color = QColor(*self._track_color, int(50 * self._hover_factor))
            for i in range(3):
                blur_radius = 5 + i * 2
                glow_rect = track_rect.adjusted(
                    -blur_radius, -blur_radius, blur_radius, blur_radius
                )
                
                painter.setPen(QPen(glow_color, i + 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(glow_rect, 3 + blur_radius, 3 + blur_radius)
                
            # 为进度条添加更强的发光效果
            progress_glow_color = QColor(*self._track_color, int(80 * self._hover_factor))
            for i in range(2):
                blur_radius = 3 + i * 2
                
                if self._orientation == Qt.Orientation.Horizontal:
                    progress_glow_rect = progress_rect.adjusted(
                        -blur_radius, -blur_radius, blur_radius, blur_radius
                    )
                else:
                    progress_glow_rect = progress_rect.adjusted(
                        -blur_radius, -blur_radius, blur_radius, blur_radius
                    )
                
                painter.setPen(QPen(progress_glow_color, i + 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(progress_glow_rect, 3 + blur_radius, 3 + blur_radius)
        
        painter.end()

class AnimatedSlider(QWidget):
    """动画滑块组件，支持水平和垂直方向
    
    特性：
    - 流畅的动画效果
    - 自定义手势图案滑块
    - 渐变颜色和发光效果
    - 可自定义主题颜色和样式
    - 支持悬停反馈和交互动画
    - 支持步长吸附功能
    """
    
    # 定义信号
    valueChanged = pyqtSignal(int)
    sliderPressed = pyqtSignal()
    sliderReleased = pyqtSignal()
    sliderMoved = pyqtSignal(int)
    
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        self.logger = get_logger("AnimatedSlider")
        
        # 基本属性
        self._minimum = 0
        self._maximum = 100
        self._value = 50
        self._step = 1  # 默认步长为1
        self._orientation = orientation
        self._pressed = False
        self._handle_hovered = False  # 手柄悬停状态
        self._dragged_value = None  # 拖动过程中的实际值（未吸附）
        
        # 配置颜色
        self._primary_color = [52, 152, 219]  # 默认蓝色
        self._handle_size = 24
        
        # 设置适当的尺寸策略
        if orientation == Qt.Orientation.Horizontal:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.setMinimumHeight(self._handle_size + 8)
            self.setMinimumWidth(100)
        else:
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            self.setMinimumWidth(self._handle_size + 8)
            self.setMinimumHeight(100)
        
        # 创建子组件
        self._create_components()
        
        # 创建动画
        self._setup_animations()
        
        # 初始化
        self._update_handle_position()
        self.setMouseTracking(True)
        
        self.logger.info("滑块组件初始化完成")
        
    def _create_components(self):
        """创建滑块组件"""
        # 创建布局
        if self._orientation == Qt.Orientation.Horizontal:
            self._layout = QVBoxLayout(self)
        else:
            self._layout = QHBoxLayout(self)
            
        self._layout.setContentsMargins(4, 4, 4, 4)
        
        # 创建轨道
        self._track = SliderTrack(self, self._orientation, self._primary_color)
        
        # 创建手柄
        self._handle = GesturePattern(self, self._handle_size, self._primary_color)
        self._handle.raise_()  # 确保手柄在顶层
        self._handle.setMouseTracking(True)  # 确保手柄接收鼠标移动事件
        self._handle.set_value(self._value)  # 设置初始值
        
        # 添加阴影效果
        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setBlurRadius(12)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        self._shadow.setOffset(0, 2)
        self._handle.setGraphicsEffect(self._shadow)
        
        # 将轨道添加到布局
        self._layout.addWidget(self._track)
        
        # 设置布局
        self.setLayout(self._layout)
        
    def _setup_animations(self):
        """设置动画效果"""
        # 手柄位置动画
        self._handle_animation = QPropertyAnimation(self, b"handle_pos")
        self._handle_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._handle_animation.setDuration(200)
        
        # 手柄大小动画
        self._handle_size_animation = QPropertyAnimation(self, b"handle_size")
        self._handle_size_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        self._handle_size_animation.setDuration(200)
        
        # 阴影动画
        self._shadow_animation = QPropertyAnimation(self._shadow, b"blurRadius")
        self._shadow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._shadow_animation.setDuration(200)
        
        # 阴影颜色动画
        self._shadow_color_animation = QPropertyAnimation(self, b"shadow_color_alpha")
        self._shadow_color_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._shadow_color_animation.setDuration(350)
    
    # 定义阴影颜色Alpha通道属性
    @pyqtProperty(int)
    def shadow_color_alpha(self):
        return self._shadow.color().alpha()
    
    @shadow_color_alpha.setter
    def shadow_color_alpha(self, value):
        color = self._shadow.color()
        color.setAlpha(value)
        self._shadow.setColor(color)
    
    def _get_handle_pos(self):
        """获取手柄位置，归一化值 (0.0 到 1.0)"""
        if self._minimum == self._maximum:
            return 0.0
        
        return (self._value - self._minimum) / float(self._maximum - self._minimum)
    
    def _set_handle_pos(self, pos):
        """设置手柄位置 (0.0 到 1.0)"""
        self._track.set_progress(pos)
        
        # 更新手柄位置
        if self._orientation == Qt.Orientation.Horizontal:
            x = int(pos * (self.width() - self._handle.width()))
            self._handle.move(x, (self.height() - self._handle.height()) // 2)
        else:
            y = int((1.0 - pos) * (self.height() - self._handle.height()))
            self._handle.move((self.width() - self._handle.width()) // 2, y)
    
    def _get_handle_size(self):
        """获取当前手柄大小"""
        return self._handle.width()
    
    def _set_handle_size(self, size):
        """设置手柄大小"""
        current_pos = self._get_handle_pos()
        self._handle.setFixedSize(size, size)
        self._set_handle_pos(current_pos)  # 重新定位手柄
    
    # 定义属性    
    handle_pos = pyqtProperty(float, _get_handle_pos, _set_handle_pos)
    handle_size = pyqtProperty(int, _get_handle_size, _set_handle_size)
    
    def setValue(self, value):
        """设置滑块的值"""
        value = min(max(value, self._minimum), self._maximum)
        
        if value != self._value:
            old_value = self._value
            self._value = value
            
            # 更新显示
            self._handle.set_value(value)
            self._update_handle_position(animate=True)
            
            # 发出信号
            self.valueChanged.emit(value)
            
            # 如果处于拖动状态，还要发送sliderMoved信号
            if self._pressed:
                self.sliderMoved.emit(value)
                
    def value(self):
        """获取当前值"""
        return self._value
    
    def setMinimum(self, min_value):
        """设置最小值"""
        if min_value != self._minimum:
            self._minimum = min_value
            if self._minimum > self._value:
                self.setValue(self._minimum)
            else:
                self._update_handle_position()
    
    def minimum(self):
        """获取最小值"""
        return self._minimum
    
    def setMaximum(self, max_value):
        """设置最大值"""
        if max_value != self._maximum:
            self._maximum = max_value
            if self._maximum < self._value:
                self.setValue(self._maximum)
            else:
                self._update_handle_position()
    
    def maximum(self):
        """获取最大值"""
        return self._maximum
    
    def setRange(self, min_value, max_value):
        """设置值范围"""
        self.setMinimum(min_value)
        self.setMaximum(max_value)
    
    def setPrimaryColor(self, color):
        """设置主题颜色"""
        if isinstance(color, list) and len(color) >= 3:
            self._primary_color = color
            self._track.set_track_color(color)
            self._handle.set_primary_color(color)
            self.update()
    
    def _update_handle_position(self, animate=False):
        """更新手柄位置"""
        pos = self._get_handle_pos()
        
        if animate:
            self._handle_animation.setStartValue(self._track.get_progress())
            self._handle_animation.setEndValue(pos)
            self._handle_animation.start()
        else:
            self._set_handle_pos(pos)
    
    def _animate_handle_press(self):
        """手柄按下动画"""
        # 显示值
        self._handle.set_show_value(True)
        
        self._handle_size_animation.setStartValue(self._handle.width())
        self._handle_size_animation.setEndValue(self._handle_size * 1.2)
        self._handle_size_animation.start()
        
        self._shadow_animation.setStartValue(12)
        self._shadow_animation.setEndValue(16)
        self._shadow_animation.start()
        
        # 增强阴影颜色
        self._shadow_color_animation.setStartValue(self._shadow.color().alpha())
        self._shadow_color_animation.setEndValue(120)
        self._shadow_color_animation.start()
    
    def _animate_handle_release(self):
        """手柄释放动画"""
        # 如果不是悬停状态，隐藏值
        if not self._handle_hovered:
            self._handle.set_show_value(False)
        
        self._handle_size_animation.setStartValue(self._handle.width())
        self._handle_size_animation.setEndValue(self._handle_size)
        self._handle_size_animation.start()
        
        self._shadow_animation.setStartValue(self._shadow.blurRadius())
        self._shadow_animation.setEndValue(12)
        self._shadow_animation.start()
        
        # 恢复阴影颜色
        alpha = 80
        if self._handle_hovered:
            alpha = 100  # 悬停时保持稍强的阴影
            
        self._shadow_color_animation.setStartValue(self._shadow.color().alpha())
        self._shadow_color_animation.setEndValue(alpha)
        self._shadow_color_animation.start()
    
    def _animate_handle_hover(self, hovered):
        """手柄悬停动画"""
        self._handle_hovered = hovered
        
        if hovered:
            # 悬停状态，显示值
            self._handle.set_show_value(True)
            
            # 悬停状态
            self._handle_size_animation.setStartValue(self._handle.width())
            target_size = min(self._handle_size * 1.1, self._handle_size * 1.2 if self._pressed else self._handle_size * 1.1)
            self._handle_size_animation.setEndValue(target_size)
            self._handle_size_animation.start()
            
            # 增强阴影
            self._shadow_animation.setStartValue(self._shadow.blurRadius())
            self._shadow_animation.setEndValue(14)  # 比正常状态稍强但比按下状态弱
            self._shadow_animation.start()
            
            # 增强阴影颜色
            self._shadow_color_animation.setStartValue(self._shadow.color().alpha())
            self._shadow_color_animation.setEndValue(100)  # 比正常状态深但比按下状态浅
            self._shadow_color_animation.start()
        else:
            # 非悬停状态，如果没有按下则隐藏值
            if not self._pressed:
                self._handle.set_show_value(False)
            
            # 非悬停状态
            if not self._pressed:  # 如果没有按下，才恢复正常大小
                self._handle_size_animation.setStartValue(self._handle.width())
                self._handle_size_animation.setEndValue(self._handle_size)
                self._handle_size_animation.start()
                
                # 恢复阴影
                self._shadow_animation.setStartValue(self._shadow.blurRadius())
                self._shadow_animation.setEndValue(12)
                self._shadow_animation.start()
                
                # 恢复阴影颜色
                self._shadow_color_animation.setStartValue(self._shadow.color().alpha())
                self._shadow_color_animation.setEndValue(80)
                self._shadow_color_animation.start()
    
    def _pos_to_value(self, pos):
        """将位置转换为值"""
        if self._orientation == Qt.Orientation.Horizontal:
            return self._minimum + (self._maximum - self._minimum) * (pos / float(self.width()))
        else:
            return self._minimum + (self._maximum - self._minimum) * (1.0 - (pos / float(self.height())))
    
    def _bound_pos_to_range(self, pos):
        """将位置限制在组件范围内"""
        if self._orientation == Qt.Orientation.Horizontal:
            return min(max(pos, 0), self.width())
        else:
            return min(max(pos, 0), self.height())
    
    def setStep(self, step):
        """设置滑块的步长"""
        if step > 0:
            self._step = step
    
    def step(self):
        """获取步长值"""
        return self._step
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            
            # 更新位置
            if self._orientation == Qt.Orientation.Horizontal:
                pos = self._bound_pos_to_range(int(event.position().x()))
            else:
                pos = self._bound_pos_to_range(int(event.position().y()))
            
            # 转换到值
            value = int(round(self._pos_to_value(pos)))
            self.setValue(value)
            
            # 动画效果
            self._animate_handle_press()
            
            # 发送信号
            self.sliderPressed.emit()
            
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self._pressed:
            # 更新位置
            if self._orientation == Qt.Orientation.Horizontal:
                pos = self._bound_pos_to_range(int(event.position().x()))
            else:
                pos = self._bound_pos_to_range(int(event.position().y()))
            
            # 转换到值，但不进行吸附
            raw_value = self._pos_to_value(pos)
            self._dragged_value = raw_value  # 保存拖动的实际值
            
            # 转换到显示值 (如果希望拖动时显示吸附预览，可以注释下面一行，让显示值也按步长对齐)
            value = int(round(raw_value))
            
            # 更新滑块位置
            self.setValue(value)
            
            event.accept()
        else:
            # 检查是否悬停在手柄上
            handle_rect = self._handle.geometry()
            is_over_handle = handle_rect.contains(event.position().toPoint())
            
            # 如果悬停状态改变，触发动画
            if is_over_handle != self._handle_hovered:
                self._animate_handle_hover(is_over_handle)
                
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            
            # 动画效果
            self._animate_handle_release()
            
            # 如果有拖动值，应用吸附
            if self._dragged_value is not None:
                # 计算最接近步长的值
                stepped_value = round(self._dragged_value / self._step) * self._step
                # 确保值在范围内
                snapped_value = max(self._minimum, min(self._maximum, stepped_value))
                # 设置最终值并触发动画
                self.setValue(snapped_value)
                self._dragged_value = None
            
            # 发送信号
            self.sliderReleased.emit()
            
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        """鼠标进入组件事件"""
        # 略过处理，让mouseMoveEvent处理悬停检测
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开组件事件"""
        # 如果之前悬停在手柄上，触发离开动画
        if self._handle_hovered:
            self._animate_handle_hover(False)
            
        super().leaveEvent(event)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        self._update_handle_position()
    
    def showEvent(self, event):
        """组件显示事件"""
        super().showEvent(event)
        self._update_handle_position()


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QWidget()
    window.setWindowTitle("GestroKey 滑块测试")
    window.setMinimumSize(600, 400)
    window.setStyleSheet("background-color: #f5f5f5;")
    
    # 创建布局
    layout = QVBoxLayout(window)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(30)
    
    # 添加标题
    title = QLabel("GestroKey 滑块组件")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #333;")
    layout.addWidget(title)
    
    # 添加水平滑块（默认步长=1）
    h_slider_label = QLabel("水平滑块 (步长=1)：")
    h_slider_label.setStyleSheet("font-size: 12pt; color: #555;")
    layout.addWidget(h_slider_label)
    
    h_slider = AnimatedSlider(Qt.Orientation.Horizontal)
    h_slider.setMinimumWidth(500)
    h_slider.setRange(0, 100)
    h_slider.setValue(30)
    layout.addWidget(h_slider)
    
    # 添加步长为5的滑块
    custom_label = QLabel("步长为5的滑块：")
    custom_label.setStyleSheet("font-size: 12pt; color: #555;")
    layout.addWidget(custom_label)
    
    custom_slider = AnimatedSlider(Qt.Orientation.Horizontal)
    custom_slider.setMinimumWidth(500)
    custom_slider.setRange(0, 100)
    custom_slider.setValue(70)
    custom_slider.setStep(5)  # 设置步长为5
    custom_slider.setPrimaryColor([231, 76, 60])  # 红色系
    layout.addWidget(custom_slider)
    
    # 添加步长为10的滑块
    step10_label = QLabel("步长为10的滑块：")
    step10_label.setStyleSheet("font-size: 12pt; color: #555;")
    layout.addWidget(step10_label)
    
    step10_slider = AnimatedSlider(Qt.Orientation.Horizontal)
    step10_slider.setMinimumWidth(500)
    step10_slider.setRange(0, 100)
    step10_slider.setValue(50)
    step10_slider.setStep(10)  # 设置步长为10
    step10_slider.setPrimaryColor([155, 89, 182])  # 紫色系
    layout.addWidget(step10_slider)
    
    # 添加垂直滑块
    slider_row = QHBoxLayout()
    
    v_slider_label = QLabel("垂直滑块 (步长=1)：")
    v_slider_label.setStyleSheet("font-size: 12pt; color: #555;")
    slider_row.addWidget(v_slider_label)
    
    v_slider = AnimatedSlider(Qt.Orientation.Vertical)
    v_slider.setMinimumHeight(200)
    v_slider.setRange(0, 100)
    v_slider.setValue(60)
    slider_row.addWidget(v_slider)
    
    # 添加另一个自定义颜色的垂直滑块（步长为5）
    v_slider2 = AnimatedSlider(Qt.Orientation.Vertical)
    v_slider2.setMinimumHeight(200)
    v_slider2.setRange(0, 100)
    v_slider2.setValue(40)
    v_slider2.setStep(5)  # 步长为5
    v_slider2.setPrimaryColor([46, 204, 113])  # 绿色系
    slider_row.addWidget(v_slider2)
    
    # 添加步长为20的垂直滑块
    v_slider3 = AnimatedSlider(Qt.Orientation.Vertical)
    v_slider3.setMinimumHeight(200)
    v_slider3.setRange(0, 100)
    v_slider3.setValue(60)
    v_slider3.setStep(20)  # 步长为20
    v_slider3.setPrimaryColor([52, 152, 219])  # 蓝色系
    slider_row.addWidget(v_slider3)
    
    slider_row.addStretch(1)  # 添加弹性空间
    layout.addLayout(slider_row)
    
    # 添加操作说明
    info_label = QLabel("使用说明：拖动滑块时可以任意位置拖动，松开后会自动吸附到最近的步长刻度")
    info_label.setStyleSheet("font-size: 11pt; color: #555; font-style: italic;")
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(info_label)
    
    # 添加弹性空间
    layout.addStretch(1)
    
    # 显示窗口
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec()) 