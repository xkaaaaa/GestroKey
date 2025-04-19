import sys
import os
from PyQt6.QtWidgets import (QWidget, QScrollBar, QScrollArea, QApplication, QVBoxLayout, 
                            QLabel, QFrame, QSizePolicy, QHBoxLayout)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QEvent, QRect, pyqtProperty, 
                         QPoint, QTimer, QSequentialAnimationGroup, QParallelAnimationGroup, 
                         QAbstractAnimation)
from PyQt6.QtGui import QPainter, QColor, QPalette, QPainterPath, QBrush

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from core.logger import get_logger


class AnimatedScrollBar(QScrollBar):
    """自定义动画滚动条，提供平滑动画效果和简洁界面"""
    
    def __init__(self, orientation=Qt.Orientation.Vertical, parent=None):
        super().__init__(orientation, parent)
        self.logger = get_logger("AnimatedScrollBar")
        
        # 初始化属性
        self._color_alpha = 180  # 初始透明度
        self._handle_position = 0
        self._normal_width = 10  # 正常宽度
        self._collapsed_width = 2  # 收缩宽度
        self._current_width = self._collapsed_width  # 当前宽度，初始为收缩状态
        self._orientation = orientation  # 保存方向
        
        # 定义滚动条样式参数
        self._primary_color = [41, 128, 185]  # 主题蓝色，与应用其他元素保持一致
        self._hover_color = [52, 152, 219]    # 悬停颜色（更亮的蓝色）
        self._bg_color = [240, 240, 240]      # 背景颜色（浅灰色）
        self._border_radius = 4               # 圆角半径
        self._handle_radius = 4               # 滑块圆角半径
        self._min_handle_length = 30          # 最小滑块长度
        self._is_hovered = False              # 悬停状态
        self._is_pressed = False              # 按下状态
        self._is_collapsed = True             # 收缩状态，初始为收缩状态
        self._animation_duration = 150        # 动画持续时间（毫秒）
        self._collapse_delay = 800            # 收缩延迟时间（毫秒）
        
        # 设置滚动条初始大小
        if orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(self._collapsed_width)  # 使用收缩宽度
        else:
            self.setFixedHeight(self._collapsed_width)  # 使用收缩宽度
        
        # 鼠标跟踪
        self.setMouseTracking(True)
        
        # 设置滚动条样式
        self.set_color_alpha(self._color_alpha)
        
        # 创建动画对象
        self._setupAnimations()
        
        # 创建收缩延迟定时器
        self._collapse_timer = QTimer(self)
        self._collapse_timer.setSingleShot(True)
        self._collapse_timer.timeout.connect(self._startCollapseAnimation)
        
        # 记录初始化完成
        self.logger.debug(f"{'垂直' if orientation == Qt.Orientation.Vertical else '水平'}滚动条初始化完成（折叠状态）")
    
    def _updateStyle(self):
        """更新滚动条样式"""
        # 通过样式表更新颜色
        r, g, b = self._primary_color
        alpha = self._color_alpha / 255.0
        
        # 根据当前宽度设置样式表
        width = int(self._current_width)  # 确保宽度是整数
        
        if self._orientation == Qt.Orientation.Vertical:
            self.setStyleSheet(f"""
                QScrollBar:vertical {{
                    border: none;
                    background-color: rgba({self._bg_color[0]}, {self._bg_color[1]}, {self._bg_color[2]}, 0);
                    width: {width}px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: rgba({r}, {g}, {b}, {alpha});
                    border-radius: {min(self._handle_radius, width//2)}px;
                    min-height: {self._min_handle_length}px;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    border: none;
                    background: none;
                    height: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
            """)
            self.setFixedWidth(width)
        else:
            self.setStyleSheet(f"""
                QScrollBar:horizontal {{
                    border: none;
                    background-color: rgba({self._bg_color[0]}, {self._bg_color[1]}, {self._bg_color[2]}, 0);
                    height: {width}px;
                    margin: 0px;
                }}
                QScrollBar::handle:horizontal {{
                    background-color: rgba({r}, {g}, {b}, {alpha});
                    border-radius: {min(self._handle_radius, width//2)}px;
                    min-width: {self._min_handle_length}px;
                }}
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                    border: none;
                    background: none;
                    width: 0px;
                }}
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                    background: none;
                }}
            """)
            self.setFixedHeight(width)
    
    def _setupAnimations(self):
        """设置动画对象"""
        # 悬停动画 - 透明度动画
        self._hover_animation = QPropertyAnimation(self, b"color_alpha")
        self._hover_animation.setDuration(self._animation_duration)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 按下动画
        self._press_animation = QPropertyAnimation(self, b"handle_position")
        self._press_animation.setDuration(self._animation_duration)
        self._press_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 折叠/展开动画 - 宽度动画
        self._width_animation = QPropertyAnimation(self, b"current_width")
        self._width_animation.setDuration(int(self._animation_duration * 1.5))  # 将浮点数转换为整数
        self._width_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self._is_hovered = True
        self._collapse_timer.stop()  # 停止收缩定时器
        
        # 如果处于收缩状态，立即展开
        if self._is_collapsed:
            self._startExpandAnimation()
        
        # 透明度动画
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self.color_alpha)
        self._hover_animation.setEndValue(255)  # 完全不透明
        self._hover_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._is_hovered = False
        
        # 如果不是按下状态，启动收缩定时器
        if not self._is_pressed:
            # 透明度动画
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self.color_alpha)
            self._hover_animation.setEndValue(180)  # 恢复半透明
            self._hover_animation.start()
            
            # 启动收缩延迟定时器
            self._collapse_timer.start(self._collapse_delay)
        
        super().leaveEvent(event)
    
    def _startCollapseAnimation(self):
        """开始收缩动画"""
        if not self._is_hovered and not self._is_pressed and not self._is_collapsed:
            self._width_animation.stop()
            self._width_animation.setStartValue(self._current_width)
            self._width_animation.setEndValue(self._collapsed_width)
            self._width_animation.finished.connect(self._onCollapseFinished)
            self._width_animation.start()
    
    def _startExpandAnimation(self):
        """开始展开动画"""
        if self._is_collapsed:
            self._width_animation.stop()
            self._width_animation.setStartValue(self._current_width)
            self._width_animation.setEndValue(self._normal_width)
            self._width_animation.finished.connect(self._onExpandFinished)
            self._width_animation.start()
    
    def _onCollapseFinished(self):
        """收缩动画完成回调"""
        self._is_collapsed = True
        self._width_animation.finished.disconnect(self._onCollapseFinished)
        self.logger.debug("滚动条已收缩")
    
    def _onExpandFinished(self):
        """展开动画完成回调"""
        self._is_collapsed = False
        self._width_animation.finished.disconnect(self._onExpandFinished)
        self.logger.debug("滚动条已展开")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = True
            self._press_animation.stop()
            self._collapse_timer.stop()  # 停止收缩定时器
            
            # 如果处于收缩状态，立即展开
            if self._is_collapsed:
                self._startExpandAnimation()
                
            # 更新样式以反映按下状态
            self._updateStyle()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_pressed = False
            self._press_animation.stop()
            
            # 如果鼠标不在滚动条上，启动收缩定时器
            if not self._is_hovered:
                self._collapse_timer.start(self._collapse_delay)
                
            # 更新样式以反映正常状态
            self._updateStyle()
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """滚轮事件 - 重置收缩定时器"""
        # 任何滚轮事件都会重置收缩定时器
        if self._is_collapsed:
            self._startExpandAnimation()
        else:
            self._collapse_timer.stop()
            self._collapse_timer.start(self._collapse_delay)
        
        # 更新值：直接使用事件的angleDelta来调整滚动条位置
        self.setValue(self.value() - event.angleDelta().y() // 3)
        
        # 阻止事件传播
        event.accept()
    
    # 自定义属性动画支持
    def get_color_alpha(self):
        """获取颜色透明度"""
        return self._color_alpha
    
    def set_color_alpha(self, alpha):
        """设置颜色透明度"""
        self._color_alpha = alpha
        self._updateStyle()
    
    def get_handle_position(self):
        """获取滑块位置"""
        return self._handle_position
    
    def set_handle_position(self, position):
        """设置滑块位置 - 用于动画效果"""
        self._handle_position = position
        self.update()
    
    def get_current_width(self):
        """获取当前宽度"""
        return self._current_width
    
    def set_current_width(self, width):
        """设置当前宽度 - 用于折叠/展开动画"""
        self._current_width = width
        self._updateStyle()
        self.update()
    
    # 定义可动画的属性
    color_alpha = pyqtProperty(int, get_color_alpha, set_color_alpha)
    handle_position = pyqtProperty(int, get_handle_position, set_handle_position)
    current_width = pyqtProperty(float, get_current_width, set_current_width)


class AnimatedScrollArea(QScrollArea):
    """自定义动画滚动区域，集成自定义滚动条"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("AnimatedScrollArea")
        
        # 设置框架样式
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        # 创建并设置自定义滚动条
        self.vertical_scrollbar = AnimatedScrollBar(Qt.Orientation.Vertical, self)
        self.horizontal_scrollbar = AnimatedScrollBar(Qt.Orientation.Horizontal, self)
        
        # 替换默认滚动条
        self.setVerticalScrollBar(self.vertical_scrollbar)
        self.setHorizontalScrollBar(self.horizontal_scrollbar)
        
        # 设置滚动条策略 - 默认按需显示
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 设置窗口部件可调整大小
        self.setWidgetResizable(True)
        
        # 平滑滚动相关
        self._smooth_scroll_animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self._smooth_scroll_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._smooth_scroll_animation.setDuration(300)  # 300毫秒的平滑滚动
        
        # 安装事件过滤器，以拦截滚动事件
        self.viewport().installEventFilter(self)
        
        # 记录初始化完成
        self.logger.debug("动画滚动区域初始化完成")
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于拦截滚轮事件以实现平滑滚动"""
        if obj is self.viewport() and event.type() == QEvent.Type.Wheel:
            # 阻止默认的瞬移行为
            if self._handleWheelEvent(event):
                return True
        return super().eventFilter(obj, event)
    
    def _handleWheelEvent(self, event):
        """处理滚轮事件，实现平滑滚动"""
        # 如果动画正在进行，停止它
        if self._smooth_scroll_animation.state() == QAbstractAnimation.State.Running:
            self._smooth_scroll_animation.stop()
        
        # 获取垂直滚动条
        scrollbar = self.verticalScrollBar()
        
        # 计算目标值（方向与标准滚动相反）
        delta = event.angleDelta().y()
        
        # 根据滚轮速度调整滚动速度 - 增加滚动速度
        delta_adjusted = delta  # 不再减半，使用完整的delta值
        
        # 计算目标滚动位置
        target_value = scrollbar.value() - delta_adjusted
        
        # 确保目标值在有效范围内
        target_value = max(scrollbar.minimum(), min(target_value, scrollbar.maximum()))
        
        # 设置动画
        self._smooth_scroll_animation.setStartValue(scrollbar.value())
        self._smooth_scroll_animation.setEndValue(target_value)
        
        # 启动动画
        self._smooth_scroll_animation.start()
        
        # 返回True表示已处理事件
        return True
    
    def setVerticalScrollBarPolicy(self, policy):
        """设置垂直滚动条策略"""
        super().setVerticalScrollBarPolicy(policy)
        if policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOff:
            self.logger.debug("垂直滚动条已禁用")
        elif policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOn:
            self.logger.debug("垂直滚动条始终显示")
        else:
            self.logger.debug("垂直滚动条按需显示")
    
    def setHorizontalScrollBarPolicy(self, policy):
        """设置水平滚动条策略"""
        super().setHorizontalScrollBarPolicy(policy)
        if policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOff:
            self.logger.debug("水平滚动条已禁用")
        elif policy == Qt.ScrollBarPolicy.ScrollBarAlwaysOn:
            self.logger.debug("水平滚动条始终显示")
        else:
            self.logger.debug("水平滚动条按需显示")


# 以下代码用于测试滚动条组件
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QWidget()
    window.setWindowTitle("动画滚动条测试")
    window.resize(400, 500)
    
    # 创建布局
    layout = QVBoxLayout(window)
    
    # 添加标题
    title = QLabel("增强版动画滚动条演示")
    title.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # 添加功能说明
    features = QLabel("特性：1. 鼠标离开时自动折叠为细线  2. 平滑滚动效果")
    features.setStyleSheet("font-size: 10pt; margin-bottom: 15px;")
    features.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(features)
    
    # 创建使用自定义滚动区域的测试部分
    scroll_area = AnimatedScrollArea()
    
    # 创建内容窗口部件
    content = QWidget()
    content_layout = QVBoxLayout(content)
    
    # 添加多个标签以产生滚动效果
    for i in range(50):
        label = QLabel(f"测试项目 {i+1}")
        label.setStyleSheet("font-size: 14pt; padding: 10px;")
        label.setFixedHeight(40)
        if i % 2 == 0:
            label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        content_layout.addWidget(label)
    
    # 设置内容到滚动区域
    scroll_area.setWidget(content)
    
    # 添加到主布局
    layout.addWidget(scroll_area)
    
    # 显示窗口
    window.show()
    
    sys.exit(app.exec()) 