import sys
import os
from PyQt6.QtWidgets import (QLineEdit, QApplication, QWidget, QVBoxLayout, 
                            QGraphicsDropShadowEffect, QLabel, QHBoxLayout,
                            QPushButton, QGraphicsOpacityEffect)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty, 
                         pyqtSignal, QRect, QSequentialAnimationGroup, QParallelAnimationGroup, 
                         QTimer, QPoint, QRectF, QEvent, QLineF)
from PyQt6.QtGui import (QColor, QPainter, QFont, QPainterPath, QBrush, QPen, 
                        QIcon, QPixmap, QPalette, QValidator, QLinearGradient, QFontMetrics, QAction)

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

# 禁用PNG警告
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*libpng warning.*")

# 定义属性的 getter 和 setter 方法
def _get_label_position(self):
    """获取标签位置"""
    return self._label_widget.pos()

def _set_label_position(self, pos):
    """设置标签位置"""
    self._label_widget.move(pos)

def _get_label_size(self):
    """获取标签大小"""
    size = self._label_widget.font().pointSizeF()
    return max(size, 10.0)  # 确保返回值大于0

def _set_label_size(self, size):
    """设置标签大小"""
    # 确保字体大小大于0，防止出现负值或0导致错误
    size = max(size, 10.0)  # 设置最小字体大小为10
    font = self._label_widget.font()
    font.setPointSizeF(size)
    self._label_widget.setFont(font)

def _get_label_color(self):
    """获取标签颜色"""
    return self._label_widget.palette().color(QPalette.WindowText)

def _set_label_color(self, color):
    """设置标签颜色"""
    palette = self._label_widget.palette()
    palette.setColor(QPalette.WindowText, color)
    self._label_widget.setPalette(palette)

def _get_border_color(self):
    """获取边框颜色"""
    return self._current_border_color

def _set_border_color(self, color):
    """设置边框颜色"""
    self._current_border_color = color
    
    # 立即更新容器样式，使颜色变化更平滑
    container = self.findChild(QWidget, "InputContainer")
    if container:
        container.setStyleSheet(f"""
            QWidget#InputContainer {{
                background-color: {self._background_color.name()};
                border: 1px solid {color.name()};
                border-radius: 6px;
            }}
        """)
    
    # 触发重绘
    self.update()

def _get_border_width(self):
    """获取边框宽度"""
    return self._border_width

def _set_border_width(self, width):
    """设置边框宽度"""
    self._border_width = width
    self.update()  # 触发重绘

def _get_shadow_strength(self):
    """获取阴影强度"""
    container = self.findChild(QWidget, "InputContainer")
    if container and container.graphicsEffect():
        return container.graphicsEffect().blurRadius()
    return 0

def _set_shadow_strength(self, strength):
    """设置阴影强度"""
    container = self.findChild(QWidget, "InputContainer")
    if container and container.graphicsEffect():
        shadow = container.graphicsEffect()
        shadow.setBlurRadius(strength)
        # 调整阴影透明度
        opacity = min(30 + strength * 5, 80)  # 透明度随着模糊半径增加
        shadow.setColor(QColor(self._current_shadow_color.red(),
                            self._current_shadow_color.green(),
                            self._current_shadow_color.blue(),
                            int(opacity)))

def _update_font_size(self):
    """更新字体大小"""
    font = self._label_widget.font()
    current_size = font.pointSizeF()
    if current_size <= 0:
        current_size = 13.0 if not (self._has_text or self._is_focused) else 11.0
        font.setPointSizeF(current_size)
        self._label_widget.setFont(font)
    return font

