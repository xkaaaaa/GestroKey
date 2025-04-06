import sys
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QApplication, 
                            QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QPushButton)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, 
                         QRect, QSize, QParallelAnimationGroup, QSequentialAnimationGroup,
                         pyqtSignal, pyqtProperty, QObject, QRectF, QEvent)
from PyQt5.QtGui import (QColor, QPainter, QPen, QBrush, QPainterPath, QFont, 
                        QFontMetrics, QIcon, QPixmap, QLinearGradient)

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

class CloseButton(QWidget):
    """关闭按钮组件"""
    
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self._hovered = False
        self._pressed = False
        self._opacity = 0.0
        
        # 创建透明度动画
        self.opacityAni = QPropertyAnimation(self, b"opacity")
        self.opacityAni.setDuration(150)
        self.opacityAni.setEasingCurve(QEasingCurve.OutCubic)
        
        # 鼠标追踪
        self.setMouseTracking(True)
    
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, o):
        self._opacity = o
        self.update()
    
    def enterEvent(self, e):
        self._hovered = True
        self.update()
    
    def leaveEvent(self, e):
        self._hovered = False
        self._pressed = False
        self.update()
    
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._pressed = True
            self.update()
    
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self._pressed:
            self._pressed = False
            self.clicked.emit()
        self.update()
    
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 根据状态设置颜色
        if self._pressed:
            color = QColor(255, 255, 255, int(220 * self._opacity))
        elif self._hovered:
            color = QColor(255, 255, 255, int(200 * self._opacity))
        else:
            color = QColor(255, 255, 255, int(160 * self._opacity))
        
        # 绘制 X 形状
        painter.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap))
        
        # 计算中心点和偏移
        center = self.rect().center()
        offset = 4
        
        # 绘制 X
        painter.drawLine(center.x() - offset, center.y() - offset, 
                         center.x() + offset, center.y() + offset)
        painter.drawLine(center.x() + offset, center.y() - offset, 
                         center.x() - offset, center.y() + offset)

