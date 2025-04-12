import sys
import math
import os
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, 
                           QLabel, QApplication, QSizePolicy, QGraphicsDropShadowEffect, QGridLayout, QPushButton,
                           QSlider, QFrame, QDialog)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QPoint, QPointF, QRect, QRectF, pyqtProperty
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QLinearGradient, QPen, QBrush, QConicalGradient

try:
    from core.logger import get_logger
    from ui.components.button import AnimatedButton
    from ui.components.slider import AnimatedSlider
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger
    from ui.components.button import AnimatedButton
    from ui.components.slider import AnimatedSlider

class ColorSwatch(QWidget):
    """颜色样本组件，用于显示单一颜色"""
    
    clicked = pyqtSignal(list)  # 发送RGB颜色列表
    
    def __init__(self, color=[0, 120, 255], size=30, selected=False, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ColorSwatch")
        
        # 初始化属性
        self.color = color
        self.selected = selected
        self.hovered = False
        self._scale = 1.0  # 用于动画效果
        
        # 设置固定大小
        self.base_size = size
        self.setFixedSize(size, size)
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        # 添加阴影效果
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(6)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
        # 创建动画
        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    # 定义Qt属性，用于动画效果
    @pyqtProperty(float)
    def scale(self):
        return self._scale
        
    @scale.setter
    def scale(self, value):
        self._scale = value
        # 不再调整组件大小，只触发重绘
        self.update()
    
    def set_color(self, color):
        """设置颜色"""
        if isinstance(color, list) and len(color) >= 3:
            self.color = color
            self.update()
            
    def set_selected(self, selected):
        """设置选中状态"""
        if self.selected != selected:
            self.selected = selected
            # 如果被选中，播放缩放动画
            if selected:
                self.scale_animation.setStartValue(1.0)
                self.scale_animation.setEndValue(1.2)
                self.scale_animation.start()
                # 增加阴影
                self.shadow.setBlurRadius(12)
                self.shadow.setColor(QColor(0, 0, 0, 80))
            else:
                self.scale_animation.setStartValue(self._scale)
                self.scale_animation.setEndValue(1.0)
                self.scale_animation.start()
                # 减少阴影
                self.shadow.setBlurRadius(6)
                self.shadow.setColor(QColor(0, 0, 0, 50))
            self.update()
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.hovered = True
        if not self.selected:
            self.scale_animation.setStartValue(1.0)
            self.scale_animation.setEndValue(1.1)
            self.scale_animation.start()
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.hovered = False
        if not self.selected:
            self.scale_animation.setStartValue(self._scale)
            self.scale_animation.setEndValue(1.0)
            self.scale_animation.start()
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.color)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def paintEvent(self, event):
        """绘制颜色样本"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # 获取组件中心
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # 保存画家状态以应用缩放
        painter.save()
        
        # 应用缩放变换 - 从中心点缩放
        painter.translate(center_x, center_y)
        painter.scale(self._scale, self._scale)
        painter.translate(-center_x, -center_y)
        
        # 计算实际绘制尺寸，考虑缩放因子
        actual_radius = min(width, height) / 2 - 2
        
        # 定义样本形状
        path = QPainterPath()
        path.addEllipse(QPointF(center_x, center_y), actual_radius, actual_radius)
        
        # 创建颜色渐变
        r, g, b = self.color[0], self.color[1], self.color[2]
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor(min(255, int(r * 1.2)), 
                                    min(255, int(g * 1.2)), 
                                    min(255, int(b * 1.2))))
        gradient.setColorAt(1, QColor(r, g, b))
        
        # 绘制背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(path)
        
        # 恢复画家状态
        painter.restore()
        
        # 如果选中，绘制边框
        if self.selected:
            pen = QPen(Qt.GlobalColor.white)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), actual_radius + 1, actual_radius + 1)
        
        # 如果悬停但未选中，绘制半透明边框
        elif self.hovered:
            pen = QPen(QColor(255, 255, 255, 120))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), actual_radius + 1, actual_radius + 1)

class RainbowColorButton(QWidget):
    """彩虹颜色按钮，用于打开更多颜色选择"""
    
    clicked = pyqtSignal()
    
    def __init__(self, size=30, parent=None):
        super().__init__(parent)
        self.logger = get_logger("RainbowColorButton")
        
        # 初始化属性
        self.hovered = False
        self._scale = 1.0  # 用于动画效果
        
        # 设置固定大小
        self.base_size = size
        self.setFixedSize(size, size)
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        # 添加阴影效果
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(6)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
        # 创建动画
        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 定义彩虹颜色
        self.rainbow_colors = [
            [231, 76, 60],    # 红色
            [241, 196, 15],   # 黄色
            [46, 204, 113],   # 绿色
            [52, 152, 219],   # 蓝色
            [155, 89, 182],   # 紫色
        ]
    
    # 定义Qt属性，用于动画效果
    @pyqtProperty(float)
    def scale(self):
        return self._scale
        
    @scale.setter
    def scale(self, value):
        self._scale = value
        # 移除setFixedSize调用，不改变组件实际大小
        self.update()
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.hovered = True
        self.scale_animation.setStartValue(1.0)
        self.scale_animation.setEndValue(1.1)
        self.scale_animation.start()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.hovered = False
        self.scale_animation.setStartValue(self._scale)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.start()
        self.shadow.setBlurRadius(6)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def paintEvent(self, event):
        """绘制彩虹色按钮"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # 获取组件中心和尺寸
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # 保存画家状态
        painter.save()
        
        # 应用缩放变换 - 从中心点缩放
        painter.translate(center_x, center_y)
        painter.scale(self._scale, self._scale)
        painter.translate(-center_x, -center_y)
        
        # 定义基本形状
        radius = min(width, height) / 2 - 2
        outer_circle = QRect(int(center_x - radius), int(center_y - radius), 
                          int(radius * 2), int(radius * 2))
        
        # 绘制彩虹色圆环
        color_count = len(self.rainbow_colors)
        for i in range(color_count):
            # 每个颜色占据的角度范围
            start_angle = i * 360 / color_count
            span_angle = 360 / color_count
            
            # 设置颜色
            color = self.rainbow_colors[i]
            painter.setBrush(QBrush(QColor(color[0], color[1], color[2])))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # 绘制扇形
            painter.drawPie(outer_circle, int(start_angle * 16), int(span_angle * 16))
        
        # 绘制白色中心圆和加号
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawEllipse(QPointF(center_x, center_y), radius * 0.5, radius * 0.5)
        
        # 绘制加号
        pen = QPen(QColor(60, 60, 60))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # 横线
        line_length = radius * 0.4
        painter.drawLine(
            QPointF(center_x - line_length/2, center_y),
            QPointF(center_x + line_length/2, center_y)
        )
        
        # 竖线
        painter.drawLine(
            QPointF(center_x, center_y - line_length/2),
            QPointF(center_x, center_y + line_length/2)
        )
        
        # 恢复画家状态
        painter.restore()
        
        # 如果悬停，绘制边框（在原始大小上绘制边框）
        if self.hovered:
            pen = QPen(QColor(255, 255, 255, 180))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), radius + 1, radius + 1)

