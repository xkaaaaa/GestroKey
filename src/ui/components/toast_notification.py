import math
import os
import sys
import time
from functools import partial

from PyQt6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QEvent,
    QMetaObject,
    QObject,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    QRectF,
    QRunnable,
    QSequentialAnimationGroup,
    QSize,
    Qt,
    QThread,
    QThreadPool,
    QTimer,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QTextOption,
    QTransform,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

# 尝试导入日志模块，如果不存在则忽略
try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger

# 全局变量，用于存储预加载的通知
_preloaded_toast = None

# 添加一个全局变量来标记预加载状态
_preloading_in_progress = False

# 添加一个表示预加载完成的标志
_preload_complete = False

# 添加一个全局变量来表示是否曾经完成过预加载
_preload_ever_completed = False

# 添加全局线程池
_thread_pool = None


def get_thread_pool():
    """获取全局线程池实例"""
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = QThreadPool.globalInstance()
        _thread_pool.setMaxThreadCount(4)  # 设置最大线程数
    return _thread_pool


# 通知预加载工作类
class ToastPreloadWorker(QRunnable):
    """通知预加载工作线程"""

    def __init__(self):
        """初始化预加载工作线程"""
        super().__init__()

        # 设置低优先级
        self.setAutoDelete(True)

        # 获取日志器
        self.logger = get_logger("ToastPreloadWorker")

        # 创建线程通信信号
        self.signals = ToastPreloadSignals()

    @pyqtSlot()
    def run(self):
        """在线程池中执行的预加载操作"""
        # 记录预加载开始
        self.logger.info("===== 预加载工作线程开始执行 =====")

        try:
            # 将实际创建通知的任务调度到主线程中执行
            # 因为PyQt中UI组件应该在主线程创建
            app = QApplication.instance()
            if not app:
                self.logger.error("预加载失败：QApplication实例不存在")
                return

            # 添加信号处理
            self.signals.load_complete.connect(self._handle_load_complete)

            # 报告进度：开始
            self.signals.progress_updated.emit("开始预加载通知组件...", 5)
            self.logger.info("发出进度信号：5%")

            # 直接在当前线程执行预加载任务，避免使用QTimer可能的延迟问题
            self.logger.info("开始执行_create_preloaded_toast_part1")
            self._create_preloaded_toast_part1()

        except Exception as e:
            # 确保异常被捕获并记录
            self.logger.error(f"预加载工作线程执行异常: {e}")
            # 发送完成信号以避免卡住
            self.signals.progress_updated.emit(f"预加载失败: {e}", 0)
            self.signals.load_complete.emit()

            # 重置全局状态
            global _preloading_in_progress
            _preloading_in_progress = False

    def _handle_load_complete(self):
        """处理预加载完成信号"""
        # 发送完成事件
        global _preloading_in_progress, _preload_complete, _preload_ever_completed
        _preloading_in_progress = False
        _preload_complete = True
        _preload_ever_completed = True  # 标记已经完成过一次预加载

        # 报告进度：完成
        self.signals.progress_updated.emit("预加载完成", 100)

        # 记录完成
        self.logger.info("===== 预加载工作线程完成 =====")

    def _create_preloaded_toast_part1(self):
        """预加载第一部分：创建基本实例"""
        global _preloaded_toast, _preloading_in_progress
        try:
            # 报告进度：创建实例
            self.signals.progress_updated.emit("创建通知实例...", 20)
            self.logger.info("发出进度信号：20%")

            # 找到应用的主窗口作为父窗口
            app = QApplication.instance()
            if app and app.activeWindow():
                parent = app.activeWindow()
                self.logger.info(f"找到活动窗口作为父窗口: {parent}")
            else:
                # 没有活动窗口时创建无父级通知
                parent = None
                self.logger.info("未找到活动窗口，使用None作为父窗口")

            # 创建包含所有可能通知类型的实例
            self.logger.info("开始创建ElegantToast实例")
            _preloaded_toast = ElegantToast(
                parent=parent,
                message="这是一条预加载的通知，内容较长以支持自动换行测试，确保预渲染完成后能够快速显示通知而不出现卡顿现象。",
                toast_type=ElegantToast.INFO,
                duration=0,
                text_mode=ElegantToast.TEXT_WRAP,
            )
            self.logger.info("ElegantToast实例创建成功")

            # 报告进度：初始化组件
            self.signals.progress_updated.emit("初始化通知组件...", 40)
            self.logger.info("发出进度信号：40%")

            # 立即执行延迟初始化，减少首次显示延迟
            self.logger.info("开始执行_delayed_init")
            _preloaded_toast._delayed_init()
            self.logger.info("_delayed_init执行完成")

            # 确保完全初始化所有组件
            self.logger.info("检查并创建动画")
            if (
                not hasattr(_preloaded_toast, "opacity_animation")
                or not _preloaded_toast.opacity_animation
            ):
                _preloaded_toast.create_animations()
                self.logger.info("动画创建完成")

            self.logger.info("检查并创建阴影效果")
            if not hasattr(_preloaded_toast, "_shadow") or not _preloaded_toast._shadow:
                _preloaded_toast.set_shadow_effect()
                self.logger.info("阴影效果创建完成")

            # 预先计算换行文本高度
            self.logger.info("检查并计算文本高度")
            if _preloaded_toast.text_mode == _preloaded_toast.TEXT_WRAP:
                _preloaded_toast._adjust_height_for_text()
                self.logger.info("文本高度计算完成")

            # 不显示，只预初始化
            _preloaded_toast.hide()

            # 报告进度：准备渲染
            self.signals.progress_updated.emit("准备渲染通知组件...", 60)
            self.logger.info("发出进度信号：60%")

            # 继续进行预渲染 - 直接调用，避免QTimer可能的延迟
            self.logger.info("开始预渲染")
            self._pre_render_toast(_preloaded_toast)

        except Exception as e:
            self.logger.error(f"预加载创建实例失败: {e}")
            import traceback

            self.logger.error(f"异常堆栈: {traceback.format_exc()}")
            self.signals.progress_updated.emit(f"预加载失败: {e}", 0)
            global _preloading_in_progress
            _preloading_in_progress = False
            # 确保发送完成信号
            self.signals.load_complete.emit()

    def _pre_render_toast(self, toast):
        """预先渲染通知内容，确保首次显示时无需重计算"""
        try:
            if not toast:
                self.logger.error("预渲染失败: 通知对象为空")
                self.signals.progress_updated.emit("预渲染失败: 通知对象为空", 0)
                self.signals.load_complete.emit()
                return

            # 强制通知小部件完成布局
            self.logger.info("开始强制布局")
            toast.updateGeometry()
            toast.layout().activate()
            self.logger.info("布局强制完成")

            # 创建临时图像并在其上预渲染通知
            size = toast.size()
            self.logger.info(f"通知大小: {size.width()}x{size.height()}")

            if size.width() > 0 and size.height() > 0:
                # 预渲染所有四种通知类型，确保样式缓存都已生成
                toast_types = [
                    ElegantToast.INFO,
                    ElegantToast.SUCCESS,
                    ElegantToast.WARNING,
                    ElegantToast.ERROR,
                ]

                # 为每种类型创建一个离屏渲染
                for i, toast_type in enumerate(toast_types):
                    # 报告渲染进度
                    progress = 60 + int((i + 1) / len(toast_types) * 30)
                    self.signals.progress_updated.emit(
                        f"渲染{['信息', '成功', '警告', '错误'][i]}类型通知...", progress
                    )
                    self.logger.info(f"发出进度信号：{progress}%")

                    # 更改类型并应用样式
                    toast.toast_type = toast_type
                    toast.setup_colors()

                    # 更新样式
                    toast.label.setStyleSheet(
                        f"""
                        color: {toast.text_color.name()}; 
                        font-size: 11pt;
                        padding: 0px;
                        margin: 0px;
                        text-align: left;
                    """
                    )

                    # 预渲染
                    self.logger.info(f"开始渲染{['信息', '成功', '警告', '错误'][i]}类型通知")
                    pixmap = QPixmap(size)
                    pixmap.fill(Qt.GlobalColor.transparent)
                    toast.render(pixmap)
                    self.logger.info(f"{['信息', '成功', '警告', '错误'][i]}类型通知渲染完成")

                # 记录日志
                self.logger.info(f"预渲染通知完成: 尺寸={size.width()}x{size.height()}")
            else:
                self.logger.warning(f"无效的通知大小: {size.width()}x{size.height()}, 跳过渲染")

            # 发送预加载完成信号
            self.signals.progress_updated.emit("预渲染完成，准备就绪", 90)
            self.logger.info("发出进度信号：90%")
            self.signals.load_complete.emit()

        except Exception as e:
            self.logger.error(f"预渲染失败: {e}")
            import traceback

            self.logger.error(f"异常堆栈: {traceback.format_exc()}")
            # 即使失败也要发送完成信号，确保不会卡住预加载状态
            self.signals.progress_updated.emit(f"预渲染失败: {e}", 0)
            self.signals.load_complete.emit()


