import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTabBar, QStackedWidget, QStyleOption, QStyle, QFrame, QPushButton)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QRect, QEasingCurve, QSize, 
                        pyqtProperty, QPoint, QRectF, QParallelAnimationGroup, pyqtSignal)
from PyQt6.QtGui import (QColor, QPainter, QFont, QIcon, QPainterPath, 
                        QBrush, QPen, QLinearGradient)

try:
    from core.logger import get_logger
except ImportError:
    # 相对导入处理，便于直接运行此文件进行测试
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

class AnimatedStackedWidget(QStackedWidget):
    """
    动画堆栈组件
    
    一个带有切换动画效果的堆栈组件，用于实现选项卡内容的平滑过渡。
    支持多种切换效果，如滑动、渐变等。
    """
    
    # 定义动画方向常量
    ANIMATION_LEFT_TO_RIGHT = 0    # 从左到右
    ANIMATION_RIGHT_TO_LEFT = 1    # 从右到左
    ANIMATION_TOP_TO_BOTTOM = 2    # 从上到下
    ANIMATION_BOTTOM_TO_TOP = 3    # 从下到上
    ANIMATION_FADE = 4             # 淡入淡出
    
    # 信号：动画完成时发出
    animationFinished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("AnimatedStackedWidget")
        
        # 动画属性
        self._fade_value = 0.0              # 淡入淡出值
        self._horizontal_offset = 0.0       # 水平偏移
        self._vertical_offset = 0.0         # 垂直偏移
        
        # 动画设置
        self._animation_type = self.ANIMATION_RIGHT_TO_LEFT  # 默认动画类型
        self._animation_duration = 300                       # 默认动画持续时间（毫秒）
        self._animation_curve = QEasingCurve.Type.OutCubic       # 默认动画曲线
        self._animations_enabled = True                      # 是否启用动画
        
        # 动画组
        self._animation_group = QParallelAnimationGroup(self)
        self._animation_group.finished.connect(self._onAnimationFinished)
        
        # 当前页面和下一页面的快照
        self._current_widget_snapshot = None
        self._next_widget_snapshot = None
        
        # 动画状态
        self._is_animating = False
        self._next_index = -1
        
        # 设置属性，允许窗口更新
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        
        # 启用自动填充背景
        self.setAutoFillBackground(False)
        
        # 添加尺寸变化处理
        self.resizeEvent = self._handleResize
    
    # 属性访问器和修改器
    def _get_fade_value(self):
        return self._fade_value
    
    def _set_fade_value(self, value):
        self._fade_value = value
        self.update()
    
    def _get_horizontal_offset(self):
        return self._horizontal_offset
    
    def _set_horizontal_offset(self, value):
        self._horizontal_offset = value
        self.update()
    
    def _get_vertical_offset(self):
        return self._vertical_offset
    
    def _set_vertical_offset(self, value):
        self._vertical_offset = value
        self.update()
    
    # 定义PyQt属性
    fade_value = pyqtProperty(float, _get_fade_value, _set_fade_value)
    horizontal_offset = pyqtProperty(float, _get_horizontal_offset, _set_horizontal_offset)
    vertical_offset = pyqtProperty(float, _get_vertical_offset, _set_vertical_offset)
    
    def setAnimationEnabled(self, enabled):
        """设置是否启用动画"""
        self._animations_enabled = enabled
    
    def setAnimationType(self, animation_type):
        """设置动画类型"""
        if animation_type in [self.ANIMATION_LEFT_TO_RIGHT, self.ANIMATION_RIGHT_TO_LEFT,
                            self.ANIMATION_TOP_TO_BOTTOM, self.ANIMATION_BOTTOM_TO_TOP,
                            self.ANIMATION_FADE]:
            self._animation_type = animation_type
    
    def setAnimationDuration(self, duration):
        """设置动画持续时间（毫秒）"""
        if duration > 0:
            self._animation_duration = duration
    
    def setAnimationCurve(self, curve):
        """设置动画曲线"""
        self._animation_curve = curve
    
    def setCurrentIndex(self, index):
        """设置当前索引，带动画效果"""
        # 检查索引是否有效
        if self.currentIndex() == index or index < 0 or index >= self.count():
            return
        
        if not self._animations_enabled:
            # 如果动画被禁用，直接切换
            super().setCurrentIndex(index)
            return
        
        # 如果动画已经在运行，停止它
        if self._is_animating:
            self._animation_group.stop()
            self._animation_group.clear()
            self._is_animating = False
            
            # 如果有快照，释放它们
            self._current_widget_snapshot = None
            self._next_widget_snapshot = None
        
        # 获取当前窗口和目标窗口
        current_widget = self.currentWidget()
        next_widget = self.widget(index)
        
        if not current_widget or not next_widget:
            # 如果窗口不存在，直接切换
            super().setCurrentIndex(index)
            return
        
        # 先将下一页面调整为当前容器的大小，避免切换后的位移调整
        next_widget.resize(self.size())
        
        # 创建快照并设置可见性
        current_widget.setVisible(True)
        self._current_widget_snapshot = current_widget.grab()
        
        # 临时显示目标窗口以创建快照，然后隐藏所有窗口
        for i in range(self.count()):
            widget = self.widget(i)
            widget.setVisible(i == index)
            if i == index:
                self._next_widget_snapshot = widget.grab()
        
        # 隐藏所有窗口，将通过绘制快照来展示
        for i in range(self.count()):
            self.widget(i).setVisible(False)
        
        # 保存目标索引，用于动画结束后切换
        self._next_index = index
        
        # 设置动画标记
        self._is_animating = True
        
        # 根据动画类型设置动画
        self._animation_group.clear()
        
        if self._animation_type == self.ANIMATION_FADE:
            # 淡入淡出效果
            fade_anim = QPropertyAnimation(self, b"fade_value")
            fade_anim.setDuration(self._animation_duration)
            fade_anim.setStartValue(0.0)
            fade_anim.setEndValue(1.0)
            fade_anim.setEasingCurve(self._animation_curve)
            self._animation_group.addAnimation(fade_anim)
            
        elif self._animation_type in [self.ANIMATION_LEFT_TO_RIGHT, self.ANIMATION_RIGHT_TO_LEFT]:
            # 水平滑动效果
            horz_anim = QPropertyAnimation(self, b"horizontal_offset")
            horz_anim.setDuration(self._animation_duration)
            
            if self._animation_type == self.ANIMATION_LEFT_TO_RIGHT:
                # 从左到右
                horz_anim.setStartValue(0)
                horz_anim.setEndValue(self.width())
            else:
                # 从右到左
                horz_anim.setStartValue(0)
                horz_anim.setEndValue(-self.width())
            
            horz_anim.setEasingCurve(self._animation_curve)
            self._animation_group.addAnimation(horz_anim)
            
        elif self._animation_type in [self.ANIMATION_TOP_TO_BOTTOM, self.ANIMATION_BOTTOM_TO_TOP]:
            # 垂直滑动效果
            vert_anim = QPropertyAnimation(self, b"vertical_offset")
            vert_anim.setDuration(self._animation_duration)
            
            if self._animation_type == self.ANIMATION_TOP_TO_BOTTOM:
                # 从上到下
                vert_anim.setStartValue(0)
                vert_anim.setEndValue(self.height())
            else:
                # 从下到上
                vert_anim.setStartValue(0)
                vert_anim.setEndValue(-self.height())
            
            vert_anim.setEasingCurve(self._animation_curve)
            self._animation_group.addAnimation(vert_anim)
        
        # 启动动画
        self._animation_group.start()
        
        # 重要：不要在这里调用父类的setCurrentIndex，等动画结束后再调用

    def _onAnimationFinished(self):
        """动画完成时调用"""
        # 标记动画已完成
        self._is_animating = False
        
        # 通过父类方法切换到目标页面
        if self._next_index != -1:
            QStackedWidget.setCurrentIndex(self, self._next_index)
            
            # 确保当前窗口适应堆栈大小
            current_widget = self.currentWidget()
            if current_widget:
                current_widget.resize(self.size())
                
            self._next_index = -1
        
        # 释放快照资源
        self._current_widget_snapshot = None
        self._next_widget_snapshot = None
        
        # 更新所有子窗口的可见性
        for i in range(self.count()):
            widget = self.widget(i)
            if i == self.currentIndex():
                widget.setVisible(True)
            else:
                widget.setVisible(False)
        
        # 发射动画完成信号
        self.animationFinished.emit()
        
        # 强制更新
        self.update()
    
    def paintEvent(self, event):
        """绘制事件，用于实现自定义动画效果"""
        if not self._is_animating or not self._animations_enabled:
            # 如果没有动画，使用默认绘制
            super().paintEvent(event)
            return
        
        # 创建画笔
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._animation_type == self.ANIMATION_FADE:
            # 淡入淡出效果
            if self._current_widget_snapshot and self._next_widget_snapshot:
                # 绘制当前页面，随着动画进度降低透明度
                painter.setOpacity(1.0 - self._fade_value)
                painter.drawPixmap(0, 0, self._current_widget_snapshot)
                
                # 绘制下一页面，随着动画进度增加透明度
                painter.setOpacity(self._fade_value)
                painter.drawPixmap(0, 0, self._next_widget_snapshot)
        
        elif self._animation_type in [self.ANIMATION_LEFT_TO_RIGHT, self.ANIMATION_RIGHT_TO_LEFT]:
            # 水平滑动效果
            if self._current_widget_snapshot and self._next_widget_snapshot:
                if self._animation_type == self.ANIMATION_LEFT_TO_RIGHT:
                    # 从左到右：当前页面向右移动，新页面从左进入
                    current_x = self._horizontal_offset
                    next_x = self._horizontal_offset - self.width()
                else:
                    # 从右到左：当前页面向左移动，新页面从右进入
                    current_x = self._horizontal_offset
                    next_x = self._horizontal_offset + self.width()
                
                # 绘制当前页面
                painter.drawPixmap(int(current_x), 0, self._current_widget_snapshot)
                
                # 绘制下一页面
                painter.drawPixmap(int(next_x), 0, self._next_widget_snapshot)
        
        elif self._animation_type in [self.ANIMATION_TOP_TO_BOTTOM, self.ANIMATION_BOTTOM_TO_TOP]:
            # 垂直滑动效果
            if self._current_widget_snapshot and self._next_widget_snapshot:
                if self._animation_type == self.ANIMATION_TOP_TO_BOTTOM:
                    # 从上到下：当前页面向下移动，新页面从上进入
                    current_y = self._vertical_offset
                    next_y = self._vertical_offset - self.height()
                else:
                    # 从下到上：当前页面向上移动，新页面从下进入
                    current_y = self._vertical_offset
                    next_y = self._vertical_offset + self.height()
                
                # 绘制当前页面
                painter.drawPixmap(0, int(current_y), self._current_widget_snapshot)
                
                # 绘制下一页面
                painter.drawPixmap(0, int(next_y), self._next_widget_snapshot)
    
    def _handleResize(self, event):
        """处理尺寸变化事件"""
        # 调用父类的resizeEvent
        super().resizeEvent(event)
        
        # 如果没有在动画中，调整当前可见窗口的大小
        if not self._is_animating:
            current_widget = self.currentWidget()
            if current_widget:
                current_widget.resize(self.size())
        
        # 确保所有窗口在调整大小后仍然在正确位置
        self.update()

