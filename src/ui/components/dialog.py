import sys

from PyQt6.QtCore import (
    QEasingCurve,
    QEvent,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFontDialog,
    QFrame,
    QGraphicsBlurEffect,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from core.logger import get_logger  # 导入日志工具
except ImportError:
    import os

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger

# --- 配置 ---
CONFIG = {
    "win_title": "对话框",  # 窗口标题
    "font_family": "Segoe UI",  # 主字体
    "font_size_base": 10,  # 基础字号 (pt)
    "color_white": "#ffffff",  # 白色
    "color_primary": "#667eea",  # 主题色1
    "color_secondary": "#764ba2",  # 主题色2
    "color_text_light": "#ffffff",  # 浅色文本
    "color_text_dark": "#333333",  # 深色文本
    "color_text_medium": "#555555",  # 中等文本
    "color_text_muted": "#777777",  # 柔和文本
    "color_modal_bg": "#ffffff",  # 对话框背景
    "color_modal_shadow": "#30000000",  # 对话框阴影 (带透明度)
    "color_overlay": QColor(0, 0, 0, 0),  # 遮罩颜色 (完全透明)
    "color_btn_primary_bg": "#667eea",  # 主按钮背景
    "color_btn_primary_hover": "#5a6fd1",  # 主按钮悬停
    "color_btn_secondary_bg": "#f1f1f1",  # 次按钮背景
    "color_btn_secondary_hover": "#e1e1e1",  # 次按钮悬停
    "color_warning": "#FFC107",  # 警告颜色
    "color_error": "#F44336",  # 错误颜色
    "color_question": "#4CAF50",  # 问题颜色
    "color_btn_cancel": "#9e9e9e",  # 取消按钮颜色
    "radius_modal": 16,  # 对话框圆角
    "radius_button": 8,  # 按钮圆角
    "anim_duration": 400,  # 动画时长 (ms)
    "anim_easing": QEasingCurve.Type.OutCubic,  # 动画曲线 (通用)
    "scale_anim_factor": 0.8,  # 缩放动画起始因子
    "slide_anim_offset": 100,  # 滑动动画偏移
    "blur_radius": 15,  # 背景模糊半径
}

# 消息类型和配置
MESSAGE_TYPES = {
    "warning": {
        "name": "警告消息",
        "icon": "⚠️",
        "description": "提醒用户注意某些操作可能会带来的后果",
        "buttons": ["确定", "取消"],
        "color": CONFIG["color_warning"],
        "button_colors": {
            "确定": CONFIG["color_warning"],
            "取消": CONFIG["color_btn_cancel"],
        },
    },
    "question": {
        "name": "确认消息",
        "icon": "❓",
        "description": "需要用户确认是否执行某个操作",
        "buttons": ["是", "否", "取消"],
        "color": CONFIG["color_question"],
        "button_colors": {
            "是": CONFIG["color_question"],
            "否": CONFIG["color_error"],
            "取消": CONFIG["color_btn_cancel"],
        },
    },
    "retry": {
        "name": "重试消息",
        "icon": "❌",
        "description": "告知用户操作失败，但可以尝试再次执行",
        "buttons": ["重试", "取消"],
        "color": CONFIG["color_error"],
        "button_colors": {
            "重试": CONFIG["color_error"],
            "取消": CONFIG["color_btn_cancel"],
        },
    },
    "timeout": {
        "name": "超时消息",
        "icon": "⚠️",
        "description": "告知用户操作超时，需要采取措施",
        "buttons": ["确定", "取消"],
        "color": CONFIG["color_warning"],
        "button_colors": {
            "确定": CONFIG["color_warning"],
            "取消": CONFIG["color_btn_cancel"],
        },
    },
    "custom": {
        "name": "自定义消息",
        "icon": "⚙️",
        "description": "开发者可以根据需要自定义消息内容、按钮和图标",
        "buttons": ["确定", "取消"],
        "color": CONFIG["color_primary"],
        "button_colors": {
            "确定": CONFIG["color_primary"],
            "取消": CONFIG["color_btn_cancel"],
        },
    },
}


class MessageDialog(QWidget):  # 对话框组件
    """
    选择对话框组件，支持多种交互类型和动画效果

    Args:
        message_type (str): 消息类型，可选值：
            - 'warning': 警告消息
            - 'question': 确认消息
            - 'retry': 重试消息
            - 'timeout': 超时消息
            - 'custom': 自定义消息
        content_widget (QWidget, optional): 自定义内容组件
        parent (QWidget, optional): 父组件
        show_title (bool, optional): 是否显示标题栏，默认True
        show_buttons (bool, optional): 是否显示底部按钮，默认True
        title_text (str, optional): 标题文本，默认为"消息提示"
        message (str, optional): 消息内容
        custom_icon (str, optional): 自定义图标
        custom_buttons (list, optional): 自定义按钮
        custom_button_colors (dict, optional): 自定义按钮颜色
        on_button_clicked (function, optional): 按钮点击回调函数
    """

    def __init__(
        self,
        message_type="warning",
        content_widget=None,
        parent=None,
        show_title=True,
        show_buttons=True,
        title_text="消息提示",
        message="",
        custom_icon=None,
        custom_buttons=None,
        custom_button_colors=None,
        on_button_clicked=None,
    ):
        super().__init__(parent)
        self.logger = get_logger("MessageDialog")  # 添加日志记录器
        self.logger.info(f"初始化对话框 - 类型: {message_type}")
        self.message_type = message_type
        self.message = message
        self.custom_icon = custom_icon
        self.custom_buttons = custom_buttons
        self.custom_button_colors = custom_button_colors
        self.on_button_clicked = on_button_clicked
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景

        # --- 自定义透明度属性和效果 ---
        self._opacity = 1.0  # 初始透明度值

        # --- 背景模糊效果 ---
        self.parent_original_effect = None
        if parent:
            # 保存父组件原来的effect
            self.parent_original_effect = parent.graphicsEffect()
            # 添加父组件的模糊效果
            self.setup_parent_blur()

        # --- 布局和控件 ---
        self.content_container = QWidget(self)
        self.content_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self.content_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinimumSize)

        # 主布局设为无边距，所有内容都在content_container中
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.content_container)

        # 根据show_title参数决定是否添加标题栏
        if show_title:
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(0, 0, 0, 0)

            # 添加图标
            icon_label = QLabel(
                MESSAGE_TYPES[message_type]["icon"]
                if self.custom_icon is None
                else self.custom_icon
            )
            icon_label.setStyleSheet(
                f"font-size: {CONFIG['font_size_base']+8}pt; color: {MESSAGE_TYPES[message_type]['color']};"
            )
            header_layout.addWidget(icon_label)

            # 添加标题
            title = QLabel(title_text)
            title.setStyleSheet(
                f"font-size: {CONFIG['font_size_base']+5}pt; font-weight: 600; color: {CONFIG['color_text_dark']}; background-color: transparent;"
            )
            header_layout.addWidget(title)

            header_layout.addStretch()

            # 关闭按钮
            close_btn = QPushButton("×")
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.setStyleSheet(
                f"""QPushButton {{ background: none; border: none; font-size: {CONFIG['font_size_base']+5}pt; color: {CONFIG['color_text_dark']}; padding: 0 5px; background-color: transparent; }}
                                      QPushButton:hover {{ color: {CONFIG['color_text_dark']}; opacity: 0.7; }}"""
            )
            close_btn.clicked.connect(lambda: self.handle_button_click("关闭"))
            header_layout.addWidget(close_btn)

            layout.addLayout(header_layout)

        # 添加内容布局
        body_layout = QVBoxLayout()
        body_layout.setSpacing(15)
        body_layout.setContentsMargins(0, 0, 0, 0)  # 内容垂直布局

        # 添加消息内容
        if message:
            message_label = QLabel(message)
            message_label.setStyleSheet(
                f"color: {CONFIG['color_text_dark']}; line-height: 1.6;"
            )
            message_label.setWordWrap(True)
            body_layout.addWidget(message_label)

        # 添加自定义内容
        if content_widget:
            self.logger.debug("添加自定义内容组件")
            body_layout.addWidget(content_widget)

        layout.addLayout(body_layout)

        # 根据show_buttons参数决定是否添加底部按钮
        if show_buttons:
            footer_layout = QHBoxLayout()
            footer_layout.setContentsMargins(0, 0, 0, 0)
            footer_layout.setSpacing(10)  # 底部水平布局

            # 添加其他按钮
            buttons_to_show = MESSAGE_TYPES[message_type]["buttons"]
            if self.message_type == "custom" and self.custom_buttons:
                buttons_to_show = self.custom_buttons

            for button_text in buttons_to_show:
                # 获取按钮颜色
                button_color = MESSAGE_TYPES[message_type]["button_colors"].get(
                    button_text, CONFIG["color_btn_secondary_bg"]
                )
                if (
                    self.message_type == "custom"
                    and self.custom_button_colors
                    and button_text in self.custom_button_colors
                ):
                    button_color = self.custom_button_colors[button_text]

                btn = QPushButton(button_text)
                # 应用基本样式：背景色为按钮颜色，白字，圆角，固定高度
                btn.setStyleSheet(f"background-color: {button_color}; color: white; border-radius: {CONFIG['radius_button']}px; height: 32px;")
                btn.clicked.connect(
                    lambda checked, text=button_text: self.handle_button_click(text)
                )
                footer_layout.addWidget(btn)

            layout.addLayout(footer_layout)

        # --- 动画准备 ---
        self.opacity_anim = QPropertyAnimation(self, b"opacity")
        self.opacity_anim.setDuration(CONFIG["anim_duration"])
        self.opacity_anim.setEasingCurve(CONFIG["anim_easing"])
        self.geom_anim = QPropertyAnimation(self, b"geometry")
        self.geom_anim.setDuration(CONFIG["anim_duration"])
        self.geom_anim.setEasingCurve(CONFIG["anim_easing"])

        self.logger.debug("对话框初始化完成")

    def setup_parent_blur(self):
        """为父窗口设置阴影效果，使背景变暗"""
        if not self.parent():
            return

        # 创建阴影效果（背景变暗）
        try:
            # 获取要应用效果的部件
            target_widget = self._get_target_widget()
            if not target_widget:
                self.logger.warning("找不到适合应用阴影效果的目标组件")
                return

            # 创建半透明覆盖层
            if not hasattr(self, "overlay_widget"):
                # 创建覆盖层，设置为目标组件的直接子部件
                self.overlay_widget = QWidget(target_widget)
                self.overlay_widget.setObjectName("dialog_overlay")

                # 优化覆盖层，确保全屏覆盖
                self.overlay_widget.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
                self.overlay_widget.setGeometry(
                    0, 0, target_widget.width(), target_widget.height()
                )
                self.overlay_widget.setFixedSize(target_widget.size())
                self.overlay_widget.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents, False
                )

                # 确保覆盖层在所有其他部件之上
                self.overlay_widget.raise_()
                self.raise_()  # 确保对话框在覆盖层之上

                # 显示覆盖层
                self.overlay_widget.show()

                # 添加全局事件过滤器，捕获所有父窗口的事件
                target_widget.installEventFilter(self)

                # 创建动画以逐渐改变背景颜色
                self.fade_anim = QPropertyAnimation(self, b"overlayOpacity")
                self.fade_anim.setDuration(CONFIG["anim_duration"])
                self.fade_anim.setEasingCurve(CONFIG["anim_easing"])
                self.fade_anim.setStartValue(0)
                self.fade_anim.setEndValue(80)  # 透明度值（0-255）
                self.fade_anim.start()

            self.logger.debug("已添加背景阴影效果")
        except Exception as e:
            self.logger.error(f"设置父窗口阴影效果时出错: {str(e)}")

    def _get_target_widget(self):
        """获取要应用效果的目标组件"""
        parent = self.parent()
        if not parent:
            return None

        # 如果父窗口是主窗口，直接使用主窗口
        if hasattr(parent, "centralWidget") and callable(
            getattr(parent, "centralWidget")
        ):
            self.logger.debug("检测到主窗口，使用主窗口的中央部件")
            return parent.centralWidget()

        # 1. 其他窗口类型的处理
        # 如果父窗口有central_widget属性
        if hasattr(parent, "central_widget"):
            return parent.central_widget

        # 2. 查找内容部件 (可能在QScrollArea或自定义结构中)
        if hasattr(parent, "content_widget"):
            return parent.content_widget

        # 3. 查找滚动区域内的部件
        scroll_areas = parent.findChildren(QScrollArea)
        for scroll_area in scroll_areas:
            if scroll_area.widget():
                return scroll_area.widget()

        # 4. 如果是TabWidget，获取当前标签页
        if isinstance(parent, QTabWidget):
            current_index = parent.currentIndex()
            if current_index >= 0:
                return parent.widget(current_index)

        # 5. 最后使用父窗口本身
        return parent

    def remove_parent_blur(self):
        """移除父窗口的阴影效果"""
        if not self.parent() or not hasattr(self, "overlay_widget"):
            return

        try:
            # 停止正在进行的动画
            if (
                hasattr(self, "fade_anim")
                and self.fade_anim
                and self.fade_anim.state() == QPropertyAnimation.State.Running
            ):
                self.fade_anim.stop()

            # 创建淡出动画
            self.fade_anim = QPropertyAnimation(self, b"overlayOpacity")
            self.fade_anim.setDuration(CONFIG["anim_duration"])
            self.fade_anim.setEasingCurve(CONFIG["anim_easing"])
            self.fade_anim.setStartValue(self.getOverlayOpacity())
            self.fade_anim.setEndValue(0)

            # 动画完成后删除覆盖层
            def on_animation_finished():
                try:
                    if hasattr(self, "overlay_widget") and self.overlay_widget:
                        self.overlay_widget.deleteLater()
                        self.overlay_widget = None

                    # 移除事件过滤器
                    target_widget = self._get_target_widget()
                    if target_widget:
                        target_widget.removeEventFilter(self)
                except Exception as e:
                    self.logger.error(f"清除阴影效果时出错: {str(e)}")

            self.fade_anim.finished.connect(on_animation_finished)
            self.fade_anim.start()
            self.logger.debug("正在移除背景阴影效果")
        except Exception as e:
            self.logger.error(f"移除父窗口阴影效果时出错: {str(e)}")
            # 如果出错，尝试直接删除覆盖层
            try:
                if hasattr(self, "overlay_widget") and self.overlay_widget:
                    self.overlay_widget.deleteLater()
                    self.overlay_widget = None
            except Exception as inner_e:
                self.logger.error(f"清除阴影效果时出错: {str(inner_e)}")

    # 自定义覆盖层透明度属性
    def getOverlayOpacity(self):
        if hasattr(self, "overlay_widget") and self.overlay_widget:
            style = self.overlay_widget.styleSheet()
            if "rgba(0, 0, 0, " in style:
                try:
                    opacity = int(
                        float(style.split("rgba(0, 0, 0, ")[1].split(")")[0]) * 255
                    )
                    return opacity
                except:
                    return 0
        return 0

    def setOverlayOpacity(self, opacity):
        if hasattr(self, "overlay_widget") and self.overlay_widget:
            opacity_float = opacity / 255.0
            self.overlay_widget.setStyleSheet(
                f"background-color: rgba(0, 0, 0, {opacity_float});"
            )
            self.logger.debug(f"阴影透明度已设置为: {opacity_float:.2f}")

    # 暴露给 QPropertyAnimation 的属性
    overlayOpacity = pyqtProperty(int, getOverlayOpacity, setOverlayOpacity)

    def eventFilter(self, obj, event):
        """处理事件过滤器"""
        # 如果监听的是目标组件，且是大小变化事件，需要调整覆盖层大小
        target_widget = self._get_target_widget()
        if obj == target_widget:
            if event.type() == QEvent.Type.Resize:
                if hasattr(self, "overlay_widget") and self.overlay_widget:
                    # 确保覆盖层总是与目标部件大小相同
                    self.overlay_widget.setGeometry(
                        0, 0, target_widget.width(), target_widget.height()
                    )
                    self.overlay_widget.setFixedSize(target_widget.size())

                    # 当父窗口大小变化时，重新计算并更新对话框的位置
                    if self.isVisible():
                        try:
                            self.logger.debug("父窗口大小变化，重新计算对话框位置")
                            # 仅计算目标几何位置(不使用动画)
                            _, target_geom = self._calc_geometries()

                            # 设置新位置
                            current_opacity = self._opacity  # 保存当前的透明度
                            current_size = self.size()  # 保存当前的大小

                            # 停止任何正在进行的动画
                            if (
                                self.geom_anim.state()
                                == QPropertyAnimation.State.Running
                            ):
                                self.geom_anim.stop()

                            # 更新位置，保持大小不变
                            target_geom.setSize(current_size)
                            self.setGeometry(target_geom)

                            # 确保对话框仍然在覆盖层之上
                            self.raise_()
                        except Exception as e:
                            self.logger.error(f"重新定位对话框时出错: {str(e)}")

            elif event.type() == QEvent.Type.ChildAdded:
                # 如果添加了新的子部件，确保覆盖层和对话框仍然在最上方
                if hasattr(self, "overlay_widget") and self.overlay_widget:
                    self.overlay_widget.raise_()
                    self.raise_()

        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        """处理大小变化事件"""
        super().resizeEvent(event)  # 调用父类方法

        # 如果是对话框自身的大小变化（而不是在动画中），重新计算位置
        sender = self.sender()
        if not sender or not isinstance(sender, QPropertyAnimation):
            start_geom, end_geom = self._calc_geometries()
            if self.isVisible():
                self.setGeometry(end_geom)

    # 自定义透明度属性
    def getOpacity(self):
        return self._opacity

    def setOpacity(self, opacity):
        if self._opacity != opacity:
            self._opacity = opacity
            self.update()  # 触发重绘
            self.logger.debug(f"透明度已设置为: {opacity:.2f}")

    # 暴露给 QPropertyAnimation 的属性
    opacity = pyqtProperty(float, getOpacity, setOpacity)

    def paintEvent(self, event):
        """绘制事件，确保正确处理绘制"""
        # 首先调用父类的paintEvent以确保所有子控件都被正确绘制
        super().paintEvent(event)

        # 然后进行我们自己的绘制
        try:
            # 确保只在必要时创建QPainter对象
            painter = QPainter(self)
            if not painter.isActive():
                self.logger.warning("QPainter不活跃，跳过绘制")
                return

            # 开启抗锯齿
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 绘制背景矩形
            bg_color = QColor(CONFIG["color_modal_bg"])
            bg_color.setAlphaF(self._opacity)
            painter.setBrush(bg_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                self.rect(), CONFIG["radius_modal"], CONFIG["radius_modal"]
            )

            # 2. 确保内容容器的透明度效果
            # 注意：不在paintEvent中设置graphicsEffect，而是在初始化或其他地方
            # 这里只确保效果存在时透明度值正确
            if self.content_container:
                effect = self.content_container.graphicsEffect()
                if effect and isinstance(effect, QGraphicsOpacityEffect):
                    effect.setOpacity(self._opacity)

            # 安全结束绘制
            painter.end()
        except Exception as e:
            self.logger.error(f"绘制对话框时出错: {str(e)}")

    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)

        # 当对话框显示时，设置图形效果
        if self.content_container and self._opacity < 1.0:
            effect = self.content_container.graphicsEffect()
            if not effect or not isinstance(effect, QGraphicsOpacityEffect):
                new_effect = QGraphicsOpacityEffect(self.content_container)
                new_effect.setOpacity(self._opacity)
                self.content_container.setGraphicsEffect(new_effect)

        # 当对话框显示时，确保它在正确的位置并置于覆盖层之上
        _, target_geom = self._calc_geometries()
        self.setGeometry(target_geom)
        self.raise_()  # 确保对话框在覆盖层之上

    def _calc_geometries(self):  # 计算不同动画的起始/结束几何位置
        # 获取父窗口或屏幕大小
        if self.parent():
            parent_rect = self.parent().rect()
        else:
            # QApplication.desktop() 已弃用，使用 QApplication.primaryScreen().availableGeometry()
            try:
                parent_rect = QApplication.primaryScreen().availableGeometry()
            except:
                # 兼容旧版本
                try:
                    parent_rect = QApplication.desktop().availableGeometry()
                except:
                    parent_rect = QRect(0, 0, 800, 600)  # 默认值

        target_size = self.sizeHint()  # 获取推荐大小
        target_size.setWidth(min(int(parent_rect.width() * 0.9), 500))  # 限制最大宽度和相对宽度
        self.resize(target_size)  # 先调整大小以获得准确的尺寸

        # 计算居中位置 - 直接使用父窗口的坐标系
        center_x = (parent_rect.width() - self.width()) // 2
        center_y = (parent_rect.height() - self.height()) // 2
        target_geom = QRect(center_x, center_y, self.width(), self.height())

        start_geom = QRect(target_geom)  # 默认起始等于目标

        # 缩放：中心小矩形
        scaled_width = int(target_geom.width() * CONFIG["scale_anim_factor"])
        scaled_height = int(target_geom.height() * CONFIG["scale_anim_factor"])
        scaled_x = center_x + (self.width() - scaled_width) // 2
        scaled_y = center_y + (self.height() - scaled_height) // 2
        start_geom = QRect(scaled_x, scaled_y, scaled_width, scaled_height)

        self.logger.debug(f"已计算位置 - 起始: {start_geom}, 目标: {target_geom}")
        return start_geom, target_geom

    def show_animated(self):  # 带动画显示
        self.logger.info("开始显示动画")
        start_geom, end_geom = self._calc_geometries()  # 获取位置
        self.setGeometry(start_geom)  # 设置初始位置

        # 初始设置透明度为0
        self._opacity = 0.0  # 直接设置内部变量而不是通过setter，避免额外的重绘

        # 缩放动画
        self.logger.debug("使用缩放动画")
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()
        self.geom_anim.setStartValue(start_geom)
        self.geom_anim.setEndValue(end_geom)
        self.geom_anim.start()

        self.show()  # 显示窗口

    def close_animated(self):  # 带动画关闭
        self.logger.info("开始关闭动画")
        start_geom, end_geom = self._calc_geometries()  # 获取位置 (用于计算结束位置)
        current_geom = self.geometry()  # 当前位置

        # 断开所有之前的连接，防止重复连接
        try:
            self.opacity_anim.finished.disconnect()
            self.geom_anim.finished.disconnect()
        except:
            pass  # 如果没有连接，忽略错误

        # 通知父窗口处理关闭
        if hasattr(self.parent(), "handle_dialog_close"):
            self.parent().handle_dialog_close(self)

        # 始终移除模糊效果，不再检查是否有其他对话框
        self.remove_parent_blur()

        # 缩放退出
        self.logger.debug("使用缩放退出动画")
        end_geom.setSize(
            QSize(
                int(current_geom.width() * CONFIG["scale_anim_factor"]),
                int(current_geom.height() * CONFIG["scale_anim_factor"]),
            )
        )
        end_geom.moveCenter(current_geom.center())
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.geom_anim.setStartValue(current_geom)
        self.geom_anim.setEndValue(end_geom)
        # 两个动画都结束后隐藏
        finished_count = 0

        def check_finish():
            nonlocal finished_count
            finished_count += 1
            if finished_count == 2:
                self.hide()
                # 确保删除对话框时清理资源
                if hasattr(self, "blur_anim"):
                    self.blur_anim = None

        self.opacity_anim.finished.connect(check_finish)
        self.geom_anim.finished.connect(check_finish)
        self.opacity_anim.start()
        self.geom_anim.start()

    def handle_button_click(self, button_text):
        """处理按钮点击事件"""
        self.logger.debug(f"按钮点击: {button_text}")

        # 调用回调函数
        if self.on_button_clicked:
            self.on_button_clicked(button_text)

        # 关闭对话框
        self.close_animated()