class ElegantToast(QWidget):
    """
    一个现代优雅的消息提示组件。
    在窗口角落显示一个平滑动画的提示。
    """
    
    # 类型
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    
    # 文本显示模式
    TEXT_TRUNCATE = "truncate"  # 截断模式（默认）
    TEXT_SCROLL = "scroll"      # 滚动模式
    TEXT_WRAP = "wrap"          # 自动换行模式
    
    # 当提示关闭时发出的信号
    closed = pyqtSignal(object)
    
    def __init__(self, parent=None, message="", toast_type=INFO, 
                duration=3000, icon=None, position='top-right',
                text_mode=TEXT_TRUNCATE):
        """
        初始化提示通知
        
        参数:
            parent: 父窗口
            message: 消息文本
            toast_type: 提示类型 (info, success, warning, error)
            duration: 显示持续时间（毫秒）
            icon: 自定义图标（默认为类型图标）
            position: 屏幕位置 ('top-right', 'top-left', 'bottom-right', 'bottom-left')
            text_mode: 文本显示模式 ('truncate', 'scroll', 'wrap')
        """
        super().__init__(parent)
        self.logger = get_logger("ElegantToast")
        
        # 存储参数
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self.custom_icon = icon
        self.position = position
        self.text_mode = text_mode
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 状态变量
        self._opacity = 0.0
        self._progress = 1.0
        self._closing = False
        self._hovered = False
        self._close_button_opacity = 0.0
        self._text_scroll_offset = 0.0
        self._original_pos = None  # 用于保存晃动前的原始位置
        
        # 根据类型设置颜色
        self.setup_colors()
        
        # 初始化UI
        self.init_ui()
        
        # 设置定时器
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.start_closing)
        
        # 创建动画
        self.create_animations()
        
        # 设置阴影效果
        self.set_shadow_effect()
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        self.logger.debug(f"创建通知提示: {toast_type}, 消息: {message}")
    
    def setup_colors(self):
        """根据提示类型配置颜色"""
        if self.toast_type == self.INFO:
            self.main_color = QColor(41, 128, 185)  # 蓝色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
        elif self.toast_type == self.SUCCESS:
            self.main_color = QColor(39, 174, 96)  # 绿色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
        elif self.toast_type == self.WARNING:
            self.main_color = QColor(211, 159, 15)  # 黄色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
        elif self.toast_type == self.ERROR:
            self.main_color = QColor(192, 57, 43)  # 红色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
        else:
            # 默认颜色
            self.main_color = QColor(41, 128, 185)  # 蓝色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
        
        # 边框颜色略深
        self.border_color = QColor(self.main_color)
        self.border_color.setAlpha(150)
    
    def init_ui(self):
        """初始化用户界面"""
        # 根据文本模式设置大小
        if self.text_mode == self.TEXT_WRAP:
            # 换行模式，计算需要的高度
            font = QFont("Arial", 10)
            metrics = QFontMetrics(font)
            text_width = 300 - 70  # 考虑左右边距
            text_rect = metrics.boundingRect(0, 0, text_width, 1000, Qt.TextWordWrap, self.message)
            # 限制最大高度，避免提示框过长
            height = min(max(60, text_rect.height() + 24), 120)  # 最小高度60，最大高度120
            self.setFixedSize(300, height)
        else:
            # 固定大小
            self.setFixedSize(300, 60)
    
    def set_shadow_effect(self):
        """为提示添加阴影效果"""
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)
    
    def create_animations(self):
        """创建显示和隐藏的动画"""
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 进度动画（用于进度指示器）
        self.progress_animation = QPropertyAnimation(self, b"progress")
        self.progress_animation.setEasingCurve(QEasingCurve.Linear)
        self.progress_animation.setStartValue(1.0)
        self.progress_animation.setEndValue(0.0)
        
        # 文本滚动动画（仅在滚动模式下使用）
        if self.text_mode == self.TEXT_SCROLL:
            self.scroll_animation = QPropertyAnimation(self, b"text_scroll_offset")
            # 不在这里设置时长，在showEvent中根据文本长度动态设置
            self.scroll_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.scroll_animation.setLoopCount(-1)  # 循环滚动
        
        # 错误提示的晃动动画
        if self.toast_type == self.ERROR:
            self.shake_animation = QSequentialAnimationGroup(self)
            self.shake_animation.finished.connect(self.reset_position)
            
            # 增加晃动幅度和次数
            shake_distance = 12  # 增加晃动幅度，原来是6
            shake_count = 5
            
            for i in range(shake_count):
                # 向右晃动
                right_anim = QPropertyAnimation(self, b"pos", self)
                right_anim.setDuration(70)  # 稍微延长动画时间
                right_anim.setEasingCurve(QEasingCurve.InOutSine)
                # 末尾衰减震动幅度
                factor = 1.0 - (i / shake_count) * 0.5
                distance = int(shake_distance * factor)
                right_anim.setPropertyName(b"pos")
                
                # 向左晃动
                left_anim = QPropertyAnimation(self, b"pos", self)
                left_anim.setDuration(70)  # 稍微延长动画时间
                left_anim.setEasingCurve(QEasingCurve.InOutSine)
                left_anim.setPropertyName(b"pos")
                
                # 添加到动画组
                self.shake_animation.addAnimation(right_anim)
                self.shake_animation.addAnimation(left_anim)
                
            # 回到原位置的动画
            final_anim = QPropertyAnimation(self, b"pos", self)
            final_anim.setDuration(70)  # 稍微延长动画时间
            final_anim.setEasingCurve(QEasingCurve.OutCubic)
            self.shake_animation.addAnimation(final_anim)
    
    # 属性
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        # 更新整个组件及子组件
        self.update()
    
    @pyqtProperty(float)
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()
    
    @pyqtProperty(float)
    def close_button_opacity(self):
        return self._close_button_opacity
    
    @close_button_opacity.setter
    def close_button_opacity(self, value):
        self._close_button_opacity = value
        self.update()
    
    @pyqtProperty(float)
    def text_scroll_offset(self):
        return self._text_scroll_offset
    
    @text_scroll_offset.setter
    def text_scroll_offset(self, value):
        self._text_scroll_offset = value
        self.update()
    
    def showEvent(self, event):
        """处理显示事件"""
        super().showEvent(event)
        
        # 开始显示动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
        
        # 如果是错误提示，直接开始晃动动画，不等待透明度动画完成
        if self.toast_type == self.ERROR:
            # 保存原始位置并开始晃动
            QTimer.singleShot(50, self.start_shake_animation)  # 短暂延迟确保已经定位
        
        # 如果设置了持续时间，开始进度动画
        if self.duration > 0:
            self.progress_animation.setDuration(self.duration)
            self.progress_animation.start()
            
            # 设置自动关闭定时器
            self.timer.start(self.duration)
        
        # 如果是滚动模式且文本过长，开始滚动动画
        if self.text_mode == self.TEXT_SCROLL:
            # 计算文本宽度
            font = QFont("Arial", 10)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(self.message)
            display_width = self.width() - 70  # 可显示宽度
            
            if text_width > display_width:
                # 需要滚动，设置动画
                self.scroll_animation.setStartValue(0)
                # 确保完整显示文本 - 增加滚动范围并添加额外空间
                end_offset = -(text_width - display_width/2)
                self.scroll_animation.setEndValue(end_offset)
                
                # 调整滚动持续时间，使速度恒定
                # 基准：每100像素滚动距离大约需要3000毫秒
                pixels_to_scroll = abs(end_offset)
                # 设置固定的每像素滚动时间，确保一致的滚动体验
                pixel_duration = 25  # 每像素滚动所需的毫秒数
                
                # 最小持续时间确保短文本也有足够的动画效果
                min_duration = 4000
                duration = max(min_duration, int(pixels_to_scroll * pixel_duration))
                
                # 设置动画持续时间
                self.logger.debug(f"文本滚动距离: {pixels_to_scroll}像素, 动画时长: {duration}毫秒")
                self.scroll_animation.setDuration(duration)
                self.scroll_animation.start()
    
    def start_shake_animation(self):
        """开始错误提示的晃动动画"""
        if hasattr(self, 'shake_animation'):
            # 保存原始位置
            self._original_pos = self.pos()
            
            # 设置晃动的起始和结束位置
            shake_distance = 12  # 增加晃动幅度，原来是6
            
            current_x = self._original_pos.x()
            current_y = self._original_pos.y()
            
            for i in range(0, self.shake_animation.animationCount() - 1, 2):
                # 向右
                right_anim = self.shake_animation.animationAt(i)
                right_anim.setStartValue(QPoint(current_x, current_y))
                right_anim.setEndValue(QPoint(current_x + shake_distance - int(i/2), current_y))
                
                # 向左
                if i + 1 < self.shake_animation.animationCount():
                    left_anim = self.shake_animation.animationAt(i + 1)
                    left_anim.setStartValue(QPoint(current_x + shake_distance - int(i/2), current_y))
                    left_anim.setEndValue(QPoint(current_x - shake_distance + int(i/2), current_y))
                    
                shake_distance = max(shake_distance - 1, 3)  # 增加最小幅度
            
            # 最后回到原位
            final_anim = self.shake_animation.animationAt(self.shake_animation.animationCount() - 1)
            final_anim.setStartValue(QPoint(current_x - 4, current_y))  # 增加偏移量
            final_anim.setEndValue(self._original_pos)
            
            # 开始晃动
            self.shake_animation.start()
    
    def reset_position(self):
        """晃动动画结束后重置位置"""
        if self._original_pos:
            self.move(self._original_pos)
            self._original_pos = None
    
    def start_closing(self):
        """开始关闭动画"""
        if self._closing:
            return
        
        self._closing = True
        self.timer.stop()
        self.progress_animation.stop()
        
        # 开始关闭动画
        self.opacity_animation.setStartValue(self._opacity)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self.on_close_finished)
        self.opacity_animation.start()
    
    def on_close_finished(self):
        """关闭动画完成后清理"""
        self.hide()
        self.closed.emit(self)
    
    def enterEvent(self, event):
        """鼠标进入事件 - 显示关闭按钮但不暂停滚动"""
        self._hovered = True
        
        # 显示关闭按钮
        self.closeBtn_animation = QPropertyAnimation(self, b"close_button_opacity")
        self.closeBtn_animation.setDuration(200)
        self.closeBtn_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.closeBtn_animation.setStartValue(self._close_button_opacity)
        self.closeBtn_animation.setEndValue(1.0)
        self.closeBtn_animation.start()
        
        # 不再暂停滚动动画
        
        # 暂停定时器
        if not self._closing and self.duration > 0:
            self.timer.stop()
            self.progress_animation.pause()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件 - 恢复定时器并隐藏关闭按钮"""
        self._hovered = False
        
        # 隐藏关闭按钮
        self.closeBtn_animation = QPropertyAnimation(self, b"close_button_opacity")
        self.closeBtn_animation.setDuration(200)
        self.closeBtn_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.closeBtn_animation.setStartValue(self._close_button_opacity)
        self.closeBtn_animation.setEndValue(0.0)
        self.closeBtn_animation.start()
        
        # 不再恢复滚动动画
        
        # 恢复定时器
        if not self._closing and self.duration > 0:
            # 计算剩余时间
            remaining_time = int(self.duration * self._progress)
            if remaining_time > 100:  # 至少100毫秒
                self.timer.start(remaining_time)
                
                # 恢复进度动画
                # 先停止进度动画，避免多次pause/resume导致的异常
                self.progress_animation.stop()
                # 从正确的位置重新开始
                self.progress_animation.setStartValue(self._progress)
                self.progress_animation.setEndValue(0.0)
                self.progress_animation.setDuration(remaining_time)
                self.progress_animation.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """检测关闭按钮的点击"""
        if event.button() == Qt.LeftButton and self.close_button_rect().contains(event.pos()):
            self.start_closing()
        super().mousePressEvent(event)
    
    def close_button_rect(self):
        """返回关闭按钮的矩形区域"""
        return QRect(self.width() - 25, 10, 16, 16)
    
    def paintEvent(self, event):
        """绘制通知提示"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置透明度
        painter.setOpacity(self._opacity)
        
        # 绘制背景
        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        
        # 填充背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self.main_color)
        gradient.setColorAt(1, self.main_color.darker(110))
        painter.fillPath(path, QBrush(gradient))
        
        # 绘制边框
        pen = QPen(self.border_color)
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 设置文本颜色
        painter.setPen(QPen(self.text_color))
        painter.setFont(QFont("Arial", 10))
        
        # 根据不同文本模式绘制消息文本
        message_rect = QRect(45, 12, self.width() - 70, self.height() - 24)
        
        if self.text_mode == self.TEXT_TRUNCATE:
            # 截断模式
            text = self.message
            # 创建字体度量来计算文本宽度
            metrics = QFontMetrics(painter.font())
            elided_text = metrics.elidedText(text, Qt.ElideRight, message_rect.width())
            painter.drawText(message_rect, Qt.AlignLeft | Qt.AlignVCenter, elided_text)
            
        elif self.text_mode == self.TEXT_SCROLL:
            # 滚动模式
            # 保存当前状态
            painter.save()
            # 创建剪裁区域
            painter.setClipRect(message_rect)
            
            # 获取文本宽度
            text_width = QFontMetrics(painter.font()).horizontalAdvance(self.message)
            
            # 设置足够宽的矩形来容纳全部文本
            scrolled_rect = QRect(message_rect)
            scrolled_rect.setWidth(text_width + 50)  # 添加额外空间
            scrolled_rect.moveLeft(message_rect.left() + int(self._text_scroll_offset))
            
            # 绘制文本
            painter.drawText(scrolled_rect, Qt.AlignLeft | Qt.AlignVCenter, self.message)
            # 恢复状态
            painter.restore()
            
        elif self.text_mode == self.TEXT_WRAP:
            # 自动换行模式，可能需要垂直滚动
            # 保存当前状态
            painter.save()
            # 创建剪裁区域，防止文字溢出
            painter.setClipRect(message_rect)
            
            # 检查文本是否需要换行
            metrics = QFontMetrics(painter.font())
            if metrics.horizontalAdvance(self.message) <= message_rect.width():
                # 单行文本，水平居中
                painter.drawText(message_rect, Qt.AlignHCenter | Qt.AlignVCenter, self.message)
            else:
                # 多行文本，左对齐
                painter.drawText(message_rect, Qt.AlignLeft | Qt.TextWordWrap, self.message)
                
            # 恢复状态
            painter.restore()
        
        # 如需要，绘制进度条
        if self.duration > 0 and not self._closing:
            progress_height = 3
            progress_y = self.height() - progress_height
            
            # 进度条背景（半透明）
            progress_bg_rect = QRectF(0, progress_y, self.width(), progress_height)
            painter.fillRect(progress_bg_rect, QBrush(QColor(0, 0, 0, 40)))
            
            # 实际进度
            progress_rect = QRectF(0, progress_y, self.width() * self._progress, progress_height)
            progress_color = QColor(255, 255, 255, 180)
            painter.fillRect(progress_rect, QBrush(progress_color))
            
        # 在左侧绘制类型图标
        self.draw_icon(painter)
        
        # 如果鼠标悬停，绘制关闭按钮
        if self._close_button_opacity > 0:
            painter.save()
            painter.setOpacity(self._close_button_opacity * self._opacity)
            
            # 绘制关闭按钮
            btn_rect = self.close_button_rect()
            
            # 根据状态设置颜色
            color = QColor(255, 255, 255, 160)
            
            # 绘制 X 形状
            painter.setPen(QPen(color, 1.5, Qt.SolidLine, Qt.RoundCap))
            
            # 计算中心点和偏移
            center = btn_rect.center()
            offset = 4
            
            # 绘制 X
            painter.drawLine(center.x() - offset, center.y() - offset, 
                             center.x() + offset, center.y() + offset)
            painter.drawLine(center.x() + offset, center.y() - offset, 
                             center.x() - offset, center.y() + offset)
            
            painter.restore()
    
    def draw_icon(self, painter):
        """根据提示类型绘制适当的图标"""
        icon_rect = QRect(18, (self.height() - 20) // 2, 20, 20)
        icon_color = self.icon_color
        
        if self.toast_type == self.INFO:
            # 信息图标 (i)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
            painter.drawEllipse(icon_rect)
            
            painter.setPen(QPen(icon_color))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.drawText(icon_rect, Qt.AlignCenter, "i")
            
        elif self.toast_type == self.SUCCESS:
            # 成功图标 (✓)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
            painter.drawEllipse(icon_rect)
            
            painter.setPen(QPen(icon_color, 2))
            center = icon_rect.center()
            painter.drawLine(center.x() - 5, center.y(), center.x() - 2, center.y() + 3)
            painter.drawLine(center.x() - 2, center.y() + 3, center.x() + 5, center.y() - 4)
            
        elif self.toast_type == self.WARNING:
            # 警告图标 (!)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
            painter.drawEllipse(icon_rect)
            
            painter.setPen(QPen(icon_color))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.drawText(icon_rect, Qt.AlignCenter, "!")
            
        elif self.toast_type == self.ERROR:
            # 错误图标 (✕)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
            painter.drawEllipse(icon_rect)
            
            painter.setPen(QPen(icon_color, 2))
            center = icon_rect.center()
            painter.drawLine(center.x() - 4, center.y() - 4, center.x() + 4, center.y() + 4)
            painter.drawLine(center.x() - 4, center.y() + 4, center.x() + 4, center.y() - 4)

class SimpleToast(QWidget):
    """
    简单的提示组件，仅显示彩色圆角矩形
    无文本或图标，在设定时间后自动消失。
    """
    
    closed = pyqtSignal(object)
    
    def __init__(self, parent=None, color=QColor(41, 128, 185), duration=2000, 
                 size=QSize(150, 40)):
        """
        初始化简单提示
        
        参数:
            parent: 父窗口
            color: 背景颜色
            duration: 显示持续时间（毫秒）
            size: 提示大小
        """
        super().__init__(parent)
        self.logger = get_logger("SimpleToast")
        
        # 存储参数
        self.bg_color = color
        self.border_color = color.darker(110)
        self.duration = duration
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 状态变量
        self._opacity = 0.0
        self._closing = False
        
        # 设置固定大小
        self.setFixedSize(size)
        
        # 设置定时器
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.start_closing)
        
        # 创建动画
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(250)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 设置阴影效果
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(0, 3)
        self.setGraphicsEffect(self.shadow)
        
        self.logger.debug("创建简单提示")
    
    @pyqtProperty(float)
    def opacity(self):
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        # 更新整个组件及子组件
        self.update()
    
    def showEvent(self, event):
        """处理显示事件"""
        super().showEvent(event)
        
        # 开始显示动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
        
        # 开始自动关闭定时器
        if self.duration > 0:
            self.timer.start(self.duration)
    
    def start_closing(self):
        """开始关闭动画"""
        if self._closing:
            return
        
        self._closing = True
        self.timer.stop()
        
        # 开始关闭动画
        self.opacity_animation.setStartValue(self._opacity)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self.on_close_finished)
        self.opacity_animation.start()
    
    def on_close_finished(self):
        """处理关闭动画完成"""
        self.hide()
        self.closed.emit(self)
    
    def paintEvent(self, event):
        """绘制简单提示"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置透明度
        painter.setOpacity(self._opacity)
        
        # 绘制背景
        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)
        
        # 填充背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self.bg_color)
        gradient.setColorAt(1, self.bg_color.darker(110))
        painter.fillPath(path, QBrush(gradient))
        
        # 绘制边框
        pen = QPen(self.border_color)
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawPath(path)

class ToastManager(QObject):
    """管理多个提示，处理它们的定位和堆叠"""
    
    # 单例实例
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToastManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, parent=None):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        super().__init__(parent)
        self.logger = get_logger("ToastManager")
        
        # 活动提示
        self.active_toasts = []
        
        # 位置动画
        self.position_animations = {}
        
        # 提示间距
        self.spacing = 10
        
        # 边距
        self.top_margin = 20
        self.right_margin = 20
        self.left_margin = 20
        self.bottom_margin = 20
        
        # 记录上次窗口大小
        self.last_parent_size = QSize()
        
        # 主窗口引用
        self.main_window = None
        
        self._initialized = True
        self.logger.debug("提示管理器初始化")
    
    def set_main_window(self, window):
        """设置主窗口引用，确保通知显示在主窗口上而不是当前选项卡上"""
        self.main_window = window
        self.logger.debug(f"设置主窗口引用: {window}")
        
        # 当设置主窗口时安装事件过滤器
        if window and not window.property("_toast_resize_filter_installed"):
            window.installEventFilter(self)
            window.setProperty("_toast_resize_filter_installed", True)
            self.last_parent_size = window.size()
    
    def show_toast(self, parent, message, toast_type=ElegantToast.INFO, 
                  duration=3000, icon=None, position='top-right',
                  text_mode=ElegantToast.TEXT_TRUNCATE):
        """
        显示通知提示
        
        参数:
            parent: 父窗口
            message: 消息内容
            toast_type: 提示类型
            duration: 显示持续时间（毫秒）
            icon: 自定义图标
            position: 位置 ('top-right', 'top-left', 'bottom-right', 'bottom-left')
            text_mode: 文本显示模式 ('truncate', 'scroll', 'wrap')
            
        返回:
            通知提示对象
        """
        self.logger.debug(f"创建提示: {message}")
        
        # 如果有主窗口引用，使用主窗口作为父窗口
        if self.main_window is not None:
            parent = self.main_window
            self.logger.debug(f"使用主窗口作为提示的父窗口")
        
        # 创建提示
        toast = ElegantToast(
            parent=parent,
            message=message,
            toast_type=toast_type,
            duration=duration,
            icon=icon,
            position=position,
            text_mode=text_mode
        )
        
        # 连接关闭信号
        toast.closed.connect(self.on_toast_closed)
        
        # 添加到活动提示
        self.active_toasts.append(toast)
        
        # 安装事件过滤器监听父窗口大小变化
        if parent and not parent.property("_toast_resize_filter_installed"):
            parent.installEventFilter(self)
            parent.setProperty("_toast_resize_filter_installed", True)
            self.last_parent_size = parent.size()
        
        # 先计算正确的位置
        self.calculate_toast_position(toast, parent, position)
        
        # 显示提示
        toast.show()
        
        return toast
    
    def calculate_toast_position(self, toast, parent, position='top-right'):
        """计算通知的正确位置（不使用动画）"""
        if not parent:
            return
            
        # 获取父窗口尺寸
        parent_width = parent.width()
        parent_height = parent.height()
        
        toast_width = toast.width()
        toast_height = toast.height()
        
        # 计算位置
        if position.endswith('right'):
            x = parent_width - toast_width - self.right_margin
        else:
            x = self.left_margin
            
        # 计算y坐标和剩余通知的偏移
        y_offset = self.top_margin
        
        # 计算当前位置应该有的y偏移
        for t in self.active_toasts:
            if t != toast and t.parent() == parent and getattr(t, 'position', 'top-right') == position:
                # 如果是之前的通知，增加y偏移
                if self.active_toasts.index(t) < self.active_toasts.index(toast):
                    y_offset += t.height() + self.spacing
        
        # 设置位置
        if position.startswith('top'):
            toast.move(x, y_offset)
        else:
            # 底部位置
            y = parent_height - self.bottom_margin - toast_height
            for t in self.active_toasts:
                if t != toast and t.parent() == parent and getattr(t, 'position', 'top-right') == position:
                    # 如果是之前的通知，减少y坐标（向上堆叠）
                    if self.active_toasts.index(t) < self.active_toasts.index(toast):
                        y -= (t.height() + self.spacing)
            toast.move(x, y)
    
    def show_simple(self, parent, color=QColor(41, 128, 185), duration=2000, 
                   size=QSize(150, 40), position='top-right'):
        """
        显示简单提示
        
        参数:
            parent: 父窗口
            color: 背景颜色
            duration: 显示持续时间（毫秒）
            size: 提示大小
            position: 位置 ('top-right', 'top-left', 'bottom-right', 'bottom-left')
            
        返回:
            SimpleToast对象
        """
        # 如果有主窗口引用，使用主窗口作为父窗口
        if self.main_window is not None:
            parent = self.main_window
            self.logger.debug(f"使用主窗口作为提示的父窗口")
            
        # 创建提示
        toast = SimpleToast(
            parent=parent,
            color=color,
            duration=duration,
            size=size
        )
        
        # 存储位置信息
        toast.position = position
        
        # 连接关闭信号
        toast.closed.connect(self.on_toast_closed)
        
        # 添加到活动提示
        self.active_toasts.append(toast)
        
        # 安装事件过滤器监听父窗口大小变化
        if parent and not parent.property("_toast_resize_filter_installed"):
            parent.installEventFilter(self)
            parent.setProperty("_toast_resize_filter_installed", True)
            self.last_parent_size = parent.size()
        
        # 先计算正确的位置
        self.calculate_toast_position(toast, parent, position)
        
        # 显示提示
        toast.show()
        
        return toast
    
    def arrange_toasts(self, parent, position='top-right'):
        """在指定位置排列提示（仅用于重新排列）"""
        if not parent or not self.active_toasts:
            return
        
        # 获取父窗口尺寸
        parent_width = parent.width()
        parent_height = parent.height()
        
        # 起始偏移取决于位置
        if position.startswith('top'):
            y_offset = self.top_margin
            y_direction = 1  # 向下
        else:
            y_offset = parent_height - self.bottom_margin
            y_direction = -1  # 向上
        
        # 仅获取此位置的通知
        position_toasts = [t for t in self.active_toasts if t.parent() == parent and getattr(t, 'position', 'top-right') == position]
        
        # 排列提示
        for toast in position_toasts:
            toast_width = toast.width()
            toast_height = toast.height()
            
            # 计算位置
            if position.endswith('right'):
                x = parent_width - toast_width - self.right_margin
            else:
                x = self.left_margin
            
            # 设置位置
            if position.startswith('top'):
                # 创建位置动画
                self.animate_position(toast, QPoint(x, y_offset))
                y_offset += toast_height + self.spacing
            else:
                # 创建位置动画
                self.animate_position(toast, QPoint(x, y_offset - toast_height))
                y_offset -= (toast_height + self.spacing)
    
    def animate_position(self, toast, target_position):
        """创建通知位置的平滑动画"""
        # 创建位置动画
        animation = QPropertyAnimation(toast, b"pos")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.setStartValue(toast.pos())
        animation.setEndValue(target_position)
        
        # 存储动画实例以防止被垃圾回收
        if toast in self.position_animations:
            self.position_animations[toast].stop()
        self.position_animations[toast] = animation
        
        # 动画结束后清理
        animation.finished.connect(lambda: self.on_position_animation_finished(toast))
        
        # 启动动画
        animation.start()
    
    def on_position_animation_finished(self, toast):
        """位置动画完成后的清理"""
        if toast in self.position_animations:
            del self.position_animations[toast]
    
    def on_toast_closed(self, toast):
        """处理提示关闭事件"""
        try:
            # 从活动提示中移除
            if toast in self.active_toasts:
                # 保存位置信息，以便重新排列其他提示
                position = getattr(toast, "position", "top-right")
                parent = toast.parent()
                
                # 移除toast
                self.active_toasts.remove(toast)
                
                # 删除相关动画
                if toast in self.position_animations:
                    self.position_animations[toast].stop()
                    del self.position_animations[toast]
                
                # 删除提示
                toast.deleteLater()
                
                # 重新排列剩余提示
                if parent:
                    self.arrange_toasts(parent, position)
        except Exception as e:
            self.logger.error(f"处理提示关闭时出错: {e}")
    
    def close_all(self):
        """关闭所有活动提示"""
        # 复制列表以避免迭代时修改
        toasts = self.active_toasts.copy()
        
        for toast in toasts:
            toast.start_closing()
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于监听父窗口大小变化"""
        if event.type() == QEvent.Resize:
            # 窗口大小变化时，重新排列提示
            current_size = obj.size()
            if current_size != self.last_parent_size and self.active_toasts:
                # 对于每个位置重新排列
                positions = set()
                for toast in self.active_toasts:
                    if toast.parent() == obj:
                        positions.add(getattr(toast, "position", "top-right"))
                
                for position in positions:
                    self.arrange_toasts(obj, position)
                
                self.last_parent_size = current_size
        
        return super().eventFilter(obj, event)

