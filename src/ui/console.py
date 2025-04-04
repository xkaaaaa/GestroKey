import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QSizePolicy, QSpacerItem, QHBoxLayout, QGridLayout, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QCursor, QColor

try:
    from core.logger import get_logger
    from core.drawer import DrawingManager
    from core.system_monitor import SystemMonitor, format_bytes
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.card import CardWidget  # 导入自定义卡片组件
    from version import APP_NAME  # 导入应用名称
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger
    from core.drawer import DrawingManager
    from core.system_monitor import SystemMonitor, format_bytes
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.card import CardWidget  # 导入自定义卡片组件
    from version import APP_NAME  # 导入应用名称


# 自定义进度条类，支持动画和渐变色
class AnimatedProgressBar(QProgressBar):
    """动画进度条，支持平滑过渡和颜色渐变"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("AnimatedProgressBar")
        
        # 设置基本样式
        self.setTextVisible(False)
        self.setRange(0, 100)
        
        # 动画相关属性
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(800)  # 动画持续800毫秒
        self._animation.setEasingCurve(QEasingCurve.OutCubic)  # 平滑的减速动画效果
        
        # 颜色相关属性
        self._base_color = QColor(46, 204, 113)  # 绿色 (低使用率)
        self._mid_color = QColor(241, 196, 15)   # 黄色 (中等使用率)
        self._high_color = QColor(231, 76, 60)   # 红色 (高使用率)
        
        # 初始化样式
        self._update_style(0)
    
    def _update_style(self, value):
        """根据值更新进度条样式和颜色"""
        # 根据值计算颜色
        if value <= 50:
            # 从绿色到黄色的渐变 (0-50%)
            ratio = value / 50.0
            current_color = QColor(
                int(self._base_color.red() + (self._mid_color.red() - self._base_color.red()) * ratio),
                int(self._base_color.green() + (self._mid_color.green() - self._base_color.green()) * ratio),
                int(self._base_color.blue() + (self._mid_color.blue() - self._base_color.blue()) * ratio)
            )
        else:
            # 从黄色到红色的渐变 (50-100%)
            ratio = (value - 50) / 50.0
            current_color = QColor(
                int(self._mid_color.red() + (self._high_color.red() - self._mid_color.red()) * ratio),
                int(self._mid_color.green() + (self._high_color.green() - self._mid_color.green()) * ratio),
                int(self._mid_color.blue() + (self._high_color.blue() - self._mid_color.blue()) * ratio)
            )
        
        # 设置进度条样式
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 50);
                height: 8px;
            }}
            QProgressBar::chunk {{
                border-radius: 5px;
                background-color: {current_color.name()};
            }}
        """)
    
    def set_animated_value(self, value):
        """设置进度条值，带动画效果"""
        # 停止当前运行的动画
        self._animation.stop()
        
        # 设置新的动画
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(value)
        
        # 更新样式
        self._update_style(value)
        
        # 启动动画
        self._animation.start()
        
    def set_color_theme(self, base_color, mid_color, high_color):
        """设置进度条的颜色主题"""
        self._base_color = QColor(base_color) if isinstance(base_color, str) else QColor(*base_color)
        self._mid_color = QColor(mid_color) if isinstance(mid_color, str) else QColor(*mid_color)
        self._high_color = QColor(high_color) if isinstance(high_color, str) else QColor(*high_color)
        self._update_style(self.value())