class ToastPreloadSignals(QObject):
    """预加载线程信号"""

    load_complete = pyqtSignal()
    progress_updated = pyqtSignal(str, int)  # 消息, 进度百分比


# 初始预加载应立即启动，不要等待
def initialize_toast_system():
    """在模块导入时初始化通知系统并以非阻塞方式触发预加载"""
    # 获取通知管理器
    manager = get_toast_manager()

    # 在应用程序事件循环开始后立即触发预加载
    app = QApplication.instance()
    if app:
        # 如果应用实例已存在且未进行过预加载，立即触发预加载
        global _preload_ever_completed, _preloading_in_progress
        if not _preload_ever_completed and not _preloading_in_progress:
            QTimer.singleShot(100, schedule_preload)
            logger = get_logger("ToastNotification")
            logger.info("通知系统初始化完成，将立即开始后台预加载")
        else:
            logger = get_logger("ToastNotification")
            logger.info("通知系统初始化完成，已有预加载过程，跳过重复预加载")
    else:
        # 应用实例不存在，稍后会通过ensure_toast_system_initialized处理
        logger = get_logger("ToastNotification")
        logger.info("通知系统初始化：等待应用程序初始化")


def schedule_preload():
    """安排后台预加载任务"""
    global _preloading_in_progress, _preload_ever_completed

    # 如果已经完成过一次预加载或正在预加载中，就不再触发新的预加载
    if _preloading_in_progress or _preload_ever_completed:
        return

    _preloading_in_progress = True

    # 创建预加载工作线程
    worker = ToastPreloadWorker()

    # 提交到线程池前记录日志
    logger = get_logger("ToastPreloader")
    logger.info("准备提交预加载任务到线程池")

    # 提交到线程池
    thread_pool = get_thread_pool()
    thread_pool.start(worker)

    logger.info(f"通知预加载任务已提交到线程池，当前活动线程数：{thread_pool.activeThreadCount()}")