# 公开函数，用于显示对话框
def show_dialog(
    parent,
    message_type="warning",
    title_text=None,
    message="",
    content_widget=None,
    custom_icon=None,
    custom_buttons=None,
    custom_button_colors=None,
    callback=None,
):
    """
    显示对话框

    Args:
        parent: 父窗口
        message_type: 对话框类型，可选值：'warning', 'question', 'retry', 'timeout', 'custom'
        title_text: 标题文本，默认使用对话框类型的名称
        message: 消息内容
        content_widget: 自定义内容组件
        custom_icon: 自定义图标
        custom_buttons: 自定义按钮列表
        custom_button_colors: 自定义按钮颜色字典
        callback: 按钮点击回调函数，参数为按钮文本

    Returns:
        MessageDialog: 对话框实例
    """
    if title_text is None:
        title_text = MESSAGE_TYPES[message_type]["name"]

    # 创建对话框
    dialog = MessageDialog(
        message_type=message_type,
        content_widget=content_widget,
        parent=parent,
        title_text=title_text,
        message=message,
        custom_icon=custom_icon,
        custom_buttons=custom_buttons,
        custom_button_colors=custom_button_colors,
        on_button_clicked=callback,
    )

    # 显示对话框
    dialog.show_animated()

    return dialog


# --- 测试部分，仅在直接运行时执行 ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建测试窗口
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.logger = get_logger("TestWindow")
            self.setWindowTitle("对话框组件测试")
            self.setGeometry(100, 100, 800, 600)
            self.current_dialog = None

            # 设置背景渐变
            self.setAutoFillBackground(True)
            p = self.palette()
            grad = QLinearGradient(0, 0, 0, self.height())
            grad.setColorAt(0.0, QColor(CONFIG["color_primary"]))
            grad.setColorAt(1.0, QColor(CONFIG["color_secondary"]))
            p.setBrush(QPalette.ColorRole.Window, QBrush(grad))
            self.setPalette(p)

            # 创建中心部件和布局
            self.central_widget = QWidget(self)
            self.setCentralWidget(self.central_widget)
            self.central_widget.setAutoFillBackground(False)
            self.central_widget.setStyleSheet("background-color: transparent;")

            main_layout = QVBoxLayout(self.central_widget)
            main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_widget.setMaximumWidth(600)

            # 添加标题和说明
            title_label = QLabel("对话框演示")
            title_label.setStyleSheet(
                f"font-size: {CONFIG['font_size_base']+15}pt; font-weight: 600; color: {CONFIG['color_text_light']}; margin-bottom: 10px;"
            )
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            desc_label = QLabel("测试不同类型的选择对话框")
            desc_label.setStyleSheet(
                f"font-size: {CONFIG['font_size_base']+2}pt; color: {CONFIG['color_text_light']}; opacity: 0.9; margin-bottom: 15px; line-height: 1.6;"
            )
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 创建按钮容器
            buttons_container = QWidget()
            buttons_layout = QVBoxLayout(buttons_container)
            buttons_layout.setSpacing(10)

            # 添加对话框类型按钮
            for msg_type, info in MESSAGE_TYPES.items():
                if msg_type != "custom":  # 跳过custom类型，因为移除了自定义设置功能
                    btn = QPushButton(f"{info['icon']} {info['name']}")
                    btn.setStyleSheet(
                        f"""QPushButton {{ background-color: {info['color']}; color: {CONFIG['color_white']}; border: none;
                                        padding: 10px 20px; border-radius: {CONFIG['radius_button']}px; font-size: {CONFIG['font_size_base']}pt; }}
                                    QPushButton:hover {{ opacity: 0.9; }}"""
                    )
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.clicked.connect(
                        lambda checked, t=msg_type: self.show_test_dialog(t)
                    )
                    btn.setSizePolicy(
                        QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
                    )
                    buttons_layout.addWidget(btn)

            # 组装界面
            content_layout.addWidget(title_label)
            content_layout.addWidget(desc_label)
            content_layout.addWidget(buttons_container)
            main_layout.addWidget(content_widget)

            self.logger.debug("测试窗口初始化完成")

        def show_test_dialog(self, message_type):
            """显示测试对话框"""
            try:
                # 根据消息类型设置内容
                if message_type == "warning":
                    message = "这是一条警告消息，提醒用户注意某些操作可能会带来的后果。"
                elif message_type == "question":
                    message = "您确定要执行此操作吗？"
                elif message_type == "retry":
                    message = "操作失败，是否重试？"
                elif message_type == "timeout":
                    message = "操作超时，请检查网络连接后重试。"
                else:  # 其他类型
                    message = "这是一条一般消息，可以根据需要设置内容和按钮。"

                # 显示对话框
                self.current_dialog = show_dialog(
                    parent=self,
                    message_type=message_type,
                    title_text=MESSAGE_TYPES[message_type]["name"],
                    message=message,
                    callback=self.handle_dialog_result,
                )
            except Exception as e:
                self.logger.error(f"显示对话框时出错: {str(e)}")

        def handle_dialog_result(self, button_text):
            """处理对话框结果"""
            self.logger.info(f"对话框结果: {button_text}")
            # 在实际应用中，这里可以根据按钮文本执行相应的操作

        def handle_dialog_close(self, dialog):
            """处理对话框关闭"""
            self.logger.debug("对话框关闭")
            if self.current_dialog == dialog:
                self.current_dialog = None

        def resizeEvent(self, event):
            """窗口大小变化事件"""
            super().resizeEvent(event)

            # 更新渐变背景
            p = self.palette()
            grad = QLinearGradient(0, 0, 0, self.height())
            grad.setColorAt(0.0, QColor(CONFIG["color_primary"]))
            grad.setColorAt(1.0, QColor(CONFIG["color_secondary"]))
            p.setBrush(QPalette.ColorRole.Window, QBrush(grad))
            self.setPalette(p)

    # 创建并显示测试窗口
    window = TestWindow()
    window.show()

    sys.exit(app.exec())