class AnimatedInputField(QWidget):
    """
    带动画效果的输入框组件
    
    特性：
    - 标签文本动画：输入时标签文本缩小并移至顶部
    - 边框样式动画：聚焦和失焦时边框颜色和阴影动画
    - 支持验证状态：可显示成功/错误状态和消息
    """
    # 自定义信号
    textChanged = pyqtSignal(str)  # 文本变化信号，参数：新文本
    textEdited = pyqtSignal(str)   # 文本编辑信号（仅用户输入），参数：新文本
    focusChanged = pyqtSignal(bool)  # 焦点变化信号，参数：是否获得焦点
    
    # 属性动画支持
    label_position = pyqtProperty(QPoint, _get_label_position, _set_label_position)
    label_size = pyqtProperty(float, _get_label_size, _set_label_size)
    label_color = pyqtProperty(QColor, _get_label_color, _set_label_color)
    border_color = pyqtProperty(QColor, _get_border_color, _set_border_color)
    border_width = pyqtProperty(float, _get_border_width, _set_border_width)
    shadow_strength = pyqtProperty(float, _get_shadow_strength, _set_shadow_strength)
    
    def __init__(self, parent=None, placeholder="", label=None, border_color=None, focus_color=None, 
                 error_color=None, success_color=None, text_color=None, label_color=None, border_radius=8):
        """
        初始化输入框组件
        
        Args:
            parent: 父组件
            placeholder (str): 占位符文本
            label (str): 标签文本，如果不设置则使用placeholder
            border_color (list/str): 边框颜色，RGB列表[r,g,b]或颜色字符串"#RRGGBB"
            focus_color (list/str): 聚焦时边框颜色
            error_color (list/str): 错误状态颜色
            success_color (list/str): 成功状态颜色
            text_color (list/str): 文本颜色
            label_color (list/str): 标签颜色
            border_radius (int): 边框圆角半径
        """
        super().__init__(parent)
        self.logger = get_logger("AnimatedInputField")
        self.logger.debug(f"初始化输入框: {placeholder}")
        
        # 保存基本参数
        self._placeholder = placeholder
        self._label = label if label else placeholder
        self._border_radius = border_radius
        
        # 设置颜色
        self._border_color = self._parse_color(border_color) if border_color else QColor(208, 215, 222)  # 默认边框颜色 #D0D7DE
        self._focus_color = self._parse_color(focus_color) if focus_color else QColor(33, 136, 255)      # 默认聚焦颜色 #2188FF
        self._error_color = self._parse_color(error_color) if error_color else QColor(255, 99, 71)       # 默认错误颜色 #FF6347
        self._success_color = self._parse_color(success_color) if success_color else QColor(46, 204, 113) # 默认成功颜色 #2ECC71
        self._text_color = self._parse_color(text_color) if text_color else QColor(36, 41, 47)          # 默认文本颜色 #24292F
        self._label_color = self._parse_color(label_color) if label_color else QColor(110, 119, 129)     # 默认标签颜色 #6E7781
        self._disabled_color = QColor(200, 200, 200)  # 禁用状态颜色 #C8C8C8
        self._hover_color = QColor("#D0D7DE")  # 初始化悬停颜色
        self._background_color = QColor("white")  # 初始化背景颜色
        
        # 状态变量
        self._is_focused = False
        self._has_text = False
        self._is_valid = True      # 保留但不使用
        self._is_disabled = False  # 新增禁用状态标志
        self._animation_in_progress = False
        self._label_opacity = 1.0
        self._border_width = 0.3  # 默认边框宽度，单位：mm
        self._current_border_color = self._border_color
        self._current_shadow_color = self._focus_color
        
        # 波纹动画相关
        self._last_click_pos = QPoint(0, 0)  # 记录最后一次点击位置
        self._ripple_opacity = 0.0
        self._ripple_radius = 0
        self._ripple_position = QPoint(0, 0)
        self._ripple_animation = None
        self._ripple_color = self._focus_color.lighter(130)
        
        # 预先初始化动画对象以避免AttributeError
        self._label_pos_animation = None
        self._label_size_animation = None
        self._border_color_animation = None
        self._border_width_animation = None
        self._hover_color_animation = None
        self._bg_color_animation = None
        self._shadow_animation = None
        self._focus_animation_group = None
        
        # 初始化属性
        self._setup_properties()
        
        # 创建布局和控件
        self._create_widgets()
        self._setup_animations() # 这里初始化所有动画
        self._setup_layout()
        
        # 立即强制居中标签，确保初始状态正确
        self._force_center_label()
        
        # 设置连接
        self._setup_connections()
        
        # 初始样式
        self._update_styles()
        
        # 确保标签居中对齐 - 使用多次调用，确保标签能够正确居中
        # 第一轮立即尝试
        QTimer.singleShot(0, self._force_center_label)
        # 第二轮在组件布局计算完成后尝试
        QTimer.singleShot(10, self._force_center_label)
        QTimer.singleShot(50, self._force_center_label)
        QTimer.singleShot(100, self._force_center_label)
        QTimer.singleShot(200, self._force_center_label)
        # 第三轮在窗口可能完全显示后再次尝试
        QTimer.singleShot(500, self._force_center_label)
        QTimer.singleShot(1000, self._force_center_label)
        
        # 确保在初始状态下标签可见且透明度正常
        self._label_widget.setVisible(True)
        
        # 添加布局变化监听
        self.installEventFilter(self)
    
    def _parse_color(self, color):
        """解析颜色参数，支持RGB列表和十六进制颜色字符串"""
        if isinstance(color, list) and len(color) >= 3:
            alpha = color[3] if len(color) > 3 else 255
            return QColor(color[0], color[1], color[2], alpha)
        elif isinstance(color, str) and color.startswith("#"):
            return QColor(color)
        else:
            self.logger.warning(f"不支持的颜色格式: {color}，使用默认颜色")
            return QColor(208, 215, 222)  # 默认边框颜色
    
    def _create_widgets(self):
        """创建组件"""
        # 创建输入框
        self._line_edit = QLineEdit(self)
        self._line_edit.setPlaceholderText("")  # 清空默认占位符，我们使用自定义标签
        self._line_edit.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)  # 移除macOS上的聚焦矩形
        self._line_edit.setFrame(False)  # 移除默认边框
        self._line_edit.setCursorMoveStyle(Qt.CursorMoveStyle.LogicalMoveStyle)  # 确保光标移动逻辑一致
        
        # 设置鼠标光标为文本光标样式
        self._line_edit.setCursor(Qt.CursorShape.IBeamCursor)  # 使用标准的I形状文本编辑光标
        
        # 创建标签 - 强制设置文本居中对齐
        self._label_widget = QLabel(self._label, self)
        self._label_widget.setObjectName("AnimatedLabel")
        self._label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置文本居中对齐
        self._label_widget.setTextFormat(Qt.TextFormat.PlainText)   # 使用纯文本格式
        # 设置省略号模式
        self._label_widget.setWordWrap(False)  # 禁用自动换行
        self._label_widget.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)  # 禁用文本交互
        
        # 强制设置标签居中样式，确保覆盖所有情况
        self._label_widget.setStyleSheet("""
            QLabel#AnimatedLabel {
                qproperty-alignment: AlignCenter;
                text-align: center;
            }
        """)
        
        # 创建波纹效果容器
        self._ripple_container = QWidget(self)
        self._ripple_container.setObjectName("RippleContainer")
        self._ripple_container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)  # 鼠标事件穿透
        self._ripple_container.setStyleSheet("background: transparent;")
        self._ripple_container.setVisible(True)
        
        # 波纹效果相关变量
        self._ripple_opacity = 0.0
        self._ripple_radius = 0
        self._ripple_position = QPoint(0, 0)
        self._ripple_animation = None
        self._ripple_color = self._focus_color.lighter(130)
    
    def _setup_animations(self):
        """设置动画"""
        # 标签位置动画
        self._label_pos_animation = QPropertyAnimation(self._label_widget, b"pos", self)
        self._label_pos_animation.setDuration(300)
        self._label_pos_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 标签大小动画 - 修改为fontSize属性
        self._label_size_animation = QPropertyAnimation(self, b"label_size", self)
        self._label_size_animation.setDuration(300)
        self._label_size_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 边框颜色动画 - 增加持续时间，使边框颜色变化更加明显
        self._border_color_animation = QPropertyAnimation(self, b"border_color", self)
        self._border_color_animation.setDuration(400) # 增加为400ms，使颜色渐变更流畅
        self._border_color_animation.setEasingCurve(QEasingCurve.Type.OutCubic) # 使用OutCubic缓动，更平滑
        
        # 边框宽度动画
        self._border_width_animation = QPropertyAnimation(self, b"border_width", self)
        self._border_width_animation.setDuration(300)
        self._border_width_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 悬停动画
        self._hover_color_animation = QPropertyAnimation(self, b"hover_color", self)
        self._hover_color_animation.setDuration(300)
        self._hover_color_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 背景颜色动画
        self._bg_color_animation = QPropertyAnimation(self, b"background_color", self)
        self._bg_color_animation.setDuration(300)
        self._bg_color_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 阴影动画
        self._shadow_animation = QPropertyAnimation(self, b"shadow_strength", self)
        self._shadow_animation.setDuration(300)
        self._shadow_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # 创建动画组
        self._focus_animation_group = QParallelAnimationGroup(self)
        self._focus_animation_group.addAnimation(self._label_pos_animation)
        self._focus_animation_group.addAnimation(self._label_size_animation)
        self._focus_animation_group.addAnimation(self._border_color_animation)
        self._focus_animation_group.addAnimation(self._border_width_animation)
        self._focus_animation_group.addAnimation(self._shadow_animation)
    
    def _setup_layout(self):
        """设置布局"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建输入框容器
        container = QWidget(self)
        container.setObjectName("InputContainer")
        container.setMinimumHeight(32)  # 减小容器高度
        
        # 设置容器为可点击
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        container.setCursor(Qt.CursorShape.IBeamCursor)  # 设置文本输入光标
        
        # 创建容器布局
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(8, 0, 8, 0)  # 减小左右内边距
        container_layout.setSpacing(0)
        
        # 添加输入框到容器
        container_layout.addWidget(self._line_edit)
        
        # 添加容器到主布局
        main_layout.addWidget(container)
        
        # 设置波纹容器
        self._ripple_container.setParent(container)
        self._ripple_container.resize(container.size())
        self._ripple_container.move(0, 0)
        
        # 设置标签
        self._label_widget.setParent(container)
        
        # 强制设置标签居中对齐
        self._label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 初始化标签位置 (水平居中)
        container_width = container.width() if container.width() > 0 else 200
        label_width = container_width - 12
        self._label_widget.setFixedWidth(label_width)
        
        # 计算水平居中位置和垂直居中位置
        x_pos = (container_width - label_width) // 2
        container_height = container.height() if container.height() > 0 else 32
        
        # 确保container_height是有效值
        if container_height <= 0:
            container_height = 32
            
        if self._has_text or self._is_focused:
            y_pos = 1  # 上边距
        else:
            # 使用更精确的方式计算垂直居中位置
            font = self._label_widget.font()
            # 确保字体大小有效
            if font.pointSizeF() <= 0:
                font.setPointSizeF(13.0)
                self._label_widget.setFont(font)
                
            metrics = QFontMetrics(font)
            text_height = metrics.height()
            
            # 如果无法获取文本高度，使用默认值
            if text_height <= 0:
                text_height = 14
                
            y_pos = (container_height - text_height) // 2
            
            # 确保y_pos在合理范围内
            if y_pos < 0 or y_pos >= container_height:
                y_pos = container_height // 2 - 7  # 更准确的垂直居中位置
                
        self.logger.debug(f"标签初始位置计算: container_height={container_height}, y_pos={y_pos}")
        
        # 设置标签位置
        self._label_widget.move(x_pos, y_pos)
        
        # 设置标签透明度正常
        self._label_opacity = 1.0
        self._label_widget.setVisible(True)
        
        self._label_widget.raise_()  # 确保标签在最上层
        
        # 设置输入框样式
        self._line_edit.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                padding: 6px 0;
                color: #24292F;
            }
        """)
        
        # 设置容器样式
        container.setStyleSheet("""
            QWidget#InputContainer {
                background-color: white;
                border: 1px solid #D0D7DE;
                border-radius: 4px;
            }
        """)
        
        # 设置标签样式
        font = self._label_widget.font()
        font.setPointSize(13)  # 使用setPointSize而不是setPointSizeF
        self._label_widget.setFont(font)
        
        # 应用文本截断和省略号处理
        truncated_text = self._truncate_text_with_ellipsis(self._label, label_width, font)
        self._label_widget.setText(truncated_text)
        
        self._label_widget.setStyleSheet("""
            QLabel#AnimatedLabel {
                color: #6E7781;
                background-color: transparent;
                qproperty-alignment: AlignCenter;
                text-align: center;
            }
        """)
        
        # 应用阴影效果
        self._apply_shadow()
        
        # 立即强制刷新标签位置
        self._ensure_label_centered()

    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获各种事件"""
        if obj == self:
            if event.type() == QEvent.Type.Resize:
                # 窗口大小变化时重新居中标签
                QTimer.singleShot(0, self._force_center_label)
            elif event.type() == QEvent.Type.Show:
                # 窗口显示时重新居中标签
                QTimer.singleShot(0, self._force_center_label)
                QTimer.singleShot(50, self._force_center_label)  # 额外保证
        elif obj == self.findChild(QWidget, "InputContainer") or obj == self._line_edit:
            if event.type() == QEvent.Type.MouseButtonPress:
                # 如果点击的是输入框容器或输入框本身，设置焦点
                self._line_edit.setFocus()
                return True
            elif event.type() == QEvent.Type.Enter:
                # 鼠标进入时的动画
                if not self._is_focused and obj == self.findChild(QWidget, "InputContainer"):
                    self._hover_color_animation.stop()
                    self._bg_color_animation.stop()
                    self._hover_color_animation.setStartValue(QColor("#D0D7DE"))
                    self._hover_color_animation.setEndValue(QColor("#0969DA"))
                    self._bg_color_animation.setStartValue(QColor("white"))
                    self._bg_color_animation.setEndValue(QColor("#F6F8FA"))
                    self._hover_color_animation.start()
                    self._bg_color_animation.start()
                return False
            elif event.type() == QEvent.Type.Leave:
                # 鼠标离开时的动画
                if not self._is_focused and obj == self.findChild(QWidget, "InputContainer"):
                    self._hover_color_animation.stop()
                    self._bg_color_animation.stop()
                    self._hover_color_animation.setStartValue(QColor("#0969DA"))
                    self._hover_color_animation.setEndValue(QColor("#D0D7DE"))
                    self._bg_color_animation.setStartValue(QColor("#F6F8FA"))
                    self._bg_color_animation.setEndValue(QColor("white"))
                    self._hover_color_animation.start()
                    self._bg_color_animation.start()
                return False
                
        return super().eventFilter(obj, event)

    def _ensure_label_centered(self):
        """确保标签居中显示"""
        container = self.findChild(QWidget, "InputContainer")
        if not container:
            self.logger.warning("无法找到InputContainer，无法居中标签")
            return
            
        # 确保标签所有者正确
        if self._label_widget.parent() != container:
            self._label_widget.setParent(container)
            self._label_widget.show()  # 确保标签可见
            
        # 强制设置标签对齐方式
        self._label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置标签宽度
        container_width = container.width()
        if container_width <= 0:
            container_width = 200  # 默认宽度
            self.logger.debug(f"容器宽度无效，使用默认宽度: {container_width}")
            
        label_width = container_width - 12  # 减小左右边距
        self._label_widget.setFixedWidth(label_width)
            
        # 计算水平居中位置
        x_pos = (container_width - label_width) // 2
            
        # 计算垂直位置
        container_height = container.height()
        if container_height <= 0:
            container_height = 32  # 默认高度
            self.logger.debug(f"容器高度无效，使用默认高度: {container_height}")
            
        # 垂直位置：有文本或聚焦时固定在顶部，否则居中
        if self._has_text or self._is_focused:
            y_pos = 1  # 减小顶部边距
        else:
            # 获取标签实际高度，如果不可用则使用固定值
            label_height = self._label_widget.height()
            if label_height <= 0:
                label_height = 14  # 使用更准确的标签高度
            
            # 精确计算垂直居中位置
            y_pos = (container_height - label_height) // 2
            
            # 确保y_pos在合理范围内，防止极端值
            if y_pos < 0 or y_pos > container_height:
                y_pos = container_height // 2 - 7  # 强制居中作为后备方案
                
        # 设置新位置
        self._label_widget.move(x_pos, y_pos)
        self.logger.debug(f"标签新位置: x={x_pos}, y={y_pos}, 宽度={label_width}, 容器高度={container_height}")
            
        # 获取标签字体
        font = self._label_widget.font()
        font.setPointSize(13 if not (self._has_text or self._is_focused) else 11)  # 使用setPointSize而不是setPointSizeF
        self._label_widget.setFont(font)
        
        # 应用文本省略处理
        truncated_text = self._truncate_text_with_ellipsis(self._label, label_width, font)
        if truncated_text != self._label_widget.text():
            self._label_widget.setText(truncated_text)
        
        # 确保居中样式应用
        if self._is_disabled:
            self._label_widget.setStyleSheet(f"""
                QLabel#AnimatedLabel {{
                    color: {self._disabled_color.name()};
                    background-color: transparent;
                    qproperty-alignment: AlignCenter;
                    text-align: center;
                }}
            """)
        else:
            label_color = self._focus_color if self._is_focused else self._label_color
            self._label_widget.setStyleSheet(f"""
                QLabel#AnimatedLabel {{
                    color: {label_color.name()};
                    background-color: transparent;
                    qproperty-alignment: AlignCenter;
                    text-align: center;
                }}
            """)

    def _ensure_initial_state(self):
        """确保初始状态正确设置"""
        # 更新样式
        self._update_styles()
        
        # 确保标签居中
        self._ensure_label_centered()
        
        # 确保动画属性有初始值
        if not self._has_text and not self._is_focused:
            # 默认未聚焦且无文本状态
            current_pos = self._label_widget.pos()
            self._label_pos_animation.setStartValue(current_pos)
            self._label_pos_animation.setEndValue(current_pos)  # 使用相同值，避免动画
            
            # 确保字体大小有效
            current_font = self._label_widget.font()
            current_size = current_font.pointSizeF() 
            # 确保字体大小大于0
            if current_size <= 0:
                current_size = 14.0
                
            self._label_size_animation.setStartValue(current_size)
            self._label_size_animation.setEndValue(current_size)  # 使用相同值，避免动画
            
            # 设置边框颜色动画的初始值
            self._border_color_animation.setStartValue(self._border_color)
            self._border_color_animation.setEndValue(self._border_color)
            
            # 设置边框宽度动画的初始值
            self._border_width_animation.setStartValue(self._border_width)
            self._border_width_animation.setEndValue(self._border_width)
            
            # 设置悬停颜色动画的初始值
            self._hover_color_animation.setStartValue(self._border_color)
            self._hover_color_animation.setEndValue(self._border_color)
            
            # 设置背景颜色动画的初始值
            self._bg_color_animation.setStartValue(QColor("white"))
            self._bg_color_animation.setEndValue(QColor("white"))
            
            # 安全获取InputContainer和它的阴影效果
            input_container = self.findChild(QWidget, "InputContainer")
            if input_container:
                shadow = input_container.graphicsEffect()
                if shadow and isinstance(shadow, QGraphicsDropShadowEffect):
                    current_blur = shadow.blurRadius()
                    self._shadow_animation.setStartValue(current_blur)
                    self._shadow_animation.setEndValue(current_blur)
                else:
                    # 如果没有阴影，使用默认值
                    self._shadow_animation.setStartValue(0)
                    self._shadow_animation.setEndValue(0)
            else:
                # 如果没有找到容器，使用默认值
                self._shadow_animation.setStartValue(0)
                self._shadow_animation.setEndValue(0)
    
        # 更新标签样式
        if self._is_disabled:
            self._label_widget.setStyleSheet(f"""
                QLabel#AnimatedLabel {{
                    color: {self._disabled_color.name()};
                    background-color: transparent;
                    qproperty-alignment: AlignCenter;
                    text-align: center;
                }}
            """)
        else:
            label_color = self._focus_color if self._is_focused else self._label_color
            self._label_widget.setStyleSheet(f"""
                QLabel#AnimatedLabel {{
                    color: {label_color.name()};
                    background-color: transparent;
                    qproperty-alignment: AlignCenter;
                    text-align: center;
                }}
            """)

    def _update_styles(self):
        """更新样式"""
        # 获取输入框容器
        container = self.findChild(QWidget, "InputContainer")
        if not container:
            return
            
        # 更新容器样式
        if self._is_disabled:
            container.setStyleSheet(f"""
                QWidget#InputContainer {{
                    background-color: #F6F8FA;
                    border: 1px solid {self._disabled_color.name()};
                    border-radius: 6px;
                }}
            """)
        else:
            container.setStyleSheet(f"""
                QWidget#InputContainer {{
                    background-color: white;
                    border: 1px solid {self._current_border_color.name()};
                    border-radius: 6px;
                }}
            """)
        
        # 更新输入框样式
        if self._is_disabled:
            self._line_edit.setStyleSheet(f"""
                QLineEdit {{
                    background-color: transparent;
                    border: none;
                    padding: 8px 0;
                    color: {self._disabled_color.name()};
                }}
            """)
        else:
            self._line_edit.setStyleSheet(f"""
                QLineEdit {{
                    background-color: transparent;
                    border: none;
                    padding: 8px 0;
                    color: {self._text_color.name()};
                }}
            """)
        
        # 更新标签样式
        if self._is_disabled:
            self._label_widget.setStyleSheet(f"""
                QLabel#AnimatedLabel {{
                    color: {self._disabled_color.name()};
                    background-color: transparent;
                    qproperty-alignment: AlignCenter;
                    text-align: center;
                }}
            """)
        else:
            label_color = self._focus_color if self._is_focused else self._label_color
            self._label_widget.setStyleSheet(f"""
                QLabel#AnimatedLabel {{
                    color: {label_color.name()};
                    background-color: transparent;
                    qproperty-alignment: AlignCenter;
                    text-align: center;
                }}
            """)
        
        # 应用阴影效果
        self._apply_shadow()
    
    def _apply_shadow(self):
        """应用阴影效果"""
        container = self.findChild(QWidget, "InputContainer")
        if not container:
            return
            
        # 创建或更新阴影效果
        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(8)  # 增加模糊半径
        shadow.setColor(QColor(0, 0, 0, 20))  # 降低阴影不透明度
        shadow.setOffset(0, 2)  # 微调阴影偏移
        container.setGraphicsEffect(shadow)
        
        # 确保_shadow_animation已初始化
        if hasattr(self, '_shadow_animation') and self._shadow_animation is not None:
            # 设置阴影动画的起始和结束值
            self._shadow_animation.setStartValue(0)
            self._shadow_animation.setEndValue(8)  # 与模糊半径一致
    
    def _focus_in_event(self, event):
        """输入框获得焦点事件"""
        # 调用原始的焦点获取事件处理
        QLineEdit.focusInEvent(self._line_edit, event)
        
        # 更新状态
        self._is_focused = True
        
        # 确保有文本时标签不可见
        self._label_widget.setVisible(not self._has_text)
        
        # 更新边框颜色
        self._current_border_color = self._focus_color
        self._current_shadow_color = self._focus_color
        
        # 更新字体大小
        font = self._label_widget.font()
        font.setPointSize(11)  # 使用setPointSize而不是setPointSizeF
        self._label_widget.setFont(font)
        
        self._label_widget.setStyleSheet(f"""
            QLabel#AnimatedLabel {{
                color: {self._focus_color.name()};
                background-color: transparent;
                qproperty-alignment: AlignCenter;
                text-align: center;
            }}
        """)
        
        # 执行聚焦动画
        self._animate_focus(True)
        
        # 重绘控件
        self._line_edit.update()
        
        # 发送焦点变化信号
        self.focusChanged.emit(True)
    
    def _focus_out_event(self, event):
        """输入框失去焦点事件"""
        # 调用原始的焦点失去事件处理
        QLineEdit.focusOutEvent(self._line_edit, event)
        
        # 更新状态
        self._is_focused = False
        
        # 确保有文本时标签不可见
        self._label_widget.setVisible(not self._has_text)
        
        # 更新边框颜色
        if not self._is_valid:
            self._current_border_color = self._error_color
            self._current_shadow_color = self._error_color
        else:
            self._current_border_color = self._border_color
            self._current_shadow_color = self._focus_color
        
        # 更新字体大小
        font = self._label_widget.font()
        font.setPointSize(13 if not (self._has_text or self._is_focused) else 11)  # 使用setPointSize而不是setPointSizeF
        self._label_widget.setFont(font)
        
        self._label_widget.setStyleSheet(f"""
            QLabel#AnimatedLabel {{
                color: {self._label_color.name()};
                background-color: transparent;
                qproperty-alignment: AlignCenter;
                text-align: center;
            }}
        """)
        
        # 执行失焦动画
        self._animate_focus(False)
        
        # 重绘控件
        self._line_edit.update()
        
        # 发送焦点变化信号
        self.focusChanged.emit(False)
    
    def _start_ripple_animation(self, position):
        """开始波纹动画"""
        # 保存波纹中心位置
        self._ripple_position = position
        
        # 计算最大半径（对角线长度）
        container = self.findChild(QWidget, "InputContainer")
        if not container:
            self.logger.warning("无法找到InputContainer，波纹动画无法启动")
            return
            
        max_radius = int(((container.width() ** 2) + (container.height() ** 2)) ** 0.5)
        
        # 创建波纹动画
        self._ripple_animation = QPropertyAnimation(self, b"ripple_radius")
        self._ripple_animation.setStartValue(0)
        self._ripple_animation.setEndValue(max_radius)
        self._ripple_animation.setDuration(400)
        self._ripple_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 创建不透明度动画
        self._ripple_opacity_animation = QPropertyAnimation(self, b"ripple_opacity")
        self._ripple_opacity_animation.setStartValue(0.35)
        self._ripple_opacity_animation.setEndValue(0.0)
        self._ripple_opacity_animation.setDuration(400)
        self._ripple_opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # 创建动画组
        ripple_group = QParallelAnimationGroup(self)  # 设置父对象，确保内存管理
        ripple_group.addAnimation(self._ripple_animation)
        ripple_group.addAnimation(self._ripple_opacity_animation)
        
        # 连接动画完成信号
        ripple_group.finished.connect(self._on_ripple_finished)
        
        # 启动动画
        ripple_group.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        
        # 设置波纹可见
        self._ripple_container.setVisible(True)
        
        # 触发重绘
        self._ripple_container.update()
    
    def _on_ripple_finished(self):
        """波纹动画完成处理"""
        self._ripple_radius = 0
        self._ripple_opacity = 0.0
        self._ripple_container.update()
    
    def _get_ripple_radius(self):
        """获取波纹半径"""
        return self._ripple_radius
    
    def _set_ripple_radius(self, radius):
        """设置波纹半径"""
        self._ripple_radius = radius
        self._ripple_container.update()
    
    def _get_ripple_opacity(self):
        """获取波纹不透明度"""
        return self._ripple_opacity
    
    def _set_ripple_opacity(self, opacity):
        """设置波纹不透明度"""
        self._ripple_opacity = opacity
        self._ripple_container.update()
    
    def _animate_focus(self, focused):
        """动画聚焦/失焦效果"""
        # 停止正在进行的动画
        if self._focus_animation_group:
            self._focus_animation_group.stop()
        
        # 立即更新标签颜色 - 确保用户能立即看到颜色变化
        label_color = self._focus_color if focused else self._label_color
        self._label_widget.setStyleSheet(f"""
            QLabel#AnimatedLabel {{
                color: {label_color.name()};
                background-color: transparent;
                qproperty-alignment: AlignCenter;
                text-align: center;
            }}
        """)
        
        # 设置边框颜色动画
        current_container = self.findChild(QWidget, "InputContainer")
        if current_container and self._border_color_animation:
            current_color = self._current_border_color
            
            # 根据状态设置目标颜色
            if focused:
                # 聚焦时边框变为蓝色，颜色更鲜艳，透明度稍高
                target_color = self._focus_color
                # 更新当前颜色状态
                self._current_border_color = target_color
            else:
                # 失焦时根据验证状态变色
                if not self._is_valid:
                    target_color = self._error_color
                else:
                    target_color = self._border_color
                # 更新当前颜色状态
                self._current_border_color = target_color
                
            # 设置颜色动画
            self._border_color_animation.setStartValue(current_color)
            self._border_color_animation.setEndValue(target_color)
            
            # 立即应用初始颜色到容器样式，确保动画有正确的起点
            self._update_container_style()
        
        # 设置边框宽度动画
        if self._border_width_animation:
            current_width = self._border_width
            target_width = 0.4 if focused else 0.3  # 聚焦时边框变粗
            self._border_width_animation.setStartValue(current_width)
            self._border_width_animation.setEndValue(target_width)
        
        # 设置阴影动画
        shadow = None
        if current_container:
            shadow = current_container.graphicsEffect()
        
        if shadow and self._shadow_animation:
            current_blur = shadow.blurRadius()
            target_blur = 12 if focused else 8  # 聚焦时增加阴影
            self._shadow_animation.setStartValue(current_blur)
            self._shadow_animation.setEndValue(target_blur)
        elif self._shadow_animation:
            # 没有阴影效果时，设置默认值
            self._shadow_animation.setStartValue(0)
            self._shadow_animation.setEndValue(8 if focused else 0)
        
        # 同时动画标签
        self._animate_label()
        
        # 启动动画组
        if self._focus_animation_group:
            self._focus_animation_group.start()
    
    def _animate_label(self):
        """动画标签位置和大小"""
        container = self.findChild(QWidget, "InputContainer")
        if not container:
            return
            
        # 计算标签目标位置
        container_width = container.width()
        container_height = container.height()
        label_width = container_width - 16  # 使用更小的左右边距
        
        # 设置标签宽度（确保每次动画更新宽度）
        self._label_widget.setFixedWidth(label_width)
        
        # 获取字体
        font = self._label_widget.font()
        # 确保字体大小有效
        current_size = font.pointSizeF()
        if current_size <= 0:
            current_size = 13.0 if not (self._has_text or self._is_focused) else 11.0
            font.setPointSizeF(current_size)
            self._label_widget.setFont(font)
        
        # 应用文本省略处理
        truncated_text = self._truncate_text_with_ellipsis(self._label, label_width, font)
        self._label_widget.setText(truncated_text)
        
        # 立即更新标签颜色 - 确保标签颜色随焦点状态变化
        label_color = self._focus_color if self._is_focused else self._label_color
        self._label_widget.setStyleSheet(f"""
            QLabel#AnimatedLabel {{
                color: {label_color.name()};
                background-color: transparent;
                qproperty-alignment: AlignCenter;
                text-align: center;
            }}
        """)
        
        # 计算水平居中位置
        x_pos = (container_width - label_width) // 2
        
        # 设置标签位置动画
        current_pos = self._label_widget.pos()
        # 确定垂直位置：聚焦或有文本时在顶部，否则垂直居中
        target_y = 2 if self._has_text or self._is_focused else (container_height - self._label_widget.height()) // 2
        
        self._label_pos_animation.setStartValue(current_pos)
        self._label_pos_animation.setEndValue(QPoint(x_pos, target_y))
        
        # 设置标签大小动画
        target_size = 11.0 if self._has_text or self._is_focused else 13.0
        # 确保目标大小也有效
        target_size = max(target_size, 10.0)
        
        self._label_size_animation.setStartValue(current_size)
        self._label_size_animation.setEndValue(target_size)
        
        # 启动动画组
        self._focus_animation_group.start()
    
    def _animate_button_opacity(self, button, visible):
        """动画改变按钮透明度"""
        # 获取动画对象
        animation = None
        
        if animation:
            # 设置动画起始值和结束值
            animation.setStartValue(0.0 if visible else 1.0)
            animation.setEndValue(1.0 if visible else 0.0)
            # 启动动画
            animation.start()
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于捕获鼠标点击事件"""
        if event.type() == QEvent.Type.MouseButtonPress:
            # 如果点击的是输入框容器或输入框本身，设置焦点
            if obj == self or obj == self._line_edit:
                self._line_edit.setFocus()
                return True
        return super().eventFilter(obj, event)
    
    # 以下是公共方法接口
    
    def setText(self, text):
        """设置文本"""
        self._line_edit.setText(text)
        # 更新标签可见性
        self._has_text = bool(text)
        self._label_widget.setVisible(not self._has_text)
        
        # 确保标签位置正确并居中 - 使用更强的强制刷新
        QTimer.singleShot(0, self._force_center_label)
    
    def text(self):
        """获取文本"""
        return self._line_edit.text()
    
    def clear(self):
        """清空文本"""
        # 先更新状态变量，防止textChanged信号触发时状态不一致
        self._has_text = False
        
        # 确保标签可见
        self._label_widget.setVisible(True)
        
        # 清空文本
        self._line_edit.clear()
        
        # 手动调用标签动画（因为状态已经提前改变）
        is_floating = self._label_widget.y() < 10
        if is_floating and not self._is_focused:
            # 确保字体大小正确
            font = self._label_widget.font()
            if font.pointSizeF() <= 0:
                font.setPointSizeF(13.0)
                self._label_widget.setFont(font)
                
            # 执行标签动画
            self._animate_label()
            # 启动动画组
            self._focus_animation_group.start()
            
    def setPlaceholder(self, placeholder):
        """设置占位符"""
        self._placeholder = placeholder
        # 如果没有自定义标签，则更新标签文本
        if not self._label:
            self._label = placeholder
            
            # 应用省略处理
            font = self._label_widget.font()
            width = self._label_widget.width()
            truncated_text = self._truncate_text_with_ellipsis(placeholder, width, font)
            self._label_widget.setText(truncated_text)
    
    def setLabel(self, label):
        """设置标签文本"""
        self._label = label
        
        # 应用省略处理
        font = self._label_widget.font()
        width = self._label_widget.width()
        truncated_text = self._truncate_text_with_ellipsis(label, width, font)
        self._label_widget.setText(truncated_text)
    
    def setValidator(self, validator):
        """设置验证器"""
        self._line_edit.setValidator(validator)
    
    def setError(self, error_message):
        """设置错误状态 - 已移除验证功能，此方法只保留接口兼容性"""
        pass
    
    def setSuccess(self, success_message=""):
        """设置成功状态 - 已移除验证功能，此方法只保留接口兼容性"""
        pass
    
    def clearValidation(self):
        """清除验证状态 - 已移除验证功能，此方法只保留接口兼容性"""
        pass
    
    def setReadOnly(self, read_only):
        """设置只读状态"""
        self._line_edit.setReadOnly(read_only)
    
    def isReadOnly(self):
        """获取只读状态"""
        return self._line_edit.isReadOnly()
    
    def setFocus(self):
        """设置焦点到输入框"""
        # 禁用状态下不允许获取焦点
        if not self._is_disabled:
            self._line_edit.setFocus()
    
    def setDisabled(self, disabled):
        """设置禁用状态"""
        self._is_disabled = disabled
        self._line_edit.setDisabled(disabled)
        
        # 更新样式
        if disabled:
            # 设置禁用状态的样式
            self._current_border_color = self._disabled_color
            self._line_edit.setStyleSheet(f"""
                QLineEdit {{
                    background-color: transparent;
                    color: {self._disabled_color.name()};
                    border: none;
                    padding: 6px 0;
                }}
            """)
            
            # 更新标签颜色并确保标签始终居中
            self._label_widget.setStyleSheet(f"""
                QLabel#AnimatedLabel {{
                    color: {self._disabled_color.name()};
                    background-color: transparent;
                    qproperty-alignment: AlignCenter;
                    text-align: center;
                }}
            """)
            
            # 确保禁用后标签仍然居中
            QTimer.singleShot(0, self._force_center_label)
        else:
            # 恢复正常样式
            self._update_styles()
            # 确保启用后标签仍然居中
            QTimer.singleShot(0, self._force_center_label)
        
        # 更新视图
        self.update()
    
    def isDisabled(self):
        """获取禁用状态"""
        return self._is_disabled
    
    def _force_center_label(self):
        """强制标签居中，并刷新显示"""
        container = self.findChild(QWidget, "InputContainer")
        if not container:
            self.logger.warning("强制居中标签失败：找不到InputContainer")
            return
            
        # 确保标签居中
        self._ensure_label_centered()
        
        # 强制更新字体大小和颜色
        font = self._label_widget.font()
        if self._has_text or self._is_focused:
            font.setPointSizeF(11.0)
        else:
            font.setPointSizeF(13.0)
        # 确保字体大小有效
        if font.pointSizeF() <= 0:
            font.setPointSizeF(13.0 if not (self._has_text or self._is_focused) else 11.0)
        self._label_widget.setFont(font)
        
        # 获取当前位置进行记录
        current_pos = self._label_widget.pos()
        
        # 记录当前标签状态信息
        self.logger.debug(f"强制标签居中 - 位置: ({current_pos.x()}, {current_pos.y()}), "
                          f"状态: 聚焦={self._is_focused}, 有文本={self._has_text}, "
                          f"字体大小={font.pointSizeF()}")
        
        # 主动触发重绘
        self.update()
        
        # 强制布局更新
        self.updateGeometry()
        
        # 确保标签也更新
        self._label_widget.update()
        
        # 如果container有效，尝试更新它的布局
        if container:
            container.updateGeometry()

    def _create_opacity_effect(self, opacity=1.0):
        """创建透明度效果"""
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(opacity)
        return effect

    def _setup_connections(self):
        """设置信号连接"""
        # 安装事件过滤器
        container = self.findChild(QWidget, "InputContainer")
        if container:
            container.installEventFilter(self)
            container.setAttribute(Qt.WidgetAttribute.WA_Hover)  # 启用悬停事件
        self._line_edit.installEventFilter(self)
        
        # 连接文本变化信号
        self._line_edit.textChanged.connect(self._handle_text_changed)
        self._line_edit.textEdited.connect(self._handle_text_edited)
        
        # 焦点变化时的处理
        self._line_edit.focusInEvent = self._focus_in_event
        self._line_edit.focusOutEvent = self._focus_out_event
        
        # 在初始化完成后，使用定时器触发一次更新，确保所有状态正确设置
        QTimer.singleShot(0, self._ensure_initial_state)
    
    def _is_dark_mode(self):
        """判断是否为暗黑模式"""
        return False  # 始终使用亮色模式
    
    def _handle_text_changed(self, text):
        """处理文本变化"""
        # 更新状态
        had_text = self._has_text
        self._has_text = bool(text)
        
        # 根据是否有文本来设置标签的可见性
        self._label_widget.setVisible(not self._has_text)
        
        # 如果标签可见，确保应用文本省略处理
        if not self._has_text:
            font = self._label_widget.font()
            # 确保字体大小有效
            if font.pointSizeF() <= 0:
                font.setPointSizeF(13.0)
                self._label_widget.setFont(font)
                
            width = self._label_widget.width()
            truncated_text = self._truncate_text_with_ellipsis(self._label, width, font)
            self._label_widget.setText(truncated_text)
        
        # 如果有文本但标签不在上方，或者无文本但标签在上方，则执行标签动画
        is_floating = self._label_widget.y() < 10
        if (self._has_text and not is_floating) or (not self._has_text and is_floating and not self._is_focused):
            self._animate_label()
            # 启动动画组
            self._focus_animation_group.start()
        
        # 发射自定义信号
        self.textChanged.emit(text)
    
    def _handle_text_edited(self, text):
        """处理文本编辑（用户输入）"""
        # 发射自定义信号
        self.textEdited.emit(text)
    
    # 定义波纹相关的属性
    ripple_radius = pyqtProperty(int, _get_ripple_radius, _set_ripple_radius)
    ripple_opacity = pyqtProperty(float, _get_ripple_opacity, _set_ripple_opacity)

    def _truncate_text_with_ellipsis(self, text, width, font):
        """
        在必要时截断文本并添加省略号
        
        参数:
            text (str): 原始文本
            width (int): 可用宽度
            font (QFont): 使用的字体
        
        返回:
            str: 处理后的文本
        """
        metrics = QFontMetrics(font)
        if metrics.horizontalAdvance(text) <= width:
            return text
            
        # 开始截断文本
        ellipsis = "..."
        ellipsis_width = metrics.horizontalAdvance(ellipsis)
        available_width = width - ellipsis_width
        
        # 初始截断位置
        length = len(text)
        pos = length
        
        # 逐步减少文本长度直到适合宽度
        while pos > 0 and metrics.horizontalAdvance(text[:pos]) > available_width:
            pos -= 1
        
        return text[:pos] + ellipsis if pos < length else text

    def showEvent(self, event):
        """显示事件处理，确保标签居中"""
        super().showEvent(event)
        
        # 立即尝试居中
        self._force_center_label()
        
        # 使用递增延迟多次尝试，确保成功
        QTimer.singleShot(50, self._force_center_label)
        QTimer.singleShot(100, self._force_center_label)
        QTimer.singleShot(200, self._force_center_label)
        QTimer.singleShot(300, self._force_center_label)
        # 添加更长时间的尝试，确保布局完全初始化后再次调整
        QTimer.singleShot(500, self._force_center_label)
        QTimer.singleShot(1000, self._force_center_label)

    def changeEvent(self, event):
        """变化事件处理，捕获窗口状态变化"""
        super().changeEvent(event)
        # 当窗口状态变化时（如禁用/启用状态变化）
        if event.type() == QEvent.Type.EnabledChange:
            QTimer.singleShot(0, self._force_center_label)
    
    def moveEvent(self, event):
        """移动事件处理"""
        super().moveEvent(event)
        # 组件位置变化时确保标签居中
        QTimer.singleShot(0, self._ensure_label_centered)

    def _setup_properties(self):
        """设置属性"""
        self._border_color = QColor("#D0D7DE")
        self._hover_color = QColor("#D0D7DE")
        self._background_color = QColor("white")
        
        # 注册属性
        self.setProperty("border_color", self._border_color)
        self.setProperty("hover_color", self._hover_color)
        self.setProperty("background_color", self._background_color)

    @pyqtProperty(QColor)
    def hover_color(self):
        return self._hover_color

    @hover_color.setter
    def hover_color(self, color):
        self._hover_color = color
        self._update_container_style()

    @pyqtProperty(QColor)
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self._update_container_style()

    def _update_container_style(self):
        """更新容器样式"""
        container = self.findChild(QWidget, "InputContainer")
        if container:
            # 更新容器样式
            container.setStyleSheet(f"""
                QWidget#InputContainer {{
                    background-color: {self._background_color.name()};
                    border: 1px solid {self._hover_color.name()};
                    border-radius: 4px;
                }}
            """)
            
            # 同时更新标签颜色 - 确保边框颜色变化时标签颜色也随之变化
            if hasattr(self, '_label_widget') and self._label_widget:
                label_color = self._focus_color if self._is_focused else self._label_color
                self._label_widget.setStyleSheet(f"""
                    QLabel#AnimatedLabel {{
                        color: {label_color.name()};
                        background-color: transparent;
                        qproperty-alignment: AlignCenter;
                        text-align: center;
                    }}
                """)

