import os
import sys

from PyQt6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    Qt,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)

try:
    from core.logger import get_logger
except ImportError:
    # 相对导入处理，便于直接运行此文件进行测试
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger


class CardWidget(QWidget):
    """
    卡片组件

    带有动画效果的卡片组件，可以包含其他组件。
    卡片具有悬停、点击动画效果，并支持被选中状态。
    可以自定义颜色、边框半径等视觉效果。
    """

    # 自定义信号
    clicked = pyqtSignal()  # 卡片被点击时的信号

    def __init__(
        self,
        parent=None,
        primary_color=None,
        hover_color=None,
        text_color=None,
        selected_color=None,
        border_radius=12,
        title=None,
        min_width=None,
        min_height=None,
        shadow_color=None,
    ):
        """
        初始化卡片组件

        参数:
            parent (QWidget): 父组件
            primary_color (list/str): 主色调，RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            hover_color (list/str): 悬停色调，RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            text_color (list/str): 文本颜色，RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            selected_color (list/str): 选中状态颜色，RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            border_radius (int): 边框圆角半径
            title (str): 卡片标题，如果设置则会在卡片顶部显示一个标题标签
            min_width (int): 最小宽度
            min_height (int): 最小高度
            shadow_color (list/str): 阴影颜色，RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
        """
        super().__init__(parent)
        self.logger = get_logger("CardWidget")
        self.logger.debug(f"初始化卡片: {title if title else '无标题'}")

        # 默认参数设置 - 使用淡蓝色主题
        self._primary_color = (
            self._parse_color(primary_color) if primary_color else QColor(248, 253, 255)
        )  # 更浅的淡蓝色背景

        # 如果没有指定悬停色，基于主色自动计算一个更亮的颜色作为悬停色
        if hover_color:
            self._hover_color = self._parse_color(hover_color)
        else:
            # 基于主色调自动计算悬停色，将RGB值提高10%，但不超过255
            self._hover_color = QColor(
                min(255, int(self._primary_color.red() * 1.1)),
                min(255, int(self._primary_color.green() * 1.1)),
                min(255, int(self._primary_color.blue() * 1.1)),
            )

        # 选中状态颜色 - 如果未指定则使用更淡的主题色
        self._selected_color = (
            self._parse_color(selected_color)
            if selected_color
            else QColor(180, 220, 250)
        )  # 更浅的主题蓝色

        self._text_color = (
            self._parse_color(text_color) if text_color else QColor(50, 50, 50)
        )  # 深灰色文本
        self._border_color = self._primary_color.darker(110)
        self._shadow_color = (
            self._parse_color(shadow_color) if shadow_color else QColor(0, 0, 0, 30)
        )

        self._border_radius = border_radius
        self._title = title

        # 设置卡片大小限制
        if min_width:
            self.setMinimumWidth(min_width)
        else:
            self.setMinimumWidth(180)  # 默认最小宽度

        if min_height:
            self.setMinimumHeight(min_height)
        else:
            self.setMinimumHeight(120)  # 默认最小高度

        # 状态属性
        self._hovered = False
        self._pressed = False
        self._selected = False
        self._scale_factor = 1.0
        self._opacity = 0.0
        self._elevation = 4.0  # 初始阴影高度

        # 设置样式
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 设置鼠标样式为手型

        # 创建动画
        self._setup_animations()

        # 允许鼠标追踪，以便及时捕获鼠标进入和离开事件
        self.setMouseTracking(True)

        # 创建布局
        self._create_layout()

        # 应用阴影效果
        self._apply_shadow()

    def _parse_color(self, color):
        """解析颜色参数，支持RGB列表和十六进制颜色字符串"""
        if isinstance(color, list) and len(color) >= 3:
            alpha = color[3] if len(color) > 3 else 255
            return QColor(color[0], color[1], color[2], alpha)
        elif isinstance(color, str) and color.startswith("#"):
            return QColor(color)
        else:
            self.logger.warning(f"不支持的颜色格式: {color}，使用默认颜色")
            return QColor(240, 248, 255)  # 默认淡蓝色

    def _apply_shadow(self):
        """应用阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(self._shadow_color)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def _create_layout(self):
        """创建卡片内部布局"""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 12, 12, 12)  # 增加内边距，避免内容挡住边框

        # 如果有标题，添加标题标签
        if self._title:
            title_label = QLabel(self._title)
            title_label.setStyleSheet(
                f"color: {self._text_color.name()}; font-weight: bold;"
            )
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(title_label)

        self.setLayout(self._layout)

    def _setup_animations(self):
        """设置动画效果"""
        # 卡片缩放动画 - 用于点击效果
        self._scale_animation = QPropertyAnimation(self, b"scale_factor")
        self._scale_animation.setDuration(150)  # 150毫秒
        self._scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 颜色过渡动画 - 用于悬停效果
        self._color_animation = QPropertyAnimation(self, b"opacity")
        self._color_animation.setDuration(300)  # 增加持续时间到300毫秒
        self._color_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 阴影高度动画 - 用于悬停效果
        self._elevation_animation = QPropertyAnimation(self, b"elevation")
        self._elevation_animation.setDuration(300)  # 与颜色动画保持一致
        self._elevation_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        # 悬停动画组
        self._hover_animation_group = QParallelAnimationGroup()
        self._hover_animation_group.addAnimation(self._color_animation)
        self._hover_animation_group.addAnimation(self._elevation_animation)

    def sizeHint(self):
        """返回首选大小"""
        size = super().sizeHint()
        # 确保卡片有合适的大小
        return QSize(max(size.width(), 180), max(size.height(), 120))

    def enterEvent(self, event):
        """鼠标进入事件"""
        self._hovered = True
        self._hover_animation_group.stop()

        # 设置颜色动画
        self._color_animation.setStartValue(self._opacity)
        self._color_animation.setEndValue(1.0)

        # 设置阴影高度动画 - 悬停时阴影更明显
        self._elevation_animation.setStartValue(self._elevation)
        self._elevation_animation.setEndValue(8.0)

        # 更新阴影效果
        shadow = self.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(15)
            shadow.setOffset(0, 3)

        # 启动动画组
        self._hover_animation_group.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._hovered = False
        self.logger.debug("鼠标离开卡片，开始颜色过渡动画")

        # 停止所有可能正在运行的动画
        self._hover_animation_group.stop()
        self._scale_animation.stop()

        # 设置颜色动画，确保从当前值开始
        self._color_animation.setStartValue(self._opacity)
        self._color_animation.setEndValue(0.0)

        # 设置阴影高度动画 - 恢复正常阴影
        self._elevation_animation.setStartValue(self._elevation)
        self._elevation_animation.setEndValue(4.0)

        # 卡片大小动画
        self._scale_animation.setDuration(300)
        self._scale_animation.setStartValue(self._scale_factor)
        self._scale_animation.setEndValue(1.0)

        # 启动所有动画
        self._hover_animation_group.start()
        self._scale_animation.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True

            # 卡片缩放动画
            self._scale_animation.stop()
            self._scale_animation.setStartValue(self._scale_factor)
            self._scale_animation.setEndValue(0.97)  # 缩小到97%
            self._scale_animation.start()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False

            # 卡片回弹动画
            self._scale_animation.stop()
            self._scale_animation.setStartValue(self._scale_factor)
            self._scale_animation.setEndValue(1.0)  # 恢复到100%
            self._scale_animation.start()

            # 发射点击信号
            self.clicked.emit()

        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        """调整大小事件"""
        super().resizeEvent(event)
        # 在调整大小时需要重新布局内容组件
        self._layout.update()

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 计算当前使用的颜色
        if self._selected:
            current_color = self._selected_color
        else:
            # 根据不透明度动画混合主色和悬停色
            r = int(
                self._primary_color.red() * (1 - self._opacity)
                + self._hover_color.red() * self._opacity
            )
            g = int(
                self._primary_color.green() * (1 - self._opacity)
                + self._hover_color.green() * self._opacity
            )
            b = int(
                self._primary_color.blue() * (1 - self._opacity)
                + self._hover_color.blue() * self._opacity
            )
            current_color = QColor(r, g, b)

            # 记录调试信息，帮助诊断颜色动画过渡问题
            if self._opacity > 0 and self._opacity < 1:
                self.logger.debug(f"颜色混合: 不透明度={self._opacity}, RGB=({r},{g},{b})")

        # 应用动画缩放
        painter.save()
        painter.translate(self.rect().center())
        painter.scale(self._scale_factor, self._scale_factor)
        painter.translate(-self.rect().center())

        # 绘制卡片背景
        button_rect = self.rect().adjusted(2, 2, -2, -2)  # 稍微缩小以显示阴影
        button_path = QPainterPath()
        button_path.addRoundedRect(
            QRectF(button_rect), self._border_radius, self._border_radius
        )

        # 使用纯色填充
        painter.fillPath(button_path, QBrush(current_color))

        # 绘制边框 - 更细的边框
        if self._selected:
            # 选中状态使用稍微深一点的边框
            pen = QPen(self._selected_color.darker(120))
            pen.setWidth(2)
        else:
            pen = QPen(self._border_color)
            pen.setWidth(1)

        painter.setPen(pen)
        painter.drawRoundedRect(button_rect, self._border_radius, self._border_radius)

        # 绘制微妙的高光效果 - 扁平化设计中的微妙细节
        if not self._pressed:
            highlight_path = QPainterPath()
            highlight_rect = button_rect.adjusted(
                1, 1, -1, button_rect.height() // 4 - 1
            )
            highlight_path.addRoundedRect(
                QRectF(highlight_rect), self._border_radius - 1, self._border_radius - 1
            )
            highlight_color = QColor(255, 255, 255, 20)  # 微妙的白色高光
            painter.fillPath(highlight_path, highlight_color)

        # 如果按下，添加一个微妙的内阴影效果
        if self._pressed:
            inner_shadow = QPainterPath()
            inner_shadow_rect = button_rect.adjusted(1, 1, -1, -1)
            inner_shadow.addRoundedRect(
                QRectF(inner_shadow_rect), self._border_radius, self._border_radius
            )
            inner_shadow_color = QColor(0, 0, 0, 15)  # 微妙的内阴影
            painter.fillPath(inner_shadow, inner_shadow_color)

        painter.restore()

    # 添加组件到卡片内部
    def add_widget(self, widget):
        """添加组件到卡片内部"""
        self._layout.addWidget(widget)

    # 根据缩放比例重新计算整个卡片大小
    def _apply_scaling(self):
        """应用缩放比例到整个卡片"""
        # 在缩放时需要更新布局
        self._layout.update()

        # 当缩放比例变化时更新阴影效果
        shadow = self.graphicsEffect()
        if shadow and isinstance(shadow, QGraphicsDropShadowEffect):
            blur_radius = 10 + self._elevation * 0.8
            shadow.setBlurRadius(blur_radius)
            shadow.setOffset(0, self._pressed and 1 or self._elevation / 3)

    # 选中状态控制
    def is_selected(self):
        """返回卡片是否被选中"""
        return self._selected

    def set_selected(self, selected):
        """设置卡片的选中状态"""
        if self._selected != selected:
            self._selected = selected
            self.update()  # 重绘卡片

    # 定义标题相关方法
    def set_title(self, title):
        """设置卡片标题"""
        # 如果布局中已经有标题标签，更新它
        if self._title is not None and self._layout.count() > 0:
            title_label = self._layout.itemAt(0).widget()
            if isinstance(title_label, QLabel):
                title_label.setText(title)
        # 否则创建新的标题标签
        elif title:
            title_label = QLabel(title)
            title_label.setStyleSheet(
                f"color: {self._text_color.name()}; font-weight: bold;"
            )
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.insertWidget(0, title_label)

        self._title = title

    def get_title(self):
        """获取卡片标题"""
        return self._title

    # 定义动画属性
    def _get_scale_factor(self):
        return self._scale_factor

    def _set_scale_factor(self, factor):
        """设置缩放因子，同时更新组件的变换效果"""
        self._scale_factor = factor
        self._apply_scaling()  # 应用缩放效果
        # 需要调用update()来触发重绘
        self.update()

    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, opacity):
        """设置不透明度属性，同时触发重绘"""
        if self._opacity != opacity:
            self._opacity = opacity
            # 记录调试信息
            self.logger.debug(f"卡片不透明度变化: {opacity}")
            self.update()  # 确保触发重绘

    def _get_elevation(self):
        return self._elevation

    def _set_elevation(self, elevation):
        self._elevation = elevation
        shadow = self.graphicsEffect()
        if shadow:
            shadow.setBlurRadius(elevation + 5)  # 高度越高，模糊半径越大
            shadow.setOffset(0, elevation / 3)  # 根据高度调整阴影偏移
        self.update()

    # 属性定义，用于QPropertyAnimation
    scale_factor = pyqtProperty(float, _get_scale_factor, _set_scale_factor)
    opacity = pyqtProperty(float, _get_opacity, _set_opacity)
    elevation = pyqtProperty(float, _get_elevation, _set_elevation)

    # 外观定制方法
    def set_primary_color(self, color):
        """设置卡片主色调"""
        self._primary_color = self._parse_color(color)
        self.update()

    def set_hover_color(self, color):
        """设置卡片悬停色调"""
        self._hover_color = self._parse_color(color)
        self.update()

    def set_selected_color(self, color):
        """设置卡片选中状态的颜色"""
        self._selected_color = self._parse_color(color)
        self.update()

    def set_text_color(self, color):
        """设置卡片文本颜色"""
        self._text_color = self._parse_color(color)
        # 更新标题标签颜色
        if self._title is not None and self._layout.count() > 0:
            title_label = self._layout.itemAt(0).widget()
            if isinstance(title_label, QLabel):
                title_label.setStyleSheet(
                    f"color: {self._text_color.name()}; font-weight: bold;"
                )
        self.update()

    def set_border_radius(self, radius):
        """设置卡片边框圆角半径"""
        self._border_radius = radius
        self.update()


# 以下代码用于测试卡片组件
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("卡片组件测试")
    window.resize(800, 600)
    window.setStyleSheet("background-color: #f0f0f0;")

    layout = QVBoxLayout(window)

    # 创建卡片示例
    card1 = CardWidget(title="基本卡片")
    label1 = QLabel("这是一个基本的卡片示例，\n包含标题和内容。")
    label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label1.setContentsMargins(5, 5, 5, 5)  # 为标签添加内边距
    card1.add_widget(label1)

    # 自定义颜色的卡片
    card2 = CardWidget(
        title="自定义颜色卡片",
        primary_color=[230, 230, 250],  # 淡紫色
        hover_color=[200, 200, 240],
        selected_color=[85, 170, 225],  # 更淡的主题蓝色
        text_color=[70, 70, 120],
    )
    label2 = QLabel("这是一个自定义颜色的卡片，\n悬停和选中状态有不同颜色。")
    label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
    card2.add_widget(label2)

    # 无标题卡片
    card3 = CardWidget(primary_color=[255, 240, 240])
    label3 = QLabel("这是一个没有标题的卡片。")
    label3.setAlignment(Qt.AlignmentFlag.AlignCenter)
    card3.add_widget(label3)

    # 添加卡片到窗口
    layout.addWidget(card1)
    layout.addWidget(card2)
    layout.addWidget(card3)

    def toggle_selection(card):
        card.set_selected(not card.is_selected())

    # 连接点击信号
    card1.clicked.connect(lambda: toggle_selection(card1))
    card2.clicked.connect(lambda: toggle_selection(card2))
    card3.clicked.connect(lambda: toggle_selection(card3))

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())
