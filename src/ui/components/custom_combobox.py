import os
import sys
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, 
                         QParallelAnimationGroup, QSequentialAnimationGroup,
                         QTimer, pyqtProperty, pyqtSignal, QPoint, QEvent, QRect, QRectF)
from PyQt6.QtGui import (QColor, QPainter, QBrush, QPen, QTransform, 
                        QPixmap, QImage, QLinearGradient, QFont, QFontMetrics, QPainterPath)
from PyQt6.QtWidgets import (QComboBox, QStyledItemDelegate, QListView, 
                            QApplication, QWidget, QGraphicsDropShadowEffect,
                            QStyleOptionComboBox, QStyle, QVBoxLayout, QGraphicsOpacityEffect)

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from core.logger import get_logger

class CustomComboBox(QComboBox):
    # 自定义信号
    hoverEntered = pyqtSignal()
    hoverLeft = pyqtSignal()
    clicked = pyqtSignal()
    released = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        初始化自定义下拉框
        :param parent: 父组件
        """
        super(CustomComboBox, self).__init__(parent)
        
        # 初始化日志
        self.logger = get_logger("CustomComboBox")
        self.logger.debug("初始化自定义下拉菜单")
        
        # 设置基本属性
        self.setMinimumWidth(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 自定义属性
        self._backgroundColor = QColor(255, 255, 255)
        self._backgroundHoverColor = QColor(245, 245, 245)
        self._backgroundPressColor = QColor(235, 235, 235)
        self._borderColor = QColor(200, 200, 200)
        self._textColor = QColor(50, 50, 50)
        self._textHoverColor = QColor(30, 30, 30)
        self._borderRadius = 2  # 减小默认圆角
        self._borderWidth = 1
        self._dropdownBorderRadius = 2  # 减小默认圆角
        self._hoverBorderColor = QColor(52, 152, 219)  # 蓝色
        self._pressBorderColor = QColor(41, 128, 185)  # 深蓝色
        self._arrowColor = QColor(100, 100, 100)
        self._arrowHoverColor = QColor(52, 152, 219)  # 蓝色
        self._arrowPressColor = QColor(41, 128, 185)  # 深蓝色
        self._dropShadowColor = QColor(0, 0, 0, 50)
        self._dropShadowRadius = 10
        
        # 动画属性
        self._hoverProgress = 0.0
        self._pressProgress = 0.0
        self._arrowRotation = 0.0
        self._popupProgress = 0.0
        
        # 状态标志
        self._hovered = False
        self._pressed = False
        self._popupVisible = False
        
        # 创建动画
        self._setupAnimations()
        
        # 设置列表视图
        self.view = QListView()
        self.setView(self.view)
        
        # 设置项目代理
        self.delegate = ComboBoxDelegate(self.view)
        self.setItemDelegate(self.delegate)
        
        # 添加事件过滤器，监听事件
        self.installEventFilter(self)
        
        # 添加阴影效果
        self._shadowEffect = QGraphicsDropShadowEffect(self)
        self._shadowEffect.setColor(self._dropShadowColor)
        self._shadowEffect.setBlurRadius(0)  # 初始为0，悬停时增加
        self._shadowEffect.setOffset(0, 0)
        self.setGraphicsEffect(self._shadowEffect)
        
        # 连接自定义信号到槽函数
        self.hoverEntered.connect(self._onHoverEnter)
        self.hoverLeft.connect(self._onHoverLeave)
        self.clicked.connect(self._onPress)
        self.released.connect(self._onRelease)
        
        # 连接选择项目的信号，用于自动关闭下拉菜单
        self.activated.connect(self._onItemActivated)
        
        # 连接下拉框显示和隐藏信号
        self.view.window().installEventFilter(self)
        
        # 加载样式表
        self._updateStyleSheet()

    # 动画相关方法
    def _setupAnimations(self):
        """设置所有动画效果"""
        # 悬停动画
        self._hoverAnimation = QPropertyAnimation(self, b"hoverProgress")
        self._hoverAnimation.setDuration(200)
        self._hoverAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 按下动画
        self._pressAnimation = QPropertyAnimation(self, b"pressProgress")
        self._pressAnimation.setDuration(100)
        self._pressAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 箭头旋转动画
        self._arrowRotationAnimation = QPropertyAnimation(self, b"arrowRotation")
        self._arrowRotationAnimation.setDuration(400)  # 增加箭头旋转动画时间
        self._arrowRotationAnimation.setEasingCurve(QEasingCurve.Type.OutBack)
        
        # 下拉框显示动画
        self._popupAnimation = QPropertyAnimation(self, b"popupProgress")
        self._popupAnimation.setDuration(400)  # 增加下拉显示动画时间
        self._popupAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _onHoverEnter(self):
        """鼠标悬停进入事件处理"""
        self._hoverAnimation.stop()
        self._hoverAnimation.setStartValue(self._hoverProgress)
        self._hoverAnimation.setEndValue(1.0)
        self._hoverAnimation.start()
        
        # 阴影效果动画
        shadowAnim = QPropertyAnimation(self._shadowEffect, b"blurRadius")
        shadowAnim.setDuration(200)
        shadowAnim.setStartValue(self._shadowEffect.blurRadius())
        shadowAnim.setEndValue(self._dropShadowRadius)
        shadowAnim.start()
    
    def _onHoverLeave(self):
        """鼠标悬停离开事件处理"""
        if not self._pressed and not self._popupVisible:
            self._hoverAnimation.stop()
            self._hoverAnimation.setStartValue(self._hoverProgress)
            self._hoverAnimation.setEndValue(0.0)
            self._hoverAnimation.start()
            
            # 阴影效果动画
            shadowAnim = QPropertyAnimation(self._shadowEffect, b"blurRadius")
            shadowAnim.setDuration(200)
            shadowAnim.setStartValue(self._shadowEffect.blurRadius())
            shadowAnim.setEndValue(0)
            shadowAnim.start()
    
    def _onPress(self):
        """鼠标按下事件处理"""
        self._pressAnimation.stop()
        self._pressAnimation.setStartValue(self._pressProgress)
        self._pressAnimation.setEndValue(1.0)
        self._pressAnimation.start()
        
        # 箭头旋转动画
        self._arrowRotationAnimation.stop()
        self._arrowRotationAnimation.setStartValue(self._arrowRotation)
        self._arrowRotationAnimation.setEndValue(180 if not self._popupVisible else 0)
        self._arrowRotationAnimation.start()
    
    def _onRelease(self):
        """鼠标释放事件处理"""
        self._pressAnimation.stop()
        self._pressAnimation.setStartValue(self._pressProgress)
        self._pressAnimation.setEndValue(0.0)
        self._pressAnimation.start()
    
    def _onPopupShow(self):
        """下拉框显示事件处理"""
        self._popupVisible = True
        self._popupAnimation.stop()
        self._popupAnimation.setStartValue(self._popupProgress)
        self._popupAnimation.setEndValue(1.0)
        self._popupAnimation.start()
        
        # 箭头旋转动画
        self._arrowRotationAnimation.stop()
        self._arrowRotationAnimation.setStartValue(self._arrowRotation)
        self._arrowRotationAnimation.setEndValue(180)
        self._arrowRotationAnimation.start()
    
    def _onPopupHide(self):
        """下拉框隐藏事件处理"""
        self._popupVisible = False
        self._popupAnimation.stop()
        self._popupAnimation.setStartValue(self._popupProgress)
        self._popupAnimation.setEndValue(0.0)
        self._popupAnimation.start()
        
        # 箭头旋转动画
        self._arrowRotationAnimation.stop()
        self._arrowRotationAnimation.setStartValue(self._arrowRotation)
        self._arrowRotationAnimation.setEndValue(0)
        self._arrowRotationAnimation.start()
        
        if not self._hovered:
            # 清除悬停状态
            self._onHoverLeave()
    
    def _onItemActivated(self, index):
        """
        处理项目被激活（选中）的事件
        :param index: 选中项的索引
        """
        # 在项目被选中后，使用延迟关闭下拉框，确保选择动作完成
        # 增加延迟时间，确保交互完成后再关闭
        QTimer.singleShot(100, self.hidePopup)
    
    # 属性存取器
    def _getHoverProgress(self):
        return self._hoverProgress
    
    def _setHoverProgress(self, value):
        self._hoverProgress = value
        self.update()
    
    def _getPressProgress(self):
        return self._pressProgress
    
    def _setPressProgress(self, value):
        self._pressProgress = value
        self.update()
    
    def _getArrowRotation(self):
        return self._arrowRotation
    
    def _setArrowRotation(self, value):
        self._arrowRotation = value
        self.update()
    
    def _getPopupProgress(self):
        return self._popupProgress
    
    def _setPopupProgress(self, value):
        self._popupProgress = value
        self.update()
    
    # 定义属性
    hoverProgress = pyqtProperty(float, _getHoverProgress, _setHoverProgress)
    pressProgress = pyqtProperty(float, _getPressProgress, _setPressProgress)
    arrowRotation = pyqtProperty(float, _getArrowRotation, _setArrowRotation)
    popupProgress = pyqtProperty(float, _getPopupProgress, _setPopupProgress)
    
    # 事件处理
    def eventFilter(self, obj, event):
        """事件过滤器，处理各种事件"""
        if obj == self:
            # 处理自身的事件
            if event.type() == QEvent.Type.Enter:
                # 鼠标进入
                self._hovered = True
                self.hoverEntered.emit()
                return True
            
            elif event.type() == QEvent.Type.Leave:
                # 鼠标离开
                self._hovered = False
                if not self._popupVisible:
                    self.hoverLeft.emit()
                return True
            
            elif event.type() == QEvent.Type.MouseButtonPress:
                # 鼠标按下
                self._pressed = True
                self.clicked.emit()
                return False  # 不拦截，让ComboBox处理下拉逻辑
            
            elif event.type() == QEvent.Type.MouseButtonRelease:
                # 鼠标释放
                self._pressed = False
                self.released.emit()
                return False  # 不拦截，让ComboBox处理选择逻辑
        
        # 监听popup window事件
        elif obj == self.view.window():
            if event.type() == QEvent.Type.Show:
                self._onPopupShow()
            elif event.type() == QEvent.Type.Hide:
                self._onPopupHide()
            # 处理下拉列表中的鼠标点击事件
            elif event.type() == QEvent.Type.MouseButtonRelease:
                # 如果在列表项上松开鼠标，应该隐藏下拉框
                # 在下一个事件循环中执行，确保项目选择完成后再隐藏
                QTimer.singleShot(150, self.hidePopup)
        # 处理窗口外点击
        elif event.type() == QEvent.Type.MouseButtonPress and self._popupVisible:
            # 如果下拉框显示时，点击了其他位置，则隐藏下拉框
            self.hidePopup()
            
        return super(CustomComboBox, self).eventFilter(obj, event)
    
    def showPopup(self):
        """显示下拉框"""
        # 安装全局事件过滤器，处理点击其他区域的情况
        QApplication.instance().installEventFilter(self)
        super().showPopup()
    
    def hidePopup(self):
        """隐藏下拉框，重写以添加动画"""
        # 移除全局事件过滤器
        QApplication.instance().removeEventFilter(self)
        
        # 防止已经在动画中或已经隐藏
        if not self._popupVisible:
            super().hidePopup()
            return
            
        self._popupVisible = False
        
        # 获取下拉列表视图窗口
        popup = self.view.window()
        if popup and popup.isVisible():
            # 取消滚动条显示，避免动画过程中出现滚动条
            self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            # 保存原始几何信息
            original_geometry = popup.geometry()
            
            # 设置结束高度为0，保持同样的顶部位置
            end_geometry = QRect(
                original_geometry.left(),
                original_geometry.top(),
                original_geometry.width(),
                0
            )
            
            # 使用一个简单的QPropertyAnimation进行收缩
            height_anim = QPropertyAnimation(popup, b"geometry")
            height_anim.setDuration(250)
            height_anim.setStartValue(original_geometry)
            height_anim.setEndValue(end_geometry)
            height_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            
            # 在动画完成后调用基类的hidePopup方法
            height_anim.finished.connect(lambda: super(CustomComboBox, self).hidePopup())
            height_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
            
            # 箭头旋转动画
            self._arrowRotationAnimation.stop()
            self._arrowRotationAnimation.setStartValue(self._arrowRotation)
            self._arrowRotationAnimation.setEndValue(0)
            self._arrowRotationAnimation.start()
            
            if not self._hovered:
                # 清除悬停状态
                self._onHoverLeave()
        else:
            # 如果弹出窗口不可见，直接调用父类的方法
            super().hidePopup()
    
    # 自定义方法
    def _updateStyleSheet(self):
        """更新样式表"""
        # 基本样式，主要用于下拉列表的样式
        stylesheet = """
            QComboBox QAbstractItemView {
                background-color: %s;
                border: 1px solid %s;
                border-radius: %dpx;
                selection-background-color: #e0f7fa;
                outline: 0px;
                padding: 5px;
            }
            
            QComboBox QAbstractItemView::item {
                min-height: 25px;
                border-radius: 3px;
                padding: 5px;
                color: %s;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #f5f5f5;
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #e0f7fa;
                color: %s;
            }
        """ % (
            self._backgroundColor.name(), self._borderColor.name(),
            self._dropdownBorderRadius,
            self._textColor.name(),
            self._textColor.name()
        )
        
        # 清除下拉箭头的默认样式，我们将在paintEvent中自定义绘制
        stylesheet += """
            QComboBox::drop-down {
                width: 20px;
                border: none;
                background: transparent;
            }
            
            QComboBox::down-arrow {
                width: 0px;
                height: 0px;
                background: transparent;
            }
        """
        
        self.setStyleSheet(stylesheet)
    
    def paintEvent(self, event):
        """绘制自定义下拉框"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取尺寸
        width = self.width()
        height = self.height()
        
        # 计算当前颜色（基于动画进度）
        bgColor = self._interpolateColor(self._backgroundColor, 
                                         self._interpolateColor(self._backgroundHoverColor, 
                                                               self._backgroundPressColor, 
                                                               self._pressProgress),
                                         self._hoverProgress)
        
        borderColor = self._interpolateColor(self._borderColor,
                                            self._interpolateColor(self._hoverBorderColor,
                                                                  self._pressBorderColor,
                                                                  self._pressProgress),
                                            self._hoverProgress)
        
        textColor = self._interpolateColor(self._textColor,
                                          self._textHoverColor,
                                          self._hoverProgress)
        
        arrowColor = self._interpolateColor(self._arrowColor,
                                           self._interpolateColor(self._arrowHoverColor,
                                                                 self._arrowPressColor,
                                                                 self._pressProgress),
                                           self._hoverProgress)
        
        # 绘制背景
        pen = QPen(borderColor)
        pen.setWidth(self._borderWidth)
        painter.setPen(pen)
        painter.setBrush(QBrush(bgColor))
        rect = QRectF(
            self._borderWidth/2, 
            self._borderWidth/2, 
            width - self._borderWidth, 
            height - self._borderWidth
        )
        painter.drawRoundedRect(rect, self._borderRadius, self._borderRadius)
        
        # 绘制文本
        text = self.currentText()
        font = self.font()
        painter.setFont(font)
        painter.setPen(QPen(textColor))
        
        # 计算文本绘制位置（考虑到右侧需要留出箭头的空间）
        textRect = QRect(10, 0, width - 40, height)
        painter.drawText(textRect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
        
        # 绘制箭头
        arrowSize = 8  # 箭头大小
        arrowX = width - 20  # 箭头X坐标
        arrowY = height / 2  # 箭头Y坐标（中心点）
        
        # 设置画笔绘制箭头
        arrowPen = QPen(arrowColor)
        arrowPen.setWidth(2)  # 调整箭头线宽，改为整数值
        arrowPen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrowPen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(arrowPen)
        
        # 保存当前画家状态，以便于恢复
        painter.save()
        
        # 移动到箭头中心点
        painter.translate(arrowX, arrowY)
        
        # 应用旋转变换（箭头旋转动画）
        painter.rotate(self._arrowRotation)
        
        # 创建箭头路径并绘制
        arrowPath = QPainterPath()
        arrowPath.moveTo(-arrowSize/2, -arrowSize/4)  # 左点
        arrowPath.lineTo(0, arrowSize/4)              # 中间点
        arrowPath.lineTo(arrowSize/2, -arrowSize/4)   # 右点
        
        painter.drawPath(arrowPath)
        
        # 恢复画家状态
        painter.restore()
    
    def _interpolateColor(self, color1, color2, progress):
        """在两种颜色之间进行插值"""
        r = color1.red() + int((color2.red() - color1.red()) * progress)
        g = color1.green() + int((color2.green() - color1.green()) * progress)
        b = color1.blue() + int((color2.blue() - color1.blue()) * progress)
        a = color1.alpha() + int((color2.alpha() - color1.alpha()) * progress)
        return QColor(r, g, b, a)
    
    # 自定义样式方法
    def setBackgroundColor(self, color):
        """设置背景颜色"""
        if isinstance(color, str):
            self._backgroundColor = QColor(color)
        else:
            self._backgroundColor = color
        self._updateStyleSheet()
    
    def setBackgroundHoverColor(self, color):
        """设置悬停状态的背景颜色"""
        if isinstance(color, str):
            self._backgroundHoverColor = QColor(color)
        else:
            self._backgroundHoverColor = color
    
    def setBackgroundPressColor(self, color):
        """设置按下状态的背景颜色"""
        if isinstance(color, str):
            self._backgroundPressColor = QColor(color)
        else:
            self._backgroundPressColor = color
    
    def setBorderColor(self, color):
        """设置边框颜色"""
        if isinstance(color, str):
            self._borderColor = QColor(color)
        else:
            self._borderColor = color
        self._updateStyleSheet()
    
    def setTextColor(self, color):
        """设置文本颜色"""
        if isinstance(color, str):
            self._textColor = QColor(color)
        else:
            self._textColor = color
        self._updateStyleSheet()
    
    def setTextHoverColor(self, color):
        """设置悬停状态的文本颜色"""
        if isinstance(color, str):
            self._textHoverColor = QColor(color)
        else:
            self._textHoverColor = color
    
    def setBorderRadius(self, radius):
        """设置边框圆角"""
        self._borderRadius = radius
        self._updateStyleSheet()
    
    def setBorderWidth(self, width):
        """设置边框宽度"""
        self._borderWidth = width
        self._updateStyleSheet()
    
    def setHoverBorderColor(self, color):
        """设置悬停时的边框颜色"""
        if isinstance(color, str):
            self._hoverBorderColor = QColor(color)
        else:
            self._hoverBorderColor = color
    
    def setPressBorderColor(self, color):
        """设置按下时的边框颜色"""
        if isinstance(color, str):
            self._pressBorderColor = QColor(color)
        else:
            self._pressBorderColor = color
    
    def setDropdownBorderRadius(self, radius):
        """设置下拉框圆角"""
        self._dropdownBorderRadius = radius
        self._updateStyleSheet()
    
    def setArrowColor(self, color):
        """设置箭头颜色"""
        if isinstance(color, str):
            self._arrowColor = QColor(color)
        else:
            self._arrowColor = color
    
    def setArrowHoverColor(self, color):
        """设置悬停时的箭头颜色"""
        if isinstance(color, str):
            self._arrowHoverColor = QColor(color)
        else:
            self._arrowHoverColor = color
    
    def setArrowPressColor(self, color):
        """设置按下时的箭头颜色"""
        if isinstance(color, str):
            self._arrowPressColor = QColor(color)
        else:
            self._arrowPressColor = color
    
    def setDropShadowColor(self, color):
        """设置阴影颜色"""
        if isinstance(color, str):
            self._dropShadowColor = QColor(color)
        else:
            self._dropShadowColor = color
        self._shadowEffect.setColor(self._dropShadowColor)
    
    def setDropShadowRadius(self, radius):
        """设置阴影半径"""
        self._dropShadowRadius = radius
    
    def setArrowIcons(self, normal_icon, focus_icon):
        """
        设置自定义箭头图标（已弃用，保留接口兼容性）
        :param normal_icon: 常规状态图标路径
        :param focus_icon: 焦点状态图标路径
        """
        # 实际不执行任何操作，因为现在使用绘制的箭头
        self.logger.warning("setArrowIcons方法已弃用，现在使用绘制的箭头")
        pass
    
    def setAnimationDuration(self, hover_duration=200, press_duration=100, 
                             arrow_duration=300, popup_duration=250):
        """设置动画持续时间"""
        self._hoverAnimation.setDuration(hover_duration)
        self._pressAnimation.setDuration(press_duration)
        self._arrowRotationAnimation.setDuration(arrow_duration)
        self._popupAnimation.setDuration(popup_duration)
    
    def setAnimationEasingCurve(self, hover_curve=QEasingCurve.Type.OutCubic, 
                               press_curve=QEasingCurve.Type.OutCubic,
                               arrow_curve=QEasingCurve.Type.OutBack,
                               popup_curve=QEasingCurve.Type.OutCubic):
        """设置动画缓动曲线"""
        self._hoverAnimation.setEasingCurve(hover_curve)
        self._pressAnimation.setEasingCurve(press_curve)
        self._arrowRotationAnimation.setEasingCurve(arrow_curve)
        self._popupAnimation.setEasingCurve(popup_curve)
    
    # 自定义QCustomComboBox
    def customizeCustomComboBox(self, **customValues):
        """
        自定义下拉框样式
        :param customValues: 样式属性字典
        """
        # 基本颜色
        if "backgroundColor" in customValues:
            self.setBackgroundColor(customValues["backgroundColor"])
        
        if "backgroundHoverColor" in customValues:
            self.setBackgroundHoverColor(customValues["backgroundHoverColor"])
        
        if "backgroundPressColor" in customValues:
            self.setBackgroundPressColor(customValues["backgroundPressColor"])
        
        if "borderColor" in customValues:
            self.setBorderColor(customValues["borderColor"])
        
        if "textColor" in customValues:
            self.setTextColor(customValues["textColor"])
        
        if "textHoverColor" in customValues:
            self.setTextHoverColor(customValues["textHoverColor"])
        
        # 尺寸
        if "borderRadius" in customValues:
            self.setBorderRadius(customValues["borderRadius"])
        
        if "borderWidth" in customValues:
            self.setBorderWidth(customValues["borderWidth"])
        
        # 悬停和按下颜色
        if "hoverBorderColor" in customValues:
            self.setHoverBorderColor(customValues["hoverBorderColor"])
        
        if "pressBorderColor" in customValues:
            self.setPressBorderColor(customValues["pressBorderColor"])
        
        # 下拉框
        if "dropdownBorderRadius" in customValues:
            self.setDropdownBorderRadius(customValues["dropdownBorderRadius"])
        
        # 箭头颜色
        if "arrowColor" in customValues:
            self.setArrowColor(customValues["arrowColor"])
        
        if "arrowHoverColor" in customValues:
            self.setArrowHoverColor(customValues["arrowHoverColor"])
        
        if "arrowPressColor" in customValues:
            self.setArrowPressColor(customValues["arrowPressColor"])
        
        # 阴影效果
        if "dropShadowColor" in customValues:
            self.setDropShadowColor(customValues["dropShadowColor"])
        
        if "dropShadowRadius" in customValues:
            self.setDropShadowRadius(customValues["dropShadowRadius"])
        
        # 动画设置
        if "hoverAnimationDuration" in customValues:
            self._hoverAnimation.setDuration(customValues["hoverAnimationDuration"])
        
        if "pressAnimationDuration" in customValues:
            self._pressAnimation.setDuration(customValues["pressAnimationDuration"])
        
        if "arrowAnimationDuration" in customValues:
            self._arrowRotationAnimation.setDuration(customValues["arrowAnimationDuration"])
        
        if "popupAnimationDuration" in customValues:
            self._popupAnimation.setDuration(customValues["popupAnimationDuration"])
        
        # 更新样式表
        self._updateStyleSheet()
        self.update()

# 自定义委托
class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ComboBoxDelegate, self).__init__(parent)
        self.logger = get_logger("ComboBoxDelegate")
        self.logger.debug("初始化下拉菜单项代理")
    
    def sizeHint(self, option, index):
        """
        返回项目的大小提示
        :param option: 样式选项
        :param index: 模型索引
        :return: 项目大小
        """
        size = super().sizeHint(option, index)
        # 设置项目高度
        size.setHeight(30)
        return size
    
    def paint(self, painter, option, index):
        """
        自定义绘制项目
        :param painter: QPainter对象
        :param option: 样式选项
        :param index: 模型索引
        """
        # 使用更精美的绘制方式
        painter.save()
        
        # 设置抗锯齿
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # 获取状态
        isSelected = bool(option.state & QStyle.StateFlag.State_Selected)
        isHovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        
        # 设置颜色
        if isSelected:
            bgColor = QColor("#e0f7fa")  # 选中项背景色
            textColor = QColor("#00838f")  # 选中项文字色
        elif isHovered:
            bgColor = QColor("#f5f5f5")  # 悬停项背景色
            textColor = QColor("#333333")  # 悬停项文字色
        else:
            bgColor = QColor("#ffffff")  # 普通项背景色
            textColor = QColor("#333333")  # 普通项文字色
        
        # 绘制背景
        rect = option.rect.adjusted(2, 2, -2, -2)  # 留出边距
        painter.setBrush(QBrush(bgColor))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 3, 3)
        
        # 绘制文本
        painter.setPen(QPen(textColor))
        textRect = option.rect.adjusted(10, 0, -10, 0)  # 左右各留出10px
        text = index.data(Qt.ItemDataRole.DisplayRole)
        
        # 检查文本是否过长，需要省略
        metrics = QFontMetrics(option.font)
        elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, textRect.width())
        
        painter.drawText(textRect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elidedText)
        
        painter.restore()

