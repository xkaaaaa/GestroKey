import sys
import os
from PyQt6.QtWidgets import QApplication, QStackedWidget, QWidget
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QPoint, 
                        pyqtProperty, pyqtSignal, QParallelAnimationGroup)
from PyQt6.QtGui import QPainter

try:
    from core.logger import get_logger
except ImportError:
    # 相对导入处理，便于直接运行此文件进行测试
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger

class AnimatedStackedWidget(QStackedWidget):
    """
    动画堆栈组件
    
    一个带有切换动画效果的堆栈组件，用于实现选项卡内容的平滑过渡。
    支持多种切换效果，如滑动、渐变等。
    """
    
    # 定义动画方向常量
    ANIMATION_LEFT_TO_RIGHT = 0    # 从左到右
    ANIMATION_RIGHT_TO_LEFT = 1    # 从右到左
    ANIMATION_TOP_TO_BOTTOM = 2    # 从上到下
    ANIMATION_BOTTOM_TO_TOP = 3    # 从下到上
    ANIMATION_FADE = 4             # 淡入淡出
    
    # 信号：动画完成时发出
    animationFinished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("AnimatedStackedWidget")
        
        # 动画属性
        self._fade_value = 0.0              # 淡入淡出值
        self._horizontal_offset = 0.0       # 水平偏移
        self._vertical_offset = 0.0         # 垂直偏移
        
        # 动画设置
        self._animation_type = self.ANIMATION_RIGHT_TO_LEFT  # 默认动画类型
        self._animation_duration = 300                       # 默认动画持续时间（毫秒）
        self._animation_curve = QEasingCurve.Type.OutCubic       # 默认动画曲线
        self._animations_enabled = True                      # 是否启用动画
        
        # 动画组
        self._animation_group = QParallelAnimationGroup(self)
        self._animation_group.finished.connect(self._onAnimationFinished)
        
        # 当前页面和下一页面的快照
        self._current_widget_snapshot = None
        self._next_widget_snapshot = None
        
        # 动画状态
        self._is_animating = False
        self._next_index = -1
        
        # 设置属性，允许窗口更新
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        
        # 启用自动填充背景
        self.setAutoFillBackground(False)
    
    # 属性访问器和修改器
    def _get_fade_value(self):
        return self._fade_value
    
    def _set_fade_value(self, value):
        self._fade_value = value
        self.update()
    
    def _get_horizontal_offset(self):
        return self._horizontal_offset
    
    def _set_horizontal_offset(self, value):
        self._horizontal_offset = value
        self.update()
    
    def _get_vertical_offset(self):
        return self._vertical_offset
    
    def _set_vertical_offset(self, value):
        self._vertical_offset = value
        self.update()
    
    # 定义PyQt属性
    fade_value = pyqtProperty(float, _get_fade_value, _set_fade_value)
    horizontal_offset = pyqtProperty(float, _get_horizontal_offset, _set_horizontal_offset)
    vertical_offset = pyqtProperty(float, _get_vertical_offset, _set_vertical_offset)
    
    def setAnimationEnabled(self, enabled):
        """设置是否启用动画"""
        self._animations_enabled = enabled
    
    def setAnimationType(self, animation_type):
        """设置动画类型"""
        if animation_type in [self.ANIMATION_LEFT_TO_RIGHT, self.ANIMATION_RIGHT_TO_LEFT,
                            self.ANIMATION_TOP_TO_BOTTOM, self.ANIMATION_BOTTOM_TO_TOP,
                            self.ANIMATION_FADE]:
            self._animation_type = animation_type
    
    def setAnimationDuration(self, duration):
        """设置动画持续时间（毫秒）"""
        if duration > 0:
            self._animation_duration = duration
    
    def setAnimationCurve(self, curve):
        """设置动画曲线"""
        self._animation_curve = curve
    
    def _onAnimationFinished(self):
        """动画完成时调用"""
        # 标记动画已完成
        self._is_animating = False
        
        # 通过父类方法切换到目标页面
        if self._next_index != -1:
            QStackedWidget.setCurrentIndex(self, self._next_index)
            self._next_index = -1
        
        # 释放快照资源
        self._current_widget_snapshot = None
        self._next_widget_snapshot = None
        
        # 更新所有子窗口的可见性
        for i in range(self.count()):
            widget = self.widget(i)
            if i == self.currentIndex():
                widget.setVisible(True)
            else:
                widget.setVisible(False)
        
        # 发射动画完成信号
        self.animationFinished.emit()
        
        # 强制更新
        self.update()
    
    def paintEvent(self, event):
        """绘制事件，用于实现自定义动画效果"""
        if not self._is_animating or not self._animations_enabled:
            # 如果没有动画，使用默认绘制
            super().paintEvent(event)
            return
        
        # 创建画笔
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self._animation_type == self.ANIMATION_FADE:
            # 淡入淡出效果
            if self._current_widget_snapshot and self._next_widget_snapshot:
                # 绘制当前页面，随着动画进度降低透明度
                painter.setOpacity(1.0 - self._fade_value)
                painter.drawPixmap(0, 0, self._current_widget_snapshot)
                
                # 绘制下一页面，随着动画进度增加透明度
                painter.setOpacity(self._fade_value)
                painter.drawPixmap(0, 0, self._next_widget_snapshot)
        
        elif self._animation_type in [self.ANIMATION_LEFT_TO_RIGHT, self.ANIMATION_RIGHT_TO_LEFT]:
            # 水平滑动效果
            if self._current_widget_snapshot and self._next_widget_snapshot:
                if self._animation_type == self.ANIMATION_LEFT_TO_RIGHT:
                    # 从左到右：当前页面向右移动，新页面从左进入
                    current_x = self._horizontal_offset
                    next_x = self._horizontal_offset - self.width()
                else:
                    # 从右到左：当前页面向左移动，新页面从右进入
                    current_x = self._horizontal_offset
                    next_x = self._horizontal_offset + self.width()
                
                # 绘制当前页面
                painter.drawPixmap(int(current_x), 0, self._current_widget_snapshot)
                
                # 绘制下一页面
                painter.drawPixmap(int(next_x), 0, self._next_widget_snapshot)
        
        elif self._animation_type in [self.ANIMATION_TOP_TO_BOTTOM, self.ANIMATION_BOTTOM_TO_TOP]:
            # 垂直滑动效果
            if self._current_widget_snapshot and self._next_widget_snapshot:
                if self._animation_type == self.ANIMATION_TOP_TO_BOTTOM:
                    # 从上到下：当前页面向下移动，新页面从上进入
                    current_y = self._vertical_offset
                    next_y = self._vertical_offset - self.height()
                else:
                    # 从下到上：当前页面向上移动，新页面从下进入
                    current_y = self._vertical_offset
                    next_y = self._vertical_offset + self.height()
                
                # 绘制当前页面
                painter.drawPixmap(0, int(current_y), self._current_widget_snapshot)
                
                # 绘制下一页面
                painter.drawPixmap(0, int(next_y), self._next_widget_snapshot)
    
    def setCurrentIndex(self, index):
        """设置当前索引，带动画效果"""
        # 检查索引是否有效
        if self.currentIndex() == index or index < 0 or index >= self.count():
            return
        
        if not self._animations_enabled:
            # 如果动画被禁用，直接切换
            super().setCurrentIndex(index)
            return
        
        # 如果动画已经在运行，停止它
        if self._is_animating:
            self._animation_group.stop()
            self._animation_group.clear()
            self._is_animating = False
            
            # 如果有快照，释放它们
            self._current_widget_snapshot = None
            self._next_widget_snapshot = None
        
        # 获取当前窗口和目标窗口
        current_widget = self.currentWidget()
        next_widget = self.widget(index)
        
        if not current_widget or not next_widget:
            # 如果窗口不存在，直接切换
            super().setCurrentIndex(index)
            return
        
        # 创建快照并设置可见性
        current_widget.setVisible(True)
        self._current_widget_snapshot = current_widget.grab()
        
        # 临时显示目标窗口以创建快照，然后隐藏所有窗口
        for i in range(self.count()):
            widget = self.widget(i)
            widget.setVisible(i == index)
            if i == index:
                self._next_widget_snapshot = widget.grab()
        
        # 隐藏所有窗口，将通过绘制快照来展示
        for i in range(self.count()):
            self.widget(i).setVisible(False)
        
        # 保存目标索引，用于动画结束后切换
        self._next_index = index
        
        # 设置动画标记
        self._is_animating = True
        
        # 根据动画类型设置动画
        self._animation_group.clear()
        
        if self._animation_type == self.ANIMATION_FADE:
            # 淡入淡出效果
            fade_anim = QPropertyAnimation(self, b"fade_value")
            fade_anim.setDuration(self._animation_duration)
            fade_anim.setStartValue(0.0)
            fade_anim.setEndValue(1.0)
            fade_anim.setEasingCurve(self._animation_curve)
            self._animation_group.addAnimation(fade_anim)
            
        elif self._animation_type in [self.ANIMATION_LEFT_TO_RIGHT, self.ANIMATION_RIGHT_TO_LEFT]:
            # 水平滑动效果
            horz_anim = QPropertyAnimation(self, b"horizontal_offset")
            horz_anim.setDuration(self._animation_duration)
            
            if self._animation_type == self.ANIMATION_LEFT_TO_RIGHT:
                # 从左到右
                horz_anim.setStartValue(0)
                horz_anim.setEndValue(self.width())
            else:
                # 从右到左
                horz_anim.setStartValue(0)
                horz_anim.setEndValue(-self.width())
            
            horz_anim.setEasingCurve(self._animation_curve)
            self._animation_group.addAnimation(horz_anim)
            
        elif self._animation_type in [self.ANIMATION_TOP_TO_BOTTOM, self.ANIMATION_BOTTOM_TO_TOP]:
            # 垂直滑动效果
            vert_anim = QPropertyAnimation(self, b"vertical_offset")
            vert_anim.setDuration(self._animation_duration)
            
            if self._animation_type == self.ANIMATION_TOP_TO_BOTTOM:
                # 从上到下
                vert_anim.setStartValue(0)
                vert_anim.setEndValue(self.height())
            else:
                # 从下到上
                vert_anim.setStartValue(0)
                vert_anim.setEndValue(-self.height())
            
            vert_anim.setEasingCurve(self._animation_curve)
            self._animation_group.addAnimation(vert_anim)
        
        # 启动动画
        self._animation_group.start()
        
        # 重要：不要在这里调用父类的setCurrentIndex，等动画结束后再调用

