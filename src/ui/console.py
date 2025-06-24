import os

from qtpy.QtCore import QSize, Qt, Signal
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget
)

from core.brush.manager import DrawingManager
from core.logger import get_logger
from core.system_monitor import SystemMonitor, format_bytes


def create_styled_progress_bar(color_theme="default"):
    progress_bar = QProgressBar()
    progress_bar.setTextVisible(False)
    progress_bar.setRange(0, 100)
    
    chunk_color = "#3498db" if color_theme == "memory" else "#2ecc71"
    progress_bar.setStyleSheet(f"""
        QProgressBar {{
            border: none;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 50);
            height: 8px;
        }}
        QProgressBar::chunk {{
            border-radius: 5px;
            background-color: {chunk_color};
        }}
    """)
    
    return progress_bar


class ConsolePage(QWidget):
    drawing_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ConsolePage")

        self.drawing_manager = None
        self.is_drawing_active = False

        self.system_monitor = SystemMonitor(update_interval=1500)
        self._assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "ui")

        self._setup_ui()

        self.system_monitor.dataUpdated.connect(self.update_system_info)
        self.system_monitor.start()

    def _get_icon_path(self, icon_name):
        icon_path = os.path.join(self._assets_dir, icon_name)
        return icon_path if os.path.exists(icon_path) else None

    def _set_button_icon(self, button, icon_name, size=(24, 24)):
        icon_path = self._get_icon_path(icon_name)
        if icon_path:
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(*size))

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        title_label = QLabel("控制台")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(title_label)

        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("font-size: 10pt; margin-bottom: 20px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.status_label)

        self.action_button = QPushButton("开始绘制")
        self.action_button.setMinimumSize(150, 40)
        self.action_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.action_button.clicked.connect(self.toggle_drawing)
        self._set_button_icon(self.action_button, "start-drawing.svg")
        layout.addWidget(self.action_button, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)

        self.cpu_card = self._create_system_info_card("CPU使用率", "0%", [41, 128, 185])
        cards_layout.addWidget(self.cpu_card, 0, 0)

        self.memory_card = self._create_system_info_card("内存使用率", "0%", [52, 152, 219])
        cards_layout.addWidget(self.memory_card, 0, 1)

        self.runtime_card = self._create_system_info_card("运行时间", "00:00:00", [26, 188, 156])
        cards_layout.addWidget(self.runtime_card, 1, 0)

        self.process_card = self._create_system_info_card("进程资源", "CPU: 0% | 内存: 0%", [155, 89, 182])
        cards_layout.addWidget(self.process_card, 1, 1)

        layout.addLayout(cards_layout)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _create_system_info_card(self, title, value, color):
        card = QFrame()
        card.setMinimumSize(180, 120)
        
        r, g, b = color[0], color[1], color[2]
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgb({r}, {g}, {b});
                border-radius: 8px;
                margin: 2px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: white;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(value_label)

        if "CPU" in title or "内存" in title:
            if "CPU" in title:
                progress_bar = create_styled_progress_bar("default")
            else:
                progress_bar = create_styled_progress_bar("memory")
            card_layout.addWidget(progress_bar)

        card._value_label = value_label

        if "CPU" in title or "内存" in title:
            card._progress_bar = progress_bar

        return card

    def update_system_info(self, data):
        cpu_percent = data["cpu_percent"]
        self.cpu_card._value_label.setText(f"{cpu_percent:.1f}%")
        self.cpu_card._progress_bar.setValue(int(cpu_percent))

        memory_percent = data["memory_percent"]
        memory_used = format_bytes(data["memory_used"])
        memory_total = format_bytes(data["memory_total"])
        self.memory_card._value_label.setText(f"{memory_percent:.1f}%")
        self.memory_card._progress_bar.setValue(int(memory_percent))

        self.memory_card.setToolTip(f"已用: {memory_used} / 总计: {memory_total}")

        self.runtime_card._value_label.setText(data["runtime"])

        process_cpu = data["process_cpu"]
        process_memory = data["process_memory"]
        self.process_card._value_label.setText(f"CPU: {process_cpu:.1f}% | 内存: {process_memory:.1f}%")

    def toggle_drawing(self):
        if self.is_drawing_active:
            self.stop_drawing()
        else:
            self.start_drawing()

    def start_drawing(self):
        try:
            if not self.drawing_manager:
                self.drawing_manager = DrawingManager()

            success = self.drawing_manager.start()

            if success:
                self.status_label.setText("绘制中 - 使用鼠标右键进行绘制")
                self.action_button.setText("停止绘制")
                self._set_button_icon(self.action_button, "stop-drawing.svg")
                self.is_drawing_active = True
                self.drawing_state_changed.emit(True)

        except Exception as e:
            self.logger.exception(f"启动绘制功能时发生错误: {e}")
            self.status_label.setText(f"启动失败: {str(e)}")

    def stop_drawing(self):
        if self.drawing_manager and self.is_drawing_active:
            try:
                success = self.drawing_manager.stop()

                if success:
                    self.status_label.setText("准备就绪")
                    self.action_button.setText("开始绘制")
                    self._set_button_icon(self.action_button, "start-drawing.svg")
                    self.is_drawing_active = False
                    self.drawing_state_changed.emit(False)

            except Exception as e:
                self.logger.exception(f"停止绘制功能时发生错误: {e}")
                self.status_label.setText(f"停止失败: {str(e)}")

    def closeEvent(self, event):
        self.stop_drawing()

        if self.system_monitor:
            self.system_monitor.stop()