class ColorDialogPanel(QDialog):
    """自定义颜色对话框面板"""
    
    colorSelected = pyqtSignal(list)  # 颜色选择信号
    
    def __init__(self, initial_color=[52, 152, 219], parent=None):
        super().__init__(parent)
        self.logger = get_logger("ColorDialogPanel")
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        
        # 初始颜色
        self.color = initial_color.copy()
        
        # 定义UI
        self.initUI()
        
        # 更新显示
        self.updateColorDisplay()
        
        self.logger.info("颜色对话框面板初始化完成")
    
    def initUI(self):
        """初始化用户界面"""
        # 设置固定大小
        self.setFixedSize(380, 500)  # 增加高度，避免组件重叠
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)  # 增加组件间距
        
        # 创建标题标签
        title = QLabel("精确调色")
        title.setStyleSheet("color: #333; font-weight: bold; font-size: 14px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # 创建颜色预览框
        self.color_preview = QFrame()
        self.color_preview.setFixedHeight(50)  # 固定高度
        self.color_preview.setFrameShape(QFrame.Shape.NoFrame)
        self.color_preview.setStyleSheet("border-radius: 5px;")
        main_layout.addWidget(self.color_preview)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #ddd;")
        main_layout.addWidget(separator)
        
        # 创建调色板容器
        palette_container = QWidget()
        palette_container.setFixedHeight(170)  # 固定高度
        palette_container.setStyleSheet("""
            background-color: #f8f8f8;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        """)
        
        # 创建调色板，5行8列
        palette_layout = QGridLayout(palette_container)
        palette_layout.setSpacing(8)  # 适当调整间距
        palette_layout.setContentsMargins(8, 8, 8, 8)  # 调整容器内部边距
        
        # 调色板颜色 (5行8列)，更多丰富的色调，避免与基础选色中的颜色重复
        self.palette_colors = [
            # 第一行：更多红色系色调
            [[255, 102, 51], [255, 77, 77], [255, 26, 26], [204, 51, 0], 
             [153, 0, 0], [128, 0, 0], [102, 0, 0], [77, 0, 0]],
            # 第二行：更多橙黄色系
            [[255, 179, 102], [255, 204, 128], [255, 230, 179], [255, 166, 77], 
             [230, 138, 0], [204, 122, 0], [179, 107, 0], [153, 92, 0]],
            # 第三行：更多多绿色系
            [[179, 255, 179], [102, 255, 102], [77, 230, 77], [51, 179, 51], 
             [31, 122, 31], [0, 77, 0], [20, 51, 20], [5, 31, 5]],
            # 第四行：更多多蓝色系
            [[179, 217, 255], [128, 191, 255], [77, 166, 255], [102, 140, 255], 
             [51, 102, 255], [0, 0, 153], [0, 0, 102], [0, 0, 77]],
            # 第五行：更多紫色粉色系
            [[230, 179, 255], [204, 153, 255], [179, 102, 255], [153, 51, 255], 
             [255, 179, 230], [255, 128, 217], [255, 77, 196], [204, 0, 143]]
        ]
        
        # 创建颜色样本
        self.swatches = []
        swatch_size = 20  # 再次减小样本大小，确保适合容器
        
        for row, row_colors in enumerate(self.palette_colors):
            for col, color in enumerate(row_colors):
                swatch = ColorSwatch(color, swatch_size)
                swatch.clicked.connect(self.onColorSelected)
                # 添加到网格布局，确保每个样本位置正确
                palette_layout.addWidget(swatch, row, col, Qt.AlignmentFlag.AlignCenter)
                self.swatches.append(swatch)
        
        # 添加面板到主布局
        main_layout.addWidget(palette_container)
        
        # 添加分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("background-color: #ddd;")
        main_layout.addWidget(separator2)
        
        # RGB滑块
        rgb_layout = QVBoxLayout()
        rgb_layout.setSpacing(8)
        
        # 红色滑块
        r_layout = QHBoxLayout()
        r_label = QLabel("R:")
        r_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        r_label.setMinimumWidth(15)
        
        self.r_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.r_slider.setRange(0, 255)
        self.r_slider.setValue(self.color[0])
        self.r_slider.setPrimaryColor([231, 76, 60])  # 红色
        self.r_slider.valueChanged.connect(self.onSliderColorChanged)
        
        self.r_value = QLabel(str(self.color[0]))
        self.r_value.setMinimumWidth(30)
        self.r_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        r_layout.addWidget(r_label)
        r_layout.addWidget(self.r_slider)
        r_layout.addWidget(self.r_value)
        rgb_layout.addLayout(r_layout)
        
        # 绿色滑块
        g_layout = QHBoxLayout()
        g_label = QLabel("G:")
        g_label.setStyleSheet("color: #27AE60; font-weight: bold;")
        g_label.setMinimumWidth(15)
        
        self.g_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.g_slider.setRange(0, 255)
        self.g_slider.setValue(self.color[1])
        self.g_slider.setPrimaryColor([46, 204, 113])  # 绿色
        self.g_slider.valueChanged.connect(self.onSliderColorChanged)
        
        self.g_value = QLabel(str(self.color[1]))
        self.g_value.setMinimumWidth(30)
        self.g_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        g_layout.addWidget(g_label)
        g_layout.addWidget(self.g_slider)
        g_layout.addWidget(self.g_value)
        rgb_layout.addLayout(g_layout)
        
        # 蓝色滑块
        b_layout = QHBoxLayout()
        b_label = QLabel("B:")
        b_label.setStyleSheet("color: #3498DB; font-weight: bold;")
        b_label.setMinimumWidth(15)
        
        self.b_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.b_slider.setRange(0, 255)
        self.b_slider.setValue(self.color[2])
        self.b_slider.setPrimaryColor([52, 152, 219])  # 蓝色
        self.b_slider.valueChanged.connect(self.onSliderColorChanged)
        
        self.b_value = QLabel(str(self.color[2]))
        self.b_value.setMinimumWidth(30)
        self.b_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        b_layout.addWidget(b_label)
        b_layout.addWidget(self.b_slider)
        b_layout.addWidget(self.b_value)
        rgb_layout.addLayout(b_layout)
        
        main_layout.addLayout(rgb_layout)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 应用按钮
        self.apply_button = AnimatedButton("应用", primary_color=[52, 152, 219])
        self.apply_button.setMinimumHeight(35)
        self.apply_button.clicked.connect(self.onApply)
        
        # 取消按钮
        self.cancel_button = AnimatedButton("取消", primary_color=[149, 165, 166])
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 设置布局
        self.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
            }
            QLabel {
                color: #333;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def updateColorDisplay(self):
        """更新颜色显示"""
        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: rgb({self.color[0]}, {self.color[1]}, {self.color[2]});
                border-radius: 5px;
            }}
        """)
        
        # 更新数值标签
        self.r_value.setText(str(self.color[0]))
        self.g_value.setText(str(self.color[1]))
        self.b_value.setText(str(self.color[2]))
        
        # 更新滑块而不触发信号
        self.r_slider.blockSignals(True)
        self.g_slider.blockSignals(True)
        self.b_slider.blockSignals(True)
        
        self.r_slider.setValue(self.color[0])
        self.g_slider.setValue(self.color[1])
        self.b_slider.setValue(self.color[2])
        
        self.r_slider.blockSignals(False)
        self.g_slider.blockSignals(False)
        self.b_slider.blockSignals(False)
    
    def onSliderColorChanged(self):
        """滑块颜色改变时更新颜色"""
        self.color[0] = self.r_slider.value()
        self.color[1] = self.g_slider.value()
        self.color[2] = self.b_slider.value()
        self.updateColorDisplay()
    
    def onColorSelected(self, color):
        """颜色样本被选中时更新颜色"""
        self.color = color.copy()
        self.updateColorDisplay()
    
    def onApply(self):
        """应用选择的颜色"""
        self.colorSelected.emit(self.color)
        self.accept()
    
    def setColor(self, color):
        """设置当前颜色"""
        if isinstance(color, list) and len(color) >= 3:
            self.color = color.copy()
            self.updateColorDisplay()
    
    def paintEvent(self, event):
        """自定义绘制，确保圆角和阴影效果"""
        super().paintEvent(event)
        
        # 绘制边框
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置画笔
        pen = QPen(QColor(200, 200, 200))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # 绘制圆角矩形
        painter.drawRoundedRect(0, 0, self.width()-1, self.height()-1, 10, 10)

class AnimatedColorPicker(QWidget):
    """动画色彩选择器，用于从预设颜色中选择，或打开自定义颜色对话框"""
    
    colorChanged = pyqtSignal(list)  # 发送RGB颜色列表
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("AnimatedColorPicker")
        
        # 预设颜色方案
        self.preset_colors = [
            [52, 152, 219],    # 蓝色
            [41, 128, 185],    # 深蓝色
            [155, 89, 182],    # 紫色
            [142, 68, 173],    # 深紫色
            [26, 188, 156],    # 青绿色
            [22, 160, 133],    # 深青绿色
            [46, 204, 113],    # 绿色
            [39, 174, 96],     # 深绿色
            [241, 196, 15],    # 黄色
            [243, 156, 18],    # 橙色
            [230, 126, 34],    # 橙红色
            [231, 76, 60],     # 红色
            [192, 57, 43],     # 深红色
            [149, 165, 166],   # 灰色
            [127, 140, 141],   # 深灰色
            [0, 0, 0]          # 黑色
        ]
        
        # 当前选择的颜色
        self.current_color = [52, 152, 219]  # 默认蓝色
        
        # 初始化UI
        self.initUI()
        
        # 创建颜色对话框（需要时再显示）
        self.color_dialog = ColorDialogPanel(self.current_color)
        self.color_dialog.colorSelected.connect(self.on_color_selected)
        
        self.logger.info("色彩选择器初始化完成")
    
    def initUI(self):
        """初始化用户界面"""
        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 创建颜色样本
        self.swatches = []
        for color in self.preset_colors:
            swatch = ColorSwatch(color, 30, self.current_color == color)
            swatch.clicked.connect(self.on_color_selected)
            self.swatches.append(swatch)
            layout.addWidget(swatch)
        
        # 创建彩虹色按钮替代原来的颜色对话按钮
        self.color_dialog_button = RainbowColorButton(30)
        self.color_dialog_button.clicked.connect(self.open_color_dialog)
        layout.addWidget(self.color_dialog_button)
        
        # 设置布局
        self.setLayout(layout)
        
        # 调整大小策略
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    
    def open_color_dialog(self):
        """打开颜色对话框"""
        # 设置当前颜色
        self.color_dialog.setColor(self.current_color)
        
        # 居中显示对话框
        parent_rect = self.parentWidget().geometry() if self.parentWidget() else self.geometry()
        self.color_dialog.move(
            parent_rect.x() + (parent_rect.width() - self.color_dialog.width()) // 2,
            parent_rect.y() + (parent_rect.height() - self.color_dialog.height()) // 2
        )
        
        # 显示对话框
        result = self.color_dialog.exec()
    
    def on_color_selected(self, color):
        """处理颜色选择事件"""
        # 更新当前颜色
        self.current_color = color
        
        # 更新样本选中状态
        found_match = False
        for swatch in self.swatches:
            is_match = self._colors_equal(swatch.color, color)
            swatch.set_selected(is_match)
            if is_match:
                found_match = True
        
        # 如果没有匹配预设颜色，取消所有选中状态
        if not found_match:
            for swatch in self.swatches:
                swatch.set_selected(False)
        
        # 发送信号
        self.colorChanged.emit(color)
        
        self.logger.debug(f"选择颜色: RGB({color[0]}, {color[1]}, {color[2]})")
    
    def _colors_equal(self, color1, color2):
        """比较两个颜色值是否相等"""
        if len(color1) >= 3 and len(color2) >= 3:
            return (color1[0] == color2[0] and 
                    color1[1] == color2[1] and 
                    color1[2] == color2[2])
        return False
    
    def set_color(self, color):
        """设置当前颜色"""
        if isinstance(color, list) and len(color) >= 3:
            # 更新当前颜色
            self.current_color = color
            
            # 检查是否匹配预设颜色
            match_found = False
            for swatch in self.swatches:
                is_match = self._colors_equal(swatch.color, color)
                swatch.set_selected(is_match)
                if is_match:
                    match_found = True
            
            self.update()
            
            self.logger.debug(f"设置颜色: RGB({color[0]}, {color[1]}, {color[2]})")
    
    def get_color(self):
        """获取当前颜色"""
        return self.current_color

# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建一个窗口
    window = QWidget()
    window.setWindowTitle("色彩选择器测试")
    window.setMinimumSize(600, 200)
    
    # 创建布局
    layout = QVBoxLayout(window)
    
    # 添加标题
    title = QLabel("GestroKey 色彩选择器")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")
    layout.addWidget(title)
    
    # 添加说明
    desc = QLabel("选择一个预设颜色，或点击+号打开自定义颜色对话框")
    desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
    desc.setStyleSheet("font-size: 10pt; margin-bottom: 20px;")
    layout.addWidget(desc)
    
    # 添加颜色选择器
    picker = AnimatedColorPicker()
    picker.set_color([231, 76, 60])  # 设置初始颜色为红色
    
    # 添加当前颜色显示
    color_display = QLabel()
    color_display.setFixedHeight(50)
    color_display.setStyleSheet("background-color: rgb(231, 76, 60); border-radius: 5px;")
    
    # 连接信号
    def on_color_change(color):
        r, g, b = color[0], color[1], color[2]
        color_display.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border-radius: 5px;")
    
    picker.colorChanged.connect(on_color_change)
    
    # 添加到布局
    layout.addWidget(picker, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(color_display, 1)
    
    # 显示窗口
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec()) 