class CloseButton(QWidget):
    """关闭按钮组件"""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self._hovered = False
        self._pressed = False
        self._opacity = 0.0

        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(150)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 鼠标追踪
        self.setMouseTracking(True)

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

    def enterEvent(self, event):
        """鼠标进入事件"""
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._hovered = False
        self._pressed = False
        self.update()

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self._pressed:
            self._pressed = False
            self.clicked.emit()
        self.update()

    def paintEvent(self, event):
        """绘制关闭按钮"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 根据状态设置颜色
        if self._pressed:
            color = QColor(255, 255, 255, int(220 * self._opacity))
        elif self._hovered:
            color = QColor(255, 255, 255, int(200 * self._opacity))
        else:
            color = QColor(255, 255, 255, int(160 * self._opacity))

        # 绘制 X 形状
        painter.setPen(QPen(color, 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

        # 计算中心点和偏移
        center = self.rect().center()
        offset = 4

        # 绘制 X
        painter.drawLine(
            center.x() - offset,
            center.y() - offset,
            center.x() + offset,
            center.y() + offset,
        )
        painter.drawLine(
            center.x() + offset,
            center.y() - offset,
            center.x() - offset,
            center.y() + offset,
        )


class ElegantToast(QWidget):
    """
    嵌入式通知窗口类
    在窗口角落嵌入一个通知提示
    """

    # 通知类型
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

    # 文本显示模式
    TEXT_TRUNCATE = "truncate"  # 截断模式（默认）
    TEXT_SCROLL = "scroll"  # 滚动模式
    TEXT_WRAP = "wrap"  # 自动换行模式

    # 关闭信号
    closed = pyqtSignal(object)

    # 固定尺寸
    FIXED_WIDTH = 300
    FIXED_HEIGHT = 80
    WRAP_MAX_HEIGHT = 200  # 增加最大换行高度限制

    # 垂直动画信号
    vertical_move_completed = pyqtSignal()

    # 延迟初始化标志
    _init_completed = False

    def __init__(
        self,
        parent=None,
        message="",
        toast_type=INFO,
        duration=5000,
        icon=None,
        position="top-right",
        text_mode=TEXT_WRAP,
    ):
        """
        初始化通知窗口

        参数:
            parent: 父窗口
            message: 消息文本
            toast_type: 提示类型 (info, success, warning, error)
            duration: 显示持续时间（毫秒）
            icon: 自定义图标（默认为类型图标）
            position: 屏幕位置 ('top-right', 'top-left', 'bottom-right', 'bottom-left')
            text_mode: 文本显示模式 ('truncate', 'scroll', 'wrap')
        """
        super().__init__(parent)
        self.logger = get_logger("ElegantToast")

        # 存储参数
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        self.custom_icon = icon
        self.position = position
        self.text_mode = text_mode

        # 设置窗口属性
        if text_mode == self.TEXT_WRAP:
            # 自动换行模式设置灵活高度
            self.setMinimumSize(self.FIXED_WIDTH, 80)
            self.setMaximumSize(self.FIXED_WIDTH, self.WRAP_MAX_HEIGHT)
        else:
            # 固定大小
            self.setMinimumSize(self.FIXED_WIDTH, self.FIXED_HEIGHT)
            self.setMaximumSize(self.FIXED_WIDTH, self.FIXED_HEIGHT)

        # 根据类型设置颜色
        self.setup_colors()

        # 状态变量
        self._opacity = 0.0  # 初始透明度为0
        self._progress = 1.0
        self._hovered = False
        self._closing = False
        self._original_pos = None  # 用于存储晃动前的位置
        self._close_button_opacity = 0.0
        self._text_scroll_offset = 0.0  # 文本滚动偏移量
        self._target_y = 0  # 目标Y位置，用于垂直滑动动画

        # 初始化基本UI
        self.init_ui()

        # 设置定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)

        # 默认隐藏
        self.hide()

        # 标记为未完成初始化
        self._init_completed = False

        # 使用QTimer在主事件循环中延迟初始化耗时组件
        QTimer.singleShot(0, self._delayed_init)

        self.logger.debug(f"创建通知: {toast_type}, 消息: {message}")

    def _delayed_init(self):
        """延迟初始化耗时组件，避免阻塞UI"""
        if self._init_completed:
            return

        # 创建动画
        self.create_animations()

        # 设置阴影效果
        self.set_shadow_effect()

        # 设置鼠标跟踪
        self.setMouseTracking(True)

        # 标记初始化完成
        self._init_completed = True

    def setup_colors(self):
        """根据提示类型配置颜色"""
        if self.toast_type == self.INFO:
            self.main_color = QColor(41, 128, 185)  # 蓝色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
            self.progress_color = QColor(255, 255, 255, 180)
        elif self.toast_type == self.SUCCESS:
            self.main_color = QColor(39, 174, 96)  # 绿色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
            self.progress_color = QColor(255, 255, 255, 180)
        elif self.toast_type == self.WARNING:
            self.main_color = QColor(211, 159, 15)  # 黄色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
            self.progress_color = QColor(255, 255, 255, 180)
        elif self.toast_type == self.ERROR:
            self.main_color = QColor(192, 57, 43)  # 红色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
            self.progress_color = QColor(255, 255, 255, 180)
        else:
            # 默认颜色
            self.main_color = QColor(41, 128, 185)  # 蓝色
            self.icon_color = QColor(255, 255, 255)
            self.text_color = QColor(255, 255, 255)
            self.progress_color = QColor(255, 255, 255, 180)

        # 边框颜色略深
        self.border_color = QColor(self.main_color)
        self.border_color.setAlpha(150)

    def init_ui(self):
        """初始化用户界面"""
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 10)  # 左、上、右、下
        layout.setSpacing(5)

        # 内容布局（图标+文本+关闭按钮）
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(2, 5, 0, 0)  # 调整上边距，使文本与图标对齐
        content_layout.setSpacing(8)  # 减少图标和文本间的间距

        # 预留图标区域（将在painEvent中绘制） - 调整与新图标位置一致
        icon_spacer = QSpacerItem(
            40, 30, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        content_layout.addItem(icon_spacer)

        # 添加消息标签
        self.label = QLabel(self.message)
        # 设置垂直方向居上对齐的大小策略
        self.label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 根据文本模式设置标签属性
        if self.text_mode == self.TEXT_TRUNCATE:
            self.label.setWordWrap(False)
            metrics = QFontMetrics(QFont("Arial", 11))
            elided_text = metrics.elidedText(
                self.message, Qt.TextElideMode.ElideRight, 200
            )
            self.label.setText(elided_text)

        elif self.text_mode == self.TEXT_SCROLL:
            self.label.setWordWrap(False)
            # 滚动模式下将标签文本设置为空，完全依靠绘制实现
            self.label.setText("")
            # 完全隐藏标签，防止与绘制的文本产生任何干扰
            self.label.setVisible(False)

        elif self.text_mode == self.TEXT_WRAP:
            self.label.setWordWrap(True)
            self.label.setText(self.message)

            # 使用简单直接的高度计算方法
            self._adjust_height_for_text()

        # 设置通用样式，水平靠左，垂直靠上对齐
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label.setStyleSheet(
            f"""
            color: {self.text_color.name()}; 
            font-size: 11pt;
            padding: 0px;
            margin: 0px;
            text-align: left;
        """
        )

        # 使用内容对齐方式添加到布局中
        content_layout.addWidget(
            self.label, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )

        # 添加关闭按钮，确保按钮也垂直居中
        self.close_button = CloseButton(self)
        self.close_button.clicked.connect(self.start_closing)
        content_layout.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignTop)

        # 添加到主布局
        layout.addLayout(content_layout)

        # 添加进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.progress_bar.setTextVisible(False)
        # 根据通知类型设置进度条样式
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: none;
                background-color: rgba(0, 0, 0, 40);
                height: 4px;
                margin-top: 8px;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {self.progress_color.name()};
                border-radius: 2px;
            }}
        """
        )
        layout.addWidget(self.progress_bar)

    def set_shadow_effect(self):
        """为通知窗口添加阴影效果"""
        if hasattr(self, "_shadow"):
            return  # 避免重复创建阴影

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(15)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        self._shadow.setOffset(0, 3)
        self.setGraphicsEffect(self._shadow)

    def create_animations(self):
        """创建动画效果"""
        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(250)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 进度条动画 - 优化动画曲线与更新频率
        self.progress_animation = QPropertyAnimation(self, b"progress")
        self.progress_animation.setEasingCurve(
            QEasingCurve.Type.InOutSine
        )  # 使用更平滑的动画曲线
        self.progress_animation.setStartValue(1.0)
        self.progress_animation.setEndValue(0.0)
        # 设置更新步数，使动画更加流畅
        self.progress_animation.setDuration(self.duration)

        # 关闭按钮透明度动画
        self.close_btn_animation = QPropertyAnimation(self.close_button, b"opacity")
        self.close_btn_animation.setDuration(150)
        self.close_btn_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 垂直位置动画
        self.vertical_animation = QPropertyAnimation(self, b"pos")
        self.vertical_animation.setDuration(300)
        self.vertical_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.vertical_animation.finished.connect(self.vertical_move_completed.emit)

        # 文本滚动动画（仅在滚动模式下使用）
        if self.text_mode == self.TEXT_SCROLL:
            # 使用动画组实现循环滚动效果
            self.scroll_animation_group = QSequentialAnimationGroup(self)

            # 第一段动画：从右向左滚动
            self.scroll_animation = QPropertyAnimation(self, b"text_scroll_offset")
            self.scroll_animation.setEasingCurve(QEasingCurve.Type.Linear)  # 线性匀速滚动

            # 第二段动画：快速回到起始位置准备下一轮
            self.scroll_reset_animation = QPropertyAnimation(
                self, b"text_scroll_offset"
            )
            self.scroll_reset_animation.setEasingCurve(QEasingCurve.Type.Linear)
            self.scroll_reset_animation.setDuration(100)  # 快速回位

            # 将两段动画添加到动画组
            self.scroll_animation_group.addAnimation(self.scroll_animation)
            self.scroll_animation_group.addAnimation(self.scroll_reset_animation)
            self.scroll_animation_group.setLoopCount(-1)  # 无限循环

        # 错误通知的晃动动画
        if self.toast_type == self.ERROR:
            self.shake_animation = QSequentialAnimationGroup(self)
            self.shake_animation.finished.connect(self.reset_position)

            # 增加晃动幅度和次数
            shake_distance = 10
            shake_count = 4

            for i in range(shake_count):
                # 向右晃动
                right_anim = QPropertyAnimation(self, b"pos", self)
                right_anim.setDuration(60)
                right_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

                # 向左晃动
                left_anim = QPropertyAnimation(self, b"pos", self)
                left_anim.setDuration(60)
                left_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

                # 添加到动画组
                self.shake_animation.addAnimation(right_anim)
                self.shake_animation.addAnimation(left_anim)

            # 回到原位置的动画
            final_anim = QPropertyAnimation(self, b"pos", self)
            final_anim.setDuration(60)
            final_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.shake_animation.addAnimation(final_anim)

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

    @pyqtProperty(float)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        # 同步更新进度条UI
        self.progress_bar.setValue(int(value * 100))
        self.update()

    @pyqtProperty(float)
    def text_scroll_offset(self):
        return self._text_scroll_offset

    @text_scroll_offset.setter
    def text_scroll_offset(self, value):
        self._text_scroll_offset = value
        self.update()

    def showEvent(self, event):
        """处理显示事件，开始显示动画"""
        super().showEvent(event)

        # 确保所有延迟初始化的组件都准备好了
        if not self._init_completed:
            self._delayed_init()

        # 开始显示动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()

        # 如果是错误提示，触发晃动动画
        if self.toast_type == self.ERROR and hasattr(self, "shake_animation"):
            # 短暂延迟确保已显示
            QTimer.singleShot(50, self.start_shake_animation)

        # 如果是滚动模式且文本过长，开始滚动动画
        if self.text_mode == self.TEXT_SCROLL and hasattr(
            self, "scroll_animation_group"
        ):
            # 计算文本宽度
            metrics = QFontMetrics(QFont("Arial", 11))
            text_width = metrics.horizontalAdvance(self.message)
            display_width = self.width() - 70  # 图标和边距

            if text_width > display_width:
                # 需要滚动，设置第一段动画（从右向左）
                self.scroll_animation.setStartValue(0)  # 从最右侧开始

                # 计算滚动结束位置，文本完全滚出左侧
                end_offset = -(text_width + 50)
                self.scroll_animation.setEndValue(end_offset)

                # 设置第二段动画（快速回到起始位置）
                self.scroll_reset_animation.setStartValue(end_offset)
                self.scroll_reset_animation.setEndValue(display_width)  # 从右侧重新进入

                # 设置滚动速度均匀
                pixel_duration = 20  # 每像素滚动时间（毫秒）
                total_scroll_distance = abs(end_offset) + display_width
                duration = max(4000, int(abs(end_offset) * pixel_duration))

                # 设置动画持续时间
                self.logger.debug(f"文本滚动距离: {abs(end_offset)}像素, 动画时长: {duration}毫秒")
                self.scroll_animation.setDuration(duration)

                # 使用QTimer延迟启动滚动动画组
                QTimer.singleShot(100, self.scroll_animation_group.start)

        # 开始进度条动画
        if self.duration > 0:
            # 确保进度动画持续时间与通知持续时间匹配
            self.progress_animation.setDuration(self.duration)

            # 开始进度动画 - 不再使用定时器单独更新进度条
            QTimer.singleShot(50, self.progress_animation.start)

            # 移除旧的定时器逻辑，改用动画事件
            self.progress_animation.valueChanged.connect(
                self._on_progress_animation_value_changed
            )

    def _on_progress_animation_value_changed(self, value):
        """进度动画数值变化时更新进度条"""
        # 直接更新进度条值，确保平滑过渡
        self.progress_bar.setValue(int(value * 100))

        # 进度完成时自动关闭
        if value <= 0.001 and not self._closing:
            self.start_closing()

    def start_shake_animation(self):
        """开始错误提示的晃动动画"""
        if not hasattr(self, "shake_animation"):
            return

        # 保存原始位置
        self._original_pos = self.pos()

        # 设置晃动的起始和结束位置
        shake_distance = 10

        current_x = self._original_pos.x()
        current_y = self._original_pos.y()

        for i in range(0, self.shake_animation.animationCount() - 1, 2):
            # 向右
            right_anim = self.shake_animation.animationAt(i)
            right_anim.setStartValue(QPoint(current_x, current_y))
            right_anim.setEndValue(
                QPoint(current_x + shake_distance - int(i / 2), current_y)
            )

            # 向左
            if i + 1 < self.shake_animation.animationCount():
                left_anim = self.shake_animation.animationAt(i + 1)
                left_anim.setStartValue(
                    QPoint(current_x + shake_distance - int(i / 2), current_y)
                )
                left_anim.setEndValue(
                    QPoint(current_x - shake_distance + int(i / 2), current_y)
                )

        # 最后回到原位
        final_anim = self.shake_animation.animationAt(
            self.shake_animation.animationCount() - 1
        )
        final_anim.setStartValue(QPoint(current_x - 4, current_y))
        final_anim.setEndValue(self._original_pos)

        # 开始晃动
        self.shake_animation.start()

    def reset_position(self):
        """晃动动画结束后重置位置"""
        if self._original_pos:
            self.move(self._original_pos)
            self._original_pos = None

    def start_closing(self):
        """开始关闭动画"""
        if self._closing:
            return

        self._closing = True
        self.timer.stop()

        # 停止进度条动画
        if self.progress_animation.state() == QAbstractAnimation.State.Running:
            self.progress_animation.stop()

        # 停止文本滚动动画
        if self.text_mode == self.TEXT_SCROLL and hasattr(
            self, "scroll_animation_group"
        ):
            if self.scroll_animation.state() == QAbstractAnimation.State.Running:
                self.scroll_animation.stop()

        # 开始关闭动画
        self.opacity_animation.setStartValue(self._opacity)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self.on_close_finished)
        self.opacity_animation.start()

    def on_close_finished(self):
        """关闭动画完成后清理"""
        self.hide()
        self.closed.emit(self)

    def enterEvent(self, event):
        """鼠标进入事件"""
        self._hovered = True

        # 显示关闭按钮
        self.close_btn_animation.setStartValue(self.close_button._opacity)
        self.close_btn_animation.setEndValue(1.0)
        self.close_btn_animation.start()

        # 鼠标悬停时暂停定时器和滚动
        if not self._closing:
            # 暂停进度条
            if self.duration > 0:
                if self.progress_animation.state() == QAbstractAnimation.State.Running:
                    self.progress_animation.pause()

            # 移除暂停文本滚动功能
            # 滚动文本应始终滚动，不受鼠标悬停影响

        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._hovered = False

        # 隐藏关闭按钮
        self.close_btn_animation.setStartValue(self.close_button._opacity)
        self.close_btn_animation.setEndValue(0.0)
        self.close_btn_animation.start()

        # 鼠标离开时恢复定时器和滚动
        if not self._closing:
            # 恢复进度条
            if self.duration > 0:
                # 恢复进度动画
                if self.progress_animation.state() == QAbstractAnimation.State.Paused:
                    self.progress_animation.resume()

            # 移除恢复文本滚动功能
            # 滚动文本应始终滚动，不受鼠标悬停影响

        super().leaveEvent(event)

    def update_progress(self):
        """更新进度条进度，并在进度为0时关闭窗口"""
        # 此方法保留但不再使用，由动画直接控制进度
        current_value = self.progress_bar.value()
        if current_value > 0:
            self.progress_bar.setValue(current_value - 1)
            # 更新进度属性
            self._progress = current_value / 100.0
        else:
            self.start_closing()

    def _adjust_height_for_text(self):
        """简单直接的高度计算方法，基于行数×行高×系数+固定高度"""
        # 获取字体度量
        font = QFont("Arial", 11)
        metrics = QFontMetrics(font)

        # 计算有效宽度
        available_width = self.FIXED_WIDTH - 90  # 图标宽度(40) + 边距(50)

        # 获取文本所需矩形区域
        text_rect = metrics.boundingRect(
            0, 0, available_width, 2000, Qt.TextFlag.TextWordWrap, self.message
        )

        # 基本参数计算
        line_height = metrics.lineSpacing()
        estimated_lines = max(1, math.ceil(text_rect.height() / line_height))

        # 配置系数和固定高度
        height_factor = 1.2  # 行高系数，提供一些额外空间
        fixed_height = 40  # 固定高度，用于边距、图标和进度条

        # 简单直接的高度计算
        text_height = estimated_lines * line_height * height_factor
        window_height = int(text_height + fixed_height)

        # 确保高度在合理范围内
        window_height = max(80, min(window_height, self.WRAP_MAX_HEIGHT))

        # 应用高度到标签和窗口
        self.label.setMinimumHeight(int(text_height))
        self.label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )
        self.setFixedHeight(window_height)

        # 记录日志
        self.logger.debug(
            f"简单高度计算: 行数={estimated_lines}, 行高={line_height}, "
            + f"系数={height_factor}, 固定高度={fixed_height}, 窗口高度={window_height}"
        )

    def show_notification(
        self, message=None, toast_type=None, duration=None, text_mode=None
    ):
        """显示通知并重置进度条"""
        # 重置关闭状态
        self._closing = False

        # 更新消息
        if message is not None:
            self.message = message

            # 根据文本模式设置标签
            if self.text_mode == self.TEXT_TRUNCATE:
                metrics = QFontMetrics(QFont("Arial", 11))
                elided_text = metrics.elidedText(
                    message, Qt.TextElideMode.ElideRight, 200
                )
                self.label.setText(elided_text)
            else:
                self.label.setText(message)

        # 更新通知类型
        if toast_type is not None and toast_type != self.toast_type:
            self.toast_type = toast_type
            self.setup_colors()
            # 更新样式
            self.label.setStyleSheet(
                f"""
                color: {self.text_color.name()}; 
                font-size: 11pt;
                padding: 0px;
            """
            )
            self.progress_bar.setStyleSheet(
                f"""
                QProgressBar {{
                    border: none;
                    background-color: rgba(0, 0, 0, 40);
                    height: 4px;
                    margin-top: 8px;
                    border-radius: 2px;
                }}
                QProgressBar::chunk {{
                    background-color: {self.progress_color.name()};
                    border-radius: 2px;
                }}
            """
            )

            # 如果类型变为错误，创建晃动动画
            if toast_type == self.ERROR and not hasattr(self, "shake_animation"):
                # 延迟动画创建到显示后
                QTimer.singleShot(0, self._delayed_init)

        # 更新文本模式
        if text_mode is not None and text_mode != self.text_mode:
            # 停止旧的滚动动画
            if self.text_mode == self.TEXT_SCROLL and hasattr(
                self, "scroll_animation_group"
            ):
                self.scroll_animation.stop()

            self.text_mode = text_mode

            # 根据新的文本模式更新标签
            if self.text_mode == self.TEXT_TRUNCATE:
                self.label.setWordWrap(False)
                metrics = QFontMetrics(QFont("Arial", 11))
                elided_text = metrics.elidedText(
                    self.message, Qt.TextElideMode.ElideRight, 200
                )
                self.label.setText(elided_text)

            elif self.text_mode == self.TEXT_SCROLL:
                self.label.setWordWrap(False)
                # 滚动模式下将标签文本设置为空，完全依靠绘制实现
                self.label.setText("")
                # 完全隐藏标签，防止与绘制的文本产生任何干扰
                self.label.setVisible(False)
                if not hasattr(self, "scroll_animation_group"):
                    # 使用QTimer延迟创建滚动动画
                    QTimer.singleShot(0, self._delayed_init)

            elif self.text_mode == self.TEXT_WRAP:
                self.label.setWordWrap(True)
                self.label.setText(self.message)

                # 使用简单直接的高度计算方法
                self._adjust_height_for_text()

        # 更新持续时间
        if duration is not None:
            self.duration = duration

        # 重置进度条
        self.progress_bar.setValue(100)
        self._progress = 1.0

        # 确保初始化完成
        if not self._init_completed:
            self._delayed_init()

        # 显示通知
        self.show()

    def paintEvent(self, event):
        """绘制通知窗口"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 设置透明度
        painter.setOpacity(self._opacity)

        # 绘制背景
        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)

        # 创建渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, self.main_color)
        gradient.setColorAt(1, self.main_color.darker(110))

        # 填充背景
        painter.fillPath(path, QBrush(gradient))

        # 绘制边框
        pen = QPen(self.border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)

        # 绘制类型图标
        self.draw_type_icon(painter)

        # 如果是文本滚动模式，手动绘制文本
        if self.text_mode == self.TEXT_SCROLL and hasattr(
            self, "scroll_animation_group"
        ):
            # 清空整个内容区域，防止文本重叠
            content_rect = QRectF(50, 16, self.width() - 70, self.height() - 35)
            painter.fillRect(content_rect, self.main_color)

            # 设置字体和颜色
            painter.setFont(QFont("Arial", 11))
            painter.setPen(QPen(self.text_color))

            # 获取文本宽度
            metrics = QFontMetrics(painter.font())
            text_width = metrics.horizontalAdvance(self.message)

            # 创建剪裁区域，限制文本只在内容区域显示
            painter.save()
            painter.setClipRect(content_rect)

            # 计算文本绘制位置 - 使用固定坐标确保不与其他元素重叠
            text_x = content_rect.left() + int(self._text_scroll_offset)
            text_y = content_rect.top() + 18  # 固定垂直位置，避免与底部元素重叠

            # 直接绘制文本，使用最基本的绘制方法
            painter.drawText(int(text_x), int(text_y), self.message)

            # 恢复绘制状态
            painter.restore()

    def draw_type_icon(self, painter):
        """根据通知类型绘制相应的图标"""
        # 获取整个窗口的尺寸
        total_height = self.height()

        # 计算图标垂直居中位置 - 考虑窗口可变高度
        center_y = total_height / 2 - 2

        # 定义图标区域
        icon_size = 28
        icon_left = 16
        icon_rect = QRectF(icon_left, center_y - icon_size / 2, icon_size, icon_size)

        # 绘制背景圆形
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
        painter.drawEllipse(icon_rect)

        # 根据类型绘制不同图标
        if self.toast_type == self.INFO:
            # 信息图标 (i)
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            painter.setPen(QPen(self.icon_color, 2.0))
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "i")

        elif self.toast_type == self.SUCCESS:
            # 成功图标 (✓)
            center = icon_rect.center()
            painter.setPen(QPen(self.icon_color, 2.5))
            painter.drawLine(
                int(center.x() - 7),
                int(center.y()),
                int(center.x() - 2),
                int(center.y() + 5),
            )
            painter.drawLine(
                int(center.x() - 2),
                int(center.y() + 5),
                int(center.x() + 7),
                int(center.y() - 5),
            )

        elif self.toast_type == self.WARNING:
            # 警告图标 (!)
            painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            painter.setPen(QPen(self.icon_color, 2.0))
            painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "!")

        elif self.toast_type == self.ERROR:
            # 错误图标 (✕)
            center = icon_rect.center()
            painter.setPen(QPen(self.icon_color, 2.5))
            painter.drawLine(
                int(center.x() - 6),
                int(center.y() - 6),
                int(center.x() + 6),
                int(center.y() + 6),
            )
            painter.drawLine(
                int(center.x() - 6),
                int(center.y() + 6),
                int(center.x() + 6),
                int(center.y() - 6),
            )

    def move_to(self, y_pos):
        """使用动画平滑移动到指定的垂直位置"""
        if self.isVisible():
            self._target_y = y_pos
            current_pos = self.pos()
            self.vertical_animation.setStartValue(current_pos)
            self.vertical_animation.setEndValue(QPoint(current_pos.x(), y_pos))
            self.vertical_animation.start()
        else:
            # 如果不可见，直接设置位置
            current_pos = self.pos()
            self.move(current_pos.x(), y_pos)


class ToastManager(QObject):
    """通知管理器，处理多个通知的显示和定位"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # 这通常是主窗口
        self.toasts = []
        self.toast_spacing = 10  # 通知之间的垂直间距
        self.start_y = 10  # 第一个通知的起始y坐标

        try:
            self.logger = get_logger("ToastManager")
        except:
            import logging

            self.logger = logging.getLogger("ToastManager")

    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.parent = main_window
        self.logger.debug(f"设置主窗口引用: {main_window}")

    def get_parent_window(self, widget=None):
        """
        获取主窗口作为Toast的父窗口

        即使提供了widget参数，也总是返回主窗口来确保Toast是全局的
        """
        if self.parent:
            return self.parent

        # 如果没有设置主窗口，尝试查找应用程序的主窗口
        app = QApplication.instance()
        if app:
            # 尝试查找主窗口
            for widget in app.topLevelWidgets():
                if isinstance(widget, QMainWindow):
                    self.parent = widget  # 缓存找到的主窗口
                    self.logger.debug(f"自动查找到主窗口: {widget}")
                    return widget

            # 如果找不到QMainWindow，使用任何顶级窗口
            if app.activeWindow():
                self.parent = app.activeWindow()  # 缓存找到的活动窗口
                self.logger.debug(f"使用活动窗口作为父窗口: {app.activeWindow()}")
                return app.activeWindow()

        # 如果无法找到任何父窗口，返回原始部件或None
        self.logger.warning("无法找到主窗口，提示框将不会自动跟随应用程序")
        return widget

    def show_toast(
        self,
        parent,
        message,
        toast_type=ElegantToast.INFO,
        duration=5000,
        icon=None,
        position="top-right",
        text_mode=ElegantToast.TEXT_WRAP,
    ):
        """
        添加并显示新通知

        参数:
            parent: 父窗口 (将被忽略，总是使用主窗口作为父级)
            message: 消息文本
            toast_type: 提示类型 (info, success, warning, error)
            duration: 显示持续时间（毫秒）
            icon: 自定义图标（默认为类型图标）
            position: 位置 ('top-right', 'top-left', 'bottom-right', 'bottom-left')
            text_mode: 文本显示模式 ('truncate', 'scroll', 'wrap')

        返回:
            添加的通知对象
        """
        # 总是使用主窗口作为父窗口，确保Toast是全局的
        actual_parent = self.get_parent_window(parent)

        # 创建新通知
        toast = ElegantToast(
            actual_parent, message, toast_type, duration, icon, position, text_mode
        )

        # 连接关闭信号
        toast.closed.connect(lambda obj: self.on_toast_closed(obj))

        # 添加到列表并计算位置
        self.toasts.append(toast)

        # 计算初始位置
        x = actual_parent.width() - toast.width() - 10
        y = self.calculate_toast_position(toast)
        toast.move(x, y)

        # 显示通知
        toast.show_notification(message, toast_type, duration, text_mode)

        self.logger.debug(f"添加通知: 总数 {len(self.toasts)}")
        return toast

    def calculate_toast_position(self, toast):
        """
        计算新通知的垂直位置

        参数:
            toast: 要计算位置的通知对象

        返回:
            垂直位置y坐标
        """
        y = self.start_y

        # 为之前的每个可见通知添加高度和间距
        for existing_toast in self.toasts:
            if existing_toast != toast and existing_toast.isVisible():
                y += existing_toast.height() + self.toast_spacing

        return y

    def arrange_toasts(self, position="top-right"):
        """重新计算所有可见通知的位置并应用动画"""
        if position != "top-right":
            # 目前仅实现top-right位置的布局
            return

        current_y = self.start_y

        for toast in self.toasts:
            if toast.isVisible():
                # 使用动画移动到新位置
                toast.move_to(current_y)
                current_y += toast.height() + self.toast_spacing

    def on_toast_closed(self, closed_toast):
        """
        处理通知关闭事件

        参数:
            closed_toast: 被关闭的通知对象
        """
        # 从列表中移除
        if closed_toast in self.toasts:
            self.toasts.remove(closed_toast)
            self.logger.debug(f"移除通知: 剩余 {len(self.toasts)}")

            # 重新计算其余通知的位置
            self.arrange_toasts()

    def close_all(self):
        """关闭所有通知"""
        # 创建通知列表的副本，因为在循环中会修改原列表
        toasts_to_close = self.toasts.copy()
        for toast in toasts_to_close:
            toast.start_closing()

    def update_positions_on_resize(self):
        """窗口大小改变时更新所有通知的水平位置"""
        parent = self.get_parent_window()
        if not parent:
            return

        x = parent.width() - ElegantToast.FIXED_WIDTH - 10

        for i, toast in enumerate(self.toasts):
            if toast.isVisible():
                # 只更新X坐标，保持Y坐标不变
                current_pos = toast.pos()
                toast.move(x, current_pos.y())


