import os
import sys

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    QTimer,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QCursor
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

try:
    from core.drawer import DrawingManager
    from core.logger import get_logger
    from core.system_monitor import SystemMonitor, format_bytes
    # 原生PyQt6组件替换自定义组件
    from version import APP_NAME  # 导入应用名称
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
    from core.drawer import DrawingManager
    from core.logger import get_logger
    from core.system_monitor import SystemMonitor, format_bytes
    # 原生PyQt6组件替换自定义组件
    from version import APP_NAME  # 导入应用名称


# 使用原生QProgressBar的辅助函数
def create_styled_progress_bar(color_theme="default"):
    """创建带样式的原生QProgressBar"""
    progress_bar = QProgressBar()
    progress_bar.setTextVisible(False)
    progress_bar.setRange(0, 100)
    
    # 根据主题设置样式
    if color_theme == "memory":
        # 内存进度条使用蓝色主题
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 50);
                height: 8px;
            }
            QProgressBar::chunk {
                border-radius: 5px;
                background-color: #3498db;
            }
        """)
    else:
        # CPU和默认进度条使用绿色主题
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 50);
                height: 8px;
            }
            QProgressBar::chunk {
                border-radius: 5px;
                background-color: #2ecc71;
            }
        """)
    
    return progress_bar


class ConsolePage(QWidget):
    """控制台页面
    用于显示应用程序的运行日志和状态信息。
    """

    # 添加绘制状态变化信号
    drawing_state_changed = pyqtSignal(bool)  # 参数为是否处于绘制状态

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ConsolePage")

        # 状态变量
        self.drawing_manager = None
        self.is_drawing_active = False

        # 系统监测器
        self.system_monitor = SystemMonitor(update_interval=1500)  # 1.5秒更新一次

        # 初始化UI
        self._setup_ui()

        # 连接系统监测器的信号
        self.system_monitor.dataUpdated.connect(self.update_system_info)

        # 启动系统监测
        self.system_monitor.start()

        self.logger.debug("控制台页面初始化完成")

    def _setup_ui(self):
        """初始化控制台页面UI"""
        self.logger.debug("初始化控制台页面UI")

        # 创建布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 改为顶部对齐，与其他选项卡一致

        # 顶部空白间距，增加灵活性
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        )

        # 标题标签 - 去掉APP_NAME前缀
        title_label = QLabel("控制台")
        title_label.setStyleSheet(
            "font-size: 18pt; font-weight: bold; margin-bottom: 20px;"
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(title_label)

        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("font-size: 10pt; margin-bottom: 20px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        layout.addWidget(self.status_label)

        # 使用单个按钮，根据状态切换文本和颜色
        self.action_button = QPushButton("开始绘制")
        self.action_button.setMinimumSize(150, 40)
        self.action_button.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        self.action_button.clicked.connect(self.toggle_drawing)
        layout.addWidget(self.action_button, 0, Qt.AlignmentFlag.AlignCenter)

        # 添加系统信息卡片区域
        layout.addSpacerItem(
            QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        )

        # 创建卡片网格布局
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)  # 设置卡片之间的间距

        # 创建CPU使用率卡片
        self.cpu_card = self._create_system_info_card("CPU使用率", "0%", [41, 128, 185])
        cards_layout.addWidget(self.cpu_card, 0, 0)

        # 创建内存使用率卡片
        self.memory_card = self._create_system_info_card("内存使用率", "0%", [52, 152, 219])
        cards_layout.addWidget(self.memory_card, 0, 1)

        # 创建运行时间卡片
        self.runtime_card = self._create_system_info_card(
            "运行时间", "00:00:00", [26, 188, 156]
        )
        cards_layout.addWidget(self.runtime_card, 1, 0)

        # 创建进程资源使用卡片
        self.process_card = self._create_system_info_card(
            "进程资源", "CPU: 0% | 内存: 0%", [155, 89, 182]
        )
        cards_layout.addWidget(self.process_card, 1, 1)

        # 将卡片网格添加到主布局
        layout.addLayout(cards_layout)

        # 底部空白间距，增加灵活性
        layout.addSpacerItem(
            QSpacerItem(
                20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        # 设置布局和大小策略
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 设置尺寸变化事件处理
        self.logger.debug("已启用自适应布局")

    def _create_system_info_card(self, title, value, color):
        """创建系统信息卡片"""
        # 使用 QFrame 替代 CardWidget
        card = QFrame()
        card.setMinimumSize(180, 120)
        card.setFrameStyle(QFrame.Shape.Box)
        
        # 设置卡片样式
        r, g, b = color[0], color[1], color[2]
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgb({r}, {g}, {b});
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                margin: 2px;
            }}
        """)

        # 创建卡片布局
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(5)

        # 添加标题标签
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)

        # 创建值标签
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: white;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)

        # 如果是CPU或内存卡片，添加进度条
        if "CPU" in title or "内存" in title:
            # 为不同卡片创建不同主题的进度条
            if "CPU" in title:
                progress_bar = create_styled_progress_bar("default")
            else:
                progress_bar = create_styled_progress_bar("memory")

            card_layout.addWidget(progress_bar)

        # 保存标签引用，以便后续更新
        card._value_label = value_label

        # 保存进度条引用（如果有）
        if "CPU" in title or "内存" in title:
            card._progress_bar = progress_bar

        return card

    def update_system_info(self, data):
        """更新系统信息显示"""
        # 更新CPU卡片
        cpu_percent = data["cpu_percent"]
        self.cpu_card._value_label.setText(f"{cpu_percent:.1f}%")
        self.cpu_card._progress_bar.setValue(int(cpu_percent))

        # 更新内存卡片
        memory_percent = data["memory_percent"]
        memory_used = format_bytes(data["memory_used"])
        memory_total = format_bytes(data["memory_total"])
        self.memory_card._value_label.setText(f"{memory_percent:.1f}%")
        self.memory_card._progress_bar.setValue(int(memory_percent))

        # 鼠标悬停时显示详细信息
        self.memory_card.setToolTip(f"已用: {memory_used} / 总计: {memory_total}")

        # 更新运行时间卡片
        self.runtime_card._value_label.setText(data["runtime"])

        # 更新进程资源卡片
        process_cpu = data["process_cpu"]
        process_memory = data["process_memory"]
        self.process_card._value_label.setText(
            f"CPU: {process_cpu:.1f}% | 内存: {process_memory:.1f}%"
        )

    def resizeEvent(self, event):
        """窗口尺寸变化事件处理，用于调整UI布局"""
        # 调用父类方法
        super().resizeEvent(event)

        # 可以在这里添加特定的尺寸调整逻辑
        self.logger.debug(f"控制台页面大小已调整: {self.width()}x{self.height()}")

    def toggle_drawing(self):
        """切换绘制状态"""
        if self.is_drawing_active:
            self.stop_drawing()
        else:
            self.start_drawing()

    def start_drawing(self):
        """开始绘制功能"""
        try:
            self.logger.info("启动绘制功能")

            # 创建绘制管理器（如果不存在）
            if not self.drawing_manager:
                self.drawing_manager = DrawingManager()

            # 开始绘制
            success = self.drawing_manager.start()

            if success:
                self.status_label.setText("绘制中 - 使用鼠标右键进行绘制")
                # 切换按钮为"停止绘制"
                self.action_button.setText("停止绘制")
                self.is_drawing_active = True

                # 更新托盘图标状态
                self.drawing_state_changed.emit(True)

                self.logger.debug("绘制功能已启动")

        except Exception as e:
            self.logger.exception(f"启动绘制功能时发生错误: {e}")
            self.status_label.setText(f"启动失败: {str(e)}")

    def stop_drawing(self):
        """停止绘制功能"""
        if self.drawing_manager and self.is_drawing_active:
            try:
                self.logger.info("停止绘制功能")

                # 停止绘制
                success = self.drawing_manager.stop()

                if success:
                    self.status_label.setText("准备就绪")
                    # 切换按钮为"开始绘制"
                    self.action_button.setText("开始绘制")
                    self.is_drawing_active = False

                    # 更新托盘图标状态
                    self.drawing_state_changed.emit(False)

                    self.logger.debug("绘制功能已停止")

            except Exception as e:
                self.logger.exception(f"停止绘制功能时发生错误: {e}")
                self.status_label.setText(f"停止失败: {str(e)}")

    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止绘制
        self.stop_drawing()

        # 停止系统监测
        if self.system_monitor:
            self.system_monitor.stop()


if __name__ == "__main__":
    # 独立运行测试
    app = QApplication(sys.argv)
    widget = ConsolePage()
    widget.show()
    sys.exit(app.exec())