class ConsoleTab(QWidget):
    """控制台选项卡，提供基本的绘制控制功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ConsoleTab")
        
        # 状态变量
        self.drawing_manager = None
        self.is_drawing_active = False
        
        # 系统监测器
        self.system_monitor = SystemMonitor(update_interval=1500)  # 1.5秒更新一次
        
        # 初始化UI
        self.initUI()
        
        # 连接系统监测器的信号
        self.system_monitor.dataUpdated.connect(self.update_system_info)
        
        # 启动系统监测
        self.system_monitor.start()
        
        self.logger.debug("控制台选项卡初始化完成")
    
    def initUI(self):
        """初始化用户界面"""
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)  # 改为顶部对齐，与其他选项卡一致
        
        # 顶部空白间距，增加灵活性
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # 标题标签 - 去掉APP_NAME前缀
        title_label = QLabel("控制台")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(title_label)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("font-size: 10pt; margin-bottom: 20px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.status_label)
        
        # 使用单个按钮，根据状态切换文本和颜色
        self.action_button = AnimatedButton("开始绘制", primary_color=[41, 128, 185])  # 初始为蓝色"开始绘制"按钮
        self.action_button.setMinimumSize(150, 40)
        self.action_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.action_button.clicked.connect(self.toggle_drawing)
        layout.addWidget(self.action_button, 0, Qt.AlignCenter)
        
        # 添加系统信息卡片区域
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
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
        self.runtime_card = self._create_system_info_card("运行时间", "00:00:00", [26, 188, 156])
        cards_layout.addWidget(self.runtime_card, 1, 0)
        
        # 创建进程资源使用卡片
        self.process_card = self._create_system_info_card("进程资源", "CPU: 0% | 内存: 0%", [155, 89, 182])
        cards_layout.addWidget(self.process_card, 1, 1)
        
        # 将卡片网格添加到主布局
        layout.addLayout(cards_layout)
        
        # 底部空白间距，增加灵活性
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 设置布局和大小策略
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 设置尺寸变化事件处理
        self.logger.debug("已启用自适应布局")
    
    def _create_system_info_card(self, title, value, color):
        """创建系统信息卡片"""
        card = CardWidget(title=title, primary_color=color, text_color=[255, 255, 255])
        card.setMinimumSize(180, 120)
        
        # 创建卡片内容布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)
        
        # 创建值标签
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: white;")
        value_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(value_label)
        
        # 如果是CPU或内存卡片，添加动画进度条
        if "CPU" in title or "内存" in title:
            progress_bar = AnimatedProgressBar()
            
            # 为不同卡片设置不同颜色主题
            if "CPU" in title:
                # CPU进度条使用默认的绿-黄-红主题
                pass
            else:
                # 内存进度条使用蓝色系主题
                progress_bar.set_color_theme(
                    [52, 152, 219],  # 淡蓝色 (低使用率)
                    [41, 128, 185],  # 中蓝色 (中等使用率)
                    [31, 97, 141]    # 深蓝色 (高使用率)
                )
            
            content_layout.addWidget(progress_bar)
        
        # 创建内容控件
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        
        # 将内容添加到卡片
        card.add_widget(content_widget)
        
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
        self.cpu_card._progress_bar.set_animated_value(int(cpu_percent))
        
        # 更新内存卡片
        memory_percent = data["memory_percent"]
        memory_used = format_bytes(data["memory_used"])
        memory_total = format_bytes(data["memory_total"])
        self.memory_card._value_label.setText(f"{memory_percent:.1f}%")
        self.memory_card._progress_bar.set_animated_value(int(memory_percent))
        
        # 鼠标悬停时显示详细信息
        self.memory_card.setToolTip(f"已用: {memory_used} / 总计: {memory_total}")
        
        # 更新运行时间卡片
        self.runtime_card._value_label.setText(data["runtime"])
        
        # 更新进程资源卡片
        process_cpu = data["process_cpu"]
        process_memory = data["process_memory"]
        self.process_card._value_label.setText(f"CPU: {process_cpu:.1f}% | 内存: {process_memory:.1f}%")
    
    def resizeEvent(self, event):
        """窗口尺寸变化事件处理，用于调整UI布局"""
        # 调用父类方法
        super().resizeEvent(event)
        
        # 可以在这里添加特定的尺寸调整逻辑
        self.logger.debug(f"控制台选项卡大小已调整: {self.width()}x{self.height()}")
    
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
                # 切换按钮为"停止绘制"，并改为红色
                self.action_button.setText("停止绘制")
                self.action_button.set_primary_color([220, 53, 69])  # 红色
                self.is_drawing_active = True
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
                    # 切换按钮为"开始绘制"，并改为蓝色
                    self.action_button.setText("开始绘制")
                    self.action_button.set_primary_color([41, 128, 185])  # 蓝色
                    self.is_drawing_active = False
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
    widget = ConsoleTab()
    widget.show()
    sys.exit(app.exec_()) 