# 独立运行测试
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = QWidget()
    layout = QVBoxLayout(window)
    
    # 添加标题
    title_label = QLabel("输入框组件对比")
    title_label.setStyleSheet("""
        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #24292F;
            margin: 15px 0;
            padding: 5px 0;
            border-bottom: 2px solid #E1E4E8;
        }
    """)
    layout.addWidget(title_label)
    
    # 创建对比说明
    compare_label = QLabel("左侧为原版输入框，右侧为优化后的输入框")
    compare_label.setStyleSheet("""
        QLabel {
            font-size: 14px;
            color: #6E7781;
            margin: 10px 0;
            padding: 5px 0;
        }
    """)
    layout.addWidget(compare_label)
    
    # 创建对比布局
    compare_layout = QHBoxLayout()
    compare_layout.setSpacing(20)  # 增加左右布局的间距
    
    # 左侧原版输入框
    original_layout = QVBoxLayout()
    original_layout.setSpacing(15)  # 增加输入框之间的间距
    
    original_title = QLabel("原版输入框")
    original_title.setStyleSheet("""
        QLabel {
            font-size: 15px;
            color: #24292F;
            margin: 5px 0;
            padding: 5px 0;
            border-bottom: 1px solid #E1E4E8;
        }
    """)
    original_layout.addWidget(original_title)
    
    # 原版输入框示例
    original_input1 = QLineEdit()
    original_input1.setPlaceholderText("用户名")
    original_input1.setStyleSheet("""
        QLineEdit {
            padding: 8px 12px;
            border: 1px solid #D0D7DE;
            border-radius: 6px;
            font-size: 14px;
            min-height: 40px;
            background-color: white;
            color: #24292F;
        }
        QLineEdit:hover {
            border-color: #0969DA;
        }
        QLineEdit:focus {
            border-color: #0969DA;
            border-width: 2px;
        }
    """)
    original_layout.addWidget(original_input1)
    
    original_input2 = QLineEdit()
    original_input2.setPlaceholderText("电子邮箱")
    original_input2.setStyleSheet("""
        QLineEdit {
            padding: 8px 12px;
            border: 1px solid #D0D7DE;
            border-radius: 6px;
            font-size: 14px;
            min-height: 40px;
            background-color: white;
            color: #24292F;
        }
        QLineEdit:hover {
            border-color: #0969DA;
        }
        QLineEdit:focus {
            border-color: #0969DA;
            border-width: 2px;
        }
    """)
    original_layout.addWidget(original_input2)
    
    original_input3 = QLineEdit()
    original_input3.setPlaceholderText("手机号码")
    original_input3.setStyleSheet("""
        QLineEdit {
            padding: 8px 12px;
            border: 1px solid #D0D7DE;
            border-radius: 6px;
            font-size: 14px;
            min-height: 40px;
            background-color: white;
            color: #24292F;
        }
        QLineEdit:hover {
            border-color: #0969DA;
        }
        QLineEdit:focus {
            border-color: #0969DA;
            border-width: 2px;
        }
    """)
    original_layout.addWidget(original_input3)
    
    # 原版禁用状态输入框
    original_input4 = QLineEdit()
    original_input4.setPlaceholderText("禁用状态")
    original_input4.setEnabled(False)
    original_input4.setStyleSheet("""
        QLineEdit {
            padding: 8px 12px;
            border: 1px solid #D0D7DE;
            border-radius: 6px;
            font-size: 14px;
            min-height: 40px;
            background-color: #F6F8FA;
            color: #8C959F;
        }
    """)
    original_layout.addWidget(original_input4)
    
    # 右侧优化后的输入框
    optimized_layout = QVBoxLayout()
    optimized_layout.setSpacing(15)  # 增加输入框之间的间距
    
    optimized_title = QLabel("优化后的输入框")
    optimized_title.setStyleSheet("""
        QLabel {
            font-size: 15px;
            color: #24292F;
            margin: 5px 0;
            padding: 5px 0;
            border-bottom: 1px solid #E1E4E8;
        }
    """)
    optimized_layout.addWidget(optimized_title)
    
    # 优化后的输入框示例
    optimized_input1 = AnimatedInputField(placeholder="用户名")
    optimized_layout.addWidget(optimized_input1)
    
    optimized_input2 = AnimatedInputField(placeholder="电子邮箱", label="邮箱地址")
    optimized_layout.addWidget(optimized_input2)
    
    optimized_input3 = AnimatedInputField(placeholder="手机号码")
    optimized_layout.addWidget(optimized_input3)
    
    # 优化后的禁用状态输入框
    optimized_input4 = AnimatedInputField(placeholder="禁用状态")
    optimized_input4.setDisabled(True)
    optimized_layout.addWidget(optimized_input4)
    
    # 添加对比布局到主布局
    compare_layout.addLayout(original_layout)
    compare_layout.addLayout(optimized_layout)
    layout.addLayout(compare_layout)
    
    # 添加说明文本
    description = QLabel("优化特点：\n"
                        "1. 更紧凑的高度（32px vs 40px）\n"
                        "2. 更小的内边距（6px vs 8px）\n"
                        "3. 更小的圆角（4px vs 6px）\n"
                        "4. 更小的字体（13px vs 14px）\n"
                        "5. 动态标签动画效果\n"
                        "6. 悬停和聚焦效果\n"
                        "7. 禁用状态样式优化\n"
                        "8. 平滑的过渡动画\n"
                        "9. 更细腻的阴影效果")
    description.setStyleSheet("""
        QLabel {
            font-size: 13px;
            color: #6E7781;
            margin: 15px 0;
            padding: 10px;
            line-height: 1.6;
            background-color: #F6F8FA;
            border-radius: 6px;
            border: 1px solid #E1E4E8;
        }
    """)
    layout.addWidget(description)
    
    # 设置窗口样式
    window.setStyleSheet("""
        QWidget {
            background-color: white;
        }
    """)
    
    window.setLayout(layout)
    window.setWindowTitle("输入框组件对比")
    window.resize(700, 550)  # 增加窗口大小以适应更多内容
    window.show()
    
    sys.exit(app.exec()) 