import sys
import math
import os
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, 
                           QLabel, QApplication, QSizePolicy, QGraphicsDropShadowEffect,
                           QPushButton, QFrame, QLineEdit)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QPoint, QPointF, QRectF, pyqtProperty, QTimer
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QLinearGradient, QPen, QBrush, QFont, QFontMetrics, QValidator

try:
    from core.logger import get_logger
    from version import APP_NAME
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger
    from version import APP_NAME

class SpinnerButton(QWidget):
    """数字选择器按钮，用于增加或减少值"""
    
    clicked = pyqtSignal()  # 点击信号
    
    def __init__(self, button_type="add", size=24, primary_color=None, parent=None):
        """
        初始化按钮
        
        Args:
            button_type: 按钮类型，"add"表示加号，"subtract"表示减号
            size: 按钮大小
            primary_color: 主要颜色，RGB列表[r,g,b]
            parent: 父组件
        """
        super().__init__(parent)
        self.logger = get_logger("SpinnerButton")
        
        # 默认颜色 - 蓝色系
        self.primary_color = primary_color or [52, 152, 219]
        self.secondary_color = [41, 128, 185]
        self.highlight_color = [79, 195, 247]
        
        # 设置按钮类型
        self.button_type = button_type  # "add" 或 "subtract"
        
        # 设置固定大小
        self.base_size = size
        self.setFixedSize(size, size)
        
        # 状态变量
        self.hovered = False
        self.pressed = False
        self._scale = 1.0  # 用于动画效果
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        # 添加阴影效果
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(4)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
        # 创建动画
        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    # 定义Qt属性，用于动画效果
    @pyqtProperty(float)
    def scale(self):
        return self._scale
        
    @scale.setter
    def scale(self, value):
        self._scale = value
        self.update()
    
    def set_primary_color(self, color):
        """设置主要颜色"""
        if isinstance(color, list) and len(color) >= 3:
            self.primary_color = color
            # 自动计算次要颜色和高亮颜色
            self.secondary_color = [max(0, int(c * 0.8)) for c in color]
            self.highlight_color = [min(255, int(c * 1.2)) for c in color]
            self.update()
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.hovered = True
        self.scale_animation.setStartValue(1.0)
        self.scale_animation.setEndValue(1.1)
        self.scale_animation.start()
        self.shadow.setBlurRadius(8)
        self.shadow.setColor(QColor(0, 0, 0, 70))
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.hovered = False
        self.scale_animation.setStartValue(self._scale)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.start()
        self.shadow.setBlurRadius(4)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pressed = True
            self.scale_animation.setStartValue(self._scale)
            self.scale_animation.setEndValue(0.95)
            self.scale_animation.start()
            self.update()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.pressed and event.button() == Qt.MouseButton.LeftButton:
            self.pressed = False
            self.scale_animation.setStartValue(self._scale)
            
            if self.rect().contains(event.pos()):
                # 点击在按钮内部
                self.clicked.emit()
                if self.hovered:
                    self.scale_animation.setEndValue(1.1)
                else:
                    self.scale_animation.setEndValue(1.0)
            else:
                # 释放在按钮外部
                self.scale_animation.setEndValue(1.0)
                
            self.scale_animation.start()
            self.update()
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        """绘制按钮"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # 获取组件尺寸
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # 计算实际绘制尺寸，考虑缩放因子
        scale_size = int(min(width, height) * self._scale * 0.9)
        
        # 背景
        gradient = QLinearGradient(0, 0, width, height)
        if self.pressed:
            gradient.setColorAt(0, QColor(int(self.secondary_color[0]), int(self.secondary_color[1]), int(self.secondary_color[2])))
            gradient.setColorAt(1, QColor(int(self.secondary_color[0]), int(self.secondary_color[1]), int(self.secondary_color[2])))
        else:
            gradient.setColorAt(0, QColor(int(self.primary_color[0]), int(self.primary_color[1]), int(self.primary_color[2])))
            gradient.setColorAt(1, QColor(int(self.primary_color[0]), int(self.primary_color[1]), int(self.primary_color[2])))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 绘制圆形背景
        painter.drawEllipse(QRectF(center_x - scale_size/2, center_y - scale_size/2, scale_size, scale_size))
        
        # 绘制符号
        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        
        symbol_size = scale_size * 0.4  # 符号大小
        
        if self.button_type == "add":
            # 绘制加号
            painter.drawLine(QPointF(center_x, center_y - symbol_size/2), 
                          QPointF(center_x, center_y + symbol_size/2))
            painter.drawLine(QPointF(center_x - symbol_size/2, center_y), 
                          QPointF(center_x + symbol_size/2, center_y))
        else:
            # 绘制减号
            painter.drawLine(QPointF(center_x - symbol_size/2, center_y), 
                          QPointF(center_x + symbol_size/2, center_y))

class NumberValidator(QValidator):
    """数字输入验证器，确保输入内容为有效数字"""
    
    def __init__(self, min_value, max_value, step=1, parent=None):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.is_integer = (step == int(step))  # 是否只允许整数
    
    def validate(self, input_text, pos):
        """验证输入内容"""
        if not input_text:
            return QValidator.State.Intermediate, input_text, pos  # 允许空输入，后续处理
        
        # 尝试将输入转换为浮点数
        try:
            value = float(input_text)
            # 整数验证
            if self.is_integer and value != int(value):
                return QValidator.State.Intermediate, input_text, pos
            
            # 范围验证
            if value < self.min_value or value > self.max_value:
                return QValidator.State.Intermediate, input_text, pos
                
            return QValidator.State.Acceptable, input_text, pos
        except ValueError:
            # 非数字内容，但允许编辑（例如正在输入负号、小数点等）
            return QValidator.State.Intermediate, input_text, pos

    def fixup(self, input_text):
        """修正输入内容"""
        if not input_text:
            return str(0)
            
        try:
            value = float(input_text)
            
            # 将值限制在范围内
            value = max(self.min_value, min(self.max_value, value))
            
            # 如果需要整数值，则四舍五入
            if self.is_integer:
                value = round(value)
                return str(int(value))
            else:
                # 对于小数值，保留适当的小数位
                decimal_places = max(0, int(-math.log10(self.step)))
                format_str = f"{{:.{decimal_places}f}}"
                return format_str.format(value)
        except ValueError:
            # 无法转换为数字，返回最小值
            return str(self.min_value)

class AnimatedNumberSpinner(QWidget):
    """
    动画数字选择器组件
    
    特性：
    - 加减按钮带动画效果
    - 数字变化动画
    - 可设置范围和步长
    - 悬停/点击视觉反馈
    """
    
    valueChanged = pyqtSignal(int)  # 值变化信号
    
    def __init__(self, parent=None, min_value=0, max_value=100, step=1, value=0, primary_color=None):
        """
        初始化数字选择器
        
        Args:
            parent: 父组件
            min_value: 最小值
            max_value: 最大值
            step: 步长
            value: 初始值
            primary_color: 主要颜色，RGB列表[r,g,b]
        """
        super().__init__(parent)
        self.logger = get_logger("AnimatedNumberSpinner")
        
        # 设置属性
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        self._value = self._clamp_value(value)
        self._primary_color = primary_color or [52, 152, 219]  # 默认蓝色
        
        # 属性动画
        self._old_value = self._value
        self._display_value = float(self._value)
        self._value_animation = None
        
        # 初始化UI
        self.initUI()
        
        # 添加动画
        self.setupAnimations()
        
        self.logger.debug(f"数字选择器初始化, 值: {self._value}, 范围: {min_value}-{max_value}, 步长: {step}")
    
    def initUI(self):
        """初始化用户界面"""
        # 创建布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)  # 组件间隔
        
        # 创建减号按钮
        self.subtract_button = SpinnerButton(
            button_type="subtract",
            size=28,
            primary_color=self._primary_color
        )
        self.subtract_button.clicked.connect(self.decrement)
        
        # 创建显示数值的容器
        self.value_container = QFrame()
        self.value_container.setObjectName("ValueContainer")
        self.value_container.setFixedWidth(40)  # 改为固定宽度，减小到40像素
        self.value_container.setFixedHeight(28)
        
        # 设置样式
        self.value_container.setStyleSheet("""
            QFrame#ValueContainer {
                background-color: white;
                border: 1px solid #D0D7DE;
                border-radius: 4px;
            }
        """)
        
        # 添加阴影效果
        value_shadow = QGraphicsDropShadowEffect()
        value_shadow.setBlurRadius(4)
        value_shadow.setColor(QColor(0, 0, 0, 30))
        value_shadow.setOffset(0, 1)
        self.value_container.setGraphicsEffect(value_shadow)
        
        # 创建数值输入框
        self.value_label = QLineEdit(self._format_display_value(self._value))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("""
            font-weight: bold;
            color: #24292F;
            background-color: transparent;
            border: none;
        """)
        
        # 设置验证器
        self.validator = NumberValidator(self._min_value, self._max_value, self._step)
        self.value_label.setValidator(self.validator)
        
        # 当编辑完成时更新值
        self.value_label.editingFinished.connect(self._handle_editing_finished)
        
        # 设置标签布局
        value_layout = QHBoxLayout(self.value_container)
        value_layout.setContentsMargins(5, 0, 5, 0)
        value_layout.addWidget(self.value_label)
        
        # 创建加号按钮
        self.add_button = SpinnerButton(
            button_type="add",
            size=28,
            primary_color=self._primary_color
        )
        self.add_button.clicked.connect(self.increment)
        
        # 添加组件到布局
        main_layout.addWidget(self.subtract_button)
        main_layout.addWidget(self.value_container, 1)  # 数值容器可以拉伸
        main_layout.addWidget(self.add_button)
        
        # 设置布局
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # 启用鼠标滚轮事件
        self.value_container.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.value_container.installEventFilter(self)
    
    def setupAnimations(self):
        """设置动画"""
        self._value_animation = QPropertyAnimation(self, b"display_value")
        self._value_animation.setDuration(200)
        self._value_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._value_animation.valueChanged.connect(self._update_display)
    
    def _clamp_value(self, value):
        """确保值在范围内"""
        return max(self._min_value, min(self._max_value, value))
    
    def increment(self):
        """增加值"""
        old_value = self._value
        self._value = self._clamp_value(self._value + self._step)
        if old_value != self._value:
            self._animate_value(old_value, self._value)
            self.valueChanged.emit(self._value)
            self.logger.debug(f"数字选择器增加值: {old_value} -> {self._value}")
    
    def decrement(self):
        """减少值"""
        old_value = self._value
        self._value = self._clamp_value(self._value - self._step)
        if old_value != self._value:
            self._animate_value(old_value, self._value)
            self.valueChanged.emit(self._value)
            self.logger.debug(f"数字选择器减少值: {old_value} -> {self._value}")
    
    def _animate_value(self, old_value, new_value):
        """动画显示值的变化"""
        if self._value_animation.state() == QPropertyAnimation.State.Running:
            self._value_animation.stop()
        
        self._old_value = old_value
        self._value_animation.setStartValue(float(old_value))
        self._value_animation.setEndValue(float(new_value))
        self._value_animation.start()
    
    def _update_display(self):
        """更新显示的值"""
        display_text = self._format_display_value(self._display_value)
        self.value_label.setText(display_text)
    
    # 属性动画支持
    @pyqtProperty(float)
    def display_value(self):
        return self._display_value
    
    @display_value.setter
    def display_value(self, value):
        self._display_value = value
    
    # 公共方法
    def setValue(self, value):
        """设置数值"""
        old_value = self._value
        self._value = self._clamp_value(value)
        
        # 只有当值真正改变时才触发动画和信号
        if old_value != self._value:
            self._animate_value(old_value, self._value)
            self.valueChanged.emit(self._value)
            self.logger.debug(f"数字选择器设置值: {old_value} -> {self._value}")
    
    def value(self):
        """获取当前值"""
        return self._value
    
    def setMinimum(self, min_value):
        """设置最小值"""
        if min_value > self._max_value:
            self.logger.warning(f"设置的最小值 {min_value} 大于最大值 {self._max_value}，忽略此操作")
            return
            
        self._min_value = min_value
        # 确保当前值在新范围内
        old_value = self._value
        self._value = self._clamp_value(self._value)
        
        if old_value != self._value:
            # 如果当前值需要调整，立即更新显示
            self.setValue(self._value)
    
    def minimum(self):
        """获取最小值"""
        return self._min_value
    
    def setMaximum(self, max_value):
        """设置最大值"""
        if max_value < self._min_value:
            self.logger.warning(f"设置的最大值 {max_value} 小于最小值 {self._min_value}，忽略此操作")
            return
            
        self._max_value = max_value
        # 确保当前值在新范围内
        old_value = self._value
        self._value = self._clamp_value(self._value)
        
        if old_value != self._value:
            # 如果当前值需要调整，立即更新显示
            self.setValue(self._value)
    
    def maximum(self):
        """获取最大值"""
        return self._max_value
    
    def setRange(self, min_value, max_value):
        """设置值范围"""
        if min_value > max_value:
            self.logger.warning(f"设置的范围无效：最小值 {min_value} 大于最大值 {max_value}，忽略此操作")
            return
            
        self._min_value = min_value
        self._max_value = max_value
        
        # 确保当前值在新范围内
        old_value = self._value
        self._value = self._clamp_value(self._value)
        
        if old_value != self._value:
            # 如果当前值需要调整，立即更新显示
            self.setValue(self._value)
    
    def setStep(self, step):
        """设置步长"""
        if step <= 0:
            self.logger.warning(f"步长应大于0，忽略值：{step}")
            return
            
        self._step = step
    
    def step(self):
        """获取步长"""
        return self._step
    
    def setPrimaryColor(self, color):
        """设置主题颜色"""
        if isinstance(color, list) and len(color) >= 3:
            self._primary_color = color
            self.add_button.set_primary_color(color)
            self.subtract_button.set_primary_color(color)
            self.update()

    def eventFilter(self, obj, event):
        """事件过滤器，处理鼠标滚轮事件"""
        if obj == self.value_container and event.type() == event.Type.Wheel:
            # 获取滚轮方向
            angle_delta = event.angleDelta().y()
            
            # 向上滚动增加值，向下滚动减少值
            if angle_delta > 0:
                self.increment()
            elif angle_delta < 0:
                self.decrement()
                
            # 事件已处理
            return True
            
        # 其他事件交给默认处理程序
        return super().eventFilter(obj, event)
    
    def _handle_editing_finished(self):
        """处理编辑完成事件"""
        try:
            # 获取输入文本
            text = self.value_label.text()
            
            # 尝试将文本转换为数值
            if text:
                # 使用验证器修复可能的问题
                fixed_text = self.validator.fixup(text)
                
                # 转换为适当的数值类型
                if self._step == int(self._step):
                    # 整数值
                    new_value = int(float(fixed_text))
                else:
                    # 浮点数值
                    new_value = float(fixed_text)
                
                # 确保在范围内
                new_value = self._clamp_value(new_value)
                
                # 只有在值变化时才更新
                if new_value != self._value:
                    self.setValue(new_value)
                else:
                    # 即使值未变化，也更新显示以确保格式正确
                    self.value_label.setText(self._format_display_value(self._value))
            else:
                # 空输入，恢复到当前值
                self.value_label.setText(self._format_display_value(self._value))
        except (ValueError, TypeError) as e:
            # 发生错误，恢复到当前值
            self.logger.warning(f"处理输入时出错: {e}")
            self.value_label.setText(self._format_display_value(self._value))
    
    def _format_display_value(self, value):
        """格式化显示的值"""
        # 对于整数值，直接显示整数
        if self._step == int(self._step):
            return str(int(value))
        else:
            # 对于小数值，保留适当的小数位
            decimal_places = max(0, int(-math.log10(self._step)))
            format_str = f"{{:.{decimal_places}f}}"
            return format_str.format(value)

# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建一个窗口
    window = QWidget()
    window.setWindowTitle("动画数字选择器测试")
    window.setMinimumSize(300, 200)
    
    # 创建布局
    layout = QVBoxLayout(window)
    
    # 添加标题
    title = QLabel(f"{APP_NAME} 数字选择器")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")
    layout.addWidget(title)
    
    # 添加说明
    desc = QLabel("可通过点击按钮或滚轮调整数值")
    desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
    desc.setStyleSheet("font-size: 10pt; margin-bottom: 20px;")
    layout.addWidget(desc)
    
    # 创建水平布局
    h_layout = QHBoxLayout()
    
    # 添加标签
    label = QLabel("数值:")
    h_layout.addWidget(label)
    
    # 添加数字选择器
    spinner = AnimatedNumberSpinner(min_value=0, max_value=100, step=1, value=50)
    
    # 连接信号
    def on_value_changed(value):
        print(f"数值变化为: {value}")
    
    spinner.valueChanged.connect(on_value_changed)
    
    h_layout.addWidget(spinner)
    layout.addLayout(h_layout)
    
    # 第二个选择器 - 不同颜色和步长
    h_layout2 = QHBoxLayout()
    label2 = QLabel("小数值:")
    h_layout2.addWidget(label2)
    
    spinner2 = AnimatedNumberSpinner(
        min_value=0, 
        max_value=5, 
        step=0.1, 
        value=2.5,
        primary_color=[231, 76, 60]  # 红色主题
    )
    h_layout2.addWidget(spinner2)
    layout.addLayout(h_layout2)
    
    # 添加间距
    layout.addStretch()
    
    # 显示窗口
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec())