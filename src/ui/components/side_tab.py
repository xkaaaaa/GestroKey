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
    from ui.components.animated_stacked_widget import AnimatedStackedWidget
except ImportError:
    # 相对导入处理，便于直接运行此文件进行测试
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger
    from ui.components.animated_stacked_widget import AnimatedStackedWidget

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
    
    # 选项卡位置常量
    POSITION_TOP = 0      # 顶部位置
    POSITION_BOTTOM = 1   # 底部位置
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("SideTabWidget")
        
        # 选项卡数据结构
        self._buttons = []         # 按钮列表
        self._widgets = []         # 内容窗口列表
        self._positions = []       # 选项卡位置列表
        self._current_index = -1   # 当前选中的选项卡索引
        self._animations_enabled = True  # 是否启用动画
        
        # 设置UI
        self._setup_ui()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建主布局
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # 左侧选项卡区域
        self._tab_area = QWidget()
        self._tab_area.setObjectName("tabArea")
        self._tab_area.setMinimumWidth(180)
        self._tab_area.setMaximumWidth(250)
        
        # 选项卡布局
        self._tab_layout = QVBoxLayout(self._tab_area)
        self._tab_layout.setContentsMargins(0, 10, 0, 10)
        self._tab_layout.setSpacing(5)
        
        # 创建位置容器
        self._top_container = QWidget()
        self._top_layout = QVBoxLayout(self._top_container)
        self._top_layout.setContentsMargins(0, 0, 0, 0)
        self._top_layout.setSpacing(5)
        
        self._bottom_container = QWidget()
        self._bottom_layout = QVBoxLayout(self._bottom_container)
        self._bottom_layout.setContentsMargins(0, 0, 0, 0)
        self._bottom_layout.setSpacing(5)
        
        # 添加位置容器到主选项卡布局
        self._tab_layout.addWidget(self._top_container)
        self._tab_layout.addStretch(1)  # 底部区域固定在底部
        self._tab_layout.addWidget(self._bottom_container)
        
        # 内容窗口容器 - 使用动画堆栈组件替代普通堆栈组件
        self._stack = AnimatedStackedWidget()
        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_RIGHT_TO_LEFT)
        self._stack.setAnimationDuration(300)
        self._stack.setAnimationCurve(QEasingCurve.OutCubic)
        
        # 添加到主布局
        self._main_layout.addWidget(self._tab_area, 0)  # 固定宽度
        self._main_layout.addWidget(self._stack, 1)     # 自动扩展
        
        # 设置样式
        self._apply_styles()
    
    def _apply_styles(self):
        """应用样式"""
        # 可以在这里设置QSS样式
        pass
    
    def addTab(self, widget, text, icon=None, position=POSITION_TOP):
        """
        添加新的选项卡
        
        参数:
            widget: 选项卡内容窗口
            text: 选项卡文本
            icon: 选项卡图标（可选）
            position: 选项卡位置
                      POSITION_TOP - 顶部位置（默认）
                      POSITION_BOTTOM - 底部位置
        
        返回:
            int: 新选项卡的索引
        """
        # 创建选项卡按钮
        button = AnimatedTabButton(text, icon)
        
        # 根据位置添加按钮
        if position == self.POSITION_TOP:
            self._top_layout.addWidget(button)
        elif position == self.POSITION_BOTTOM:
            self._bottom_layout.addWidget(button)
        else:
            # 如果位置无效，默认添加到顶部
            self.logger.warning(f"无效的选项卡位置: {position}，使用顶部位置代替")
            position = self.POSITION_TOP
            self._top_layout.addWidget(button)
        
        # 连接点击事件
        button.clicked.connect(lambda: self.setCurrentIndex(self._buttons.index(button)))
        
        # 将内容窗口添加到堆栈
        self._stack.addWidget(widget)
        
        # 添加到列表
        self._buttons.append(button)
        self._widgets.append(widget)
        self._positions.append(position)
        
        # 如果是第一个选项卡，设为当前选项卡
        if len(self._buttons) == 1:
            self.setCurrentIndex(0)
        
        self.logger.debug(f"添加选项卡: {text}, 位置: {position}, 索引: {len(self._buttons) - 1}")
        
        # 返回新选项卡的索引
        return len(self._buttons) - 1
    
    def setCurrentIndex(self, index):
        """
        设置当前选项卡
        
        参数:
            index: 选项卡索引
        """
        if index < 0 or index >= len(self._buttons):
            self.logger.warning(f"尝试设置无效的选项卡索引: {index}")
            return
        
        # 如果相同，不做任何事
        if self._current_index == index:
            return
        
        # 更新当前索引
        old_index = self._current_index
        self._current_index = index
        
        self.logger.debug(f"切换选项卡: {old_index} -> {index}")
        
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
    
    def currentIndex(self):
        """返回当前选项卡索引"""
        return self._current_index
    
    def count(self):
        """返回选项卡数量"""
        return len(self._buttons)
    
    def widget(self, index):
        """返回指定索引的内容窗口"""
        if index < 0 or index >= len(self._widgets):
            return None
        return self._widgets[index]
    
    def setTabText(self, index, text):
        """设置选项卡文本"""
        if index < 0 or index >= len(self._buttons):
            return
        self._buttons[index].setText(text)
    
    def setTabIcon(self, index, icon):
        """设置选项卡图标"""
        if index < 0 or index >= len(self._buttons):
            return
        self._buttons[index].setIcon(icon)
    
    def setAnimationsEnabled(self, enabled):
        """设置是否启用动画效果"""
        self._animations_enabled = enabled
        
    def setTabPosition(self, index, position):
        """
        更改已有选项卡的位置
        
        参数:
            index: 选项卡索引
            position: 新位置 (POSITION_TOP 或 POSITION_BOTTOM)
        """
        if index < 0 or index >= len(self._buttons):
            self.logger.warning(f"尝试设置无效的选项卡索引位置: {index}")
            return
        
        # 检查位置值是否有效
        if position not in [self.POSITION_TOP, self.POSITION_BOTTOM]:
            self.logger.warning(f"无效的选项卡位置值: {position}，使用顶部位置")
            position = self.POSITION_TOP
        
        # 如果位置没变，不做任何事
        if self._positions[index] == position:
            return
        
        # 记录旧位置
        old_position = self._positions[index]
        button = self._buttons[index]
        
        # 从旧容器移除按钮
        if old_position == self.POSITION_TOP:
            self._top_layout.removeWidget(button)
        elif old_position == self.POSITION_BOTTOM:
            self._bottom_layout.removeWidget(button)
        
        # 添加到新容器
        if position == self.POSITION_TOP:
            self._top_layout.addWidget(button)
        elif position == self.POSITION_BOTTOM:
            self._bottom_layout.addWidget(button)
        
        # 更新位置记录
        self._positions[index] = position
        
        self.logger.debug(f"选项卡 {index} 位置变更: {old_position} -> {position}")
    
    def tabPosition(self, index):
        """
        获取选项卡的位置
        
        参数:
            index: 选项卡索引
        
        返回:
            int: 选项卡位置 (POSITION_TOP 或 POSITION_BOTTOM)
        """
        if index < 0 or index >= len(self._positions):
            return self.POSITION_TOP  # 默认返回顶部位置
        return self._positions[index]


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
    
    tab3 = QWidget()
    tab3_layout = QVBoxLayout(tab3)
    tab3_layout.addWidget(QLabel("手势管理选项卡内容"))
    
    # 创建图标（使用本地图标文件）
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/images')
    console_icon_path = os.path.join(icons_dir, 'console.svg')
    settings_icon_path = os.path.join(icons_dir, 'settings.svg')
    gestures_icon_path = os.path.join(icons_dir, 'gestures.svg')

    # 如果图标文件存在则使用，否则使用空图标
    console_icon = QIcon(console_icon_path) if os.path.exists(console_icon_path) else QIcon()
    settings_icon = QIcon(settings_icon_path) if os.path.exists(settings_icon_path) else QIcon()
    gestures_icon = QIcon(gestures_icon_path) if os.path.exists(gestures_icon_path) else QIcon()
    
    # 添加选项卡 - 使用位置参数
    # 控制台选项卡放在顶部
    tab_widget.addTab(tab1, "控制台", console_icon, tab_widget.POSITION_TOP)
    # 手势管理选项卡放在底部
    tab_widget.addTab(tab3, "手势管理", gestures_icon, tab_widget.POSITION_BOTTOM)
    # 设置选项卡放在底部
    tab_widget.addTab(tab2, "设置", settings_icon, tab_widget.POSITION_BOTTOM)
    
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
    - <b>支持选项卡位置设置</b>：可将选项卡放置在顶部或底部<br/>
    </p>
    </html>
    """)
    info.setAlignment(Qt.AlignCenter)
    layout.addWidget(info)
    
    # 添加位置切换按钮
    buttons_layout = QHBoxLayout()
    
    move_to_top = AnimatedButton("移至顶部", primary_color=[41, 128, 185])
    move_to_bottom = AnimatedButton("移至底部", primary_color=[41, 128, 185])
    
    # 连接按钮事件
    current_tab_index = 0
    move_to_top.clicked.connect(lambda: tab_widget.setTabPosition(current_tab_index, tab_widget.POSITION_TOP))
    move_to_bottom.clicked.connect(lambda: tab_widget.setTabPosition(current_tab_index, tab_widget.POSITION_BOTTOM))
    
    buttons_layout.addWidget(move_to_top)
    buttons_layout.addWidget(move_to_bottom)
    
    layout.addLayout(buttons_layout)
    
    window.show()
    sys.exit(app.exec_()) 