# 全局提示管理器实例
_toast_manager = None

def get_toast_manager():
    """获取全局提示管理器实例"""
    global _toast_manager
    if _toast_manager is None:
        _toast_manager = ToastManager()
    return _toast_manager

def show_toast(parent, message, toast_type=ElegantToast.INFO, 
              duration=3000, icon=None, position='top-right',
              text_mode=ElegantToast.TEXT_TRUNCATE):
    """
    显示通知提示
    
    参数:
        parent: 父窗口
        message: 消息内容
        toast_type: 提示类型 (info, success, warning, error)
        duration: 显示持续时间（毫秒）
        icon: 自定义图标
        position: 位置 ('top-right', 'top-left', 'bottom-right', 'bottom-left')
        text_mode: 文本显示模式 ('truncate', 'scroll', 'wrap')
        
    返回:
        通知提示对象
    """
    manager = get_toast_manager()
    return manager.show_toast(parent, message, toast_type, duration, icon, position, text_mode)

def show_info(parent, message, duration=3000, icon=None, position='top-right', text_mode=ElegantToast.TEXT_TRUNCATE):
    """显示信息提示"""
    return show_toast(parent, message, ElegantToast.INFO, duration, icon, position, text_mode)

def show_success(parent, message, duration=3000, icon=None, position='top-right', text_mode=ElegantToast.TEXT_TRUNCATE):
    """显示成功提示"""
    return show_toast(parent, message, ElegantToast.SUCCESS, duration, icon, position, text_mode)