class AnimatedNavigationButton(QWidget):
    """
    动画导航按钮
    
    带有动画效果的导航按钮，用于SideNavigationMenu组件。
    采用扁平化设计，提供悬停和选中状态的动画效果。
    支持垂直和水平两种方向。
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, text="", icon=None, parent=None, orientation=0):
        super().__init__(parent)
        self.logger = get_logger("AnimatedNavigationButton")
        
        self._text = text
        self._icon = icon
        self._selected = False
        self._hovered = False
        self._orientation = orientation  # 0-垂直, 1-水平
        
        # 动画属性
        self._highlight_opacity = 0.0
        self._indicator_position = 0.0
        self._indicator_opacity = 0.0
        
        # 颜色设置
        self._primary_color = QColor(41, 128, 185)  # 主题蓝色
        self._text_color = QColor(120, 120, 120)    # 默认文本颜色
        self._text_selected_color = QColor(41, 128, 185)  # 选中文本颜色
        
        # 设置固定大小
        if self._orientation == 0:  # 垂直
            self.setFixedHeight(48)
            self.setMinimumWidth(160)
        else:  # 水平
            self.setFixedHeight(40)
            self.setMinimumWidth(100)
        
        # 设置鼠标样式
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 设置动画
        self._setup_animations()
        
        # 允许鼠标追踪
        self.setMouseTracking(True)
    
    def setOrientation(self, orientation):
        """设置按钮方向"""
        if self._orientation != orientation:
            self._orientation = orientation
            
            # 根据方向调整大小
            if self._orientation == 0:  # 垂直
                self.setFixedHeight(48)
                self.setMinimumWidth(160)
            else:  # 水平
                self.setFixedHeight(40)
                self.setMinimumWidth(100)
                
            self.update()
    
    def _setup_animations(self):
        """设置动画效果"""
        # 高亮动画
        self._highlight_animation = QPropertyAnimation(self, b"highlight_opacity")
        self._highlight_animation.setDuration(200)
        self._highlight_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 指示器位置动画
        self._indicator_pos_animation = QPropertyAnimation(self, b"indicator_position")
        self._indicator_pos_animation.setDuration(300)
        self._indicator_pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 指示器透明度动画
        self._indicator_opacity_animation = QPropertyAnimation(self, b"indicator_opacity")
        self._indicator_opacity_animation.setDuration(250)
        self._indicator_opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # 创建动画组
        self._indicator_animation_group = QParallelAnimationGroup()
        self._indicator_animation_group.addAnimation(self._indicator_pos_animation)
        self._indicator_animation_group.addAnimation(self._indicator_opacity_animation)
    
    def setText(self, text):
        """设置文本"""
        self._text = text
        self.update()
    
    def setIcon(self, icon):
        """设置图标"""
        self._icon = icon
        self.update()
    
    def setSelected(self, selected):
        """设置选中状态"""
        if self._selected != selected:
            self._selected = selected
            
            # 停止之前的动画
            self._indicator_animation_group.stop()
            
            # 设置指示器动画
            self._indicator_pos_animation.setStartValue(self._indicator_position)
            self._indicator_opacity_animation.setStartValue(self._indicator_opacity)
            
            if selected:
                self._indicator_pos_animation.setEndValue(1.0)
                self._indicator_opacity_animation.setEndValue(1.0)
            else:
                self._indicator_pos_animation.setEndValue(0.0)
                self._indicator_opacity_animation.setEndValue(0.0)
            
            # 启动动画组
            self._indicator_animation_group.start()
            
            self.update()
    
    def isSelected(self):
        """返回是否被选中"""
        return self._selected
    
    def sizeHint(self):
        """返回建议大小"""
        if self._orientation == 0:  # 垂直
            return QSize(180, 48)
        else:  # 水平
            return QSize(160, 40)  # 增加宽度以适应文字和图标左右排列
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self._hovered = True
        
        # 停止之前的动画
        self._highlight_animation.stop()
        
        # 设置高亮动画
        self._highlight_animation.setStartValue(self._highlight_opacity)
        self._highlight_animation.setEndValue(1.0)
        self._highlight_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._hovered = False
        
        # 停止之前的动画
        self._highlight_animation.stop()
        
        # 设置高亮动画
        self._highlight_animation.setStartValue(self._highlight_opacity)
        self._highlight_animation.setEndValue(0.0)
        self._highlight_animation.start()
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 发射点击信号
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制背景
        if self._highlight_opacity > 0:
            # 计算高亮颜色 - 使用主题色的透明版本
            highlight_color = QColor(self._primary_color)
            highlight_color.setAlphaF(0.1 * self._highlight_opacity)
            
            # 绘制高亮背景
            painter.fillRect(self.rect(), highlight_color)
        
        # 绘制指示器 (根据方向不同，位置不同)
        if self._indicator_opacity > 0:
            indicator_color = QColor(self._primary_color)
            indicator_color.setAlphaF(self._indicator_opacity)
            
            if self._orientation == 0:  # 垂直导航模式 - 指示器在左侧
                # 计算指示器几何形状
                indicator_height = self.height() * 0.7 * self._indicator_position
                indicator_y = (self.height() - indicator_height) / 2
                
                # 绘制指示器 - 使用QRectF可以接受浮点数
                indicator_rect = QRectF(0, indicator_y, 4, indicator_height)
                painter.fillRect(indicator_rect, indicator_color)
            else:  # 水平导航模式 - 指示器在底部
                # 计算指示器几何形状
                indicator_width = self.width() * 0.7 * self._indicator_position
                indicator_x = (self.width() - indicator_width) / 2
                
                # 绘制底部指示器
                indicator_rect = QRectF(indicator_x, self.height() - 4, indicator_width, 4)
                painter.fillRect(indicator_rect, indicator_color)
        
        # 绘制图标
        icon_size = 20 if self._orientation == 1 else 24
        has_valid_icon = self._icon and not self._icon.isNull()
        if has_valid_icon:
            if self._orientation == 0:  # 垂直
                icon_x = 20
                icon_y = (self.height() - icon_size) / 2
            else:  # 水平
                if self._text:
                    # 计算文本宽度
                    fm = painter.fontMetrics()
                    text_width = fm.horizontalAdvance(self._text)
                    # 为图标和文本计算总宽度和居中位置
                    total_width = icon_size + 6 + text_width  # 6像素的间距
                    start_x = (self.width() - total_width) / 2
                    icon_x = start_x
                    icon_y = (self.height() - icon_size) / 2
                else:
                    # 无文字，图标居中
                    icon_x = (self.width() - icon_size) / 2
                    icon_y = (self.height() - icon_size) / 2
            
            # 将浮点数转换为整数，避免QRect类型错误
            icon_rect = QRect(int(icon_x), int(icon_y), icon_size, icon_size)
            
            self._icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter, 
                          QIcon.Mode.Normal if not self._selected else QIcon.Mode.Selected)
        
        # 绘制文本
        if self._text:
            # 根据选中状态确定文本颜色
            if self._selected:
                text_color = self._text_selected_color
            else:
                # 如果悬停，则混合颜色
                if self._highlight_opacity > 0:
                    text_color = QColor(
                        int(self._text_color.red() * (1 - self._highlight_opacity) + self._text_selected_color.red() * self._highlight_opacity),
                        int(self._text_color.green() * (1 - self._highlight_opacity) + self._text_selected_color.green() * self._highlight_opacity),
                        int(self._text_color.blue() * (1 - self._highlight_opacity) + self._text_selected_color.blue() * self._highlight_opacity)
                    )
                else:
                    text_color = self._text_color
            
            painter.setPen(text_color)
            
            # 设置字体
            font = painter.font()
            font.setPointSize(10)
            font.setBold(self._selected)
            painter.setFont(font)
            
            # 文本位置（考虑图标）
            if self._orientation == 0:  # 垂直导航
                text_x = icon_size + 30 if has_valid_icon else 20
                text_rect = self.rect().adjusted(text_x, 0, -10, 0)
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._text)
            else:  # 水平导航
                if has_valid_icon:
                    # 有图标时，文字紧跟图标
                    fm = painter.fontMetrics()
                    text_width = fm.horizontalAdvance(self._text)
                    total_width = icon_size + 6 + text_width  # 6像素的间距
                    start_x = (self.width() - total_width) / 2
                    text_x = start_x + icon_size + 6
                    text_rect = QRect(int(text_x), 0, text_width, self.height())
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._text)
                else:
                    # 无图标时，文字完全居中
                    painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)
    
    # 动画属性定义
    def _get_highlight_opacity(self):
        return self._highlight_opacity
    
    def _set_highlight_opacity(self, opacity):
        self._highlight_opacity = opacity
        self.update()
    
    def _get_indicator_position(self):
        return self._indicator_position
    
    def _set_indicator_position(self, position):
        self._indicator_position = position
        self.update()
    
    def _get_indicator_opacity(self):
        return self._indicator_opacity
    
    def _set_indicator_opacity(self, opacity):
        self._indicator_opacity = opacity
        self.update()
    
    # 定义属性
    highlight_opacity = pyqtProperty(float, _get_highlight_opacity, _set_highlight_opacity)
    indicator_position = pyqtProperty(float, _get_indicator_position, _set_indicator_position)
    indicator_opacity = pyqtProperty(float, _get_indicator_opacity, _set_indicator_opacity)


class SideNavigationMenu(QWidget):
    """
    一个导航菜单组件，带有平滑的动画效果和扁平化设计风格。
    提供方便的页面切换功能，支持顶部和底部两个区域放置选项卡。
    支持垂直和水平两种方向，以及分组功能。
    """
    
    currentChanged = pyqtSignal(int)
    
    # 导航菜单位置常量
    POSITION_TOP = 0    # 顶部位置/左侧位置(水平模式)
    POSITION_BOTTOM = 1 # 底部位置/右侧位置(水平模式)
    
    # 导航菜单方向常量
    ORIENTATION_VERTICAL = 0   # 垂直方向
    ORIENTATION_HORIZONTAL = 1 # 水平方向
    
    def __init__(self, parent=None, orientation=ORIENTATION_VERTICAL):
        super().__init__(parent)
        self.logger = get_logger("SideNavigationMenu")
        
        # 设置方向
        self._orientation = orientation
        
        # 导航菜单数据结构
        self._buttons = []      # 导航按钮列表
        self._widgets = []      # 内容窗口列表
        self._positions = []    # 导航按钮位置列表
        self._groups = []       # 导航按钮分组信息
        self._current_index = -1   # 当前选中的导航按钮索引
        self._animations_enabled = True  # 是否启用动画
        
        # 分组结构
        self._group_containers = {}  # 存储分组容器
        
        # 设置UI
        self._setup_ui()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建主布局
        if self._orientation == self.ORIENTATION_VERTICAL:
            self._main_layout = QHBoxLayout(self)  # 垂直模式用水平布局
        else:
            self._main_layout = QVBoxLayout(self)  # 水平模式用垂直布局
            
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # 创建导航区域
        self._nav_area = QWidget()
        self._nav_area.setObjectName("navArea")
        
        if self._orientation == self.ORIENTATION_VERTICAL:
            # 垂直导航 - 菜单在左侧
            self._nav_area.setMinimumWidth(180)
            self._nav_area.setMaximumWidth(250)
            self._nav_layout = QVBoxLayout(self._nav_area)
        else:
            # 水平导航 - 菜单在顶部
            self._nav_area.setMinimumHeight(50)
            self._nav_area.setMaximumHeight(80)
            self._nav_layout = QHBoxLayout(self._nav_area)
            
        self._nav_layout.setContentsMargins(0, 10, 0, 10)
        self._nav_layout.setSpacing(5)
        
        # 创建位置容器
        self._top_container = QWidget()
        self._bottom_container = QWidget()
        
        if self._orientation == self.ORIENTATION_VERTICAL:
            self._top_layout = QVBoxLayout(self._top_container)
            self._bottom_layout = QVBoxLayout(self._bottom_container)
        else:
            self._top_layout = QHBoxLayout(self._top_container)
            self._bottom_layout = QHBoxLayout(self._bottom_container)
            
        self._top_layout.setContentsMargins(0, 0, 0, 0)
        self._top_layout.setSpacing(5)
        self._bottom_layout.setContentsMargins(0, 0, 0, 0)
        self._bottom_layout.setSpacing(5)
        
        # 添加位置容器到主导航菜单布局
        self._nav_layout.addWidget(self._top_container)
        
        if self._orientation == self.ORIENTATION_VERTICAL:
            self._nav_layout.addStretch(1)  # 垂直模式，底部区域固定在底部
        else:
            self._nav_layout.addStretch(1)  # 水平模式，右侧区域固定在右侧
            
        self._nav_layout.addWidget(self._bottom_container)
        
        # 内容窗口容器 - 使用动画堆栈组件
        self._stack = AnimatedStackedWidget()
        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_RIGHT_TO_LEFT)
        self._stack.setAnimationDuration(300)
        self._stack.setAnimationCurve(QEasingCurve.Type.OutCubic)
        
        # 添加到主布局
        if self._orientation == self.ORIENTATION_VERTICAL:
            self._main_layout.addWidget(self._nav_area, 0)  # 固定宽度
            self._main_layout.addWidget(self._stack, 1)     # 自动扩展
        else:
            self._main_layout.addWidget(self._nav_area, 0)  # 固定高度
            self._main_layout.addWidget(self._stack, 1)     # 自动扩展
        
        # 初始化分组容器
        self._createGroupContainers()
        
        # 设置样式
        self._apply_styles()
    
    def _apply_styles(self):
        """应用样式"""
        # 可以在这里设置QSS样式
        pass
    
    def _createGroupContainers(self):
        """创建分组容器"""
        # 默认创建两个基本分组：一个在TOP位置，一个在BOTTOM位置
        # 用户可以通过createGroup方法创建更多分组
        self._group_containers = {
            # 默认分组
            "default_top": {"position": self.POSITION_TOP, "widget": self._top_container, "layout": self._top_layout},
            "default_bottom": {"position": self.POSITION_BOTTOM, "widget": self._bottom_container, "layout": self._bottom_layout}
        }
    
    def createGroup(self, group_name, position=POSITION_TOP, title=None):
        """创建一个新的导航按钮分组
        
        Args:
            group_name: 分组名称，用于标识分组
            position: 分组位置，POSITION_TOP或POSITION_BOTTOM
            title: 分组标题，可选，会在分组上方显示
            
        Returns:
            bool: 创建是否成功
        """
        # 检查分组是否已存在
        if group_name in self._group_containers:
            self.logger.warning(f"分组已存在: {group_name}")
            return False
            
        # 创建分组容器
        group_container = QWidget()
        
        if self._orientation == self.ORIENTATION_VERTICAL:
            group_layout = QVBoxLayout(group_container)
        else:
            group_layout = QHBoxLayout(group_container)
            
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(5)
        
        # 如果有标题，添加标题标签
        if title:
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 根据方向设置标签样式
            if self._orientation == self.ORIENTATION_VERTICAL:
                title_label.setStyleSheet("font-size: 11px; color: #666; margin-top: 5px; margin-bottom: 2px; padding: 2px 5px;")
            else:
                title_label.setStyleSheet("font-size: 11px; color: #666; margin-right: 5px; padding: 2px 5px;")
                
            group_layout.addWidget(title_label)
        
        # 添加到对应位置的布局
        parent_container = self._top_container if position == self.POSITION_TOP else self._bottom_container
        parent_layout = self._top_layout if position == self.POSITION_TOP else self._bottom_layout
        
        # 添加分隔线（如果不是第一个分组）
        is_first_in_position = True
        for group_info in self._group_containers.values():
            if group_info["position"] == position:
                is_first_in_position = False
                break
                
        if not is_first_in_position:
            separator = QFrame()
            if self._orientation == self.ORIENTATION_VERTICAL:
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setFixedHeight(1)
                separator.setStyleSheet("background-color: #e0e0e0;")
            else:
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setFixedWidth(1)
                separator.setStyleSheet("background-color: #e0e0e0;")
            parent_layout.addWidget(separator)
        
        # 添加分组到布局
        parent_layout.addWidget(group_container)
        
        # 保存分组信息
        self._group_containers[group_name] = {
            "position": position,
            "widget": group_container,
            "layout": group_layout,
            "title": title
        }
        
        self.logger.debug(f"创建分组: {group_name}, 位置: {position}, 标题: {title}")
        return True
    
    def addPage(self, widget, text, icon=None, position=POSITION_TOP, group_name=None):
        """添加新的导航页面
        
        Args:
            widget: 页面内容窗口
            text: 页面文本
            icon: 页面图标（可选）
            position: 页面位置
            group_name: 分组名称，如不指定则使用默认分组
            
        Returns:
            int: 新页面的索引
        """
        # 创建导航按钮
        button = AnimatedNavigationButton(text, icon, parent=self, orientation=self._orientation)
        
        # 确定分组
        if group_name and group_name in self._group_containers:
            # 使用指定分组
            group_layout = self._group_containers[group_name]["layout"]
            group_layout.addWidget(button)
        else:
            # 使用默认分组
            if position == self.POSITION_TOP:
                self._top_layout.addWidget(button)
            elif position == self.POSITION_BOTTOM:
                self._bottom_layout.addWidget(button)
            else:
                # 如果位置无效，默认添加到顶部
                self.logger.warning(f"无效的页面位置: {position}，使用顶部位置代替")
                position = self.POSITION_TOP
                self._top_layout.addWidget(button)
                
            # 设置默认分组名称
            group_name = "default_top" if position == self.POSITION_TOP else "default_bottom"
        
        # 连接点击事件
        button.clicked.connect(lambda: self.setCurrentPage(self._buttons.index(button)))
        
        # 将内容窗口添加到堆栈
        self._stack.addWidget(widget)
        
        # 添加到列表
        self._buttons.append(button)
        self._widgets.append(widget)
        self._positions.append(position)
        self._groups.append(group_name)
        
        # 如果是第一个页面，设为当前页面
        if len(self._buttons) == 1:
            self.setCurrentPage(0)
        
        self.logger.debug(f"添加页面: {text}, 位置: {position}, 分组: {group_name}, 索引: {len(self._buttons) - 1}")
        
        # 返回新页面的索引
        return len(self._buttons) - 1
    
    def setCurrentPage(self, index):
        """设置当前页面
        
        Args:
            index: 页面索引
        """
        if index < 0 or index >= len(self._buttons):
            self.logger.warning(f"尝试设置无效的页面索引: {index}")
            return
        
        # 如果相同，不做任何事
        if self._current_index == index:
            return
        
        # 获取当前页面和目标页面的位置关系，决定动画方向
        if self._animations_enabled and self._current_index != -1:
            # 判断当前选项卡和目标选项卡的位置
            current_position = self._positions[self._current_index]
            target_position = self._positions[index]
            
            # 获取当前选项卡在其所在容器中的索引
            current_button = self._buttons[self._current_index]
            current_group = self._groups[self._current_index]
            current_container_layout = self._group_containers[current_group]["layout"]
            current_index_in_container = current_container_layout.indexOf(current_button)
            
            # 获取目标选项卡在其所在容器中的索引
            target_button = self._buttons[index]
            target_group = self._groups[index]
            target_container_layout = self._group_containers[target_group]["layout"]
            target_index_in_container = target_container_layout.indexOf(target_button)
            
            # 确定动画方向
            if self._orientation == self.ORIENTATION_VERTICAL:
                # 垂直模式的动画方向
                if current_position == target_position and current_group == target_group:
                    # 在同一个位置区域和同一分组内的切换
                    if current_index_in_container < target_index_in_container:
                        # 从上到下切换时，内容从下方进入
                        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_BOTTOM_TO_TOP)
                    else:
                        # 从下到上切换时，内容从上方进入
                        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_TOP_TO_BOTTOM)
                else:
                    # 跨位置区域或分组的切换
                    if current_position == self.POSITION_TOP and target_position == self.POSITION_BOTTOM:
                        # 从上方区域切换到下方区域，内容从下方进入
                        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_BOTTOM_TO_TOP)
                    else:
                        # 从下方区域切换到上方区域，内容从上方进入
                        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_TOP_TO_BOTTOM)
            else:
                # 水平模式的动画方向
                if current_position == target_position and current_group == target_group:
                    # 在同一个位置区域和同一分组内的切换
                    if current_index_in_container < target_index_in_container:
                        # 从左到右切换时，内容从右侧进入
                        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_RIGHT_TO_LEFT)
                    else:
                        # 从右到左切换时，内容从左侧进入
                        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_LEFT_TO_RIGHT)
                else:
                    # 跨位置区域或分组的切换
                    if current_position == self.POSITION_TOP and target_position == self.POSITION_BOTTOM:
                        # 从左侧区域切换到右侧区域，内容从右侧进入
                        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_RIGHT_TO_LEFT)
                    else:
                        # 从右侧区域切换到左侧区域，内容从左侧进入
                        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_LEFT_TO_RIGHT)
        
        # 更新当前索引
        old_index = self._current_index
        self._current_index = index
        
        self.logger.debug(f"切换页面: {old_index} -> {index}")
        
        # 更新按钮状态
        for i, button in enumerate(self._buttons):
            button.setSelected(i == index)
        
        # 切换堆栈窗口 - 使用动画效果
        if self._animations_enabled:
            # 使用动画堆栈组件的切换方法，自动应用动画效果
            self._stack.setCurrentIndex(index)
        else:
            # 禁用动画时，使用标准切换
            self._stack.setAnimationEnabled(False)
            self._stack.setCurrentIndex(index)
            self._stack.setAnimationEnabled(True)
        
        # 发射信号
        self.currentChanged.emit(index)
    
    def currentPageIndex(self):
        """返回当前页面索引"""
        return self._current_index
    
    def pageCount(self):
        """返回页面数量"""
        return len(self._buttons)
    
    def widget(self, index):
        """返回指定索引的内容窗口"""
        if index < 0 or index >= len(self._widgets):
            return None
        return self._widgets[index]
    
    def setPageText(self, index, text):
        """设置页面文本"""
        if index < 0 or index >= len(self._buttons):
            return
        self._buttons[index].setText(text)
    
    def setPageIcon(self, index, icon):
        """设置页面图标"""
        if index < 0 or index >= len(self._buttons):
            return
        self._buttons[index].setIcon(icon)
    
    def setAnimationsEnabled(self, enabled):
        """设置是否启用动画效果"""
        self._animations_enabled = enabled
        
    def setPagePosition(self, index, position, group_name=None):
        """更改已有页面的位置和分组
        
        Args:
            index: 页面索引
            position: 新位置
            group_name: 新分组名称，可选
        """
        if index < 0 or index >= len(self._buttons):
            self.logger.warning(f"尝试设置无效的页面索引位置: {index}")
            return
        
        # 检查位置值是否有效
        if position not in [self.POSITION_TOP, self.POSITION_BOTTOM]:
            self.logger.warning(f"无效的页面位置值: {position}，使用顶部位置")
            position = self.POSITION_TOP
        
        # 如果未指定分组，使用默认分组
        if not group_name or group_name not in self._group_containers:
            group_name = "default_top" if position == self.POSITION_TOP else "default_bottom"
        
        # 如果位置和分组都没变，不做任何事
        if self._positions[index] == position and self._groups[index] == group_name:
            return
        
        # 记录旧位置和分组
        old_position = self._positions[index]
        old_group = self._groups[index]
        button = self._buttons[index]
        
        # 从旧容器移除按钮
        old_container_layout = self._group_containers[old_group]["layout"]
        old_container_layout.removeWidget(button)
        
        # 添加到新容器
        new_container_layout = self._group_containers[group_name]["layout"]
        new_container_layout.addWidget(button)
        
        # 更新位置和分组记录
        self._positions[index] = position
        self._groups[index] = group_name
        
        self.logger.debug(f"页面 {index} 位置变更: {old_position} -> {position}, 分组: {old_group} -> {group_name}")
    
    def pagePosition(self, index):
        """获取页面的位置
        
        Args:
            index: 页面索引
            
        Returns:
            int: 页面位置 (POSITION_TOP 或 POSITION_BOTTOM)
        """
        if index < 0 or index >= len(self._positions):
            return self.POSITION_TOP  # 默认返回顶部位置
        return self._positions[index]
    
    def pageGroup(self, index):
        """获取页面的分组
        
        Args:
            index: 页面索引
            
        Returns:
            str: 页面分组名称
        """
        if index < 0 or index >= len(self._groups):
            return None
        return self._groups[index]


# 示例部分，仅在直接运行此文件时执行
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion样式以获得更好的跨平台一致性
    
    # 导入AnimatedButton类，只在测试代码中需要
    try:
        from ui.components.button import AnimatedButton
    except ImportError:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
        from ui.components.button import AnimatedButton
    
    # 主窗口
    window = QWidget()
    window.setWindowTitle("SideNavigationMenu 示例")
    window.resize(1000, 700)
    
    # 主布局
    main_layout = QVBoxLayout(window)
    
    # 切换演示模式的按钮
    mode_layout = QHBoxLayout()
    vertical_mode_btn = QPushButton("垂直导航模式")
    horizontal_mode_btn = QPushButton("水平导航模式")
    mode_layout.addWidget(vertical_mode_btn)
    mode_layout.addWidget(horizontal_mode_btn)
    main_layout.addLayout(mode_layout)
    
    # 创建堆栈来切换不同模式的演示
    demo_stack = QStackedWidget()
    main_layout.addWidget(demo_stack, 1)
    
    # 1. 垂直导航模式演示
    vertical_demo = QWidget()
    vertical_layout = QVBoxLayout(vertical_demo)
    
    # 创建垂直SideNavigationMenu
    nav_menu_vertical = SideNavigationMenu(orientation=SideNavigationMenu.ORIENTATION_VERTICAL)
    
    # 创建测试内容
    page1 = QWidget()
    page1_layout = QVBoxLayout(page1)
    page1_layout.addWidget(QLabel("控制台页面内容"))
    
    page2 = QWidget()
    page2_layout = QVBoxLayout(page2)
    page2_layout.addWidget(QLabel("设置页面内容"))
    
    page3 = QWidget()
    page3_layout = QVBoxLayout(page3)
    page3_layout.addWidget(QLabel("手势管理页面内容"))
    
    page4 = QWidget()
    page4_layout = QVBoxLayout(page4)
    page4_layout.addWidget(QLabel("偏好设置页面内容"))
    
    page5 = QWidget()
    page5_layout = QVBoxLayout(page5)
    page5_layout.addWidget(QLabel("帮助页面内容"))
    
    page6 = QWidget()
    page6_layout = QVBoxLayout(page6)
    page6_layout.addWidget(QLabel("关于页面内容"))
    
    # 创建图标
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/images')
    console_icon_path = os.path.join(icons_dir, 'console.svg')
    settings_icon_path = os.path.join(icons_dir, 'settings.svg')
    gestures_icon_path = os.path.join(icons_dir, 'gestures.svg')

    # 如果图标文件存在则使用，否则使用空图标
    console_icon = QIcon(console_icon_path) if os.path.exists(console_icon_path) else QIcon()
    settings_icon = QIcon(settings_icon_path) if os.path.exists(settings_icon_path) else QIcon()
    gestures_icon = QIcon(gestures_icon_path) if os.path.exists(gestures_icon_path) else QIcon()
    
    # 创建分组
    nav_menu_vertical.createGroup("main_features", nav_menu_vertical.POSITION_TOP, "主要功能")
    nav_menu_vertical.createGroup("settings", nav_menu_vertical.POSITION_TOP, "设置选项")
    nav_menu_vertical.createGroup("help", nav_menu_vertical.POSITION_BOTTOM, "帮助与支持")
    
    # 添加页面 - 使用分组
    nav_menu_vertical.addPage(page1, "控制台", console_icon, group_name="main_features")
    nav_menu_vertical.addPage(page3, "手势管理", gestures_icon, group_name="main_features")
    
    nav_menu_vertical.addPage(page2, "系统设置", settings_icon, group_name="settings")
    nav_menu_vertical.addPage(page4, "偏好设置", settings_icon, group_name="settings")
    
    nav_menu_vertical.addPage(page5, "帮助", QIcon(), nav_menu_vertical.POSITION_BOTTOM, "help")
    nav_menu_vertical.addPage(page6, "关于", QIcon(), nav_menu_vertical.POSITION_BOTTOM, "help")
    
    vertical_layout.addWidget(nav_menu_vertical)
    
    # 2. 水平导航模式演示
    horizontal_demo = QWidget()
    horizontal_layout = QVBoxLayout(horizontal_demo)
    
    # 创建水平SideNavigationMenu
    nav_menu_horizontal = SideNavigationMenu(orientation=SideNavigationMenu.ORIENTATION_HORIZONTAL)
    
    # 创建副本页面
    h_page1 = QWidget()
    h_page1_layout = QVBoxLayout(h_page1)
    h_page1_layout.addWidget(QLabel("控制台页面内容 (水平导航)"))
    
    h_page2 = QWidget()
    h_page2_layout = QVBoxLayout(h_page2)
    h_page2_layout.addWidget(QLabel("设置页面内容 (水平导航)"))
    
    h_page3 = QWidget()
    h_page3_layout = QVBoxLayout(h_page3)
    h_page3_layout.addWidget(QLabel("手势管理页面内容 (水平导航)"))
    
    h_page4 = QWidget()
    h_page4_layout = QVBoxLayout(h_page4)
    h_page4_layout.addWidget(QLabel("偏好设置页面内容 (水平导航)"))
    
    h_page5 = QWidget()
    h_page5_layout = QVBoxLayout(h_page5)
    h_page5_layout.addWidget(QLabel("帮助页面内容 (水平导航)"))
    
    h_page6 = QWidget()
    h_page6_layout = QVBoxLayout(h_page6)
    h_page6_layout.addWidget(QLabel("关于页面内容 (水平导航)"))
    
    # 创建分组 - 水平模式
    nav_menu_horizontal.createGroup("main_features", nav_menu_horizontal.POSITION_TOP, "主要功能")
    nav_menu_horizontal.createGroup("settings", nav_menu_horizontal.POSITION_TOP, "设置选项")
    nav_menu_horizontal.createGroup("help", nav_menu_horizontal.POSITION_BOTTOM, "帮助与支持")
    
    # 添加页面 - 水平模式
    nav_menu_horizontal.addPage(h_page1, "控制台", console_icon, group_name="main_features")
    nav_menu_horizontal.addPage(h_page3, "手势管理", gestures_icon, group_name="main_features")
    
    nav_menu_horizontal.addPage(h_page2, "系统设置", settings_icon, group_name="settings")
    nav_menu_horizontal.addPage(h_page4, "偏好设置", settings_icon, group_name="settings")
    
    nav_menu_horizontal.addPage(h_page5, "帮助", QIcon(), nav_menu_horizontal.POSITION_BOTTOM, "help")
    nav_menu_horizontal.addPage(h_page6, "关于", QIcon(), nav_menu_horizontal.POSITION_BOTTOM, "help")
    
    horizontal_layout.addWidget(nav_menu_horizontal)
    
    # 添加到堆栈
    demo_stack.addWidget(vertical_demo)
    demo_stack.addWidget(horizontal_demo)
    
    # 连接切换按钮
    vertical_mode_btn.clicked.connect(lambda: demo_stack.setCurrentIndex(0))
    horizontal_mode_btn.clicked.connect(lambda: demo_stack.setCurrentIndex(1))
    
    # 信息标签
    info = QLabel("""
    <html>
    <p style='text-align:center; margin-top:20px;'>
    SideNavigationMenu 是一个导航菜单组件，具有以下特点：<br/>
    - 支持垂直和水平两种方向<br/>
    - 支持导航分组功能<br/>
    - 扁平化设计<br/>
    - 流畅的切换动画效果<br/>
    - 页面的选中状态和悬停效果<br/>
    - 支持图标和文本<br/>
    - 符合应用主题风格<br/>
    - 支持页面位置设置：可将页面放置在顶部或底部<br/>
    </p>
    </html>
    """)
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(info)
    
    window.show()
    sys.exit(app.exec()) 