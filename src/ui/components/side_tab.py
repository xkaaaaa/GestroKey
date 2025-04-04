import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTabBar, QStackedWidget, QStyleOption, QStyle)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QRect, QEasingCurve, QSize, 
                        pyqtProperty, QPoint, QRectF, QParallelAnimationGroup, pyqtSignal)
from PyQt5.QtGui import (QColor, QPainter, QFont, QIcon, QPainterPath, 
                        QBrush, QPen, QLinearGradient)

try:
    from core.logger import get_logger
except ImportError:
    # 相对导入处理，便于直接运行此文件进行测试
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

class AnimatedTabButton(QWidget):
    """
    动画选项卡按钮
    
    带有动画效果的选项卡按钮，用于SideTabWidget组件。
    采用扁平化设计，提供悬停和选中状态的动画效果。
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, text="", icon=None, parent=None):
        super().__init__(parent)
        self.logger = get_logger("AnimatedTabButton")
        
        self._text = text
        self._icon = icon
        self._selected = False
        self._hovered = False
        
        # 动画属性
        self._highlight_opacity = 0.0
        self._indicator_position = 0.0
        self._indicator_opacity = 0.0
        
        # 颜色设置
        self._primary_color = QColor(41, 128, 185)  # 主题蓝色
        self._text_color = QColor(120, 120, 120)    # 默认文本颜色
        self._text_selected_color = QColor(41, 128, 185)  # 选中文本颜色
        
        # 设置固定大小
        self.setFixedHeight(48)
        self.setMinimumWidth(160)
        
        # 设置鼠标样式
        self.setCursor(Qt.PointingHandCursor)
        
        # 设置动画
        self._setup_animations()
        
        # 允许鼠标追踪
        self.setMouseTracking(True)
    
    def _setup_animations(self):
        """设置动画效果"""
        # 高亮动画
        self._highlight_animation = QPropertyAnimation(self, b"highlight_opacity")
        self._highlight_animation.setDuration(200)
        self._highlight_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # 指示器位置动画
        self._indicator_pos_animation = QPropertyAnimation(self, b"indicator_position")
        self._indicator_pos_animation.setDuration(300)
        self._indicator_pos_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 指示器透明度动画
        self._indicator_opacity_animation = QPropertyAnimation(self, b"indicator_opacity")
        self._indicator_opacity_animation.setDuration(250)
        self._indicator_opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
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
        return QSize(180, 48)
    
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
        
        # 添加过渡动画效果
        current_text_color = painter_text_color = None
        if self._selected:
            painter_text_color = self._text_selected_color
        else:
            if self._highlight_opacity > 0:
                r = int(self._text_color.red() * (1 - self._highlight_opacity) + 
                      self._text_selected_color.red() * self._highlight_opacity)
                g = int(self._text_color.green() * (1 - self._highlight_opacity) + 
                      self._text_selected_color.green() * self._highlight_opacity)
                b = int(self._text_color.blue() * (1 - self._highlight_opacity) + 
                      self._text_selected_color.blue() * self._highlight_opacity)
                current_text_color = QColor(r, g, b)
            else:
                current_text_color = self._text_color
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 发射点击信号
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        if self._highlight_opacity > 0:
            # 计算高亮颜色 - 使用主题色的透明版本
            highlight_color = QColor(self._primary_color)
            highlight_color.setAlphaF(0.1 * self._highlight_opacity)
            
            # 绘制高亮背景
            painter.fillRect(self.rect(), highlight_color)
        
        # 绘制左侧指示器
        if self._indicator_opacity > 0:
            indicator_color = QColor(self._primary_color)
            indicator_color.setAlphaF(self._indicator_opacity)
            
            # 计算指示器几何形状
            indicator_height = self.height() * 0.7 * self._indicator_position
            indicator_y = (self.height() - indicator_height) / 2
            
            # 绘制指示器 - 使用QRectF可以接受浮点数
            indicator_rect = QRectF(0, indicator_y, 4, indicator_height)
            painter.fillRect(indicator_rect, indicator_color)
        
        # 绘制图标
        icon_size = 24
        if self._icon:
            icon_x = 20
            icon_y = (self.height() - icon_size) / 2
            
            # 将浮点数转换为整数，避免QRect类型错误
            icon_rect = QRect(int(icon_x), int(icon_y), icon_size, icon_size)
            
            self._icon.paint(painter, icon_rect, Qt.AlignCenter, 
                           QIcon.Normal if not self._selected else QIcon.Selected)
        
        # 绘制文本
        if self._text:
            # 根据选中状态确定文本颜色
            if self._selected:
                text_color = self._text_selected_color
            else:
                # 如果悬停，则混合颜色
                if self._highlight_opacity > 0:
                    r = int(self._text_color.red() * (1 - self._highlight_opacity) + 
                          self._text_selected_color.red() * self._highlight_opacity)
                    g = int(self._text_color.green() * (1 - self._highlight_opacity) + 
                          self._text_selected_color.green() * self._highlight_opacity)
                    b = int(self._text_color.blue() * (1 - self._highlight_opacity) + 
                          self._text_selected_color.blue() * self._highlight_opacity)
                    text_color = QColor(r, g, b)
                else:
                    text_color = self._text_color
            
            painter.setPen(text_color)
            
            # 设置字体
            font = painter.font()
            font.setPointSize(10)
            font.setBold(self._selected)
            painter.setFont(font)
            
            # 文本位置（考虑图标）
            text_x = icon_size + 30 if self._icon else 20
            text_rect = self.rect().adjusted(text_x, 0, -10, 0)
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self._text)
    
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


class SideTabWidget(QWidget):
    """
    左侧选项卡组件
    
    一个位于左侧的垂直选项卡组件，带有平滑的动画效果和现代的扁平化设计风格。
    支持图标和文本，有选中状态和悬停效果。
    """
    
    currentChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("SideTabWidget")
        
        # 初始化属性
        self._current_index = -1
        self._tab_buttons = []
        self._contents = []
        self._animations_enabled = True
        
        # 布局设置
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面布局"""
        # 主布局 - 水平布局
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # 左侧选项卡区域
        self._tab_area = QWidget()
        self._tab_area.setObjectName("sideTabArea")
        self._tab_area.setMinimumWidth(180)
        self._tab_area.setMaximumWidth(220)
        self._tab_layout = QVBoxLayout(self._tab_area)
        self._tab_layout.setContentsMargins(0, 10, 0, 10)
        self._tab_layout.setSpacing(5)
        self._tab_layout.setAlignment(Qt.AlignTop)
        
        # 内容区域
        self._content_stack = QStackedWidget()
        self._content_stack.setObjectName("sideContentStack")
        
        # 添加到主布局
        self._main_layout.addWidget(self._tab_area)
        self._main_layout.addWidget(self._content_stack, 1)  # 内容区域拉伸
        
        # 设置样式
        self._tab_area.setStyleSheet("""
            QWidget#sideTabArea {
                background-color: #f8f8f8;
                border-right: 1px solid #e0e0e0;
            }
        """)
    
    def addTab(self, widget, text, icon=None):
        """添加选项卡"""
        # 创建选项卡按钮
        tab_button = AnimatedTabButton(text, icon)
        tab_button.clicked.connect(lambda: self.setCurrentIndex(self._tab_buttons.index(tab_button)))
        
        # 添加到布局
        self._tab_layout.addWidget(tab_button)
        self._tab_buttons.append(tab_button)
        
        # 添加内容窗口
        self._content_stack.addWidget(widget)
        self._contents.append(widget)
        
        # 获取当前添加的索引
        current_index = len(self._tab_buttons) - 1
        
        # 如果是第一个选项卡，自动选中
        if len(self._tab_buttons) == 1:
            # 直接设置当前索引而不使用动画，避免初始状态的显示问题
            self._current_index = current_index
            self._tab_buttons[current_index].setSelected(True)
            self._content_stack.setCurrentIndex(current_index)
            # 第一次不触发信号，避免不必要的回调
        else:
            # 如果是后续添加的选项卡，只需更新UI状态
            tab_button.setSelected(False)
        
        return current_index
    
    def setCurrentIndex(self, index):
        """设置当前选项卡索引"""
        # 检查索引有效性和是否已经是当前索引
        if index < 0 or index >= len(self._tab_buttons) or index == self._current_index:
            return
        
        # 记录之前的索引
        previous_index = self._current_index
        
        # 更新选择状态
        if previous_index >= 0 and previous_index < len(self._tab_buttons):
            self._tab_buttons[previous_index].setSelected(False)
        
        # 更新当前索引
        self._current_index = index
        self._tab_buttons[index].setSelected(True)
        
        # 直接切换内容，不再使用动画
        self._content_stack.setCurrentIndex(index)
        self.logger.debug(f"切换到索引: {index}, 内容窗口: {self._contents[index].__class__.__name__}")
        
        # 发射信号
        self.currentChanged.emit(index)
    
    def currentIndex(self):
        """返回当前选项卡索引"""
        return self._current_index
    
    def count(self):
        """返回选项卡数量"""
        return len(self._tab_buttons)
    
    def widget(self, index):
        """返回指定索引的内容窗口"""
        if 0 <= index < len(self._contents):
            return self._contents[index]
        return None
    
    def setTabText(self, index, text):
        """设置选项卡文本"""
        if 0 <= index < len(self._tab_buttons):
            self._tab_buttons[index].setText(text)
    
    def setTabIcon(self, index, icon):
        """设置选项卡图标"""
        if 0 <= index < len(self._tab_buttons):
            self._tab_buttons[index].setIcon(icon)
    
    def setAnimationsEnabled(self, enabled):
        """设置是否启用动画"""
        self._animations_enabled = enabled


