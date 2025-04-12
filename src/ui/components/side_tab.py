import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTabBar, QStackedWidget, QStyleOption, QStyle)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QRect, QEasingCurve, QSize, 
                        pyqtProperty, QPoint, QRectF, QParallelAnimationGroup, pyqtSignal)
from PyQt6.QtGui import (QColor, QPainter, QFont, QIcon, QPainterPath, 
                        QBrush, QPen, QLinearGradient)

try:
    from core.logger import get_logger
    from ui.components.animated_stacked_widget import AnimatedStackedWidget
except ImportError:
    # 相对导入处理，便于直接运行此文件进行测试
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger
    from ui.components.animated_stacked_widget import AnimatedStackedWidget

class AnimatedNavigationButton(QWidget):
    """
    动画导航按钮
    
    带有动画效果的导航按钮，用于SideNavigationMenu组件。
    采用扁平化设计，提供悬停和选中状态的动画效果。
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, text="", icon=None, parent=None):
        super().__init__(parent)
        self.logger = get_logger("AnimatedNavigationButton")
        
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
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 设置动画
        self._setup_animations()
        
        # 允许鼠标追踪
        self.setMouseTracking(True)
    
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
            text_x = icon_size + 30 if self._icon else 20
            text_rect = self.rect().adjusted(text_x, 0, -10, 0)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._text)
    
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
    """侧边栏导航菜单组件
    一个位于左侧的垂直导航菜单组件，带有平滑的动画效果和现代的扁平化设计风格。
    """
    
    currentChanged = pyqtSignal(int)
    
    # 导航菜单位置常量
    POSITION_TOP = 0    # 顶部位置
    POSITION_BOTTOM = 1 # 底部位置
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("SideNavigationMenu")
        
        # 导航菜单数据结构
        self._buttons = []      # 导航按钮列表
        self._widgets = []      # 内容窗口列表
        self._positions = []    # 导航按钮位置列表
        self._current_index = -1   # 当前选中的导航按钮索引
        self._animations_enabled = True  # 是否启用动画
        
        # 设置UI
        self._setup_ui()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建主布局
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # 左侧导航菜单区域
        self._nav_area = QWidget()
        self._nav_area.setObjectName("navArea")
        self._nav_area.setMinimumWidth(180)
        self._nav_area.setMaximumWidth(250)
        
        # 导航菜单布局
        self._nav_layout = QVBoxLayout(self._nav_area)
        self._nav_layout.setContentsMargins(0, 10, 0, 10)
        self._nav_layout.setSpacing(5)
        
        # 创建位置容器
        self._top_container = QWidget()
        self._top_layout = QVBoxLayout(self._top_container)
        self._top_layout.setContentsMargins(0, 0, 0, 0)
        self._top_layout.setSpacing(5)
        
        self._bottom_container = QWidget()
        self._bottom_layout = QVBoxLayout(self._bottom_container)
        self._bottom_layout.setContentsMargins(0, 0, 0, 0)
        self._bottom_layout.setSpacing(5)
        
        # 添加位置容器到主导航菜单布局
        self._nav_layout.addWidget(self._top_container)
        self._nav_layout.addStretch(1)  # 底部区域固定在底部
        self._nav_layout.addWidget(self._bottom_container)
        
        # 内容窗口容器 - 使用动画堆栈组件替代普通堆栈组件
        self._stack = AnimatedStackedWidget()
        self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_RIGHT_TO_LEFT)
        self._stack.setAnimationDuration(300)
        self._stack.setAnimationCurve(QEasingCurve.Type.OutCubic)
        
        # 添加到主布局
        self._main_layout.addWidget(self._nav_area, 0)  # 固定宽度
        self._main_layout.addWidget(self._stack, 1)     # 自动扩展
        
        # 设置样式
        self._apply_styles()
    
    def _apply_styles(self):
        """应用样式"""
        # 可以在这里设置QSS样式
        pass
    
    def addPage(self, widget, text, icon=None, position=POSITION_TOP):
        """添加新的导航页面
        
        Args:
            widget: 页面内容窗口
            text: 页面文本
            icon: 页面图标（可选）
            position: 页面位置
            
        Returns:
            int: 新页面的索引
        """
        # 创建导航按钮
        button = AnimatedNavigationButton(text, icon)
        
        # 根据位置添加按钮
        if position == self.POSITION_TOP:
            self._top_layout.addWidget(button)
        elif position == self.POSITION_BOTTOM:
            self._bottom_layout.addWidget(button)
        else:
            # 如果位置无效，默认添加到顶部
            self.logger.warning(f"无效的页面位置: {position}，使用顶部位置代替")
            position = self.POSITION_TOP
            self._top_layout.addWidget(button)
        
        # 连接点击事件
        button.clicked.connect(lambda: self.setCurrentPage(self._buttons.index(button)))
        
        # 将内容窗口添加到堆栈
        self._stack.addWidget(widget)
        
        # 添加到列表
        self._buttons.append(button)
        self._widgets.append(widget)
        self._positions.append(position)
        
        # 如果是第一个页面，设为当前页面
        if len(self._buttons) == 1:
            self.setCurrentPage(0)
        
        self.logger.debug(f"添加页面: {text}, 位置: {position}, 索引: {len(self._buttons) - 1}")
        
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
            current_container_layout = self._top_layout if current_position == self.POSITION_TOP else self._bottom_layout
            current_index_in_container = current_container_layout.indexOf(current_button)
            
            # 获取目标选项卡在其所在容器中的索引
            target_button = self._buttons[index]
            target_container_layout = self._top_layout if target_position == self.POSITION_TOP else self._bottom_layout
            target_index_in_container = target_container_layout.indexOf(target_button)
            
            # 确定动画方向
            if current_position == target_position:
                # 在同一个位置区域内的切换
                if current_index_in_container < target_index_in_container:
                    # 从上到下切换时，内容从下方进入
                    self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_BOTTOM_TO_TOP)
                    self.logger.debug(f"在{current_position}区域内从上到下切换: {self._current_index} -> {index}")
                else:
                    # 从下到上切换时，内容从上方进入
                    self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_TOP_TO_BOTTOM)
                    self.logger.debug(f"在{current_position}区域内从下到上切换: {self._current_index} -> {index}")
            else:
                # 跨位置区域的切换
                if current_position == self.POSITION_TOP and target_position == self.POSITION_BOTTOM:
                    # 从上方区域切换到下方区域，内容从下方进入
                    self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_BOTTOM_TO_TOP)
                    self.logger.debug(f"从顶部区域切换到底部区域: {self._current_index} -> {index}")
                else:
                    # 从下方区域切换到上方区域，内容从上方进入
                    self._stack.setAnimationType(AnimatedStackedWidget.ANIMATION_TOP_TO_BOTTOM)
                    self.logger.debug(f"从底部区域切换到顶部区域: {self._current_index} -> {index}")
        
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
        
    def setPagePosition(self, index, position):
        """更改已有页面的位置
        
        Args:
            index: 页面索引
            position: 新位置
        """
        if index < 0 or index >= len(self._buttons):
            self.logger.warning(f"尝试设置无效的页面索引位置: {index}")
            return
        
        # 检查位置值是否有效
        if position not in [self.POSITION_TOP, self.POSITION_BOTTOM]:
            self.logger.warning(f"无效的页面位置值: {position}，使用顶部位置")
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
        
        self.logger.debug(f"页面 {index} 位置变更: {old_position} -> {position}")
    
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
    window.setWindowTitle("SideNavigationMenu 示例")
    window.setMinimumSize(800, 600)
    
    layout = QVBoxLayout(window)
    
    # 创建SideNavigationMenu
    nav_menu = SideNavigationMenu()
    
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
    
    # 创建图标（使用本地图标文件）
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/images')
    console_icon_path = os.path.join(icons_dir, 'console.svg')
    settings_icon_path = os.path.join(icons_dir, 'settings.svg')
    gestures_icon_path = os.path.join(icons_dir, 'gestures.svg')

    # 如果图标文件存在则使用，否则使用空图标
    console_icon = QIcon(console_icon_path) if os.path.exists(console_icon_path) else QIcon()
    settings_icon = QIcon(settings_icon_path) if os.path.exists(settings_icon_path) else QIcon()
    gestures_icon = QIcon(gestures_icon_path) if os.path.exists(gestures_icon_path) else QIcon()
    
    # 添加页面 - 使用位置参数
    # 控制台页面放在顶部
    nav_menu.addPage(page1, "控制台", console_icon, nav_menu.POSITION_TOP)
    # 手势管理页面放在底部
    nav_menu.addPage(page3, "手势管理", gestures_icon, nav_menu.POSITION_BOTTOM)
    # 设置页面放在底部
    nav_menu.addPage(page2, "设置", settings_icon, nav_menu.POSITION_BOTTOM)
    
    layout.addWidget(nav_menu)
    
    # 信息标签
    info = QLabel("""
    <html>
    <p style='text-align:center; margin-top:20px;'>
    SideNavigationMenu 是一个左侧垂直导航菜单组件，具有以下特点：<br/>
    - 精美的扁平化设计<br/>
    - 流畅的切换动画效果<br/>
    - 页面的选中状态和悬停效果<br/>
    - 支持图标和文本<br/>
    - 符合应用主题风格<br/>
    - <b>支持页面位置设置</b>：可将页面放置在顶部或底部<br/>
    </p>
    </html>
    """)
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(info)
    
    # 添加位置切换按钮
    buttons_layout = QHBoxLayout()
    
    move_to_top = AnimatedButton("移至顶部", primary_color=[41, 128, 185])
    move_to_bottom = AnimatedButton("移至底部", primary_color=[41, 128, 185])
    
    # 连接按钮事件
    current_page_index = 0
    move_to_top.clicked.connect(lambda: nav_menu.setPagePosition(current_page_index, nav_menu.POSITION_TOP))
    move_to_bottom.clicked.connect(lambda: nav_menu.setPagePosition(current_page_index, nav_menu.POSITION_BOTTOM))
    
    buttons_layout.addWidget(move_to_top)
    buttons_layout.addWidget(move_to_bottom)
    
    layout.addLayout(buttons_layout)
    
    window.show()
    sys.exit(app.exec()) 