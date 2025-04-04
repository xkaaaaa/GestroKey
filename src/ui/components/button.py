import sys
import os
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QSize, pyqtProperty, QPoint, QRectF, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt5.QtGui import QColor, QPainter, QFont, QPixmap, QIcon, QPainterPath, QBrush, QPen, QFontMetrics, QTransform
from PyQt5.QtWidgets import QStyle

try:
    from core.logger import get_logger
except ImportError:
    # 相对导入处理，便于直接运行此文件进行测试
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

class AnimatedButton(QPushButton):
    """
    动画按钮组件
    
    一个带有悬停、点击动画效果的精美按钮。采用扁平化设计，支持文字动画效果。
    可以自定义颜色、图标、文本和大小。
    """
    
    def __init__(self, text="", parent=None, icon=None, primary_color=None, hover_color=None, 
                 text_color=None, border_radius=8, icon_size=None, min_width=None, min_height=None,
                 border_color=None, shadow_color=None):
        """
        初始化动画按钮
        
        参数:
            text (str): 按钮文本
            parent (QWidget): 父组件
            icon (str/QIcon): 图标路径或QIcon对象
            primary_color (list/str): 主色调，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            hover_color (list/str): 悬停色调，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            text_color (list/str): 文本颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            border_radius (int): 边框圆角半径
            icon_size (int): 图标大小
            min_width (int): 最小宽度
            min_height (int): 最小高度
            border_color (list/str): 边框颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
            shadow_color (list/str): 阴影颜色，可以是RGB列表[r,g,b]或hex格式的颜色字符串"#RRGGBB"
        """
        super().__init__(text, parent)
        self.logger = get_logger("AnimatedButton")
        self.logger.debug(f"初始化按钮: {text}")
        
        # 默认参数设置 - 蓝色主题
        self._primary_color = self._parse_color(primary_color) if primary_color else QColor(41, 128, 185)  # 扁平化蓝色
        
        # 如果没有指定悬停色，基于主色自动计算一个更亮的颜色作为悬停色
        if hover_color:
            self._hover_color = self._parse_color(hover_color)
        else:
            # 基于主色调自动计算悬停色，将RGB值提高20%，但不超过255
            primary_r = self._primary_color.red()
            primary_g = self._primary_color.green()
            primary_b = self._primary_color.blue()
            
            hover_r = min(255, int(primary_r * 1.2))
            hover_g = min(255, int(primary_g * 1.2))
            hover_b = min(255, int(primary_b * 1.2))
            
            self._hover_color = QColor(hover_r, hover_g, hover_b)
        
        self._text_color = self._parse_color(text_color) if text_color else QColor(255, 255, 255)
        self._border_color = self._parse_color(border_color) if border_color else self._primary_color.darker(110)
        self._shadow_color = self._parse_color(shadow_color) if shadow_color else QColor(0, 0, 0, 60)
        
        # 禁用状态的颜色
        self._disabled_bg_color = QColor(160, 160, 160)  # 灰色背景
        self._disabled_text_color = QColor(200, 200, 200)  # 浅灰色文本
        self._disabled_border_color = QColor(140, 140, 140)  # 深灰色边框
        
        self._border_radius = border_radius
        
        # 设置按钮图标
        if icon:
            if isinstance(icon, str):
                self.setIcon(QIcon(icon))
            else:
                self.setIcon(icon)
            
            if icon_size:
                self.setIconSize(QSize(icon_size, icon_size))
            else:
                self.setIconSize(QSize(24, 24))
        
        # 设置按钮大小限制
        if min_width:
            self.setMinimumWidth(min_width)
        if min_height:
            self.setMinimumHeight(min_height)
        
        # 状态属性
        self._hovered = False
        self._pressed = False
        self._scale_factor = 1.0
        self._opacity = 0.0
        self._text_y_offset = 0.0  # 文本Y轴偏移
        self._text_scale = 1.0     # 文本缩放
        
        # 设置样式
        self.setFlat(True)  # 设置为平面按钮，去除默认样式
        self.setCursor(Qt.PointingHandCursor)  # 设置鼠标样式为手型
        
        # 设置属性以允许样式表选择器
        self.setProperty("custom_animated", True)
        
        # 创建动画
        self._setup_animations()
        
        # 允许鼠标追踪，以便及时捕获鼠标进入和离开事件
        self.setMouseTracking(True)
    
    def _parse_color(self, color):
        """解析颜色参数，支持RGB列表和十六进制颜色字符串"""
        if isinstance(color, list) and len(color) >= 3:
            r, g, b = color[0], color[1], color[2]
            alpha = color[3] if len(color) > 3 else 255
            return QColor(r, g, b, alpha)
        elif isinstance(color, str) and color.startswith("#"):
            return QColor(color)
        else:
            self.logger.warning(f"不支持的颜色格式: {color}，使用默认颜色")
            return QColor(41, 128, 185)  # 默认扁平化蓝色
    
    def _setup_animations(self):
        """设置动画效果"""
        # 按钮缩放动画 - 用于点击效果
        self._scale_animation = QPropertyAnimation(self, b"scale_factor")
        self._scale_animation.setDuration(150)  # 150毫秒
        self._scale_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 颜色过渡动画 - 用于悬停效果
        self._color_animation = QPropertyAnimation(self, b"opacity")
        self._color_animation.setDuration(200)  # 200毫秒
        self._color_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 文字动画 - 悬停时的文字效果
        self._text_y_animation = QPropertyAnimation(self, b"text_y_offset")
        self._text_y_animation.setDuration(200)
        self._text_y_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        self._text_scale_animation = QPropertyAnimation(self, b"text_scale")
        self._text_scale_animation.setDuration(200)
        self._text_scale_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # 悬停动画组
        self._hover_animation_group = QParallelAnimationGroup()
        self._hover_animation_group.addAnimation(self._color_animation)
        self._hover_animation_group.addAnimation(self._text_y_animation)
        self._hover_animation_group.addAnimation(self._text_scale_animation)
        
        # 按下动画组 (新增)
        self._press_animation_group = QParallelAnimationGroup()
        
        # 按下时的文字Y轴动画
        self._press_text_y_animation = QPropertyAnimation(self, b"text_y_offset")
        self._press_text_y_animation.setDuration(100)
        self._press_text_y_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # 按下时的文字缩放动画
        self._press_text_scale_animation = QPropertyAnimation(self, b"text_scale")
        self._press_text_scale_animation.setDuration(100)
        self._press_text_scale_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        self._press_animation_group.addAnimation(self._press_text_y_animation)
        self._press_animation_group.addAnimation(self._press_text_scale_animation)
    
    def setEnabled(self, enabled):
        """
        重写设置按钮可用状态的方法
        
        参数:
            enabled (bool): 是否启用按钮
        """
        was_enabled = self.isEnabled()
        super().setEnabled(enabled)
        
        # 状态发生变化时更新按钮样式
        if was_enabled != enabled:
            self.logger.debug(f"按钮 '{self.text()}' 状态变更为 {'启用' if enabled else '禁用'}")
            
            # 更新鼠标指针样式
            if enabled:
                self.setCursor(Qt.PointingHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
                # 禁用时重置所有动画状态
                self._hovered = False
                self._pressed = False
                self._opacity = 0.0
                self._text_y_offset = 0.0
                self._text_scale = 1.0
                self._scale_factor = 1.0
                
                # 停止所有动画
                self._hover_animation_group.stop()
                self._press_animation_group.stop()
                self._scale_animation.stop()
            
            # 重绘按钮以应用新样式
            self.update()
    
    def sizeHint(self):
        """返回首选大小"""
        size = super().sizeHint()
        # 确保按钮有合适的大小
        return QSize(max(size.width(), 120), max(size.height(), 40))
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        # 禁用状态下不触发悬停动画
        if not self.isEnabled():
            super().enterEvent(event)
            return
            
        self._hovered = True
        self._hover_animation_group.stop()
        
        # 设置颜色动画
        self._color_animation.setStartValue(self._opacity)
        self._color_animation.setEndValue(1.0)
        
        # 设置文字Y轴偏移动画
        self._text_y_animation.setStartValue(self._text_y_offset)
        self._text_y_animation.setEndValue(-2.0)  # 向上移动2像素
        
        # 设置文字缩放动画
        self._text_scale_animation.setStartValue(self._text_scale)
        self._text_scale_animation.setEndValue(1.05)  # 放大到105%
        
        # 启动动画组
        self._hover_animation_group.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        # 禁用状态下不触发离开动画
        if not self.isEnabled():
            super().leaveEvent(event)
            return
            
        self._hovered = False
        
        # 停止所有可能正在运行的动画
        self._hover_animation_group.stop()
        self._press_animation_group.stop()
        self._scale_animation.stop()
        
        # 设置颜色动画，确保从当前值开始
        self._color_animation.setStartValue(self._opacity)
        self._color_animation.setEndValue(0.0)
        
        # 设置文字Y轴偏移动画，确保从当前值开始
        self._text_y_animation.setStartValue(self._text_y_offset)
        self._text_y_animation.setEndValue(0.0)  # 恢复原位
        
        # 设置文字缩放动画，确保从当前值开始
        self._text_scale_animation.setStartValue(self._text_scale)
        self._text_scale_animation.setEndValue(1.0)  # 恢复原大小
        
        # 确保按钮恢复原始大小
        self._scale_animation.setStartValue(self._scale_factor)
        self._scale_animation.setEndValue(1.0)
        self._scale_animation.start()
        
        # 启动悬停动画组
        self._hover_animation_group.start()
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 禁用状态下不响应鼠标按下事件
        if not self.isEnabled():
            return
            
        if event.button() == Qt.LeftButton:
            self._pressed = True
            
            # 按钮缩放动画
            self._scale_animation.stop()
            self._scale_animation.setStartValue(self._scale_factor)
            self._scale_animation.setEndValue(0.96)  # 缩小到96%
            self._scale_animation.start()
            
            # 文字动画 - 与按钮同步
            self._press_animation_group.stop()
            
            # 设置按下时文字下移，给人一种按下的感觉
            self._press_text_y_animation.setStartValue(self._text_y_offset)
            self._press_text_y_animation.setEndValue(1.0)  # 向下移动1像素
            
            # 设置按下时文字缩小，与按钮缩放保持一致
            self._press_text_scale_animation.setStartValue(self._text_scale)
            self._press_text_scale_animation.setEndValue(0.98)  # 缩小到98%
            
            self._press_animation_group.start()
            
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        # 禁用状态下不响应鼠标释放事件
        if not self.isEnabled():
            return
            
        if event.button() == Qt.LeftButton and self._pressed:
            self._pressed = False
            
            # 按钮回弹动画
            self._scale_animation.stop()
            self._scale_animation.setStartValue(self._scale_factor)
            self._scale_animation.setEndValue(1.0)  # 恢复到100%
            self._scale_animation.start()
            
            # 文字回弹动画 - 如果鼠标仍在按钮上，恢复悬停状态
            self._press_animation_group.stop()
            
            if self._hovered:
                # 鼠标仍在按钮上，文字恢复到悬停状态
                self._press_text_y_animation.setStartValue(self._text_y_offset)
                self._press_text_y_animation.setEndValue(-2.0)  # 恢复悬停状态的上移
                
                self._press_text_scale_animation.setStartValue(self._text_scale)
                self._press_text_scale_animation.setEndValue(1.05)  # 恢复悬停状态的放大
            else:
                # 鼠标不在按钮上，文字恢复到正常状态
                self._press_text_y_animation.setStartValue(self._text_y_offset)
                self._press_text_y_animation.setEndValue(0.0)  # 恢复正常位置
                
                self._press_text_scale_animation.setStartValue(self._text_scale)
                self._press_text_scale_animation.setEndValue(1.0)  # 恢复正常大小
            
            self._press_animation_group.start()
            
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 确定要使用的颜色 - 根据按钮状态选择
        if not self.isEnabled():
            # 禁用状态使用灰色
            current_color = self._disabled_bg_color
            text_color = self._disabled_text_color
            border_color = self._disabled_border_color
        else:
            # 启用状态使用正常颜色
            current_color = self._primary_color
            text_color = self._text_color
            border_color = self._border_color
            
            # 悬停效果
            if self._hovered:
                # 使用透明度混合颜色
                current_color = QColor(
                    int(self._primary_color.red() * (1 - self._opacity) + self._hover_color.red() * self._opacity),
                    int(self._primary_color.green() * (1 - self._opacity) + self._hover_color.green() * self._opacity),
                    int(self._primary_color.blue() * (1 - self._opacity) + self._hover_color.blue() * self._opacity)
                )
        
        # 应用动画缩放
        painter.save()
        painter.translate(self.rect().center())
        painter.scale(self._scale_factor, self._scale_factor)
        painter.translate(-self.rect().center())
        
        # 绘制阴影效果
        shadow_path = QPainterPath()
        shadow_rect = self.rect().adjusted(4, 6, -4, -2)  # 阴影偏移
        shadow_path.addRoundedRect(QRectF(shadow_rect), self._border_radius, self._border_radius)
        shadow_color = QColor(self._shadow_color)
        shadow_color.setAlpha(50 if self.isEnabled() else 20)  # 禁用状态阴影更淡
        painter.fillPath(shadow_path, shadow_color)
        
        # 绘制按钮背景 - 扁平化设计，不使用渐变
        button_rect = self.rect().adjusted(2, 2, -2, -2)  # 稍微缩小以显示阴影
        button_path = QPainterPath()
        button_path.addRoundedRect(QRectF(button_rect), self._border_radius, self._border_radius)
        
        # 使用纯色填充
        painter.fillPath(button_path, QBrush(current_color))
        
        # 绘制边框 - 更细的边框
        if not self._pressed or not self.isEnabled():
            pen = QPen(border_color)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawRoundedRect(button_rect, self._border_radius, self._border_radius)
        
        # 绘制微妙的高光效果 - 扁平化设计中的微妙细节
        if (not self._pressed) and self.isEnabled():
            highlight_path = QPainterPath()
            highlight_rect = button_rect.adjusted(1, 1, -1, button_rect.height() // 3 - 1)
            highlight_path.addRoundedRect(QRectF(highlight_rect), self._border_radius - 1, self._border_radius - 1)
            highlight_color = QColor(255, 255, 255, 15)  # 非常微妙的白色高光
            painter.fillPath(highlight_path, highlight_color)
        
        # 如果按下，添加一个微妙的内阴影效果
        if self._pressed and self.isEnabled():
            inner_shadow = QPainterPath()
            inner_shadow_rect = button_rect.adjusted(1, 1, -1, -1)
            inner_shadow.addRoundedRect(QRectF(inner_shadow_rect), self._border_radius, self._border_radius)
            inner_shadow_color = QColor(0, 0, 0, 15)  # 微妙的内阴影
            painter.fillPath(inner_shadow, inner_shadow_color)
        
        painter.restore()
        
        # 绘制图标
        if not self.icon().isNull():
            icon_rect = QRect(8, (self.height() - self.iconSize().height()) // 2,
                             self.iconSize().width(), self.iconSize().height())
            
            # 禁用状态时使用灰色图标
            if not self.isEnabled():
                self.icon().paint(painter, icon_rect, Qt.AlignCenter, QIcon.Disabled)
            else:
                self.icon().paint(painter, icon_rect)
        
        # 绘制文本 - 带动画效果
        painter.save()
        
        # 设置文本颜色
        painter.setPen(text_color)
        
        # 获取字体并调整大小
        font = self.font()
        font.setPointSize(10)  # 可根据需要调整字体大小
        painter.setFont(font)
        
        # 计算文本区域
        has_icon = not self.icon().isNull()
        text_rect = self.rect().adjusted(self.iconSize().width() + 8 if has_icon else 8, 0, -4, 0)
        
        # 应用文本动画效果 - 禁用状态下不应用动画效果
        if self.isEnabled():
            painter.translate(text_rect.center())
            painter.scale(self._text_scale, self._text_scale)
            painter.translate(-text_rect.center())
            
            # 应用文本Y轴偏移
            text_rect = text_rect.adjusted(0, int(self._text_y_offset), 0, int(self._text_y_offset))
        
        # 居中绘制文本
        painter.drawText(text_rect, Qt.AlignCenter, self.text())
        
        painter.restore()
    
    # 定义动画属性
    def _get_scale_factor(self):
        return self._scale_factor
    
    def _set_scale_factor(self, factor):
        self._scale_factor = factor
        self.update()
    
    def _get_opacity(self):
        return self._opacity
    
    def _set_opacity(self, opacity):
        self._opacity = opacity
        self.update()
    
    def _get_text_y_offset(self):
        return self._text_y_offset
    
    def _set_text_y_offset(self, offset):
        self._text_y_offset = offset
        self.update()
    
    def _get_text_scale(self):
        return self._text_scale
    
    def _set_text_scale(self, scale):
        self._text_scale = scale
        self.update()
    
    # 属性定义，用于QPropertyAnimation
    scale_factor = pyqtProperty(float, _get_scale_factor, _set_scale_factor)
    opacity = pyqtProperty(float, _get_opacity, _set_opacity)
    text_y_offset = pyqtProperty(float, _get_text_y_offset, _set_text_y_offset)
    text_scale = pyqtProperty(float, _get_text_scale, _set_text_scale)
    
    def set_primary_color(self, color):
        """设置按钮主色调"""
        self._primary_color = self._parse_color(color)
        self.update()
    
    def set_hover_color(self, color):
        """设置按钮悬停色调"""
        self._hover_color = self._parse_color(color)
        self.update()
    
    def set_text_color(self, color):
        """设置按钮文本颜色"""
        self._text_color = self._parse_color(color)
        self.update()
    
    def set_border_radius(self, radius):
        """设置按钮边框圆角半径"""
        self._border_radius = radius
        self.update()


# 示例部分，仅在直接运行此文件时执行
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion样式以获得更好的跨平台一致性
    
    # 创建窗口
    window = QWidget()
    window.setWindowTitle("AnimatedButton 示例")
    window.setMinimumSize(800, 600)
    
    # 创建布局
    layout = QVBoxLayout()
    
    # 添加标题
    title = QLabel("AnimatedButton 组件示例")
    title.setAlignment(Qt.AlignCenter)
    font = title.font()
    font.setPointSize(18)
    font.setBold(True)
    title.setFont(font)
    title.setMargin(20)
    layout.addWidget(title)
    
    # 创建按钮的网格布局
    grid_layout = QGridLayout()
    
    # 创建不同样式的按钮 - 蓝色主题
    buttons = [
        # 标准按钮
        {"text": "标准蓝色按钮", "primary_color": [41, 128, 185]},
        # 深蓝色按钮
        {"text": "深蓝色按钮", "primary_color": [25, 80, 160], "hover_color": [41, 128, 185]},
        # 天蓝色按钮
        {"text": "天蓝色按钮", "primary_color": [52, 152, 219], "hover_color": [85, 175, 237]},
        # 浅蓝色按钮，带深色文本
        {"text": "浅蓝色按钮", "primary_color": [133, 193, 233], "hover_color": [169, 204, 227], "text_color": [33, 37, 41]},
        # 带图标的按钮
        {"text": "带图标的按钮", "primary_color": [41, 128, 185], "icon": QIcon()},
        # 深色按钮
        {"text": "深色按钮", "primary_color": [52, 73, 94], "hover_color": [75, 101, 132]},
        # 大圆角按钮
        {"text": "圆角按钮", "primary_color": [41, 128, 185], "border_radius": 20},
        # 无圆角按钮
        {"text": "无圆角按钮", "primary_color": [41, 128, 185], "border_radius": 0},
    ]
    
    # 添加按钮到布局
    for i, button_config in enumerate(buttons):
        button = AnimatedButton(**button_config)
        # 如果没有提供图标且环境中有图标主题，使用一个默认图标
        if "icon" not in button_config and i % 2 == 0:  # 偶数索引的按钮添加图标
            # 使用内置的QStyle标准图标替代主题图标
            button.setIcon(button.style().standardIcon(QStyle.SP_DialogOkButton))
            button.setIconSize(QSize(20, 20))
        
        # 添加到网格，每行2个按钮
        row = i // 2
        col = i % 2
        grid_layout.addWidget(button, row, col)
    
    # 添加网格到主布局
    layout.addLayout(grid_layout)
    
    # 添加禁用状态按钮展示
    disabled_section_title = QLabel("禁用状态按钮示例")
    disabled_section_title.setAlignment(Qt.AlignCenter)
    font = disabled_section_title.font()
    font.setPointSize(16)
    font.setBold(True)
    disabled_section_title.setFont(font)
    disabled_section_title.setMargin(10)
    layout.addWidget(disabled_section_title)
    
    # 创建禁用状态按钮展示区域
    disabled_layout = QHBoxLayout()
    layout.addLayout(disabled_layout)
    
    # 创建各种样式的禁用按钮
    disabled_buttons = [
        AnimatedButton("标准按钮-禁用", primary_color=[41, 128, 185]),
        AnimatedButton("带图标按钮-禁用", primary_color=[25, 80, 160]),
        AnimatedButton("深色按钮-禁用", primary_color=[52, 73, 94])
    ]
    
    # 添加图标并禁用按钮
    for i, button in enumerate(disabled_buttons):
        if i == 1:  # 为中间的按钮添加图标
            button.setIcon(button.style().standardIcon(QStyle.SP_DialogSaveButton))
            button.setIconSize(QSize(20, 20))
        button.setEnabled(False)  # 禁用按钮
        disabled_layout.addWidget(button)
    
    # 添加切换禁用状态的测试按钮
    toggle_section = QHBoxLayout()
    layout.addLayout(toggle_section)
    
    test_button = AnimatedButton("测试按钮")
    toggle_button = AnimatedButton("切换禁用状态")
    
    toggle_section.addWidget(test_button)
    toggle_section.addWidget(toggle_button)
    
    # 切换按钮状态的函数
    def toggle_button_state():
        test_button.setEnabled(not test_button.isEnabled())
    
    toggle_button.clicked.connect(toggle_button_state)
    
    # 添加说明文本
    info = QLabel("""
    <html>
    <p style='text-align:center; margin-top:20px;'>
    AnimatedButton 是一个自定义按钮组件，具有动画效果：<br/>
    - 鼠标悬停时颜色变化<br/>
    - 鼠标悬停时文字轻微上浮和放大<br/>
    - 点击时按钮缩放动画<br/>
    - 支持自定义颜色、图标和边框圆角<br/>
    - 扁平化设计，精美的阴影和高光效果<br/>
    - 禁用状态显示灰色，无动画效果<br/>
    </p>
    <p style='text-align:center; margin-top:10px;'>
    <b>使用示例:</b><br/>
    <code>button = AnimatedButton("按钮文本", primary_color=[41, 128, 185], icon="path/to/icon.png")</code><br/>
    <code>button.setEnabled(False)  # 设置为禁用状态</code>
    </p>
    </html>
    """)
    info.setAlignment(Qt.AlignCenter)
    layout.addWidget(info)
    
    # 添加控制按钮示例
    control_layout = QHBoxLayout()
    layout.addLayout(control_layout)
    
    # 实时修改按钮
    test_button2 = AnimatedButton("测试按钮")
    control_layout.addWidget(test_button2, 1)
    
    # 控制按钮
    color_button = AnimatedButton("切换颜色", primary_color=[41, 128, 185])
    radius_button = AnimatedButton("切换圆角", primary_color=[41, 128, 185])
    reset_button = AnimatedButton("重置按钮", primary_color=[41, 128, 185])
    
    control_layout.addWidget(color_button)
    control_layout.addWidget(radius_button)
    control_layout.addWidget(reset_button)
    
    # 按钮颜色切换功能 - 蓝色主题系列
    colors = [
        [41, 128, 185],  # 标准蓝
        [25, 80, 160],   # 深蓝
        [52, 152, 219],  # 天蓝
        [133, 193, 233], # 浅蓝
        [52, 73, 94],    # 深色
    ]
    current_color_index = 0
    
    def toggle_color():
        global current_color_index
        current_color_index = (current_color_index + 1) % len(colors)
        test_button2.set_primary_color(colors[current_color_index])
    
    color_button.clicked.connect(toggle_color)
    
    # 按钮圆角切换功能
    radiuses = [8, 16, 24, 32, 0]
    current_radius_index = 0
    
    def toggle_radius():
        global current_radius_index
        current_radius_index = (current_radius_index + 1) % len(radiuses)
        test_button2.set_border_radius(radiuses[current_radius_index])
    
    radius_button.clicked.connect(toggle_radius)
    
    # 重置按钮
    def reset_test_button():
        global current_color_index, current_radius_index
        current_color_index = 0
        current_radius_index = 0
        test_button2.set_primary_color(colors[current_color_index])
        test_button2.set_border_radius(radiuses[current_radius_index])
    
    reset_button.clicked.connect(reset_test_button)
    
    # 设置窗口布局并显示
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec_()) 