def show_warning(parent, message, duration=3000, icon=None, position='top-right', text_mode=ElegantToast.TEXT_TRUNCATE):
    """显示警告提示"""
    return show_toast(parent, message, ElegantToast.WARNING, duration, icon, position, text_mode)

def show_error(parent, message, duration=3000, icon=None, position='top-right', text_mode=ElegantToast.TEXT_TRUNCATE):
    """显示错误提示"""
    return show_toast(parent, message, ElegantToast.ERROR, duration, icon, position, text_mode)

def show_simple_toast(parent, color=QColor(41, 128, 185), duration=2000, 
                     size=QSize(150, 40), position='top-right'):
    """
    显示简单彩色提示
    
    参数:
        parent: 父窗口
        color: 背景颜色
        duration: 显示持续时间（毫秒）
        size: 提示大小
        position: 位置 ('top-right', 'top-left', 'bottom-right', 'bottom-left')
        
    返回:
        SimpleToast对象
    """
    manager = get_toast_manager()
    return manager.show_simple(parent, color, duration, size, position)

# 测试代码
if __name__ == "__main__":
    import random
    
    app = QApplication(sys.argv)
    
    # 主窗口
    main_window = QWidget()
    main_window.setWindowTitle("提示通知测试")
    main_window.resize(800, 600)
    
    # 布局
    layout = QVBoxLayout(main_window)
    
    # 测试按钮
    def create_toast_button(label, toast_type, color, text_mode=ElegantToast.TEXT_TRUNCATE):
        from PyQt5.QtWidgets import QPushButton
        
        button = QPushButton(label)
        button.setMinimumHeight(40)
        button.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold;")
        
        messages = [
            "这是一条简短的通知消息，测试基本功能",
            "这是一条较长的通知消息，用于测试文本处理功能。当文本内容超过提示框宽度时，会根据设置的模式进行处理。",
            "这是一条非常长的通知消息，主要用于测试滚动和换行功能。当用户需要展示大量文本内容时，合理的文本处理方式可以提升用户体验，避免信息丢失。这条消息应该足够长来测试滚动效果了。",
            "操作已完成，所有更改已保存。",
            "连接已建立，服务器响应正常。",
            "文件已成功上传至云端存储，您可以在任何设备上访问。",
        ]
        
        def show_test_toast():
            message = random.choice(messages)
            # 修复：确保在主线程中显示
            show_toast(main_window, message, toast_type, text_mode=text_mode)
        
        button.clicked.connect(show_test_toast)
        return button
    
    # 不同文本模式的测试按钮
    layout.addWidget(QLabel("<b>文本截断模式 (默认):</b>"))
    layout.addWidget(create_toast_button("显示信息提示", ElegantToast.INFO, "#3498db"))
    layout.addWidget(create_toast_button("显示成功提示", ElegantToast.SUCCESS, "#2ecc71"))
    
    layout.addWidget(QLabel("<b>文本滚动模式:</b>"))
    layout.addWidget(create_toast_button("显示警告提示(滚动)", ElegantToast.WARNING, "#f1c40f", ElegantToast.TEXT_SCROLL))
    layout.addWidget(create_toast_button("显示错误提示(滚动)", ElegantToast.ERROR, "#e74c3c", ElegantToast.TEXT_SCROLL))
    
    layout.addWidget(QLabel("<b>文本换行模式:</b>"))
    layout.addWidget(create_toast_button("显示信息提示(换行)", ElegantToast.INFO, "#3498db", ElegantToast.TEXT_WRAP))
    layout.addWidget(create_toast_button("显示成功提示(换行)", ElegantToast.SUCCESS, "#2ecc71", ElegantToast.TEXT_WRAP))
    
    # 简单提示按钮
    from PyQt5.QtWidgets import QPushButton
    
    simple_toast_button = QPushButton("显示简单提示")
    simple_toast_button.setMinimumHeight(40)
    simple_toast_button.setStyleSheet("background-color: #9b59b6; color: white; font-weight: bold;")
    
    # 简单提示的随机颜色
    colors = [
        QColor(41, 128, 185),   # 蓝色
        QColor(39, 174, 96),    # 绿色
        QColor(211, 159, 15),   # 黄色
        QColor(192, 57, 43),    # 红色
        QColor(142, 68, 173),   # 紫色
        QColor(52, 73, 94),     # 深蓝色
    ]
    
    def show_simple_toast_test():
        color = random.choice(colors)
        show_simple_toast(main_window, color)
    
    simple_toast_button.clicked.connect(show_simple_toast_test)
    layout.addWidget(simple_toast_button)
    
    # 关闭所有按钮
    close_all_button = QPushButton("关闭所有提示")
    close_all_button.setMinimumHeight(40)
    close_all_button.setStyleSheet("background-color: #34495e; color: white; font-weight: bold;")
    close_all_button.clicked.connect(get_toast_manager().close_all)
    layout.addWidget(close_all_button)
    
    # 位置下拉框
    from PyQt5.QtWidgets import QComboBox, QLabel, QHBoxLayout
    
    position_layout = QHBoxLayout()
    position_layout.addWidget(QLabel("提示位置:"))
    
    position_combo = QComboBox()
    position_combo.addItems(["top-right", "top-left", "bottom-right", "bottom-left"])
    position_layout.addWidget(position_combo)
    
    layout.addLayout(position_layout)
    
    # 添加弹性空间
    layout.addStretch()
    
    # 显示窗口
    main_window.setLayout(layout)
    main_window.show()
    
    # 显示欢迎提示
    # 修复：不使用线程来避免跨线程问题
    QTimer.singleShot(500, lambda: show_info(
        main_window, 
        "欢迎使用重新设计的提示通知组件。点击按钮测试不同类型和文本处理模式。",
        text_mode=ElegantToast.TEXT_WRAP
    ))
    
    sys.exit(app.exec_()) 