# 如果直接运行该文件，则执行简单的测试程序
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建动画堆栈组件
    stacked_widget = AnimatedStackedWidget()
    stacked_widget.setAnimationType(AnimatedStackedWidget.ANIMATION_RIGHT_TO_LEFT)
    stacked_widget.setAnimationDuration(300)
    stacked_widget.setGeometry(100, 100, 400, 300)
    
    # 添加几个测试页面
    for color, text in [
        ("#f39c12", "Page 1 - Orange"),
        ("#3498db", "Page 2 - Blue"),
        ("#2ecc71", "Page 3 - Green"),
        ("#9b59b6", "Page 4 - Purple")
    ]:
        page = QWidget()
        page.setStyleSheet(f"background-color: {color}; color: white; font-size: 24px;")
        page.setAutoFillBackground(True)
        
        import PyQt6.QtWidgets as QtWidgets
        layout = QtWidgets.QVBoxLayout(page)
        label = QtWidgets.QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        stacked_widget.addWidget(page)
    
    # 添加按钮用于测试页面切换
    main_widget = QWidget()
    main_layout = QtWidgets.QVBoxLayout(main_widget)
    
    stacked_widget.setMinimumSize(400, 300)
    main_layout.addWidget(stacked_widget)
    
    buttons_layout = QtWidgets.QHBoxLayout()
    prev_button = QtWidgets.QPushButton("上一页")
    next_button = QtWidgets.QPushButton("下一页")
    
    buttons_layout.addWidget(prev_button)
    buttons_layout.addWidget(next_button)
    main_layout.addLayout(buttons_layout)
    
    animation_type_combo = QtWidgets.QComboBox()
    animation_type_combo.addItems([
        "从左到右", "从右到左", "从上到下", "从下到上", "淡入淡出"
    ])
    animation_type_combo.setCurrentIndex(1)  # 默认为从右到左
    main_layout.addWidget(animation_type_combo)
    
    # 连接信号
    def prev_page():
        current = stacked_widget.currentIndex()
        if current > 0:
            stacked_widget.setCurrentIndex(current - 1)
    
    def next_page():
        current = stacked_widget.currentIndex()
        if current < stacked_widget.count() - 1:
            stacked_widget.setCurrentIndex(current + 1)
    
    def change_animation_type(index):
        stacked_widget.setAnimationType(index)
    
    prev_button.clicked.connect(prev_page)
    next_button.clicked.connect(next_page)
    animation_type_combo.currentIndexChanged.connect(change_animation_type)
    
    main_widget.setWindowTitle("动画堆栈部件演示")
    main_widget.resize(500, 400)
    main_widget.show()
    
    sys.exit(app.exec()) 