if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = QWidget()
    window.setGeometry(100, 100, 400, 300)
    window.setWindowTitle("QCustomComboBox测试")
    window.setStyleSheet("background-color: #f5f5f5;")
    
    # 创建自定义下拉框
    comboBox = CustomComboBox(window)
    comboBox.setGeometry(100, 100, 200, 40)
    
    # 添加项目
    comboBox.addItem("项目1 - 默认选择")
    comboBox.addItem("项目2 - 比较长的文本选项演示效果")
    comboBox.addItem("项目3 - 短项")
    comboBox.addItem("项目4 - 中等长度的选项")
    comboBox.addItem("项目5 - 最后一项")
    
    # 自定义样式
    comboBox.customizeCustomComboBox(
        backgroundColor="#ffffff",
        backgroundHoverColor="#f5f5f5",
        backgroundPressColor="#e5e5e5",
        borderColor="#dddddd",
        hoverBorderColor="#3498db",
        pressBorderColor="#2980b9",
        textColor="#333333",
        textHoverColor="#000000",
        borderRadius=4,
        borderWidth=1,
        dropdownBorderRadius=4,
        arrowColor="#888888",
        arrowHoverColor="#3498db",
        arrowPressColor="#2980b9",
        dropShadowColor=QColor(0, 0, 0, 80),
        dropShadowRadius=15,
        hoverAnimationDuration=300,
        pressAnimationDuration=200,
        arrowAnimationDuration=400,
        popupAnimationDuration=300
    )
    
    # 布局
    layout = QVBoxLayout(window)
    layout.addWidget(comboBox)
    
    window.show()
    sys.exit(app.exec()) 