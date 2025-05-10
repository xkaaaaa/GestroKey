import sys
import os
from PyQt6.QtWidgets import (QWidget, QLabel, QApplication, QGraphicsDropShadowEffect,
                             QVBoxLayout, QFrame, QGraphicsOpacityEffect, QPushButton, QHBoxLayout, QCheckBox, QTabWidget, QGridLayout, QGroupBox)
from PyQt6.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, QRect, QRectF, QSize, pyqtProperty, QEvent, QObject, QDateTime
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QFontMetrics, QFont, QCursor

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

class AnimatedToolTip(QWidget):
    """
    美化版悬浮提示组件，具有平滑动画效果和主题样式
    
    可以替代常规的QWidget.setToolTip，提供更丰富的样式和动画效果
    
    支持自定义:
    - 显示延迟时间
    - 显示位置（上、下、左、右）
    - 颜色和样式
    """
    
    # 定义弹出方向常量
    DIRECTION_AUTO = 0   # 自动选择最合适的方向
    DIRECTION_TOP = 1    # 控件上方
    DIRECTION_BOTTOM = 2 # 控件下方
    DIRECTION_LEFT = 3   # 控件左侧
    DIRECTION_RIGHT = 4  # 控件右侧
    
    # 静态字典，保存所有已注册组件的提示信息
    _registered_tooltips = {}  # {widget: (tooltip_instance, text)}
    _global_event_filter_installed = False
    
    # 添加类变量来跟踪所有提示实例
    _all_tooltips = []
    _cleanup_timer = None  # 自动清理定时器
    _current_visible_tooltip = None  # 当前可见的提示（单例模式）
    
    @classmethod
    def hide_all_tooltips(cls):
        """强制隐藏所有提示"""
        for tooltip in cls._all_tooltips:
            if tooltip.is_visible:
                tooltip.hideTooltip(force=True)
        cls._current_visible_tooltip = None
    
    @classmethod
    def setup_auto_cleanup(cls):
        """设置自动清理机制"""
        if cls._cleanup_timer is None:
            app = QApplication.instance()
            cls._cleanup_timer = QTimer(app)
            cls._cleanup_timer.timeout.connect(cls._check_orphaned_tooltips)
            cls._cleanup_timer.start(3000)  # 每3秒检查一次
    
    @classmethod
    def _check_orphaned_tooltips(cls):
        """检查并清理可能滞留的提示"""
        current_time = QApplication.instance().property("_last_mouse_move_time")
        if current_time is None:
            return
            
        # 如果鼠标超过2秒没有移动，检查所有可见的提示
        now = QDateTime.currentMSecsSinceEpoch()
        if now - current_time > 2000:  # 2秒
            visible_tooltips = [t for t in cls._all_tooltips if t.is_visible]
            if visible_tooltips:
                for tooltip in visible_tooltips:
                    tooltip.hideTooltip(force=True)
    
    def __init__(self, parent=None, show_delay=1000, direction=DIRECTION_AUTO, 
                 primary_color=None, text_color=None, border_radius=6, 
                 hide_delay=200, fade_duration=150, min_width=80, max_width=300):
        """
        初始化提示组件
        
        Args:
            parent: 父组件
            show_delay: 显示延迟时间(毫秒)
            direction: 提示弹出方向，可选值:
                DIRECTION_AUTO: 自动选择最合适的方向
                DIRECTION_TOP: 控件上方
                DIRECTION_BOTTOM: 控件下方
                DIRECTION_LEFT: 控件左侧
                DIRECTION_RIGHT: 控件右侧
            primary_color: 主题颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            text_color: 文本颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            border_radius: 边框圆角半径
            hide_delay: 隐藏延迟时间(毫秒)
            fade_duration: 淡入淡出动画持续时间(毫秒)
            min_width: 最小宽度
            max_width: 最大宽度
        """
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        
        # 初始化日志记录器
        self.logger = get_logger("AnimatedToolTip")
        self.logger.debug("初始化悬浮提示组件")
        
        # 初始化属性
        self.target_widget = None  # 目标控件，即悬浮提示所附加的控件
        self.text = ""  # 提示文本
        self.fade_timer = None  # 淡入淡出定时器
        self.hide_timer = None  # 隐藏定时器
        self.show_delay = show_delay  # 显示延迟（毫秒）
        self.hide_delay = hide_delay  # 隐藏延迟（毫秒）
        self.fade_duration = fade_duration  # 淡入淡出动画持续时间（毫秒）
        self.is_visible = False  # 提示是否可见
        self.old_target = None  # 旧的目标控件
        self.direction = direction  # 提示弹出方向
        self.manual_event_mode = False  # 是否使用手动事件跟踪模式
        self.show_time = 0  # 提示显示的时间戳
        
        # 初始化位置检查定时器
        self.position_check_timer = None
        
        # 安装全局事件过滤器（仅安装一次）
        if not AnimatedToolTip._global_event_filter_installed:
            self._installGlobalEventFilter()
            AnimatedToolTip._global_event_filter_installed = True
            
            # 安装全局键盘事件过滤器，用Esc键隐藏所有提示
            app = QApplication.instance()
            app.installEventFilter(KeyPressFilter())
            
            # 设置自动清理机制
            AnimatedToolTip.setup_auto_cleanup()
        
        # 将当前实例添加到类的实例列表中
        AnimatedToolTip._all_tooltips.append(self)
        
        # 样式属性 - 默认使用主题蓝色
        self._primary_color = self._parse_color(primary_color) if primary_color else QColor(52, 152, 219)  # 背景色 - 天蓝色
        self._text_color = self._parse_color(text_color) if text_color else QColor(255, 255, 255)  # 文本色 - 白色
        self.border_radius = border_radius  # 边框圆角半径
        self.padding = 10  # 内边距
        self.min_width = min_width  # 最小宽度
        self.max_width = max_width  # 最大宽度
        self.line_height = 1.5  # 行高系数
        self.shadow_blur = 15  # 阴影模糊半径
        self.shadow_color = QColor(0, 0, 0, 80)  # 阴影颜色
        
        # 计算边框颜色 - 比主题色深一些
        self._border_color = QColor(self._primary_color)
        self._border_color.setRed(max(0, self._primary_color.red() - 20))
        self._border_color.setGreen(max(0, self._primary_color.green() - 20))
        self._border_color.setBlue(max(0, self._primary_color.blue() - 20))
        
        self.font = QFont("Microsoft YaHei", 9)  # 默认字体
        
        # 初始化UI
        self.initUI()
        
        # 设置透明度属性
        self._opacity = 0.0  # 使用内部变量存储透明度值，避免递归
        
        # 设置淡入淡出效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        # 创建淡入淡出动画
        self.fade_animation = QPropertyAnimation(self, b"opacity")
        self.fade_animation.setDuration(self.fade_duration)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 创建位置动画
        self.pos_animation = QPropertyAnimation(self, b"geometry")
        self.pos_animation.setDuration(self.fade_duration)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.logger.debug("悬浮提示组件初始化完成")
    
    def _parse_color(self, color):
        """解析颜色参数，支持RGB列表或十六进制颜色字符串
        
        Args:
            color: RGB列表[r,g,b]或十六进制颜色字符串"#RRGGBB"
            
        Returns:
            QColor: 解析后的QColor对象
        """
        try:
            if isinstance(color, list) and len(color) >= 3:
                # RGB列表
                return QColor(color[0], color[1], color[2])
            elif isinstance(color, str) and color.startswith("#"):
                # 十六进制颜色字符串
                return QColor(color)
            else:
                return None
        except Exception as e:
            self.logger.error(f"解析颜色参数出错: {e}")
            return None
    
    def initUI(self):
        """初始化UI"""
        # 设置窗口属性
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setMouseTracking(True)
        
        # 创建内容标签
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.label.setFont(self.font)
        self.label.setStyleSheet(f"color: rgba({self._text_color.red()}, {self._text_color.green()}, {self._text_color.blue()}, 255);")
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(self.padding, self.padding, self.padding, self.padding)
        layout.addWidget(self.label)
        
        # 添加阴影效果
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(self.shadow_blur)
        self.shadow.setColor(self.shadow_color)
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
        # 隐藏
        self.hide()
    
    def setText(self, text):
        """设置提示文本"""
        self.text = text
        self.label.setText(text)
        self.updateSize()
    
    def setShowDelay(self, delay_ms):
        """
        设置显示延迟时间
        
        Args:
            delay_ms: 延迟毫秒数
        """
        self.show_delay = max(0, delay_ms)
        self.logger.debug(f"设置显示延迟: {self.show_delay}毫秒")
    
    def setHideDelay(self, delay_ms):
        """
        设置隐藏延迟时间
        
        Args:
            delay_ms: 延迟毫秒数
        """
        self.hide_delay = max(0, delay_ms)
        self.logger.debug(f"设置隐藏延迟: {self.hide_delay}毫秒")
    
    def setFadeDuration(self, duration_ms):
        """
        设置淡入淡出动画持续时间
        
        Args:
            duration_ms: 动画持续时间(毫秒)
        """
        self.fade_duration = max(50, duration_ms)  # 最少50毫秒
        self.fade_animation.setDuration(self.fade_duration)
        self.pos_animation.setDuration(self.fade_duration)
        self.logger.debug(f"设置动画持续时间: {self.fade_duration}毫秒")
    
    def setPrimaryColor(self, color):
        """
        设置主题颜色
        
        Args:
            color: RGB列表[r,g,b]或十六进制颜色字符串"#RRGGBB"
        """
        parsed_color = self._parse_color(color)
        if not parsed_color:
            self.logger.warning(f"无效的主题颜色参数: {color}")
            return
            
        self._primary_color = parsed_color
        
        # 更新边框颜色
        self._border_color = QColor(self._primary_color)
        self._border_color.setRed(max(0, self._primary_color.red() - 20))
        self._border_color.setGreen(max(0, self._primary_color.green() - 20))
        self._border_color.setBlue(max(0, self._primary_color.blue() - 20))
        
        self.update()  # 触发重绘
        self.logger.debug(f"设置主题颜色: RGB({self._primary_color.red()}, {self._primary_color.green()}, {self._primary_color.blue()})")
    
    def setTextColor(self, color):
        """
        设置文本颜色
        
        Args:
            color: RGB列表[r,g,b]或十六进制颜色字符串"#RRGGBB"
        """
        parsed_color = self._parse_color(color)
        if not parsed_color:
            self.logger.warning(f"无效的文本颜色参数: {color}")
            return
            
        self._text_color = parsed_color
        self.label.setStyleSheet(f"color: rgba({self._text_color.red()}, {self._text_color.green()}, {self._text_color.blue()}, 255);")
        self.logger.debug(f"设置文本颜色: RGB({self._text_color.red()}, {self._text_color.green()}, {self._text_color.blue()})")
    
    def setBorderRadius(self, radius):
        """
        设置边框圆角半径
        
        Args:
            radius: 圆角半径
        """
        self.border_radius = max(0, radius)
        self.update()  # 触发重绘
        self.logger.debug(f"设置边框圆角: {self.border_radius}px")
    
    def setDirection(self, direction):
        """
        设置提示弹出方向
        
        Args:
            direction: 弹出方向，使用DIRECTION_常量
        """
        if direction in [self.DIRECTION_AUTO, self.DIRECTION_TOP, 
                        self.DIRECTION_BOTTOM, self.DIRECTION_LEFT, 
                        self.DIRECTION_RIGHT]:
            self.direction = direction
            self.logger.debug(f"设置弹出方向: {direction}")
        else:
            self.logger.warning(f"无效的弹出方向: {direction}，使用自动方向")
            self.direction = self.DIRECTION_AUTO
    
    def updateSize(self):
        """根据内容更新提示框大小"""
        # 获取文本度量
        metrics = QFontMetrics(self.font)
        
        # 计算文本宽度（限制在最大宽度以内）
        text_width = min(metrics.horizontalAdvance(self.text), self.max_width - 2 * self.padding)
        
        # 如果文本太长，需要换行并计算高度
        if metrics.horizontalAdvance(self.text) > self.max_width - 2 * self.padding:
            text_rect = metrics.boundingRect(
                0, 0, self.max_width - 2 * self.padding, 1000,
                Qt.TextFlag.TextWordWrap, self.text
            )
            text_height = text_rect.height()
        else:
            text_height = metrics.height()
        
        # 设置大小
        width = max(text_width + 2 * self.padding, self.min_width)
        height = text_height + 2 * self.padding
        self.setFixedSize(width, height)
    
    def _installGlobalEventFilter(self):
        """安装全局事件过滤器，监听鼠标移动并触发相应提示"""
        self.logger.debug("安装全局事件过滤器")
        
        # 创建全局事件过滤器
        class GlobalEventFilter(QObject):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.logger = get_logger("GlobalEventFilter")
                self.current_widget = None
                self.hover_timer = None
                self.leave_timer = None
                self.mouse_moved = False
                self.last_pos = QPoint(0, 0)
                
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.MouseMove:
                    # 记录最后一次鼠标移动的时间
                    app = QApplication.instance()
                    app.setProperty("_last_mouse_move_time", QDateTime.currentMSecsSinceEpoch())
                    
                    # 获取鼠标位置
                    try:
                        pos = event.globalPosition().toPoint()
                    except:
                        # Qt5兼容性
                        pos = event.globalPos()
                    
                    # 检查鼠标是否有实际移动（防止微小抖动触发）
                    if self.last_pos.isNull() or (pos - self.last_pos).manhattanLength() > 3:
                        self.mouse_moved = True
                        self.last_pos = pos
                    else:
                        # 鼠标几乎没有移动，忽略此事件
                        return False
                    
                    # 查找鼠标下的组件
                    widget = QApplication.widgetAt(pos)
                    
                    # 如果找到了组件，并且它有注册提示
                    if widget:
                        # 防止进入死循环：确保widget不是提示本身
                        for tooltip in AnimatedToolTip._all_tooltips:
                            if widget is tooltip or widget.isAncestorOf(tooltip):
                                return False
                        
                        if widget in AnimatedToolTip._registered_tooltips:
                            # 如果鼠标刚刚进入一个新组件
                            if widget != self.current_widget:
                                # 取消先前的定时器
                                if self.hover_timer and self.hover_timer.isActive():
                                    self.hover_timer.stop()
                                if self.leave_timer and self.leave_timer.isActive():
                                    self.leave_timer.stop()
                                
                                # 如果之前有组件，触发其离开事件
                                if self.current_widget and self.current_widget in AnimatedToolTip._registered_tooltips:
                                    tooltip, _ = AnimatedToolTip._registered_tooltips[self.current_widget]
                                    if tooltip.hide_timer:
                                        tooltip.hide_timer.stop()
                                    
                                    # 如果当前有其他提示显示，立即隐藏
                                    if AnimatedToolTip._current_visible_tooltip:
                                        AnimatedToolTip._current_visible_tooltip.hideTooltip(force=True)
                                    
                                    # 创建延迟隐藏定时器
                                    self.leave_timer = QTimer()
                                    self.leave_timer.setSingleShot(True)
                                    self.leave_timer.timeout.connect(lambda: tooltip.hideTooltip())
                                    self.leave_timer.start(tooltip.hide_delay)
                                
                                # 更新当前组件
                                self.current_widget = widget
                                
                                # 获取提示对象和文本
                                tooltip, _ = AnimatedToolTip._registered_tooltips[widget]
                                
                                # 创建延迟显示定时器
                                self.hover_timer = QTimer()
                                self.hover_timer.setSingleShot(True)
                                self.hover_timer.timeout.connect(lambda: tooltip.showTooltip())
                                self.hover_timer.start(tooltip.show_delay)
                                
                                self.logger.debug(f"鼠标进入组件: {widget.__class__.__name__}")
                        else:
                            # 如果鼠标移出到没有提示的组件，隐藏先前的提示
                            if self.current_widget and self.current_widget in AnimatedToolTip._registered_tooltips:
                                tooltip, _ = AnimatedToolTip._registered_tooltips[self.current_widget]
                                
                                # 取消先前的定时器
                                if self.hover_timer and self.hover_timer.isActive():
                                    self.hover_timer.stop()
                                
                                # 创建延迟隐藏定时器
                                self.leave_timer = QTimer()
                                self.leave_timer.setSingleShot(True)
                                self.leave_timer.timeout.connect(lambda: tooltip.hideTooltip())
                                self.leave_timer.start(tooltip.hide_delay)
                                
                                self.logger.debug(f"鼠标离开组件: {self.current_widget.__class__.__name__}")
                                
                                # 清除当前组件引用
                                self.current_widget = None
                    else:
                        # 如果没有找到组件，隐藏先前的提示
                        if self.current_widget and self.current_widget in AnimatedToolTip._registered_tooltips:
                            tooltip, _ = AnimatedToolTip._registered_tooltips[self.current_widget]
                            
                            # 取消先前的定时器
                            if self.hover_timer and self.hover_timer.isActive():
                                self.hover_timer.stop()
                            
                            # 创建延迟隐藏定时器
                            self.leave_timer = QTimer()
                            self.leave_timer.setSingleShot(True)
                            self.leave_timer.timeout.connect(lambda: tooltip.hideTooltip())
                            self.leave_timer.start(tooltip.hide_delay)
                            
                            self.logger.debug("鼠标离开所有注册组件")
                            
                            # 清除当前组件引用
                            self.current_widget = None
                
                # 处理窗口关闭事件
                elif event.type() == QEvent.Type.Close:
                    # 如果某个窗口关闭，隐藏所有提示
                    AnimatedToolTip.hide_all_tooltips()
                    
                # 处理应用程序获取或失去焦点
                elif event.type() == QEvent.Type.ApplicationStateChange:
                    # 如果应用程序失去焦点，隐藏所有提示
                    app_state = QApplication.applicationState()
                    if app_state != Qt.ApplicationState.ApplicationActive:
                        AnimatedToolTip.hide_all_tooltips()
                
                return False  # 继续传递事件
        
        # 安装全局事件过滤器
        app = QApplication.instance()
        event_filter = GlobalEventFilter(app)
        app.installEventFilter(event_filter)
        
        # 保存引用以防止被垃圾回收
        app._tooltip_global_filter = event_filter
    
    def attachTo(self, widget, text):
        """将提示附加到指定控件
        
        Args:
            widget: 目标控件
            text: 提示文本
        """
        if not widget:
            self.logger.warning("尝试附加提示到空控件")
            return
            
        self.logger.debug(f"将提示附加到控件 {widget.__class__.__name__}, 文本: {text}")
        self.target_widget = widget
        self.setText(text)
        
        # 卸载旧的事件过滤器
        if self.old_target and self.old_target != widget:
            self.old_target.removeEventFilter(self)
            # 从注册表中移除旧的关联
            if self.old_target in AnimatedToolTip._registered_tooltips:
                AnimatedToolTip._registered_tooltips.pop(self.old_target)
            self.logger.debug(f"移除旧控件的事件过滤器: {self.old_target.__class__.__name__}")
        
        # 安装事件过滤器
        widget.installEventFilter(self)
        self.old_target = widget
        
        # 对某些特殊组件启用鼠标跟踪
        widget.setMouseTracking(True)
        
        # 在全局字典中注册此组件
        AnimatedToolTip._registered_tooltips[widget] = (self, text)
    
    def showTooltip(self):
        """显示提示"""
        if not self.target_widget or not self.text:
            return
            
        if self.is_visible:
            return
        
        self.logger.debug(f"显示提示: {self.text}")
        
        # 单例模式：先隐藏所有其他提示
        if AnimatedToolTip._current_visible_tooltip and AnimatedToolTip._current_visible_tooltip != self:
            AnimatedToolTip._current_visible_tooltip.hideTooltip(force=True)
        
        # 设置当前提示为唯一可见提示
        AnimatedToolTip._current_visible_tooltip = self
            
        # 设置正确的位置
        self.updatePosition()
        
        # 停止先前的动画
        self.fade_animation.stop()
        self.pos_animation.stop()
        
        # 设置初始位置（根据弹出方向设置起始位置）
        start_pos = self.pos()
        end_rect = QRect(start_pos.x(), start_pos.y(), self.width(), self.height())
        
        # 根据弹出方向确定动画起始位置
        if self.direction == self.DIRECTION_BOTTOM or self.direction == self.DIRECTION_AUTO:
            # 从下方弹出（或自动选择默认方向）
            start_rect = QRect(start_pos.x(), start_pos.y() + 10, self.width(), self.height())
        elif self.direction == self.DIRECTION_TOP:
            # 从上方弹出
            start_rect = QRect(start_pos.x(), start_pos.y() - 10, self.width(), self.height())
        elif self.direction == self.DIRECTION_LEFT:
            # 从左侧弹出
            start_rect = QRect(start_pos.x() - 10, start_pos.y(), self.width(), self.height())
        elif self.direction == self.DIRECTION_RIGHT:
            # 从右侧弹出
            start_rect = QRect(start_pos.x() + 10, start_pos.y(), self.width(), self.height())
        
        # 设置位置动画
        self.pos_animation.setStartValue(start_rect)
        self.pos_animation.setEndValue(end_rect)
        
        # 设置淡入动画
        self.setOpacity(0.0)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        
        # 显示控件并开始动画
        self.show()
        self.fade_animation.start()
        self.pos_animation.start()
        self.is_visible = True
        
        # 记录显示时间
        self.show_time = QDateTime.currentMSecsSinceEpoch()
        
        # 设置自动隐藏定时器（10秒后强制隐藏）
        QTimer.singleShot(10000, lambda: self.check_auto_hide())
        
        # 启动位置检查定时器 - 每100毫秒检查一次鼠标是否在目标组件上
        if self.position_check_timer is None:
            self.position_check_timer = QTimer(self)
            self.position_check_timer.timeout.connect(self.check_mouse_position)
        
        # 停止之前的定时器（如果有）
        if self.position_check_timer.isActive():
            self.position_check_timer.stop()
            
        # 启动定时器
        self.position_check_timer.start(100)  # 100ms检查一次
    
    def check_mouse_position(self):
        """检查鼠标是否在目标组件上"""
        if not self.is_visible or not self.target_widget:
            return
        
        # 获取当前鼠标全局位置
        cursor_pos = QCursor.pos()
        
        # 获取目标组件的全局几何区域
        target_geo = self.target_widget.geometry()
        global_pos = self.target_widget.mapToGlobal(QPoint(0, 0))
        target_rect = QRect(global_pos.x(), global_pos.y(), 
                           target_geo.width(), target_geo.height())
        
        # 检查鼠标是否在组件上
        if not target_rect.contains(cursor_pos):
            self.logger.debug("检测到鼠标不在目标组件上，触发消失动画")
            # 使用普通隐藏（带动画）而不是强制隐藏
            self.hideTooltip(force=False)
            
            # 停止定时器
            if self.position_check_timer and self.position_check_timer.isActive():
                self.position_check_timer.stop()
    
    def check_auto_hide(self):
        """检查是否应该自动隐藏提示"""
        if self.is_visible:
            # 如果提示显示时间超过10秒，强制隐藏
            now = QDateTime.currentMSecsSinceEpoch()
            if now - self.show_time > 9500:  # 稍微提前一点检查，确保10秒后隐藏
                self.hideTooltip(force=True)
    
    def hideTooltip(self, force=False):
        """隐藏提示
        
        Args:
            force: 是否立即强制隐藏，不使用动画
        """
        if not self.is_visible:
            return
        
        self.logger.debug("隐藏提示")
        
        # 停止位置检查定时器
        if self.position_check_timer and self.position_check_timer.isActive():
            self.position_check_timer.stop()
            
        if force:
            # 立即隐藏
            self.hide()
            self.is_visible = False
            # 清除当前可见提示引用
            if AnimatedToolTip._current_visible_tooltip == self:
                AnimatedToolTip._current_visible_tooltip = None
            return
            
        # 停止先前的动画
        self.fade_animation.stop()
        self.pos_animation.stop()
        
        # 设置淡出动画
        self.fade_animation.setStartValue(self.getOpacity())
        self.fade_animation.setEndValue(0.0)
        
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
            
        self.fade_animation.finished.connect(self.hideComplete)
        
        # 设置位置动画
        current_pos = self.pos()
        start_rect = QRect(current_pos.x(), current_pos.y(), self.width(), self.height())
        
        # 根据弹出方向确定动画结束位置
        if self.direction == self.DIRECTION_BOTTOM or self.direction == self.DIRECTION_AUTO:
            # 向下淡出
            end_rect = QRect(current_pos.x(), current_pos.y() + 10, self.width(), self.height())
        elif self.direction == self.DIRECTION_TOP:
            # 向上淡出
            end_rect = QRect(current_pos.x(), current_pos.y() - 10, self.width(), self.height())
        elif self.direction == self.DIRECTION_LEFT:
            # 向左淡出
            end_rect = QRect(current_pos.x() - 10, current_pos.y(), self.width(), self.height())
        elif self.direction == self.DIRECTION_RIGHT:
            # 向右淡出
            end_rect = QRect(current_pos.x() + 10, current_pos.y(), self.width(), self.height())
            
        self.pos_animation.setStartValue(start_rect)
        self.pos_animation.setEndValue(end_rect)
        
        # 开始动画
        self.fade_animation.start()
        self.pos_animation.start()
    
    def hideComplete(self):
        """淡出动画完成后隐藏控件"""
        self.hide()
        self.is_visible = False
        
        # 清除当前可见提示引用
        if AnimatedToolTip._current_visible_tooltip == self:
            AnimatedToolTip._current_visible_tooltip = None
            
        self.logger.debug("提示完全隐藏")
        # 断开信号连接，避免重复调用
        try:
            self.fade_animation.finished.disconnect(self.hideComplete)
        except:
            pass
    
    def updatePosition(self):
        """更新提示框位置"""
        if not self.target_widget:
            return
            
        # 获取目标控件在屏幕上的位置
        target_pos = self.target_widget.mapToGlobal(QPoint(0, 0))
        target_size = self.target_widget.size()
        
        # 获取屏幕大小
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        
        # 根据指定的方向计算提示框位置
        if self.direction == self.DIRECTION_AUTO:
            # 自动选择方向 - 优先顺序：下、上、右、左
            
            # 默认显示在控件下方居中
            x = target_pos.x() + (target_size.width() - self.width()) // 2
            y = target_pos.y() + target_size.height() + 5  # 留出5像素间距
            
            # 调整X坐标，确保不超出屏幕左右边界
            if x < 0:
                x = 0
            elif x + self.width() > screen_geometry.width():
                x = screen_geometry.width() - self.width()
            
            # 如果下方空间不足，则显示在控件上方
            if y + self.height() > screen_geometry.height():
                y = target_pos.y() - self.height() - 5
                
                # 如果上方也没有足够空间，则尝试右侧
                if y < 0:
                    y = target_pos.y() + (target_size.height() - self.height()) // 2
                    x = target_pos.x() + target_size.width() + 5
                    
                    # 如果右侧也没有足够空间，则尝试左侧
                    if x + self.width() > screen_geometry.width():
                        x = target_pos.x() - self.width() - 5
                        
                        # 如果左侧也没有足够空间，则放在右下角并缩小
                        if x < 0:
                            x = screen_geometry.width() - self.width() - 10
                            y = screen_geometry.height() - self.height() - 10
        
        elif self.direction == self.DIRECTION_TOP:
            # 显示在控件上方居中
            x = target_pos.x() + (target_size.width() - self.width()) // 2
            y = target_pos.y() - self.height() - 5
            
            # 调整X坐标，确保不超出屏幕左右边界
            if x < 0:
                x = 0
            elif x + self.width() > screen_geometry.width():
                x = screen_geometry.width() - self.width()
                
            # 如果上方空间不足，则强制在下方显示
            if y < 0:
                y = target_pos.y() + target_size.height() + 5
                
        elif self.direction == self.DIRECTION_BOTTOM:
            # 显示在控件下方居中
            x = target_pos.x() + (target_size.width() - self.width()) // 2
            y = target_pos.y() + target_size.height() + 5
            
            # 调整X坐标，确保不超出屏幕左右边界
            if x < 0:
                x = 0
            elif x + self.width() > screen_geometry.width():
                x = screen_geometry.width() - self.width()
                
            # 如果下方空间不足，则强制在上方显示
            if y + self.height() > screen_geometry.height():
                y = target_pos.y() - self.height() - 5
                
        elif self.direction == self.DIRECTION_LEFT:
            # 显示在控件左侧垂直居中
            x = target_pos.x() - self.width() - 5
            y = target_pos.y() + (target_size.height() - self.height()) // 2
            
            # 调整Y坐标，确保不超出屏幕上下边界
            if y < 0:
                y = 0
            elif y + self.height() > screen_geometry.height():
                y = screen_geometry.height() - self.height()
                
            # 如果左侧空间不足，则强制在右侧显示
            if x < 0:
                x = target_pos.x() + target_size.width() + 5
                
        elif self.direction == self.DIRECTION_RIGHT:
            # 显示在控件右侧垂直居中
            x = target_pos.x() + target_size.width() + 5
            y = target_pos.y() + (target_size.height() - self.height()) // 2
            
            # 调整Y坐标，确保不超出屏幕上下边界
            if y < 0:
                y = 0
            elif y + self.height() > screen_geometry.height():
                y = screen_geometry.height() - self.height()
                
            # 如果右侧空间不足，则强制在左侧显示
            if x + self.width() > screen_geometry.width():
                x = target_pos.x() - self.width() - 5
        
        self.move(x, y)
        self.logger.debug(f"更新提示位置: ({x}, {y}), 方向: {self.direction}")
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于监听目标控件的鼠标事件"""
        if obj != self.target_widget:
            return False
            
        # 监听更多事件类型以提高不同组件的兼容性
        if event.type() == QEvent.Type.Enter or event.type() == QEvent.Type.HoverEnter:
            # 鼠标进入目标控件
            if self.hide_timer:
                self.hide_timer.stop()
            
            if not self.fade_timer:
                self.fade_timer = QTimer(self)
                self.fade_timer.setSingleShot(True)
                self.fade_timer.timeout.connect(self.showTooltip)
            
            self.fade_timer.start(self.show_delay)
            return False
        
        elif event.type() == QEvent.Type.Leave or event.type() == QEvent.Type.HoverLeave:
            # 鼠标离开目标控件
            if self.fade_timer:
                self.fade_timer.stop()
            
            if not self.hide_timer:
                self.hide_timer = QTimer(self)
                self.hide_timer.setSingleShot(True)
                self.hide_timer.timeout.connect(self.hideTooltip)
            
            self.hide_timer.start(self.hide_delay)
            return False
        
        return False
    
    def leaveEvent(self, event):
        """鼠标离开提示框时的事件"""
        # 当鼠标离开提示框后应该隐藏它
        if self.fade_timer:
            self.fade_timer.stop()
        
        if not self.hide_timer:
            self.hide_timer = QTimer(self)
            self.hide_timer.setSingleShot(True)
            self.hide_timer.timeout.connect(self.hideTooltip)
        
        self.hide_timer.start(self.hide_delay)
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """绘制事件，用于绘制自定义外观"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        path = QPainterPath()
        rect = self.rect().adjusted(1, 1, -1, -1)  # 留出1像素边框空间
        # 将 QRect 转换为 QRectF
        rectF = QRectF(rect)
        path.addRoundedRect(rectF, self.border_radius, self.border_radius)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._primary_color)
        painter.drawPath(path)
        
        # 绘制边框
        painter.setPen(QPen(self._border_color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
    
    def getOpacity(self):
        """获取不透明度属性"""
        return self._opacity
    
    def setOpacity(self, opacity):
        """设置不透明度属性"""
        self._opacity = opacity  # 使用内部变量，避免递归
        self.opacity_effect.setOpacity(opacity)
    
    # 定义不透明度属性，用于动画
    opacity = pyqtProperty(float, getOpacity, setOpacity)


def ensure_tooltip_works(widget, tooltip_instance=None):
    """
    确保组件能正确响应提示事件
    
    此函数会对组件进行必要的设置，以确保它能够响应鼠标悬停事件
    
    Args:
        widget: 目标组件
        tooltip_instance: 提示实例（可选）
    """
    logger = get_logger("AnimatedToolTip")
    
    # 确保组件启用鼠标跟踪
    widget.setMouseTracking(True)
    
    # 尝试启用悬停属性
    try:
        widget.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
    except:
        pass
        
    # 对特殊类型的组件进行特殊处理
    widget_type = widget.__class__.__name__
    logger.debug(f"优化组件 {widget_type} 的提示事件响应")
    
    # 检查是否为特殊类型组件
    special_widgets = [
        'QTextEdit', 'QLineEdit', 'QComboBox', 'QSpinBox', 
        'QDateEdit', 'QTimeEdit', 'QDateTimeEdit',
        'QTableWidget', 'QListWidget', 'QTreeWidget',
        'QRadioButton', 'QCheckBox'
    ]
    
    if widget_type in special_widgets:
        # 为特殊组件添加事件过滤器来模拟悬停事件
        class SpecialFilter(QObject):
            def __init__(self, tooltip, parent=None):
                super().__init__(parent)
                self.tooltip = tooltip
                self.widget = parent
                
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.Enter:
                    # 手动触发显示提示
                    if tooltip_instance and hasattr(tooltip_instance, 'target_widget') and tooltip_instance.target_widget == self.widget:
                        QTimer.singleShot(tooltip_instance.show_delay, tooltip_instance.showTooltip)
                elif event.type() == QEvent.Type.Leave:
                    # 手动触发隐藏提示
                    if tooltip_instance and hasattr(tooltip_instance, 'target_widget') and tooltip_instance.target_widget == self.widget:
                        QTimer.singleShot(tooltip_instance.hide_delay, tooltip_instance.hideTooltip)
                return False
        
        # 安装特殊事件过滤器
        if tooltip_instance:
            special_filter = SpecialFilter(tooltip_instance, widget)
            widget.installEventFilter(special_filter)
            # 保存过滤器引用，防止被垃圾回收
            if not hasattr(widget, '_tooltip_filter'):
                widget._tooltip_filter = special_filter


def wrap_widget_with_tooltip(widget, text, tooltip=None, show_delay=1000, direction=AnimatedToolTip.DIRECTION_AUTO, 
                            primary_color=None, text_color=None, border_radius=6):
    """
    为控件添加美化版提示，替代setToolTip
    
    Args:
        widget: 需要添加提示的控件
        text: 提示文本
        tooltip: 可选的AnimatedToolTip实例，如果不提供，会创建新的实例
        show_delay: 显示延迟(毫秒)
        direction: 提示弹出方向，使用AnimatedToolTip.DIRECTION_常量
        primary_color: 主题颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
        text_color: 文本颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
        border_radius: 边框圆角半径
        
    Returns:
        AnimatedToolTip: 创建或使用的提示实例
    """
    logger = get_logger("AnimatedToolTip")
    
    if not tooltip:
        tooltip = AnimatedToolTip(show_delay=show_delay, direction=direction, 
                                 primary_color=primary_color, text_color=text_color, 
                                 border_radius=border_radius)
    else:
        # 如果提供了已有的tooltip实例，更新其参数
        tooltip.setShowDelay(show_delay)
        tooltip.setDirection(direction)
        if primary_color:
            tooltip.setPrimaryColor(primary_color)
        if text_color:
            tooltip.setTextColor(text_color)
        if border_radius != 6:  # 默认值为6
            tooltip.setBorderRadius(border_radius)
    
    logger.debug(f"为控件 {widget.__class__.__name__} 设置提示: {text}")
    tooltip.attachTo(widget, text)
    
    # 确保提示正常工作
    ensure_tooltip_works(widget, tooltip)
    
    return tooltip


# 单例提示对象，可以复用同一个提示实例
_global_tooltip = None

def set_tooltip(widget, text, show_delay=1000, direction=AnimatedToolTip.DIRECTION_AUTO,
               primary_color=None, text_color=None, border_radius=6):
    """
    为控件设置美化版提示，使用全局单例
    
    Args:
        widget: 需要添加提示的控件
        text: 提示文本
        show_delay: 显示延迟(毫秒)
        direction: 提示弹出方向，使用AnimatedToolTip.DIRECTION_常量
        primary_color: 主题颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
        text_color: 文本颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
        border_radius: 边框圆角半径
    """
    global _global_tooltip
    logger = get_logger("AnimatedToolTip")
    
    if not _global_tooltip:
        _global_tooltip = AnimatedToolTip(show_delay=show_delay, direction=direction,
                                         primary_color=primary_color, text_color=text_color,
                                         border_radius=border_radius)
        logger.debug("创建全局提示单例")
    else:
        # 更新单例实例的参数
        _global_tooltip.setShowDelay(show_delay)
        _global_tooltip.setDirection(direction)
        if primary_color:
            _global_tooltip.setPrimaryColor(primary_color)
        if text_color:
            _global_tooltip.setTextColor(text_color)
        if border_radius != 6:  # 默认值为6
            _global_tooltip.setBorderRadius(border_radius)
    
    logger.debug(f"使用全局单例为控件 {widget.__class__.__name__} 设置提示: {text}")
    _global_tooltip.attachTo(widget, text)
    
    # 确保提示正常工作
    ensure_tooltip_works(widget, _global_tooltip)


class TooltipWrapper(QWidget):
    """
    组件包装器类，用于解决特殊组件的工具提示问题
    
    此类将创建一个透明容器，包含目标组件，并将工具提示附加到容器上，
    确保即使是特殊组件也能正常显示工具提示。
    """
    
    def __init__(self, widget, tooltip_text, parent=None, tooltip_opts=None):
        """
        初始化组件包装器
        
        Args:
            widget: 要包装的组件
            tooltip_text: 工具提示文本
            parent: 父窗口
            tooltip_opts: 工具提示选项字典，可包含:
                - primary_color: 主题颜色
                - text_color: 文本颜色
                - direction: 弹出方向
                - show_delay: 显示延迟(毫秒)
                - border_radius: 边框圆角大小
        """
        super().__init__(parent)
        self.target_widget = widget
        self.tooltip_text = tooltip_text
        self.tooltip_opts = tooltip_opts or {}
        
        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(widget)
        
        # 设置属性
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setMouseTracking(True)
        
        # 创建工具提示
        self._create_tooltip()
        
        # 安装事件过滤器以处理鼠标离开
        self.installEventFilter(self)
    
    def _create_tooltip(self):
        """创建并附加工具提示"""
        # 从选项中提取参数
        opts = self.tooltip_opts
        primary_color = opts.get('primary_color')
        text_color = opts.get('text_color')
        direction = opts.get('direction', AnimatedToolTip.DIRECTION_AUTO)
        show_delay = opts.get('show_delay', 300)
        border_radius = opts.get('border_radius', 6)
        
        # 使用wrap_widget_with_tooltip附加工具提示
        self.tooltip = wrap_widget_with_tooltip(
            self, self.tooltip_text,
            primary_color=primary_color,
            text_color=text_color,
            direction=direction,
            show_delay=show_delay,
            border_radius=border_radius
        )
    
    def sizeHint(self):
        """返回建议大小"""
        return self.target_widget.sizeHint()
    
    def minimumSizeHint(self):
        """返回最小建议大小"""
        return self.target_widget.minimumSizeHint()
    
    def resizeEvent(self, event):
        """调整大小时保持目标组件填满"""
        super().resizeEvent(event)
        self.target_widget.resize(self.size())

    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获鼠标离开事件"""
        if obj == self:
            if event.type() == QEvent.Type.Leave:
                # 触发消失动画（不强制）
                if hasattr(self, 'tooltip') and self.tooltip:
                    self.tooltip.hideTooltip(force=False)
            # 添加鼠标移动事件处理
            elif event.type() == QEvent.Type.MouseMove:
                # 检查鼠标是否在自身区域内
                pos = event.pos()
                if not self.rect().contains(pos):
                    # 如果鼠标不在区域内，触发消失动画（不强制）
                    if hasattr(self, 'tooltip') and self.tooltip:
                        self.tooltip.hideTooltip(force=False)
                
        return super().eventFilter(obj, event)


def create_tooltip_for_special_widget(widget, text, **tooltip_opts):
    """
    为特殊组件创建工具提示，通过包装器实现
    
    Args:
        widget: 目标组件
        text: 工具提示文本
        **tooltip_opts: 工具提示选项，可包含primary_color、direction等
    
    Returns:
        TooltipWrapper: 包含目标组件并带有工具提示的包装器
    """
    # 创建包装器
    wrapper = TooltipWrapper(widget, text, tooltip_opts=tooltip_opts)
    
    # 返回包装器，可以在需要时替换原组件
    return wrapper


# 键盘事件过滤器，用于捕获Esc键并隐藏所有提示
class KeyPressFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                # 按下Esc键时隐藏所有提示
                AnimatedToolTip.hide_all_tooltips()
                return True  # 事件已处理
        return False  # 继续传递事件


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 初始化日志记录器
    logger = get_logger("AnimatedToolTip_Test")
    logger.info("开始测试悬浮提示组件")
    
    # 创建一个测试窗口
    window = QWidget()
    window.setWindowTitle("AnimatedToolTip 测试")
    window.setGeometry(100, 100, 800, 600)
    main_layout = QVBoxLayout(window)
    
    # 添加一个标题
    title_label = QLabel("悬浮提示测试 - 将鼠标悬停在各种组件上")
    title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(title_label)
    
    # 创建一个选项卡式布局，分组不同类型的测试
    tab_widget = QTabWidget()
    
    # === 标准组件测试选项卡 ===
    standard_tab = QWidget()
    layout = QVBoxLayout(standard_tab)
    
    # 创建表格布局
    grid = QGridLayout()
    grid.setColumnStretch(0, 1)  # 组件列
    grid.setColumnStretch(1, 4)  # 描述列
    
    # 定义行计数器变量为全局变量
    row = 0
    
    # 添加一个函数用于添加测试组件
    def add_test_component(widget, name, description):
        global row  # 使用global关键字而非nonlocal
        label = QLabel(name + ":")
        label.setStyleSheet("font-weight: bold;")
        
        # 组件标签添加到第一列
        grid.addWidget(label, row, 0, Qt.AlignmentFlag.AlignRight)
        
        # 调整组件宽度
        if hasattr(widget, 'setMinimumWidth'):
            widget.setMinimumWidth(200)
        
        # 组件添加到第二列
        grid.addWidget(widget, row, 1)
        
        # 描述添加到第三列
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        grid.addWidget(desc_label, row, 2)
        
        row += 1
        return widget
    
    # 添加测试组件
    button = add_test_component(
        QPushButton("测试按钮"), 
        "按钮", 
        "QPushButton - 标准点击按钮，最常用的交互组件"
    )
    
    label = add_test_component(
        QLabel("这是一个标签"), 
        "标签", 
        "QLabel - 用于显示文本的静态组件"
    )
    label.setFrameShape(QFrame.Shape.Box)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    checkbox_widget = QCheckBox("勾选我")
    checkbox = add_test_component(
        create_tooltip_for_special_widget(
            checkbox_widget, 
            "勾选后将启用某功能，未勾选则禁用", 
            primary_color=[231, 76, 60]
        ),
        "复选框", 
        "QCheckBox - 可供用户选择或取消选择的选项"
    )
    
    from PyQt6.QtWidgets import QLineEdit
    text_input = add_test_component(
        QLineEdit(), 
        "文本框", 
        "QLineEdit - 单行文本输入组件"
    )
    text_input.setPlaceholderText("在此输入文本...")
    
    from PyQt6.QtWidgets import QRadioButton
    radio1 = add_test_component(
        QRadioButton("选项1"), 
        "单选按钮", 
        "QRadioButton - 在一组选项中只能选择一个"
    )
    
    from PyQt6.QtWidgets import QComboBox
    combobox_widget = QComboBox()
    combobox_widget.addItems(["选项1", "选项2", "选项3", "选项4"])
    combobox = add_test_component(
        create_tooltip_for_special_widget(
            combobox_widget, 
            "从下拉列表中选择一个选项", 
            primary_color=[155, 89, 182]
        ),
        "下拉菜单", 
        "QComboBox - 提供多个选项的下拉列表"
    )
    
    from PyQt6.QtWidgets import QSlider
    slider = add_test_component(
        QSlider(Qt.Orientation.Horizontal), 
        "滑块", 
        "QSlider - 使用滑动方式调整数值的组件"
    )
    slider.setMinimum(0)
    slider.setMaximum(100)
    slider.setValue(50)
    
    from PyQt6.QtWidgets import QSpinBox
    spinbox_widget = QSpinBox()
    spinbox_widget.setRange(0, 100)
    spinbox_widget.setValue(50)
    spinbox = add_test_component(
        create_tooltip_for_special_widget(
            spinbox_widget, 
            "通过上下箭头或直接输入调整数值", 
            primary_color=[52, 73, 94]
        ),
        "数字调节器", 
        "QSpinBox - 通过增减按钮或直接输入调整数值"
    )
    
    from PyQt6.QtWidgets import QProgressBar
    progress_widget = QProgressBar()
    progress_widget.setRange(0, 100)
    progress_widget.setValue(70)
    progress = add_test_component(
        create_tooltip_for_special_widget(
            progress_widget, 
            "这是一个进度条，显示操作完成的百分比", 
            primary_color=[41, 128, 185]
        ),
        "进度条", 
        "QProgressBar - 显示操作进度的组件"
    )
    
    from PyQt6.QtWidgets import QDateEdit
    from PyQt6.QtCore import QDate
    date_edit = add_test_component(
        QDateEdit(), 
        "日期编辑器", 
        "QDateEdit - 用于选择日期的组件"
    )
    date_edit.setDate(QDate.currentDate())
    
    from PyQt6.QtWidgets import QLCDNumber
    lcd_widget = QLCDNumber()
    lcd_widget.display(12345)
    lcd = add_test_component(
        create_tooltip_for_special_widget(
            lcd_widget, 
            "LCD数字显示器，目前显示数值12345", 
            primary_color=[231, 76, 60]
        ),
        "LCD显示器", 
        "QLCDNumber - 以LCD样式显示数字的组件"
    )
    
    from PyQt6.QtWidgets import QTextEdit
    text_edit = add_test_component(
        QTextEdit(), 
        "文本编辑器", 
        "QTextEdit - 多行文本编辑组件"
    )
    text_edit.setPlaceholderText("这是一个多行文本编辑器")
    text_edit.setMaximumHeight(80)
    
    from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
    table = QTableWidget(3, 3)
    for row_idx in range(3):
        for col_idx in range(3):
            table.setItem(row_idx, col_idx, QTableWidgetItem(f"单元格 {row_idx+1},{col_idx+1}"))
    table.setMaximumHeight(120)
    add_test_component(
        table, 
        "表格", 
        "QTableWidget - 显示行列数据的表格组件"
    )
    
    # 将网格布局添加到主布局
    layout.addLayout(grid)
    
    # === 为标准组件设置提示 ===
    wrap_widget_with_tooltip(button, "这是一个按钮的提示，用于用户点击执行操作", primary_color=[52, 152, 219])
    wrap_widget_with_tooltip(label, "这是一个标签组件，用于展示静态文本", primary_color=[46, 204, 113], direction=AnimatedToolTip.DIRECTION_BOTTOM)
    wrap_widget_with_tooltip(text_input, "请在此输入您要搜索的内容", direction=AnimatedToolTip.DIRECTION_TOP)
    wrap_widget_with_tooltip(radio1, "第一个选项的详细说明", show_delay=200)
    wrap_widget_with_tooltip(slider, "通过滑动调整数值，范围为0-100", direction=AnimatedToolTip.DIRECTION_TOP, primary_color=[243, 156, 18])
    wrap_widget_with_tooltip(date_edit, "选择或输入日期", primary_color=[155, 89, 182])
    wrap_widget_with_tooltip(text_edit, "用于输入和编辑多行文本", primary_color=[46, 204, 113])
    set_tooltip(table, "这是一个表格，显示行列数据", primary_color=[52, 152, 219])
    
    # === 添加特殊示例 ===
    example_group = QGroupBox("特殊组件测试")
    example_layout = QVBoxLayout(example_group)
    
    example_label = QLabel("下面的组件使用高级包装器处理工具提示:")
    example_layout.addWidget(example_label)
    
    # 添加复选框示例
    checkbox_example = QCheckBox("复选框示例")
    checkbox_wrapper = create_tooltip_for_special_widget(
        checkbox_example, 
        "这是使用包装器的复选框提示", 
        primary_color=[231, 76, 60]
    )
    example_layout.addWidget(checkbox_wrapper)
    
    # 添加下拉菜单示例
    combo_example = QComboBox()
    combo_example.addItems(["选项A", "选项B", "选项C"])
    combo_wrapper = create_tooltip_for_special_widget(
        combo_example, 
        "这是使用包装器的下拉菜单提示", 
        primary_color=[155, 89, 182]
    )
    example_layout.addWidget(combo_wrapper)
    
    layout.addWidget(example_group)
    
    # === 添加选项卡到主窗口 ===
    tab_widget.addTab(standard_tab, "组件测试")
    main_layout.addWidget(tab_widget)
    
    # 增加交互性说明
    info_label = QLabel("说明：将鼠标悬停在任何组件上即可测试提示效果。特殊组件使用包装器实现悬浮提示。按ESC键可强制关闭所有提示。")
    info_label.setStyleSheet("color: #555; margin-top: 10px; margin-bottom: 10px;")
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(info_label)
    
    # 添加帮助信息
    help_frame = QFrame()
    help_frame.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
    help_frame.setStyleSheet("background-color: #f8f9fa; padding: 10px;")
    help_layout = QVBoxLayout(help_frame)
    
    help_title = QLabel("使用方法")
    help_title.setStyleSheet("font-weight: bold; font-size: 14px;")
    help_layout.addWidget(help_title)
    
    help_text = """
    1. 标准组件提示:
       - wrap_widget_with_tooltip(widget, "提示文本") - 创建新提示实例
       - set_tooltip(widget, "提示文本") - 使用全局提示实例
    
    2. 特殊组件提示:
       - 对于复选框、下拉菜单等特殊组件，使用包装器方法:
       - wrapper = create_tooltip_for_special_widget(widget, "提示文本")
       - 然后使用wrapper替代原组件
    
    3. 自定义选项:
       - 主题颜色 primary_color=[r,g,b] 或 "#RRGGBB"
       - 文本颜色 text_color=[r,g,b] 或 "#RRGGBB"
       - 弹出方向 direction=AnimatedToolTip.DIRECTION_XXX
       - 显示延迟 show_delay=毫秒数
       
    4. 快捷键:
       - ESC: 隐藏所有显示的提示
    """
    help_content = QLabel(help_text)
    help_content.setWordWrap(True)
    help_layout.addWidget(help_content)
    
    main_layout.addWidget(help_frame)
    
    logger.info("显示测试窗口")
    window.show()
    
    exit_code = app.exec()
    logger.info(f"测试结束，退出码: {exit_code}")
    sys.exit(exit_code)