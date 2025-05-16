import os
import sys

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QApplication, QCheckBox, QHBoxLayout, QVBoxLayout, QWidget

try:
    from core.logger import get_logger
except ImportError:
    # 添加项目根目录到路径
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger


class AnimatedCheckBox(QCheckBox):
    """自定义动画复选框组件

    提供现代化设计的复选框，带有平滑过渡动画效果。
    支持自定义主题颜色、大小和动画速度。
    """

    # 颜色更改信号
    colorChanged = pyqtSignal(list)

    def __init__(self, text="", parent=None, primary_color=None, check_color=None):
        """初始化动画复选框

        Args:
            text: 复选框文本
            parent: 父组件
            primary_color: 主题颜色，RGB格式的数组，如[52, 152, 219]
            check_color: 选中标记的颜色，RGB格式的数组，如[255, 255, 255]
        """
        super().__init__(text, parent)

        # 初始化日志
        self.logger = get_logger("AnimatedCheckBox")

        # 设置默认颜色
        self._primary_color = primary_color or [52, 152, 219]  # 主题蓝色
        self._check_color = check_color or [255, 255, 255]  # 白色勾选标记

        # 初始化绘制参数
        self._box_size = 20  # 复选框方框大小
        self._padding = 3  # 内边距
        self._animation_duration = 250  # 动画时长（毫秒）
        self._animation_progress = 0.0  # 动画进度（0.0-1.0）
        self._hover_progress = 0.0  # 悬停效果进度

        # 调用初始化UI方法
        self._setup_animations()
        self._setup_ui()

        # 记录日志
        self.logger.debug("AnimatedCheckBox初始化完成")

    def _setup_animations(self):
        """设置动画效果"""
        try:
            # 创建选中状态动画
            self._check_animation = QPropertyAnimation(self, b"animationProgress")
            self._check_animation.setDuration(self._animation_duration)
            self._check_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            # 创建悬停效果动画
            self._hover_animation = QPropertyAnimation(self, b"hoverProgress")
            self._hover_animation.setDuration(200)
            self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

            self.logger.debug("动画设置完成")
        except Exception as e:
            self.logger.error(f"设置动画时出错: {e}")

    def _setup_ui(self):
        """设置UI样式和属性"""
        try:
            # 设置焦点和鼠标跟踪
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.setMouseTracking(True)

            # 连接信号
            self.stateChanged.connect(self._handle_state_changed)

            # 设置样式
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setStyleSheet(
                """
                QCheckBox {
                    spacing: 10px;
                    background: transparent;
                    border: none;
                    outline: none;
                }
                QCheckBox::indicator {
                    width: 0px;
                    height: 0px;
                }
            """
            )

            self.logger.debug("UI设置完成")
        except Exception as e:
            self.logger.error(f"设置UI时出错: {e}")

    def _handle_state_changed(self, state):
        """处理复选框状态变化"""
        try:
            target = 1.0 if state == Qt.CheckState.Checked.value else 0.0

            self._check_animation.stop()
            self._check_animation.setStartValue(self._animation_progress)
            self._check_animation.setEndValue(target)
            self._check_animation.start()

            self.logger.debug(
                f"复选框状态变为: {'选中' if state == Qt.CheckState.Checked.value else '未选中'}"
            )
        except Exception as e:
            self.logger.error(f"处理状态变化时出错: {e}")

    def enterEvent(self, event):
        """鼠标进入事件"""
        try:
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(1.0)
            self._hover_animation.start()
            super().enterEvent(event)
            self.logger.debug("鼠标进入复选框")
        except Exception as e:
            self.logger.error(f"处理鼠标进入事件时出错: {e}")

    def leaveEvent(self, event):
        """鼠标离开事件"""
        try:
            self._hover_animation.stop()
            self._hover_animation.setStartValue(self._hover_progress)
            self._hover_animation.setEndValue(0.0)
            self._hover_animation.start()
            super().leaveEvent(event)
            self.logger.debug("鼠标离开复选框")
        except Exception as e:
            self.logger.error(f"处理鼠标离开事件时出错: {e}")

    def paintEvent(self, event):
        """绘制复选框"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 计算位置
            box_rect = QRect(
                self._padding,
                (self.height() - self._box_size) // 2,
                self._box_size,
                self._box_size,
            )

            # 创建颜色对象
            primary = QColor(*self._primary_color)
            primary_light = QColor(*self._primary_color)
            primary_light.setAlpha(50)
            check_color = QColor(*self._check_color)

            # 绘制悬停效果
            if self._hover_progress > 0:
                hover_rect = QRect(box_rect)
                # 扩大悬停效果区域
                hover_size = int(self._box_size * (1 + 0.2 * self._hover_progress))
                hover_rect.setSize(QSize(hover_size, hover_size))
                hover_rect.moveCenter(box_rect.center())

                hover_color = primary_light
                hover_color.setAlpha(int(40 * self._hover_progress))

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(hover_color))
                painter.drawRoundedRect(hover_rect, 5, 5)

            # 绘制边框
            border_pen = QPen(primary)
            border_pen.setWidth(2)
            painter.setPen(border_pen)

            # 计算背景填充
            background_opacity = self._animation_progress * 255
            background_color = primary
            background_color.setAlpha(int(background_opacity))
            painter.setBrush(QBrush(background_color))

            # 绘制圆角矩形
            corner_radius = 5
            painter.drawRoundedRect(box_rect, corner_radius, corner_radius)

            # 绘制勾选标记
            if self._animation_progress > 0.0:
                check_pen = QPen(check_color)
                check_pen.setWidth(2)
                painter.setPen(check_pen)

                # 创建勾选标记路径
                path = QPainterPath()

                # 计算勾选标记的点
                margin = self._box_size * 0.2
                p1 = QPoint(
                    int(box_rect.left() + margin),
                    int(box_rect.top() + self._box_size * 0.5),
                )
                p2 = QPoint(
                    int(box_rect.left() + self._box_size * 0.4),
                    int(box_rect.bottom() - margin),
                )
                p3 = QPoint(
                    int(box_rect.right() - margin), int(box_rect.top() + margin)
                )

                # 根据动画进度计算绘制点
                if self._animation_progress <= 0.5:
                    progress = self._animation_progress * 2.0
                    mid_point = QPoint(
                        int(p1.x() + (p2.x() - p1.x()) * progress),
                        int(p1.y() + (p2.y() - p1.y()) * progress),
                    )
                    path.moveTo(p1.x(), p1.y())
                    path.lineTo(mid_point.x(), mid_point.y())
                else:
                    progress = (self._animation_progress - 0.5) * 2.0
                    end_point = QPoint(
                        int(p2.x() + (p3.x() - p2.x()) * progress),
                        int(p2.y() + (p3.y() - p2.y()) * progress),
                    )
                    path.moveTo(p1.x(), p1.y())
                    path.lineTo(p2.x(), p2.y())
                    path.lineTo(end_point.x(), end_point.y())

                painter.drawPath(path)

            # 绘制文本
            text_rect = self.rect()
            text_rect.setLeft(box_rect.right() + 10)  # 文本从复选框右侧开始
            # 确保文本完整显示
            text_font = painter.font()
            painter.setPen(QPen(self.palette().text().color()))
            # 使用AlignLeft确保文本从左边开始绘制，不会被截断
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                self.text(),
            )
        except Exception as e:
            self.logger.error(f"绘制复选框时出错: {e}")

    def sizeHint(self):
        """获取建议大小"""
        try:
            size = super().sizeHint()
            min_height = self._box_size + 2 * self._padding
            if size.height() < min_height:
                size.setHeight(min_height)

            # 确保宽度足够显示完整文本
            font_metrics = self.fontMetrics()
            text_width = font_metrics.horizontalAdvance(self.text())
            min_width = self._box_size + 15 + text_width  # 复选框 + 间距 + 文本宽度
            if size.width() < min_width:
                size.setWidth(min_width)

            return size
        except Exception as e:
            self.logger.error(f"获取建议大小时出错: {e}")
            return super().sizeHint()

    def minimumSizeHint(self):
        """获取最小建议大小"""
        try:
            size = super().minimumSizeHint()
            min_height = self._box_size + 2 * self._padding
            if size.height() < min_height:
                size.setHeight(min_height)
            return size
        except Exception as e:
            self.logger.error(f"获取最小建议大小时出错: {e}")
            return super().minimumSizeHint()

    # 动画属性
    def _get_animation_progress(self):
        return self._animation_progress

    def _set_animation_progress(self, value):
        self._animation_progress = value
        self.update()

    animationProgress = pyqtProperty(
        float, _get_animation_progress, _set_animation_progress
    )

    def _get_hover_progress(self):
        return self._hover_progress

    def _set_hover_progress(self, value):
        self._hover_progress = value
        self.update()

    hoverProgress = pyqtProperty(float, _get_hover_progress, _set_hover_progress)

    # 公共方法
    def set_primary_color(self, color):
        """设置主题颜色

        Args:
            color: RGB格式的数组，如[52, 152, 219]
        """
        try:
            if self._primary_color != color:
                self._primary_color = color
                self.colorChanged.emit(color)
                self.update()
                self.logger.debug(f"设置主题颜色: RGB({color[0]}, {color[1]}, {color[2]})")
        except Exception as e:
            self.logger.error(f"设置主题颜色时出错: {e}")

    def get_primary_color(self):
        """获取主题颜色

        Returns:
            RGB格式的数组，如[52, 152, 219]
        """
        return self._primary_color

    def set_check_color(self, color):
        """设置勾选标记颜色

        Args:
            color: RGB格式的数组，如[255, 255, 255]
        """
        try:
            if self._check_color != color:
                self._check_color = color
                self.update()
                self.logger.debug(f"设置勾选标记颜色: RGB({color[0]}, {color[1]}, {color[2]})")
        except Exception as e:
            self.logger.error(f"设置勾选标记颜色时出错: {e}")

    def get_check_color(self):
        """获取勾选标记颜色

        Returns:
            RGB格式的数组，如[255, 255, 255]
        """
        return self._check_color

    def set_box_size(self, size):
        """设置复选框大小

        Args:
            size: 整数，表示复选框的像素大小
        """
        try:
            if self._box_size != size:
                self._box_size = size
                self.update()
                self.logger.debug(f"设置复选框大小: {size}px")
        except Exception as e:
            self.logger.error(f"设置复选框大小时出错: {e}")

    def set_animation_duration(self, duration):
        """设置动画持续时间

        Args:
            duration: 动画持续时间，单位为毫秒
        """
        try:
            if self._animation_duration != duration:
                self._animation_duration = duration
                self._check_animation.setDuration(duration)
                self.logger.debug(f"设置动画持续时间: {duration}ms")
        except Exception as e:
            self.logger.error(f"设置动画持续时间时出错: {e}")


# 测试代码，运行此文件时将展示组件示例
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("动画复选框示例")
    window.resize(400, 300)

    layout = QVBoxLayout()

    # 默认样式复选框
    checkbox1 = AnimatedCheckBox("默认样式复选框")
    layout.addWidget(checkbox1)

    # 自定义绿色主题复选框
    checkbox2 = AnimatedCheckBox("绿色主题复选框", primary_color=[46, 204, 113])
    layout.addWidget(checkbox2)

    # 红色主题复选框
    checkbox3 = AnimatedCheckBox("红色主题复选框", primary_color=[231, 76, 60])
    layout.addWidget(checkbox3)

    # 预先选中的复选框
    checkbox4 = AnimatedCheckBox("预先选中的复选框")
    checkbox4.setChecked(True)
    layout.addWidget(checkbox4)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())