# 全局通知管理器
_toast_manager = None


def get_toast_manager():
    """获取全局通知管理器实例"""
    global _toast_manager
    if _toast_manager is None:
        _toast_manager = ToastManager()
    return _toast_manager


# 确保预加载完成或立即触发创建通知
def show_toast(
    parent,
    message,
    toast_type=ElegantToast.INFO,
    duration=5000,
    icon=None,
    position="top-right",
    text_mode=ElegantToast.TEXT_WRAP,
):
    """
    显示通知提示

    参数:
        parent: 父窗口（会被ToastManager替换为主窗口）
        message: 消息内容
        toast_type: 提示类型 (info, success, warning, error)
        duration: 显示持续时间（毫秒）
        icon: 自定义图标
        position: 位置 ('top-right', 'top-left', 'bottom-right', 'bottom-left')
        text_mode: 文本显示模式 ('truncate', 'scroll', 'wrap')

    返回:
        通知提示对象
    """
    global _preloaded_toast, _preloading_in_progress, _preload_complete
    manager = get_toast_manager()

    # 获取主窗口作为父窗口
    actual_parent = manager.get_parent_window(parent)

    # 检查是否有预加载的通知且父窗口匹配且预加载已完成
    if (
        _preloaded_toast
        and _preloaded_toast.parent() == actual_parent
        and _preload_complete
    ):
        toast = _preloaded_toast
        _preloaded_toast = None  # 清空预加载引用
        _preload_complete = False  # 重置预加载完成标志

        # 将通知添加到管理器并连接信号
        toast.closed.connect(lambda obj: manager.on_toast_closed(obj))
        manager.toasts.append(toast)

        # 计算初始位置
        x = actual_parent.width() - toast.width() - 10
        y = manager.calculate_toast_position(toast)
        toast.move(x, y)

        # 使用现有实例显示新消息
        toast.show_notification(message, toast_type, duration, text_mode)

        # 只在使用预加载通知后且没有进行中的预加载时安排新的预加载
        if not _preloading_in_progress:
            QTimer.singleShot(0, schedule_preload)

        return toast
    else:
        # 未使用预加载实例，直接创建
        toast = manager.show_toast(
            actual_parent, message, toast_type, duration, icon, position, text_mode
        )

        # 如果从未进行过预加载，则安排第一次预加载
        if not _preloading_in_progress and _preloaded_toast is None:
            QTimer.singleShot(0, schedule_preload)

        return toast


