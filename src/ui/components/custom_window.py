import sys
import math
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGraphicsDropShadowEffect, QGridLayout,
                            QSizePolicy, QFrame)
from PyQt6.QtCore import (Qt, QPoint, QRect, QPropertyAnimation, QEasingCurve, 
                         pyqtSignal, QSize, QTimer, QParallelAnimationGroup, QSequentialAnimationGroup,
                         QPoint, QEvent, QRectF, QPointF)
from PyQt6.QtGui import (QColor, QPainter, QPen, QPainterPath, QBrush, QIcon, 
                        QGradient, QLinearGradient, QRadialGradient, QPixmap,
                        QFont, QFontMetrics, QCursor)

# 导入日志模块
try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

class WindowTitleBar(QWidget):
    """自定义窗口标题栏组件"""
    
    # 定义信号
    minimizeClicked = pyqtSignal()
    maximizeClicked = pyqtSignal()
    closeClicked = pyqtSignal()
    
    def __init__(self, parent=None, title="窗口", show_min=True, show_max=True, show_close=True):
        super().__init__(parent)
        
        # 初始化日志
        self.logger = get_logger("WindowTitleBar")
        self.logger.debug(f"初始化标题栏: {title}")
        
        # 初始化变量
        self.title = title
        self.pressed = False
        self.start_pos = None
        self.icon_size = 16
        self.title_color = QColor(50, 50, 50)
        self.background_color = QColor(245, 245, 248)
        
        # 按钮状态跟踪
        self.hover_min_btn = False
        self.hover_max_btn = False
        self.hover_close_btn = False
        self.pressed_min_btn = False
        self.pressed_max_btn = False
        self.pressed_close_btn = False
        
        # 拖拽相关变量
        self.drag_position = None      # 拖拽开始时鼠标在标题栏的位置
        self.drag_ratio = 0.0          # 拖拽位置在窗口宽度上的比例
        self.restore_dragging = False  # 是否正在从最大化状态拖拽还原
        self.restore_timer = None      # 用于延迟处理拖拽还原后的移动
        
        # 添加图标支持
        self.window_icon = None
        self.show_icon = False
        
        # 设置固定高度
        self.setFixedHeight(40)
        
        # 添加圆角属性
        self.border_radius = 0
        
        # 初始化界面
        self.initUI(show_min, show_max, show_close)
        
        self.logger.debug("标题栏初始化完成")
    
    def initUI(self, show_min, show_max, show_close):
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 10, 0)
        layout.setSpacing(8)
        
        # 创建标题标签
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(
            f"""
            color: {self.title_color.name()};
            font-size: 13px;
            font-weight: 500;
            padding-left: 4px;
            """
        )
        
        # 窗口图标
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setVisible(self.show_icon)
        
        # 添加标题到布局（靠左）
        layout.addWidget(self.icon_label)
        layout.addWidget(self.title_label)
        layout.addStretch()
        
        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)
        
        if show_min:
            self.min_button = QPushButton()
            self.min_button.setFixedSize(40, 40)
            self.min_button.setStyleSheet("background: transparent; border: none;")
            self.min_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.min_button.clicked.connect(self.minimizeClicked.emit)
            self.min_button.installEventFilter(self)
            button_layout.addWidget(self.min_button)
            
        if show_max:
            self.max_button = QPushButton()
            self.max_button.setFixedSize(40, 40)
            self.max_button.setStyleSheet("background: transparent; border: none;")
            self.max_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.max_button.clicked.connect(self.maximizeClicked.emit)
            self.max_button.installEventFilter(self)
            button_layout.addWidget(self.max_button)
            
        if show_close:
            self.close_button = QPushButton()
            self.close_button.setFixedSize(40, 40)
            self.close_button.setStyleSheet("background: transparent; border: none;")
            self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.close_button.clicked.connect(self.closeClicked.emit)
            self.close_button.installEventFilter(self)
            button_layout.addWidget(self.close_button)
            
        layout.addLayout(button_layout)
        
        # 设置布局
        self.setLayout(layout)
    
    def eventFilter(self, obj, event):
        """处理按钮的鼠标事件"""
        # 最小化按钮
        if hasattr(self, 'min_button') and obj == self.min_button:
            if event.type() == QEvent.Type.Enter:
                self.hover_min_btn = True
                self.update()
            elif event.type() == QEvent.Type.Leave:
                self.hover_min_btn = False
                self.pressed_min_btn = False
                self.update()
            elif event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.pressed_min_btn = True
                self.update()
            elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                self.pressed_min_btn = False
                self.update()
                
        # 最大化按钮
        if hasattr(self, 'max_button') and obj == self.max_button:
            if event.type() == QEvent.Type.Enter:
                self.hover_max_btn = True
                self.update()
            elif event.type() == QEvent.Type.Leave:
                self.hover_max_btn = False
                self.pressed_max_btn = False
                self.update()
            elif event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.pressed_max_btn = True
                self.update()
            elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                self.pressed_max_btn = False
                self.update()
                
        # 关闭按钮
        if hasattr(self, 'close_button') and obj == self.close_button:
            if event.type() == QEvent.Type.Enter:
                self.hover_close_btn = True
                self.update()
            elif event.type() == QEvent.Type.Leave:
                self.hover_close_btn = False
                self.pressed_close_btn = False
                self.update()
            elif event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self.pressed_close_btn = True
                self.update()
            elif event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
                self.pressed_close_btn = False
                self.update()
                
        return super().eventFilter(obj, event)
        
    def set_title(self, title):
        self.title = title
        self.title_label.setText(title)
        self.logger.debug(f"设置标题: {title}")
    
    def set_icon(self, icon_path=None, icon=None):
        """设置窗口图标"""
        self.logger.debug(f"设置窗口图标: {icon_path if icon_path else '使用传入的图标'}")
        if icon_path:
            self.window_icon = QPixmap(icon_path).scaled(
                16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
        elif icon:
            if isinstance(icon, QIcon):
                self.window_icon = icon.pixmap(16, 16)
            else:
                self.window_icon = icon
        
        if self.window_icon:
            self.icon_label.setPixmap(self.window_icon)
            self.show_icon = True
            self.icon_label.setVisible(True)
    
    def set_title_color(self, color):
        """设置标题颜色"""
        self.logger.debug(f"设置标题颜色: {color}")
        if isinstance(color, list) and len(color) >= 3:
            self.title_color = QColor(color[0], color[1], color[2])
        elif isinstance(color, str):
            self.title_color = QColor(color)
        else:
            self.title_color = color
        
        self.title_label.setStyleSheet(
            f"""
            color: {self.title_color.name()};
            font-size: 13px;
            font-weight: 500;
            padding-left: 4px;
            """
        )
    
    def set_background_color(self, color):
        """设置背景颜色"""
        self.logger.debug(f"设置背景颜色: {color}")
        if isinstance(color, list) and len(color) >= 3:
            self.background_color = QColor(color[0], color[1], color[2])
        elif isinstance(color, str):
            self.background_color = QColor(color)
        else:
            self.background_color = color
        self.update()
    
    def set_border_radius(self, radius):
        """设置边框圆角半径"""
        self.logger.debug(f"设置标题栏圆角: {radius}")
        self.border_radius = radius
        self.update()
    
    def paintEvent(self, event):
        """绘制标题栏"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 创建路径并添加圆角矩形(只在顶部添加圆角)
        path = QPainterPath()
        rect = self.rect()
        
        # 使用标题栏自己的圆角值，稍微增加一点以保持视觉一致性
        radius = int(self.border_radius * 1.2)  # 增加20%的圆角半径使视觉效果更一致
        
        # 判断是否是最大化状态
        is_maximized = False
        if self.window():
            is_maximized = self.window().isMaximized()
        
        # 如果最大化，不使用圆角
        if is_maximized or radius == 0:
            # 将QRect转换为QRectF
            path.addRect(QRectF(rect))
        else:
            # 创建一个圆角矩形路径(只有顶部有圆角)
            # 将所有QPoint转换为QPointF
            path.moveTo(QPointF(rect.bottomLeft()))
            path.lineTo(QPointF(rect.bottomRight()))
            path.lineTo(QPointF(rect.right(), rect.top() + radius))
            path.arcTo(rect.right() - radius, rect.top(), radius, radius, 0, 90)
            path.lineTo(QPointF(rect.left() + radius, rect.top()))
            path.arcTo(rect.left(), rect.top(), radius, radius, 90, 90)
            path.lineTo(QPointF(rect.left(), rect.bottom()))
            path.closeSubpath()
        
        # 使用填充路径绘制背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.background_color)
        painter.drawPath(path)
        
        # 绘制最小化按钮
        if hasattr(self, 'min_button'):
            min_rect = self.min_button.geometry()
            center_x = min_rect.x() + min_rect.width() // 2
            center_y = min_rect.y() + min_rect.height() // 2
            
            # 绘制按钮背景（如果悬停）
            if self.hover_min_btn:
                # 悬停状态设置背景色
                hover_color = QColor(240, 240, 240)
                if self.pressed_min_btn:
                    # 按下状态设置更深的背景色
                    hover_color = QColor(230, 230, 230)
                
                painter.setBrush(hover_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPoint(center_x, center_y), 16, 16)
            
            # 绘制最小化图标
            icon_color = QColor(100, 100, 100)
            if self.pressed_min_btn:
                icon_color = QColor(80, 80, 80)
                
            painter.setPen(QPen(icon_color, 1.2))
            # 绘制横线表示最小化
            painter.drawLine(center_x - 6, center_y, center_x + 6, center_y)
        
        # 绘制最大化按钮
        if hasattr(self, 'max_button'):
            max_rect = self.max_button.geometry()
            center_x = max_rect.x() + max_rect.width() // 2
            center_y = max_rect.y() + max_rect.height() // 2
            
            # 绘制按钮背景（如果悬停）
            if self.hover_max_btn:
                # 悬停状态设置背景色
                hover_color = QColor(240, 240, 240)
                if self.pressed_max_btn:
                    # 按下状态设置更深的背景色
                    hover_color = QColor(230, 230, 230)
                
                painter.setBrush(hover_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPoint(center_x, center_y), 16, 16)
            
            # 绘制图标颜色
            icon_color = QColor(100, 100, 100)
            if self.pressed_max_btn:
                icon_color = QColor(80, 80, 80)
                
            painter.setPen(QPen(icon_color, 1.2))
            # 绘制方形表示最大化
            if self.window().isMaximized():
                # 绘制重叠的两个小矩形表示恢复
                painter.drawRect(center_x - 5, center_y - 3, 8, 8)
                painter.drawRect(center_x - 3, center_y - 5, 8, 8)
                painter.drawLine(center_x - 3, center_y - 5, center_x + 5, center_y - 5)
                painter.drawLine(center_x + 5, center_y - 5, center_x + 5, center_y + 3)
            else:
                # 绘制单个矩形表示最大化
                painter.drawRect(center_x - 6, center_y - 6, 12, 12)
        
        # 绘制关闭按钮
        if hasattr(self, 'close_button'):
            close_rect = self.close_button.geometry()
            center_x = close_rect.x() + close_rect.width() // 2
            center_y = close_rect.y() + close_rect.height() // 2
            
            # 绘制按钮背景（如果悬停）
            if self.hover_close_btn:
                # 关闭按钮悬停颜色是红色
                hover_color = QColor(232, 17, 35)
                if self.pressed_close_btn:
                    # 按下状态设置更深的红色
                    hover_color = QColor(200, 10, 25)
                
                # 设置一定的透明度
                hover_color.setAlpha(self.pressed_close_btn and 220 or 180)
                painter.setBrush(hover_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPoint(center_x, center_y), 16, 16)
                
                # 设置图标颜色为白色
                icon_color = QColor(255, 255, 255)
            else:
                # 正常状态下图标颜色为灰色
                icon_color = QColor(100, 100, 100)
            
            # 绘制X表示关闭
            painter.setPen(QPen(icon_color, 1.5))
            painter.drawLine(center_x - 6, center_y - 6, center_x + 6, center_y + 6)
            painter.drawLine(center_x - 6, center_y + 6, center_x + 6, center_y - 6)
    
    def mousePressEvent(self, event):
        """鼠标按下事件，用于拖动窗口"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressed = True
            self.start_pos = event.pos()
            
            # 如果窗口是最大化状态，记录鼠标位置在窗口宽度上的比例
            if self.window().isMaximized():
                window_width = self.width()
                self.drag_position = event.pos()
                self.drag_ratio = self.drag_position.x() / window_width if window_width > 0 else 0.5
                self.logger.debug(f"记录拖拽比例: {self.drag_ratio:.2f}")
            else:
                self.drag_position = None
                self.drag_ratio = 0.0
                self.restore_dragging = False
                
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.pressed = False
        self.restore_dragging = False
        self.drag_position = None
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件，实现窗口拖动"""
        if self.pressed:
            # 处理从最大化状态拖拽还原的情况
            if self.window().isMaximized():
                # 当鼠标移动足够距离时，触发还原
                if not self.restore_dragging and abs(event.pos().y() - self.drag_position.y()) > 5:
                    self.restore_dragging = True
                    self.logger.debug("检测到从最大化状态拖拽，准备还原窗口")
                    
                    # 获取屏幕几何信息
                    screen = QApplication.primaryScreen()
                    screen_geometry = screen.availableGeometry()
                    
                    # 设置标志表示这是通过拖拽还原
                    if hasattr(self.window(), 'set_drag_restoring'):
                        self.window().set_drag_restoring(True)
                    
                    # 先恢复窗口到非最大化状态
                    self.maximizeClicked.emit()  # 触发窗口还原
                    
                    # 临时禁用鼠标移动处理，以避免奇怪的跳跃
                    self.setEnabled(False)
                    
                    # 使用计时器延迟执行窗口定位，确保窗口已经完全还原
                    # 这是关键步骤，避免窗口还原过程中就开始移动导致错位
                    QTimer.singleShot(50, lambda: self._position_restored_window(event.globalPosition().toPoint()))
                    
                    return
                elif self.restore_dragging:
                    # 如果正在处理还原过程，忽略后续移动事件直到窗口定位完成
                    return
            elif not self.restore_dragging:
                # 正常的窗口拖动
                self.window().move(
                    self.window().pos() + (event.pos() - self.start_pos)
                )
        
        return super().mouseMoveEvent(event)
    
    def _position_restored_window(self, global_pos):
        """定位已还原的窗口，使拖拽点在窗口上的位置保持不变"""
        try:
            if not self.window() or not hasattr(self, 'drag_ratio'):
                return
                
            # 重新启用鼠标事件处理
            self.setEnabled(True)
            
            # 获取当前窗口几何信息
            window_geometry = self.window().geometry()
            window_width = window_geometry.width()
            
            # 计算鼠标在还原后窗口上应该对应的X坐标
            drag_x_in_window = int(window_width * self.drag_ratio)
            
            # 计算新的窗口左上角位置，使鼠标指针正好位于原来拖拽的相对位置
            new_left = global_pos.x() - drag_x_in_window
            
            # 移动窗口到新位置
            self.window().move(new_left, global_pos.y() - self.drag_position.y())
            
            # 更新开始拖拽位置，以便后续的拖拽操作正常进行
            self.start_pos = QPoint(drag_x_in_window, self.drag_position.y())
            self.logger.debug(f"窗口已定位，拖拽可以继续")
            
            # 重置还原拖拽状态
            self.restore_dragging = False
            
        except Exception as e:
            self.logger.error(f"定位还原窗口时出错: {str(e)}")
            self.restore_dragging = False
    
    def mouseDoubleClickEvent(self, event):
        """双击事件，实现最大化/还原窗口"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 判断点击位置是否在标题区域
            in_button_area = False
            
            # 检查是否点击在按钮上
            if hasattr(self, 'min_button') and self.min_button.geometry().contains(event.pos()):
                in_button_area = True
            elif hasattr(self, 'max_button') and self.max_button.geometry().contains(event.pos()):
                in_button_area = True
            elif hasattr(self, 'close_button') and self.close_button.geometry().contains(event.pos()):
                in_button_area = True
            
            # 只有当点击不在按钮区域时才处理双击
            if not in_button_area:
                self.logger.debug("检测到标题栏双击，触发最大化/还原")
                self.maximizeClicked.emit()
                
        return super().mouseDoubleClickEvent(event)
    
    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().enterEvent(event)

class ResizeHandle(QWidget):
    """窗口调整大小的句柄控件"""
    
    def __init__(self, parent, direction):
        super().__init__(parent)
        
        # 设置日志记录器
        self.logger = get_logger("ResizeHandle")
        self.logger.debug(f"初始化调整大小句柄: {direction}")
        
        # 设置方向，支持8个方向
        self.direction = direction
        
        # 设置固定大小
        self.handle_size = 8
        
        # 设置鼠标样式和属性
        self.normal_cursor = self._get_cursor_shape()
        self.setCursor(self.normal_cursor)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 初始化事件跟踪变量
        self.is_pressed = False
        self.start_pos = None
        self.start_geometry = None
    
    def _get_cursor_shape(self):
        """根据方向设置鼠标样式"""
        if self.direction in ["top-left", "bottom-right"]:
            return Qt.CursorShape.SizeFDiagCursor
        elif self.direction in ["top-right", "bottom-left"]:
            return Qt.CursorShape.SizeBDiagCursor
        elif self.direction in ["left", "right"]:
            return Qt.CursorShape.SizeHorCursor
        elif self.direction in ["top", "bottom"]:
            return Qt.CursorShape.SizeVerCursor
        else:
            return Qt.CursorShape.ArrowCursor
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        # 如果窗口最大化，不改变鼠标样式
        if self.window() and self.window().isMaximized():
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(self.normal_cursor)
        return super().enterEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 如果窗口最大化，不执行任何操作
        if self.window() and self.window().isMaximized():
            return super().mousePressEvent(event)
            
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = True
            self.start_pos = event.globalPosition().toPoint()
            self.start_geometry = self.window().geometry()
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.is_pressed = False
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动以调整窗口大小"""
        # 如果窗口最大化或未按下鼠标，不执行任何操作
        if not self.is_pressed or (self.window() and self.window().isMaximized()):
            return super().mouseMoveEvent(event)
        
        # 获取当前位置和偏移量
        current_pos = event.globalPosition().toPoint()
        delta = current_pos - self.start_pos
        
        # 获取屏幕限制
        screen_geometry = QApplication.primaryScreen().geometry()
        min_width = self.window().minimumWidth()
        min_height = self.window().minimumHeight()
        
        # 创建新的几何形状
        new_geo = QRect(self.start_geometry)
        
        # 根据方向调整窗口大小
        if "left" in self.direction:
            # 向左拖动时调整左边界和宽度
            left = self.start_geometry.left() + delta.x()
            width = self.start_geometry.width() - delta.x()
            
            if width >= min_width:
                new_geo.setLeft(left)
            else:
                # 如果宽度小于最小宽度，设置左边界使宽度等于最小宽度
                new_geo.setLeft(self.start_geometry.right() - min_width)
            
        if "right" in self.direction:
            # 向右拖动时调整宽度
            width = self.start_geometry.width() + delta.x()
            if width >= min_width:
                new_geo.setWidth(width)
            else:
                # 如果宽度小于最小宽度，设置宽度为最小宽度
                new_geo.setWidth(min_width)
            
        if "top" in self.direction:
            # 向上拖动时调整顶部边界和高度
            top = self.start_geometry.top() + delta.y()
            height = self.start_geometry.height() - delta.y()
            
            if height >= min_height:
                new_geo.setTop(top)
            else:
                # 如果高度小于最小高度，设置顶边界使高度等于最小高度
                new_geo.setTop(self.start_geometry.bottom() - min_height)
            
        if "bottom" in self.direction:
            # 向下拖动时调整高度
            height = self.start_geometry.height() + delta.y()
            if height >= min_height:
                new_geo.setHeight(height)
            else:
                # 如果高度小于最小高度，设置高度为最小高度
                new_geo.setHeight(min_height)
        
        # 应用新的几何形状
        self.window().setGeometry(new_geo)
        
        return super().mouseMoveEvent(event)

class CustomBorderlessWindow(QWidget):
    """无边框自定义窗口组件，带阴影和圆角效果"""
    
    def __init__(self, parent=None, title="自定义窗口", shadow_radius=15, 
                 border_radius=10, border_color=None, border_width=1, 
                 content_margin=2, theme_color=None):
        super().__init__(parent)
        
        # 初始化日志
        self.logger = get_logger("CustomBorderlessWindow")
        self.logger.debug(f"初始化自定义窗口: {title}")
        
        # 初始化变量
        self.title = title
        self.shadow_radius = shadow_radius
        self.border_radius = border_radius
        self.border_width = border_width
        self.content_margin = content_margin
        self.resize_enabled = True
        
        # 窗口动画设置
        self.animation_enabled = True  # 是否启用动画
        self.animation_duration = 200  # 动画持续时间(毫秒)
        self.size_factor = 0.95  # 初始大小为目标大小的比例
        self.opacity = 0.0  # 初始透明度
        self.first_show = True  # 是否是第一次显示
        self.is_closing = False  # 是否正在关闭
        self.close_animation_group = None  # 关闭动画组
        self.maximizing_animation = None  # 最大化动画
        self.minimizing_animation = None  # 最小化动画
        self.is_maximizing = False  # 是否正在执行最大化动画
        self.is_minimizing = False  # 是否正在执行最小化动画
        self.is_drag_restoring = False  # 是否通过拖拽还原窗口
        
        # 设置默认主题颜色
        if theme_color is None:
            self.theme_color = QColor(41, 128, 185)  # 默认使用蓝色主题
        elif isinstance(theme_color, list) and len(theme_color) >= 3:
            self.theme_color = QColor(theme_color[0], theme_color[1], theme_color[2])
        elif isinstance(theme_color, str):
            self.theme_color = QColor(theme_color)
        else:
            self.theme_color = theme_color
        
        # 设置默认边框颜色
        if border_color is None:
            self.border_color = QColor(230, 230, 230)
        elif isinstance(border_color, list) and len(border_color) >= 3:
            self.border_color = QColor(border_color[0], border_color[1], border_color[2])
        elif isinstance(border_color, str):
            self.border_color = QColor(border_color)
        else:
            self.border_color = border_color
            
        # 设置窗口属性
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) # 无边框
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 透明背景
        
        # 添加窗口阴影
        if shadow_radius > 0:
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(shadow_radius)
            self.shadow.setColor(QColor(0, 0, 0, 60))
            self.shadow.setOffset(0, 3)
            self.setGraphicsEffect(self.shadow)
            
        # 设置窗口最小尺寸
        self.setMinimumSize(400, 300)
        
        # 初始化调整大小句柄
        self.resize_handles = {}
        
        # 初始化动画
        self.maximize_animation = None
        self.maximize_duration = 200
        self.show_animation_group = None
        
        # 初始化界面
        self.initUI()
    
    def initUI(self):
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            self.shadow_radius + self.content_margin, 
            self.shadow_radius + self.content_margin, 
            self.shadow_radius + self.content_margin, 
            self.shadow_radius + self.content_margin
        )
        self.main_layout.setSpacing(0)
        
        # 创建内容容器（实际放置内容的地方）
        self.container = QWidget()
        self.container.setObjectName("container")
        self.container.setStyleSheet(
            f"""
            #container {{
                background-color: white;
                border-radius: {self.border_radius}px;
            }}
            """
        )
        
        # 创建容器布局
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        
        # 创建标题栏
        self.title_bar = WindowTitleBar(title=self.title)
        # 设置标题栏的背景颜色，确保与容器的圆角匹配
        self.title_bar.set_background_color(QColor(255, 255, 255))
        # 设置标题栏圆角半径与窗口一致
        self.title_bar.set_border_radius(self.border_radius)
        
        self.title_bar.minimizeClicked.connect(self.showMinimized)
        self.title_bar.maximizeClicked.connect(self.toggleMaximized)
        self.title_bar.closeClicked.connect(self.close)
        
        # 创建内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        
        # 添加标题栏和内容区域到容器
        self.container_layout.addWidget(self.title_bar)
        self.container_layout.addWidget(self.content_widget)
        
        # 添加容器到主布局
        self.main_layout.addWidget(self.container)
        
        # 设置主布局
        self.setLayout(self.main_layout)
        
        # 创建调整大小句柄
        self._setup_resize_handles()
    
    def _setup_resize_handles(self):
        """设置调整大小的句柄"""
        if not self.resize_enabled:
            return
            
        directions = ["top", "bottom", "left", "right", 
                      "top-left", "top-right", "bottom-left", "bottom-right"]
                      
        for direction in directions:
            handle = ResizeHandle(self, direction)
            self.resize_handles[direction] = handle
            
        self._update_resize_handles()
    
    def _update_resize_handles(self):
        """更新调整大小句柄的位置"""
        if not self.resize_enabled or not self.resize_handles:
            return
            
        handle_size = 8
        half_size = handle_size // 2
        
        # 获取内容区域（排除阴影）
        content_rect = self.container.geometry()
        
        # 更新各个方向句柄的位置
        # 四角
        self.resize_handles["top-left"].setGeometry(
            content_rect.left() - half_size,
            content_rect.top() - half_size,
            handle_size, handle_size
        )
        
        self.resize_handles["top-right"].setGeometry(
            content_rect.right() - half_size,
            content_rect.top() - half_size,
            handle_size, handle_size
        )
        
        self.resize_handles["bottom-left"].setGeometry(
            content_rect.left() - half_size,
            content_rect.bottom() - half_size,
            handle_size, handle_size
        )
        
        self.resize_handles["bottom-right"].setGeometry(
            content_rect.right() - half_size,
            content_rect.bottom() - half_size,
            handle_size, handle_size
        )
        
        # 四边
        self.resize_handles["top"].setGeometry(
            content_rect.left() + half_size,
            content_rect.top() - half_size,
            content_rect.width() - handle_size,
            handle_size
        )
        
        self.resize_handles["bottom"].setGeometry(
            content_rect.left() + half_size,
            content_rect.bottom() - half_size,
            content_rect.width() - handle_size,
            handle_size
        )
        
        self.resize_handles["left"].setGeometry(
            content_rect.left() - half_size,
            content_rect.top() + half_size,
            handle_size,
            content_rect.height() - handle_size
        )
        
        self.resize_handles["right"].setGeometry(
            content_rect.right() - half_size,
            content_rect.top() + half_size,
            handle_size,
            content_rect.height() - handle_size
        )
        
        # 在最大化状态下隐藏调整大小的句柄
        for handle in self.resize_handles.values():
            handle.setVisible(not self.isMaximized())
        
    def set_title(self, title):
        """设置窗口标题"""
        self.logger.debug(f"设置窗口标题: {title}")
        self.title = title
        self.title_bar.set_title(title)
    
    def set_icon(self, icon_path=None, icon=None):
        """设置窗口图标"""
        self.logger.debug(f"设置窗口图标: {icon_path if icon_path else '使用传入的图标'}")
        self.title_bar.set_icon(icon_path, icon)
        
    def set_content_widget(self, widget):
        """设置中心内容组件"""
        self.logger.debug("设置中心内容组件")
        # 清空现有内容
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新组件
        self.content_layout.addWidget(widget)
        
    def set_title_color(self, color):
        """设置标题颜色"""
        self.logger.debug(f"设置标题颜色: {color}")
        self.title_bar.set_title_color(color)
        
    def set_title_background_color(self, color):
        """设置标题栏背景颜色"""
        self.logger.debug(f"设置标题栏背景颜色: {color}")
        # 更改标题栏背景颜色
        self.title_bar.set_background_color(color)
    
    def set_border_color(self, color):
        """设置边框颜色"""
        self.logger.debug(f"设置边框颜色: {color}")
        if isinstance(color, list) and len(color) >= 3:
            self.border_color = QColor(color[0], color[1], color[2])
        elif isinstance(color, str):
            self.border_color = QColor(color)
        else:
            self.border_color = color
        self.update()
        
    def set_shadow_radius(self, radius):
        """设置阴影半径"""
        self.logger.debug(f"设置阴影半径: {radius}")
        self.shadow_radius = radius
        if hasattr(self, 'shadow'):
            self.shadow.setBlurRadius(radius)
        self.main_layout.setContentsMargins(
            self.shadow_radius + self.content_margin, 
            self.shadow_radius + self.content_margin, 
            self.shadow_radius + self.content_margin, 
            self.shadow_radius + self.content_margin
        )
    
    def set_border_radius(self, radius):
        """设置边框圆角半径"""
        self.logger.debug(f"设置边框圆角: {radius}")
        self.border_radius = radius
        
        # 同步设置标题栏的圆角
        if hasattr(self, 'title_bar'):
            self.title_bar.set_border_radius(radius)
        
        # 更新容器样式
        self.container.setStyleSheet(
            f"""
            #container {{
                background-color: white;
                border-radius: {self.border_radius}px;
            }}
            """
        )
        self.update()
    
    def set_theme_color(self, color):
        """设置主题颜色"""
        self.logger.debug(f"设置主题颜色: {color}")
        if isinstance(color, list) and len(color) >= 3:
            self.theme_color = QColor(color[0], color[1], color[2])
        elif isinstance(color, str):
            self.theme_color = QColor(color)
        else:
            self.theme_color = color
        
        # 更新界面颜色
        self.set_title_color(self.theme_color)
        self.set_border_color(self.theme_color)
        self.update()
        
    def set_resize_enabled(self, enabled):
        """设置是否允许调整大小"""
        self.logger.debug(f"设置是否允许调整大小: {enabled}")
        self.resize_enabled = enabled
        
        # 更新调整大小句柄
        if enabled and not self.resize_handles:
            self._setup_resize_handles()
        
        # 显示或隐藏句柄
        if hasattr(self, 'resize_handles'):
            for handle in self.resize_handles.values():
                handle.setVisible(enabled and not self.isMaximized())
    
    def toggleMaximized(self):
        """切换最大化状态"""
        try:
            if self.isMaximized():
                # 从最大化恢复到普通状态
                self.logger.info("请求窗口还原")
                self.showNormal()
            else:
                # 从普通状态最大化
                self.logger.info("请求窗口最大化")
                # 如果已经保存了几何形状信息，先清除，确保保存的是最新状态
                if hasattr(self, 'previous_geometry'):
                    self.previous_geometry = self.geometry()
                self.showMaximized()
        except Exception as e:
            self.logger.error(f"切换最大化状态出错: {str(e)}")
    
    def set_drag_restoring(self, value):
        """设置是否通过拖拽还原窗口"""
        self.is_drag_restoring = value
        self.logger.debug(f"设置拖拽还原状态: {value}")
    
    def showMaximized(self):
        """重载最大化方法，添加动画效果"""
        # 保存当前几何形状，只有在非最大化状态才保存
        if not self.isMaximized():
            # 确保保存的是一个有效的几何形状
            current_geo = self.geometry()
            if current_geo.isValid() and current_geo.width() > 100 and current_geo.height() > 100:
                self.previous_geometry = current_geo
                self.logger.debug(f"保存窗口位置: {self.previous_geometry}")
        
        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        
        # 如果启用动画并且不是正在动画过程中
        if self.animation_enabled and not self.is_maximizing and not self.isMaximized():
            try:
                self.is_maximizing = True
                self.logger.debug("开始最大化动画")
                
                # 设置为无状态，避免系统默认的最大化行为干扰动画
                self.setWindowState(Qt.WindowState.WindowNoState)
                
                # 临时禁用阴影效果，提高动画流畅度
                self.setGraphicsEffect(None)
                
                # 设置圆角为0（在动画过程中）
                self.container.setStyleSheet("""
                #container {
                    background-color: white;
                    border-radius: 0px;
                }
                """)
                
                # 设置标题栏圆角为0
                if hasattr(self, 'title_bar'):
                    self.title_bar.set_border_radius(0)
                
                # 隐藏所有调整大小的句柄
                if hasattr(self, 'resize_handles'):
                    for handle in self.resize_handles.values():
                        handle.setVisible(False)
                        handle.setCursor(Qt.CursorShape.ArrowCursor)
                
                # 创建更平滑的几何形状动画
                self.maximizing_animation = QPropertyAnimation(self, b"geometry")
                self.maximizing_animation.setDuration(180)  # 稍微缩短动画时间，让感觉更快
                self.maximizing_animation.setStartValue(self.geometry())
                self.maximizing_animation.setEndValue(screen_geometry)
                self.maximizing_animation.setEasingCurve(QEasingCurve.Type.OutQuint)  # 更改缓动曲线，使动画更丝滑
                
                # 连接动画完成信号
                self.maximizing_animation.finished.connect(self._on_maximize_animation_finished)
                
                # 移除内容区域边距，确保最大化时填满整个屏幕
                self.main_layout.setContentsMargins(0, 0, 0, 0)
                
                # 分步执行动画，提高流畅度
                QTimer.singleShot(0, lambda: self.maximizing_animation.start())
                
                return
                
            except Exception as e:
                self.logger.error(f"创建最大化动画时出错: {str(e)}")
                self.is_maximizing = False
                # 如果动画失败，继续执行普通最大化
        
        try:
            # 动画未启用或已出错，执行默认最大化
            # 暂时移除图形效果
            self.setGraphicsEffect(None)
            
            # 移除内容区域边距，确保最大化时填满整个屏幕
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            
            # 直接设置窗口大小为屏幕大小，确保铺满
            self.setGeometry(screen_geometry)
            
            # 更新窗口状态
            self.setWindowState(Qt.WindowState.WindowMaximized)
            
            # 更新容器样式
            self.container.setStyleSheet("""
            #container {
                background-color: white;
                border-radius: 0px;
            }
            """)
            
            # 设置标题栏圆角为0
            if hasattr(self, 'title_bar'):
                self.title_bar.set_border_radius(0)
            
            # 强制更新布局
            self.container_layout.invalidate()
            self.container_layout.activate()
            
            # 隐藏所有调整大小的句柄
            if hasattr(self, 'resize_handles'):
                for handle in self.resize_handles.values():
                    handle.setVisible(False)
                    handle.setCursor(Qt.CursorShape.ArrowCursor)
            
            self.logger.info(f"窗口已最大化: {self.geometry()}")
            
        except Exception as e:
            self.logger.error(f"最大化窗口时出错: {str(e)}")
    
    def _on_maximize_animation_finished(self):
        """最大化动画完成后的处理"""
        try:
            # 动画完成后，正式设置窗口为最大化状态
            self.is_maximizing = False
            
            # 清理动画资源
            if self.maximizing_animation:
                self.maximizing_animation.deleteLater()
                self.maximizing_animation = None
            
            # 最后再设置窗口状态为最大化
            self.setWindowState(Qt.WindowState.WindowMaximized)
            
            # 强制更新布局
            self.container_layout.invalidate()
            self.container_layout.activate()
            
            self.logger.debug("最大化动画完成")
            
        except Exception as e:
            self.logger.error(f"处理最大化动画完成事件时出错: {str(e)}")
            # 确保窗口状态正确
            self.setWindowState(Qt.WindowState.WindowMaximized)
            
    def showMinimized(self):
        """重载最小化方法，添加动画效果"""
        # 如果启用动画且不是正在最小化
        if self.animation_enabled and not self.is_minimizing:
            try:
                self.is_minimizing = True
                self.logger.debug("开始最小化动画")
                
                # 保存当前几何形状用于还原
                self.before_minimize_geometry = self.geometry()
                
                # 获取桌面任务栏的位置或屏幕底部
                screen = QApplication.primaryScreen()
                screen_geometry = screen.availableGeometry()
                target_y = screen_geometry.bottom()
                
                # 计算动画目标几何形状（缩小到任务栏高度）
                start_geo = self.geometry()
                minimized_width = min(start_geo.width() // 3, 200)  # 最小化到原始宽度的1/3，但不超过200像素
                minimized_height = min(start_geo.height() // 3, 120)  # 最小化到原始高度的1/3，但不超过120像素
                
                # 计算目标X坐标（保持水平居中）
                target_x = start_geo.x() + (start_geo.width() - minimized_width) // 2
                
                # 保存最小化动画的终点状态，以便还原时使用
                self.minimized_end_rect = QRect(target_x, target_y, minimized_width, minimized_height)
                
                # 创建几何形状动画
                self.minimizing_animation = QPropertyAnimation(self, b"geometry")
                self.minimizing_animation.setDuration(self.animation_duration)
                self.minimizing_animation.setStartValue(start_geo)
                self.minimizing_animation.setEndValue(self.minimized_end_rect)
                self.minimizing_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                # 创建透明度动画
                self.minimize_opacity_animation = QPropertyAnimation(self, b"windowOpacity")
                self.minimize_opacity_animation.setDuration(self.animation_duration)
                self.minimize_opacity_animation.setStartValue(1.0)
                self.minimize_opacity_animation.setEndValue(0.0)
                self.minimize_opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                # 创建动画组
                self.minimize_animation_group = QParallelAnimationGroup()
                self.minimize_animation_group.addAnimation(self.minimizing_animation)
                self.minimize_animation_group.addAnimation(self.minimize_opacity_animation)
                
                # 连接动画完成信号
                self.minimize_animation_group.finished.connect(self._on_minimize_animation_finished)
                
                # 临时移除阴影效果，避免动画过程中出现UpdateLayeredWindowIndirect错误
                self.setGraphicsEffect(None)
                
                # 启动动画
                self.minimize_animation_group.start()
                
                return
                
            except Exception as e:
                self.logger.error(f"创建最小化动画时出错: {str(e)}")
                self.is_minimizing = False
                # 如果动画失败，继续执行普通最小化
        
        # 动画未启用或已出错，执行默认最小化
        super().showMinimized()
    
    def _on_minimize_animation_finished(self):
        """最小化动画完成后的处理"""
        try:
            # 动画完成后，真正设置窗口为最小化状态
            self.is_minimizing = False
            
            # 清理动画资源
            if hasattr(self, 'minimize_animation_group'):
                self.minimize_animation_group.deleteLater()
                self.minimize_animation_group = None
            
            # 恢复窗口不透明度，否则在还原时窗口会保持透明
            self.setWindowOpacity(1.0)
            
            # 真正进行最小化
            super().showMinimized()
            
            self.logger.debug("最小化动画完成")
            
        except Exception as e:
            self.logger.error(f"处理最小化动画完成事件时出错: {str(e)}")
            # 确保窗口正确最小化
            super().showMinimized()
    
    def showNormal(self):
        """重载还原方法，添加动画效果"""
        try:
            # 如果是通过拖拽还原，不播放动画
            if self.is_drag_restoring:
                self.logger.debug("通过拖拽还原窗口，不播放动画")
                self.is_drag_restoring = False  # 重置标志
                
                # 先清除最大化状态
                self.setWindowState(Qt.WindowState.WindowNoState)
                
                # 恢复容器样式
                self.container.setStyleSheet(f"""
                #container {{
                    background-color: white;
                    border-radius: {self.border_radius}px;
                }}
                """)
                
                # 恢复标题栏圆角
                if hasattr(self, 'title_bar'):
                    self.title_bar.set_border_radius(self.border_radius)
                
                # 恢复内容边距
                self.main_layout.setContentsMargins(
                    self.shadow_radius + self.content_margin, 
                    self.shadow_radius + self.content_margin, 
                    self.shadow_radius + self.content_margin, 
                    self.shadow_radius + self.content_margin
                )
                
                # 如果有保存的几何形状，恢复它
                if hasattr(self, 'previous_geometry') and self.previous_geometry.isValid():
                    self.logger.debug(f"还原窗口位置: {self.previous_geometry}")
                    # 直接设置几何形状
                    self.setGeometry(self.previous_geometry)
                
                # 强制更新布局
                self.container_layout.invalidate()
                self.container_layout.activate()
                self.title_bar.updateGeometry()
                
                # 显示调整大小的句柄，并恢复鼠标样式
                if hasattr(self, 'resize_handles') and self.resize_enabled:
                    for handle in self.resize_handles.values():
                        handle.setVisible(True)
                        handle.setCursor(handle.normal_cursor)
                
                # 强制刷新
                self.update()
                
                return
            
            # 如果启用动画并且当前处于最大化状态，添加还原动画
            if self.animation_enabled and self.isMaximized() and hasattr(self, 'previous_geometry'):
                self.logger.debug("开始最大化还原动画")
                
                # 暂时禁用阴影效果，提高动画流畅度
                self.setGraphicsEffect(None)
                
                # 记录当前几何信息（最大化状态）
                current_geometry = self.geometry()
                
                # 先清除最大化状态，但保持当前大小
                self.setWindowState(Qt.WindowState.WindowNoState)
                self.setGeometry(current_geometry)
                
                # 恢复内容边距，确保动画过程中布局正确
                self.main_layout.setContentsMargins(
                    self.shadow_radius + self.content_margin, 
                    self.shadow_radius + self.content_margin, 
                    self.shadow_radius + self.content_margin, 
                    self.shadow_radius + self.content_margin
                )
                
                # 恢复容器样式
                self.container.setStyleSheet(f"""
                #container {{
                    background-color: white;
                    border-radius: {self.border_radius}px;
                }}
                """)
                
                # 恢复标题栏圆角
                if hasattr(self, 'title_bar'):
                    self.title_bar.set_border_radius(self.border_radius)
                
                # 创建几何形状动画
                self.restore_anim = QPropertyAnimation(self, b"geometry")
                self.restore_anim.setDuration(180)  # 较短的动画时间
                self.restore_anim.setStartValue(current_geometry)
                self.restore_anim.setEndValue(self.previous_geometry)
                self.restore_anim.setEasingCurve(QEasingCurve.Type.OutQuint)  # 平滑的缓动曲线
                
                # 连接动画完成信号
                self.restore_anim.finished.connect(self._on_restore_from_maximized_finished)
                
                # 显示调整大小的句柄，并恢复鼠标样式
                if hasattr(self, 'resize_handles') and self.resize_enabled:
                    for handle in self.resize_handles.values():
                        handle.setVisible(True)
                        handle.setCursor(handle.normal_cursor)
                
                # 强制更新布局
                self.container_layout.invalidate()
                self.container_layout.activate()
                self.title_bar.update()
                
                # 启动动画
                self.restore_anim.start()
                return
            
            # 确保窗口不透明
            self.setWindowOpacity(1.0)
            
            # 先清除最大化状态
            self.setWindowState(Qt.WindowState.WindowNoState)
            
            # 恢复容器样式
            self.container.setStyleSheet(f"""
            #container {{
                background-color: white;
                border-radius: {self.border_radius}px;
            }}
            """)
            
            # 恢复标题栏圆角
            if hasattr(self, 'title_bar'):
                self.title_bar.set_border_radius(self.border_radius)
            
            # 恢复内容边距
            self.main_layout.setContentsMargins(
                self.shadow_radius + self.content_margin, 
                self.shadow_radius + self.content_margin, 
                self.shadow_radius + self.content_margin, 
                self.shadow_radius + self.content_margin
            )
            
            # 如果有保存的几何形状，恢复它
            if hasattr(self, 'previous_geometry') and self.previous_geometry.isValid():
                self.logger.debug(f"还原窗口位置: {self.previous_geometry}")
                # 直接设置几何形状
                self.setGeometry(self.previous_geometry)
            
            # 强制更新布局
            self.container_layout.invalidate()
            self.container_layout.activate()
            self.title_bar.updateGeometry()
            
            # 显示调整大小的句柄，并恢复鼠标样式
            if hasattr(self, 'resize_handles') and self.resize_enabled:
                for handle in self.resize_handles.values():
                    handle.setVisible(True)
                    handle.setCursor(handle.normal_cursor)
            
            # 强制刷新
            self.update()
            
            self.logger.info("窗口已还原")
            
        except Exception as e:
            self.logger.error(f"还原窗口时出错: {str(e)}")
    
    def _on_restore_from_maximized_finished(self):
        """从最大化恢复动画完成后的处理"""
        try:
            self.logger.debug("最大化还原动画完成")
            
            # 清理动画资源
            if hasattr(self, 'restore_anim'):
                self.restore_anim.deleteLater()
                self.restore_anim = None
            
            # 确保窗口状态正确
            self.setWindowState(Qt.WindowState.WindowNoState)
            
            # 再次确认几何形状，避免任何偏差
            if hasattr(self, 'previous_geometry') and self.previous_geometry.isValid():
                self.setGeometry(self.previous_geometry)
            
            # 延迟更新调整大小句柄的位置
            QTimer.singleShot(50, self._update_resize_handles)
            
        except Exception as e:
            self.logger.error(f"处理最大化还原动画完成事件时出错: {str(e)}")
    
    def changeEvent(self, event):
        """处理窗口状态变化事件"""
        if event.type() == QEvent.Type.WindowStateChange:
            # 如果窗口从最小化状态恢复
            if event.oldState() & Qt.WindowState.WindowMinimized and not self.windowState() & Qt.WindowState.WindowMinimized:
                self.logger.debug("从最小化状态恢复")
                # 确保窗口不透明
                self.setWindowOpacity(1.0)
                
                # 如果启用了动画，播放恢复动画
                if self.animation_enabled and not self.isMaximized():
                    self._play_restore_from_minimized_animation()
                else:
                    # 否则直接应用样式
                    self._apply_window_style_after_restore()
            
            # 窗口即将被最小化
            elif not (event.oldState() & Qt.WindowState.WindowMinimized) and self.windowState() & Qt.WindowState.WindowMinimized:
                self.logger.debug("窗口被最小化")
                # 记录当前几何信息，以便恢复时使用
                if not hasattr(self, 'before_minimize_geometry'):
                    self.before_minimize_geometry = self.geometry()
                
        super().changeEvent(event)
    
    def _play_restore_from_minimized_animation(self):
        """播放从最小化状态恢复的动画"""
        try:
            self.logger.debug("开始从最小化状态恢复动画")
            
            # 临时禁用阴影效果，避免动画过程中的UpdateLayeredWindowIndirect错误
            # 先清理旧的图形效果
            old_effect = self.graphicsEffect()
            if old_effect:
                old_effect.setEnabled(False)
                self.setGraphicsEffect(None)
                old_effect.deleteLater()
            
            # 使用之前保存的最小化前的几何形状作为目标
            if hasattr(self, 'before_minimize_geometry') and self.before_minimize_geometry.isValid():
                target_geometry = self.before_minimize_geometry
            else:
                # 如果没有保存的几何信息，使用默认几何信息
                target_geometry = self.geometry()
            
            # 使用之前保存的最小化动画的终点作为恢复动画的起点
            if hasattr(self, 'minimized_end_rect') and self.minimized_end_rect.isValid():
                start_rect = self.minimized_end_rect
            else:
                # 如果没有保存的最小化终点，计算一个合理的起点
                screen = QApplication.primaryScreen()
                screen_geometry = screen.availableGeometry()
                start_width = min(target_geometry.width() // 3, 200)
                start_height = min(target_geometry.height() // 3, 120)
                start_x = target_geometry.x() + (target_geometry.width() - start_width) // 2
                start_y = screen_geometry.bottom()
                start_rect = QRect(start_x, start_y, start_width, start_height)
            
            # 确保窗口初始位置和大小正确
            # 更新窗口几何形状前，确保没有图形效果
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setGeometry(start_rect)
            
            # 设置起始透明度
            self.setWindowOpacity(0.0)
            
            # 创建几何形状动画（最小化的反向）
            self.restore_geometry_animation = QPropertyAnimation(self, b"geometry")
            self.restore_geometry_animation.setDuration(self.animation_duration)
            self.restore_geometry_animation.setStartValue(start_rect)
            self.restore_geometry_animation.setEndValue(target_geometry)
            self.restore_geometry_animation.setEasingCurve(QEasingCurve.Type.InCubic)  # 使用InCubic作为OutCubic的反向
            
            # 创建透明度动画（最小化的反向）
            self.restore_opacity_animation = QPropertyAnimation(self, b"windowOpacity")
            self.restore_opacity_animation.setDuration(self.animation_duration)
            self.restore_opacity_animation.setStartValue(0.0)
            self.restore_opacity_animation.setEndValue(1.0)
            self.restore_opacity_animation.setEasingCurve(QEasingCurve.Type.InCubic)  # 使用InCubic作为OutCubic的反向
            
            # 创建动画组
            self.restore_animation_group = QParallelAnimationGroup()
            self.restore_animation_group.addAnimation(self.restore_geometry_animation)
            self.restore_animation_group.addAnimation(self.restore_opacity_animation)
            
            # 连接动画完成信号
            self.restore_animation_group.finished.connect(self._on_restore_animation_finished)
            
            # 启动动画
            self.restore_animation_group.start()
            
        except Exception as e:
            self.logger.error(f"创建还原动画时出错: {str(e)}")
            # 如果动画失败，直接应用样式
            self._apply_window_style_after_restore()
    
    def _on_restore_animation_finished(self):
        """从最小化状态恢复动画完成的处理"""
        try:
            # 确保窗口完全不透明
            self.setWindowOpacity(1.0)
            
            # 清理动画资源
            if hasattr(self, 'restore_animation_group'):
                self.restore_animation_group.deleteLater()
                self.restore_animation_group = None
            
            self.logger.debug("从最小化状态恢复动画完成")
            
            # 使用更长的延迟应用窗口样式和阴影效果，避免UpdateLayeredWindowIndirect错误
            QTimer.singleShot(100, self._apply_window_style_after_restore)
            
        except Exception as e:
            self.logger.error(f"处理恢复动画完成事件时出错: {str(e)}")
            # 确保窗口样式正确
            QTimer.singleShot(100, self._apply_window_style_after_restore)
    
    def _apply_window_style_after_restore(self):
        """应用窗口从最小化状态恢复后的样式"""
        try:
            # 更新窗口样式根据当前状态
            if self.isMaximized():
                # 最大化样式
                self.container.setStyleSheet("""
                #container {
                    background-color: white;
                    border-radius: 0px;
                }
                """)
                
                # 设置标题栏圆角为0
                if hasattr(self, 'title_bar'):
                    self.title_bar.set_border_radius(0)
                    
                # 隐藏调整大小的句柄
                if hasattr(self, 'resize_handles'):
                    for handle in self.resize_handles.values():
                        handle.setVisible(False)
            else:
                # 正常样式
                self.container.setStyleSheet(f"""
                #container {{
                    background-color: white;
                    border-radius: {self.border_radius}px;
                }}
                """)
                
                # 恢复标题栏圆角
                if hasattr(self, 'title_bar'):
                    self.title_bar.set_border_radius(self.border_radius)
                
                # 从最小化恢复时，不使用阴影效果，避免UpdateLayeredWindowIndirect错误
                # 注释掉应用阴影效果的代码
                # if hasattr(self, 'shadow') and self.shadow_radius > 0:
                #     # 确保先删除之前的阴影效果
                #     old_effect = self.graphicsEffect()
                #     if old_effect:
                #         old_effect.setEnabled(False)
                #         old_effect.deleteLater()
                #     
                #     # 添加新的阴影效果时使用长延迟，避免UpdateLayeredWindowIndirect错误
                #     QTimer.singleShot(150, self._apply_shadow_effect)
                
                # 显示调整大小的句柄
                if hasattr(self, 'resize_handles') and self.resize_enabled:
                    for handle in self.resize_handles.values():
                        handle.setVisible(True)
                        handle.setCursor(handle.normal_cursor)
            
            # 先更新内容，然后再延迟更新调整大小句柄
            self.update()
            
            # 延迟更新调整大小句柄的位置
            QTimer.singleShot(50, self._update_resize_handles)
            
        except Exception as e:
            self.logger.error(f"应用还原样式时出错: {str(e)}")
    
    def _apply_shadow_effect(self):
        """安全地应用阴影效果"""
        try:
            # 确保窗口几何形状已经稳定，且不是最大化状态
            if self.shadow_radius > 0 and not self.isMaximized():
                # 先确保没有正在运行的动画
                if (hasattr(self, 'restore_animation_group') and 
                    self.restore_animation_group and 
                    self.restore_animation_group.state() == QParallelAnimationGroup.State.Running):
                    # 如果动画还在运行，延迟应用阴影
                    QTimer.singleShot(100, self._apply_shadow_effect)
                    return
                    
                # 先检查并清理已有的图形效果
                old_effect = self.graphicsEffect()
                if old_effect:
                    old_effect.setEnabled(False)
                    old_effect.deleteLater()
                
                # 延迟一帧再创建新的阴影效果
                QTimer.singleShot(16, self._create_shadow_effect)
                
        except Exception as e:
            self.logger.error(f"应用阴影效果时出错: {str(e)}")
            # 如果添加阴影失败，至少确保窗口正常显示
            self.setGraphicsEffect(None)
    
    def _create_shadow_effect(self):
        """创建并应用阴影效果，分离出来以防止堆栈过深的问题"""
        try:
            if self.shadow_radius > 0 and not self.isMaximized():
                # 创建新的阴影效果
                shadow = QGraphicsDropShadowEffect(self)
                shadow.setBlurRadius(self.shadow_radius)
                shadow.setColor(QColor(0, 0, 0, 60))
                shadow.setOffset(0, 3)
                
                # 先禁用效果
                shadow.setEnabled(False)
                
                # 应用效果
                self.setGraphicsEffect(shadow)
                
                # 延迟启用效果，防止UpdateLayeredWindowIndirect错误
                QTimer.singleShot(50, lambda: self._enable_shadow_effect(shadow))
        except Exception as e:
            self.logger.error(f"创建阴影效果时出错: {str(e)}")
            self.setGraphicsEffect(None)
    
    def _enable_shadow_effect(self, shadow):
        """安全地启用阴影效果"""
        try:
            if shadow and not self.isMaximized():
                shadow.setEnabled(True)
                self.update()
        except Exception as e:
            self.logger.error(f"启用阴影效果时出错: {str(e)}")
            self.setGraphicsEffect(None)
    
    def closeEvent(self, event):
        """窗口关闭事件，添加关闭动画"""
        # 如果启用了动画且不是正在关闭状态，则播放关闭动画
        if self.animation_enabled and not self.is_closing and not self.isMaximized():
            self.logger.info("窗口关闭 - 开始关闭动画")
            event.ignore()  # 忽略这次关闭事件，让动画完成后再关闭
            self._play_close_animation()
            return
        super().closeEvent(event)
    
    def _play_close_animation(self):
        """播放窗口关闭动画"""
        try:
            self.is_closing = True
            
            # 记录当前窗口大小和位置
            start_geometry = self.geometry()
            
            # 计算结束大小和位置
            end_width = int(start_geometry.width() * self.size_factor)
            end_height = int(start_geometry.height() * self.size_factor)
            
            # 计算结束位置，保持窗口中心不变
            dx = (start_geometry.width() - end_width) // 2
            dy = (start_geometry.height() - end_height) // 2
            end_x = start_geometry.x() + dx
            end_y = start_geometry.y() + dy
            
            # 创建大小动画
            self.close_size_animation = QPropertyAnimation(self, b"geometry")
            self.close_size_animation.setDuration(self.animation_duration)
            self.close_size_animation.setStartValue(start_geometry)
            self.close_size_animation.setEndValue(QRect(end_x, end_y, end_width, end_height))
            self.close_size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # 创建透明度动画
            self.close_opacity_animation = QPropertyAnimation(self, b"windowOpacity")
            self.close_opacity_animation.setDuration(self.animation_duration)
            self.close_opacity_animation.setStartValue(1.0)
            self.close_opacity_animation.setEndValue(0.0)
            self.close_opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # 创建动画组
            self.close_animation_group = QParallelAnimationGroup()
            self.close_animation_group.addAnimation(self.close_size_animation)
            self.close_animation_group.addAnimation(self.close_opacity_animation)
            
            # 连接动画完成信号
            self.close_animation_group.finished.connect(self._on_close_animation_finished)
            
            # 启动动画
            self.close_animation_group.start()
            
        except Exception as e:
            self.logger.error(f"创建窗口关闭动画时出错: {str(e)}")
            # 确保窗口能正常关闭，即使动画失败
            self.is_closing = False
            self.close()
    
    def _on_close_animation_finished(self):
        """窗口关闭动画完成后的处理"""
        try:
            # 清理动画资源
            if self.close_animation_group:
                self.close_animation_group.deleteLater()
                self.close_animation_group = None
            
            # 真正关闭窗口
            # 不要重置is_closing标志，避免触发新的动画循环
            # self.is_closing = False
            self.logger.debug("窗口关闭动画完成，执行实际关闭")
            # 使用QWidget的close方法直接关闭，绕过自定义的closeEvent
            QWidget.close(self)
            
        except Exception as e:
            self.logger.error(f"处理关闭动画完成事件时出错: {str(e)}")
            # 确保窗口能正常关闭
            QWidget.close(self)
    
    def resizeEvent(self, event):
        """大小变化事件，处理最大化时的边框显示"""
        super().resizeEvent(event)
        
        # 更新调整大小句柄的位置
        self._update_resize_handles()
        
        # 强制标题栏重绘，确保圆角更新
        if hasattr(self, 'title_bar'):
            self.title_bar.update()
            
        self.update()
    
    def moveEvent(self, event):
        """窗口移动事件"""
        super().moveEvent(event)
        
    def enterEvent(self, event):
        """鼠标进入窗口事件"""
        # 光标可能会因为调整大小的句柄而变化，所以当鼠标离开句柄区域时恢复默认光标
        self.setCursor(Qt.CursorShape.ArrowCursor)
        return super().enterEvent(event)

    def set_animation_enabled(self, enabled):
        """设置是否启用窗口动画效果"""
        self.logger.debug(f"设置动画效果: {enabled}")
        self.animation_enabled = enabled
    
    def set_animation_duration(self, duration):
        """设置动画持续时间(毫秒)"""
        self.logger.debug(f"设置动画持续时间: {duration}ms")
        self.animation_duration = max(50, duration)  # 至少50毫秒
        
    def showEvent(self, event):
        """重写显示事件，添加窗口弹出动画效果"""
        super().showEvent(event)
        
        # 如果启用了动画且是第一次显示
        if self.animation_enabled and self.first_show and not self.isMaximized():
            self.first_show = False
            self.logger.debug("触发窗口弹出动画")
            
            try:
                # 记录目标大小和位置
                target_geometry = self.geometry()
                
                # 计算起始大小和位置
                start_width = int(target_geometry.width() * self.size_factor)
                start_height = int(target_geometry.height() * self.size_factor)
                
                # 计算起始位置，保持窗口中心不变
                dx = (target_geometry.width() - start_width) // 2
                dy = (target_geometry.height() - start_height) // 2
                start_x = target_geometry.x() + dx
                start_y = target_geometry.y() + dy
                
                # 设置起始大小和透明度
                self.setWindowOpacity(self.opacity)
                
                # 创建尺寸动画
                self.size_animation = QPropertyAnimation(self, b"geometry")
                self.size_animation.setDuration(self.animation_duration)
                self.size_animation.setStartValue(QRect(start_x, start_y, start_width, start_height))
                self.size_animation.setEndValue(target_geometry)
                self.size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                # 创建透明度动画
                self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
                self.opacity_animation.setDuration(self.animation_duration)
                self.opacity_animation.setStartValue(self.opacity)
                self.opacity_animation.setEndValue(1.0)
                self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                
                # 创建动画组
                self.show_animation_group = QParallelAnimationGroup()
                self.show_animation_group.addAnimation(self.size_animation)
                self.show_animation_group.addAnimation(self.opacity_animation)
                
                # 连接动画完成信号
                self.show_animation_group.finished.connect(self.on_show_animation_finished)
                
                # 启动动画
                self.show_animation_group.start()
                
            except Exception as e:
                self.logger.error(f"创建窗口弹出动画时出错: {str(e)}")
                # 确保窗口可见，即使动画失败
                self.setWindowOpacity(1.0)
    
    def on_show_animation_finished(self):
        """窗口弹出动画完成后的处理"""
        try:
            # 确保窗口完全不透明
            self.setWindowOpacity(1.0)
            
            # 清理动画资源
            if self.show_animation_group:
                self.show_animation_group.deleteLater()
                self.show_animation_group = None
                
            # 更新调整大小句柄的位置
            self._update_resize_handles()
            
            self.logger.debug("窗口弹出动画完成")
            
        except Exception as e:
            self.logger.error(f"处理动画完成事件时出错: {str(e)}")
            
    def show(self):
        """重载show方法，确保动画状态重置"""
        # 重置第一次显示标志，使动画可以再次触发
        self.first_show = True
        
        # 调用父类的show方法
        super().show()
    
    def hide(self):
        """重载hide方法，确保下次显示时有动画效果"""
        # 重置第一次显示标志
        self.first_show = True
        
        # 如果有正在运行的动画，停止它
        if self.show_animation_group and self.show_animation_group.state() == QParallelAnimationGroup.State.Running:
            self.show_animation_group.stop()
            self.show_animation_group.deleteLater()
            self.show_animation_group = None
        
        # 调用父类的hide方法
        super().hide()

# 示例用法
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = CustomBorderlessWindow(title="无边框窗口示例")
    
    # 创建内容
    content = QWidget()
    content_layout = QVBoxLayout(content)
    content_layout.addWidget(QLabel("这是一个自定义无边框窗口示例"))
    
    # 设置内容
    window.set_content_widget(content)
    
    # 设置主题样式
    window.set_theme_color([41, 128, 185])
    
    # 显示窗口
    window.resize(600, 400)
    window.show()
    
    sys.exit(app.exec())