# 为页面提供统一的对话框连接辅助函数
def connect_page_to_main_window(page):
    """
    为页面提供与主窗口的对话框连接

    此方法应在页面的showEvent中调用，用于建立页面与主窗口的对话框连接，
    避免每个页面都实现相同的连接逻辑。

    Args:
        page: 需要连接对话框的页面对象，必须有request_dialog信号

    Returns:
        bool: 连接是否成功
    """
    try:
        # 确保页面有request_dialog信号
        if not hasattr(page, "request_dialog"):
            page.logger.error("页面没有request_dialog信号，无法连接到主窗口")
            return False

        # 获取主窗口引用
        main_window = page.window()
        if main_window and hasattr(main_window, "show_global_dialog"):
            # 检查信号是否已连接，防止重复连接
            if hasattr(page, "_dialog_connected") and page._dialog_connected:
                page.logger.debug("对话框信号已连接，跳过重复连接")
                return True

            # 将信号连接到主窗口的方法
            page.request_dialog.connect(
                lambda message_type, title, message, callback: main_window.show_global_dialog(
                    message_type=message_type,
                    title_text=title,
                    message=message,
                    callback=callback,
                )
            )
            # 标记信号已连接
            page._dialog_connected = True
            page.logger.debug("已连接到主窗口的对话框方法")
            return True
        else:
            page.logger.warning(
                f"未找到主窗口或主窗口没有show_global_dialog方法，找到的窗口类型: {type(main_window)}"
            )
            return False
    except Exception as e:
        page.logger.error(f"连接到主窗口时出错: {e}")
        return False