# 示例部分，仅在直接运行此文件时执行
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用Fusion样式以获得更好的跨平台一致性
    
    window = QWidget()
    window.setWindowTitle("SideTabWidget 示例")
    window.setMinimumSize(800, 600)
    
    layout = QVBoxLayout(window)
    
    # 创建SideTabWidget
    tab_widget = SideTabWidget()
    
    # 创建测试内容
    tab1 = QWidget()
    tab1_layout = QVBoxLayout(tab1)
    tab1_layout.addWidget(QLabel("控制台选项卡内容"))
    
    tab2 = QWidget()
    tab2_layout = QVBoxLayout(tab2)
    tab2_layout.addWidget(QLabel("设置选项卡内容"))
    
    # 创建图标（使用本地图标文件）
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/images')
    console_icon_path = os.path.join(icons_dir, 'console.svg')
    settings_icon_path = os.path.join(icons_dir, 'settings.svg')

    # 如果图标文件存在则使用，否则使用空图标
    console_icon = QIcon(console_icon_path) if os.path.exists(console_icon_path) else QIcon()
    settings_icon = QIcon(settings_icon_path) if os.path.exists(settings_icon_path) else QIcon()
    
    # 添加选项卡
    tab_widget.addTab(tab1, "控制台", console_icon)
    tab_widget.addTab(tab2, "设置", settings_icon)
    
    layout.addWidget(tab_widget)
    
    # 信息标签
    info = QLabel("""
    <html>
    <p style='text-align:center; margin-top:20px;'>
    SideTabWidget 是一个左侧垂直选项卡组件，具有以下特点：<br/>
    - 精美的扁平化设计<br/>
    - 流畅的切换动画效果<br/>
    - 选项卡的选中状态和悬停效果<br/>
    - 支持图标和文本<br/>
    - 符合应用主题风格<br/>
    </p>
    </html>
    """)
    info.setAlignment(Qt.AlignCenter)
    layout.addWidget(info)
    
    window.show()
    sys.exit(app.exec_()) 