def show_info(
    parent,
    message,
    duration=5000,
    icon=None,
    position="top-right",
    text_mode=ElegantToast.TEXT_WRAP,
):
    """显示信息提示"""
    return show_toast(
        parent, message, ElegantToast.INFO, duration, icon, position, text_mode
    )


def show_success(
    parent,
    message,
    duration=5000,
    icon=None,
    position="top-right",
    text_mode=ElegantToast.TEXT_WRAP,
):
    """显示成功提示"""
    return show_toast(
        parent, message, ElegantToast.SUCCESS, duration, icon, position, text_mode
    )


def show_warning(
    parent,
    message,
    duration=5000,
    icon=None,
    position="top-right",
    text_mode=ElegantToast.TEXT_WRAP,
):
    """显示警告提示"""
    return show_toast(
        parent, message, ElegantToast.WARNING, duration, icon, position, text_mode
    )


def show_error(
    parent,
    message,
    duration=5000,
    icon=None,
    position="top-right",
    text_mode=ElegantToast.TEXT_WRAP,
):
    """显示错误提示"""
    return show_toast(
        parent, message, ElegantToast.ERROR, duration, icon, position, text_mode
    )


# 启动时预加载要更快更积极
def ensure_toast_system_initialized():
    """确保通知系统已初始化并触发背景预加载"""
    # 只在未预加载过的情况下触发预加载
    global _preloading_in_progress, _preload_ever_completed
    if not _preloading_in_progress and not _preload_ever_completed:
        schedule_preload()
    return True


