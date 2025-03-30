import sys
import os
from PyQt5.QtWidgets import (QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QLabel, QApplication, QSpinBox, QFileDialog, 
                            QGroupBox, QCheckBox, QSlider)
from PyQt5.QtCore import Qt

try:
    from core.logger import get_logger
    from ui.settings.settings import get_settings
except ImportError:
    sys.path.append('../../')
    from core.logger import get_logger
    from ui.settings.settings import get_settings

class SettingsTab(QWidget):
    """设置选项卡，提供应用程序设置管理功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("SettingsTab")
        self.settings = get_settings()
        
        self.initUI()
        self.logger.debug("设置选项卡初始化完成")
    
    def initUI(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        
        # 标题标签
        title_label = QLabel("GestroKey 设置")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 绘制设置组
        drawing_group = QGroupBox("绘制设置")
        drawing_layout = QVBoxLayout()
        
        # 笔尖粗细设置
        pen_layout = QHBoxLayout()
        pen_label = QLabel("笔尖粗细:")
        self.pen_width_spinner = QSpinBox()
        self.pen_width_spinner.setRange(1, 20)
        self.pen_width_spinner.setValue(self.settings.get("pen_width"))
        self.pen_width_spinner.valueChanged.connect(self.pen_width_changed)
        
        pen_layout.addWidget(pen_label)
        pen_layout.addWidget(self.pen_width_spinner)
        pen_layout.addStretch()
        drawing_layout.addLayout(pen_layout)
        
        # 绘制预览框
        preview_layout = QHBoxLayout()
        preview_label = QLabel("笔尖预览:")
        self.preview_widget = PenPreviewWidget(self.settings.get("pen_width"))
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_widget)
        preview_layout.addStretch()
        drawing_layout.addLayout(preview_layout)
        
        drawing_group.setLayout(drawing_layout)
        main_layout.addWidget(drawing_group)
        
        # 重置和保存按钮
        buttons_layout = QHBoxLayout()
        
        reset_button = QPushButton("重置为默认设置")
        reset_button.clicked.connect(self.reset_settings)
        
        save_button = QPushButton("保存设置")
        save_button.clicked.connect(self.save_settings)
        
        buttons_layout.addWidget(reset_button)
        buttons_layout.addWidget(save_button)
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        # 设置布局
        self.setLayout(main_layout)
    
    def pen_width_changed(self, value):
        """处理笔尖粗细变化"""
        self.logger.debug(f"笔尖粗细已更改为: {value}")
        self.preview_widget.update_width(value)
        self.settings.set("pen_width", value)
        
        # 实时更新绘制管理器的参数
        self._update_drawing_manager()
    
    def reset_settings(self):
        """重置为默认设置"""
        self.logger.info("重置为默认设置")
        self.settings.reset_to_default()
        
        # 更新UI显示
        self.pen_width_spinner.setValue(self.settings.get("pen_width"))
        self.preview_widget.update_width(self.settings.get("pen_width"))
        
        # 更新绘制管理器的参数
        self._update_drawing_manager()
    
    def save_settings(self):
        """保存设置到文件"""
        self.logger.info("保存设置到文件")
        self.settings.save()
        
        # 更新绘制管理器的参数
        self._update_drawing_manager()
    
    def _update_drawing_manager(self):
        """更新绘制管理器的参数（内部方法）"""
        try:
            # 尝试获取主窗口
            main_window = self.window()
            if hasattr(main_window, 'console_tab') and main_window.console_tab:
                console_tab = main_window.console_tab
                
                # 如果console_tab有drawing_manager且处于活动状态，更新参数
                if hasattr(console_tab, 'drawing_manager') and console_tab.drawing_manager:
                    drawing_manager = console_tab.drawing_manager
                    if drawing_manager.update_settings():
                        self.logger.debug("已更新绘制管理器参数")
                    else:
                        self.logger.warning("更新绘制管理器参数失败")
        except Exception as e:
            self.logger.error(f"尝试更新绘制管理器参数时发生错误: {e}")


class PenPreviewWidget(QWidget):
    """笔尖预览小部件"""
    
    def __init__(self, width=3, parent=None):
        super().__init__(parent)
        self.pen_width = width
        self.setFixedSize(100, 50)
    
    def update_width(self, width):
        """更新笔尖粗细"""
        self.pen_width = width
        self.update()  # 触发重绘
    
    def paintEvent(self, event):
        """绘制预览"""
        import math
        from PyQt5.QtGui import QPainter, QPen, QColor
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置画笔
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(self.pen_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # 绘制正弦波来展示笔尖效果
        w = self.width()
        h = self.height()
        mid_y = int(h / 2)  # 将浮点数转换为整数
        
        # 绘制水平线
        painter.drawLine(10, mid_y, w - 10, mid_y)
        
        # 绘制两端的圆点
        painter.drawPoint(10, mid_y)
        painter.drawPoint(w - 10, mid_y)


if __name__ == "__main__":
    # 独立运行测试
    app = QApplication(sys.argv)
    widget = SettingsTab()
    widget.show()
    sys.exit(app.exec_()) 