if __name__ == "__main__":

    class MainWindow(QMainWindow):
        """主窗口类"""

        def __init__(self):
            super().__init__()
            self.setWindowTitle("嵌入式通知示例")
            self.setGeometry(100, 100, 600, 500)

            # 创建中央部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # 创建主布局
            main_layout = QGridLayout(central_widget)

            # 创建通知管理器
            self.toast_manager = ToastManager(self)

            # 创建用于测试不同类型通知的按钮
            button_layout = QVBoxLayout()

            # 添加预加载状态监控区域
            self.preload_frame = QFrame()
            self.preload_frame.setFrameShape(QFrame.Shape.StyledPanel)
            self.preload_frame.setFrameShadow(QFrame.Shadow.Raised)
            preload_layout = QVBoxLayout(self.preload_frame)

            # 添加标题
            preload_title = QLabel("<b>通知预加载状态</b>")
            preload_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preload_layout.addWidget(preload_title)

            # 添加状态标签
            self.preload_status = QLabel("未开始预加载")
            self.preload_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preload_layout.addWidget(self.preload_status)

            # 添加进度条
            self.preload_progress = QProgressBar()
            self.preload_progress.setRange(0, 100)
            self.preload_progress.setValue(0)
            preload_layout.addWidget(self.preload_progress)

            # 添加手动预加载按钮
            self.preload_button = QPushButton("手动触发预加载")
            self.preload_button.clicked.connect(self.trigger_preload)
            preload_layout.addWidget(self.preload_button)

            # 添加到主布局
            main_layout.addWidget(self.preload_frame, 0, 0, 1, 1)

            # 添加标题
            title_label = QLabel("<b>测试不同类型通知</b>")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            button_layout.addWidget(title_label)

            # 信息通知按钮
            self.info_button = QPushButton("显示信息通知")
            self.info_button.clicked.connect(
                lambda: self.show_notification("这是一条信息通知", ElegantToast.INFO)
            )
            button_layout.addWidget(self.info_button)

            # 成功通知按钮
            self.success_button = QPushButton("显示成功通知")
            self.success_button.clicked.connect(
                lambda: self.show_notification("操作已成功完成！", ElegantToast.SUCCESS)
            )
            button_layout.addWidget(self.success_button)

            # 警告通知按钮
            self.warning_button = QPushButton("显示警告通知")
            self.warning_button.clicked.connect(
                lambda: self.show_notification("请注意，这是一个警告！", ElegantToast.WARNING)
            )
            button_layout.addWidget(self.warning_button)

            # 错误通知按钮
            self.error_button = QPushButton("显示错误通知")
            self.error_button.clicked.connect(
                lambda: self.show_notification("发生错误，操作失败！", ElegantToast.ERROR)
            )
            button_layout.addWidget(self.error_button)

            # 将按钮布局添加到主布局
            main_layout.addLayout(button_layout, 1, 0, Qt.AlignmentFlag.AlignCenter)

            # 初始化预加载监控 - 延迟初始化，等待窗口显示后再初始化
            QTimer.singleShot(100, self.init_preload_monitoring)

        def init_preload_monitoring(self):
            """初始化预加载监控"""
            # 监控预加载状态变量
            global _preloading_in_progress, _preload_complete

            # 更新状态标签
            if _preload_complete:
                self.preload_status.setText("预加载已完成")
                self.preload_progress.setValue(100)
            elif _preloading_in_progress:
                self.preload_status.setText("预加载进行中...")
                self.preload_progress.setValue(30)  # 默认值
            else:
                self.preload_status.setText("未开始预加载")
                self.preload_progress.setValue(0)

            # 创建定时器定期检查预加载状态
            self.preload_timer = QTimer(self)
            self.preload_timer.timeout.connect(self.update_preload_status)
            self.preload_timer.start(500)  # 每500毫秒更新一次

            # 连接全局预加载信号处理器
            self.setup_global_preload_handler()

            # 启动预加载（如果尚未启动）
            if not _preloading_in_progress and not _preload_complete:
                QTimer.singleShot(500, self.trigger_preload)

        def setup_global_preload_handler(self):
            """设置全局预加载信号处理器"""
            # 创建一个全局处理器对象来接收所有预加载信号
            global _global_preload_handler
            if _global_preload_handler is None:
                _global_preload_handler = PreloadSignalHandler()

            # 连接信号到UI更新
            _global_preload_handler.progress_updated.connect(
                self.update_preload_progress
            )

        def update_preload_status(self):
            """更新预加载状态显示"""
            global _preloading_in_progress, _preload_complete

            if _preload_complete:
                self.preload_status.setText("预加载已完成")
                self.preload_progress.setValue(100)
                self.preload_button.setEnabled(True)
            elif _preloading_in_progress:
                # 状态会通过信号更新，这里不做更改
                self.preload_button.setEnabled(False)
            else:
                self.preload_status.setText("未开始预加载")
                self.preload_progress.setValue(0)
                self.preload_button.setEnabled(True)

        def trigger_preload(self):
            """手动触发预加载"""
            global _preloading_in_progress, _preload_complete

            if not _preloading_in_progress:
                # 重置状态
                _preload_complete = False

                # 更新UI
                self.preload_status.setText("开始预加载...")
                self.preload_progress.setValue(5)
                self.preload_button.setEnabled(False)

                # 创建预加载工作线程
                worker = ToastPreloadWorker()

                # 连接进度信号到全局处理器
                global _global_preload_handler
                if _global_preload_handler:
                    worker.signals.progress_updated.connect(
                        _global_preload_handler.handle_progress
                    )

                # 提交到线程池
                thread_pool = get_thread_pool()
                thread_pool.start(worker)

        def update_preload_progress(self, message, progress):
            """更新预加载进度"""
            self.preload_status.setText(message)
            self.preload_progress.setValue(progress)

        def show_notification(
            self,
            message,
            toast_type=ElegantToast.INFO,
            duration=5000,
            text_mode=ElegantToast.TEXT_WRAP,
        ):
            """显示指定类型的通知"""
            self.toast_manager.show_toast(
                self, message, toast_type, duration, None, "top-right", text_mode
            )

        def resizeEvent(self, event):
            """窗口大小改变时重新计算通知窗口位置"""
            super().resizeEvent(event)
            # 更新所有通知位置
            self.toast_manager.update_positions_on_resize()

    # 全局变量：预加载信号处理器
    _global_preload_handler = None

    # 全局预加载信号处理器
    class PreloadSignalHandler(QObject):
        """全局预加载信号处理器，用于桥接预加载线程和UI"""

        # 定义自己的信号
        progress_updated = pyqtSignal(str, int)

        def handle_progress(self, message, progress):
            """处理预加载进度更新"""
            # 重新发射信号给UI
            self.progress_updated.emit(message, progress)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    # 延迟启动预加载，确保窗口显示后再开始
    QTimer.singleShot(1000, schedule_preload)

    sys.exit(app.exec())

# 在模块导入时自动初始化通知系统
initialize_toast_system()
