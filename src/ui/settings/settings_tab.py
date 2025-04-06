import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QApplication, QSpinBox, QFileDialog, 
                            QGroupBox, QCheckBox, QSlider, QColorDialog, QPushButton, QMessageBox,
                            QSizePolicy, QSpacerItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

try:
    from core.logger import get_logger
    from ui.settings.settings import get_settings
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.scrollbar import AnimatedScrollArea  # 导入自定义滚动区域
    from ui.components.slider import AnimatedSlider  # 导入自定义滑块组件
    from ui.components.color_picker import AnimatedColorPicker  # 导入自定义色彩选择器
    from version import APP_NAME  # 导入应用名称
except ImportError:
    sys.path.append('../../')
    from core.logger import get_logger
    from ui.settings.settings import get_settings
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.scrollbar import AnimatedScrollArea  # 导入自定义滚动区域
    from ui.components.slider import AnimatedSlider  # 导入自定义滑块组件
    from ui.components.color_picker import AnimatedColorPicker  # 导入自定义色彩选择器
    from version import APP_NAME  # 导入应用名称

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
        
        # 创建滚动区域，以便在窗口较小时可以滚动查看所有设置
        # 使用自定义动画滚动区域替代标准滚动区域
        scroll_area = AnimatedScrollArea()
        scroll_area.setFrameShape(AnimatedScrollArea.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建内容部件
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题标签
        title_label = QLabel("设置")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        content_layout.addWidget(title_label)
        
        # 添加顶部间距
        content_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # 绘制设置组
        drawing_group = QGroupBox("绘制设置")
        drawing_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        drawing_layout = QVBoxLayout()
        
        # 笔尖粗细设置
        pen_layout = QHBoxLayout()
        pen_label = QLabel("笔尖粗细:")
        pen_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        # 使用自定义动画滑块替代普通SpinBox
        self.pen_width_slider = AnimatedSlider(Qt.Horizontal)
        self.pen_width_slider.setRange(1, 20)
        self.pen_width_slider.setValue(self.settings.get("pen_width"))
        self.pen_width_slider.valueChanged.connect(self.pen_width_changed)
        self.pen_width_slider.setMinimumWidth(200)
        self.pen_width_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # 保留SpinBox，与滑块配合使用
        self.pen_width_spinner = QSpinBox()
        self.pen_width_spinner.setRange(1, 20)
        self.pen_width_spinner.setValue(self.settings.get("pen_width"))
        self.pen_width_spinner.valueChanged.connect(self.pen_width_slider_sync)
        self.pen_width_spinner.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        pen_layout.addWidget(pen_label)
        pen_layout.addWidget(self.pen_width_slider)
        pen_layout.addWidget(self.pen_width_spinner)
        drawing_layout.addLayout(pen_layout)
        
        # 笔尖颜色设置
        color_layout = QVBoxLayout()  # 改为垂直布局
        color_label = QLabel("笔尖颜色:")
        color_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        # 使用自定义色彩选择器组件替代简单的按钮
        self.color_picker = AnimatedColorPicker()
        self.color_picker.set_color(self.settings.get("pen_color"))
        self.color_picker.colorChanged.connect(self.color_changed)
        self.color_picker.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_picker)
        drawing_layout.addLayout(color_layout)
        
        # 绘制预览框
        preview_layout = QHBoxLayout()
        preview_label = QLabel("笔尖预览:")
        preview_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        self.preview_widget = PenPreviewWidget(
            self.settings.get("pen_width"), 
            self.settings.get("pen_color")
        )
        self.preview_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_widget)
        preview_layout.addStretch()
        drawing_layout.addLayout(preview_layout)
        
        drawing_group.setLayout(drawing_layout)
        content_layout.addWidget(drawing_group)
        
        # 添加中间间距
        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # 重置和保存按钮
        buttons_layout = QHBoxLayout()
        
        # 使用自定义动画按钮替换标准按钮
        reset_button = AnimatedButton("重置为默认设置", primary_color=[108, 117, 125])  # 灰色
        reset_button.setMinimumSize(140, 36)  # 设置最小大小而不是固定大小
        reset_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        reset_button.clicked.connect(self.reset_settings)
        
        save_button = AnimatedButton("保存设置", primary_color=[41, 128, 185])  # 蓝色
        save_button.setMinimumSize(120, 36)  # 设置最小大小而不是固定大小
        save_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        save_button.clicked.connect(self.save_settings)
        
        buttons_layout.addWidget(reset_button)
        buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        buttons_layout.addWidget(save_button)
        
        content_layout.addLayout(buttons_layout)
        
        # 底部弹性空间
        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 设置内容部件
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area)
        
        # 设置布局和大小策略
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 记录自适应布局启用
        self.logger.debug("设置选项卡自适应布局已启用")
    
    def resizeEvent(self, event):
        """窗口尺寸变化事件处理，用于调整UI布局"""
        # 调用父类方法
        super().resizeEvent(event)
        
        # 记录窗口大小变化
        self.logger.debug(f"设置选项卡大小已调整: {self.width()}x{self.height()}")
    
    def color_changed(self, color):
        """处理颜色变化事件"""
        self.logger.debug(f"设置笔尖颜色: RGB({color[0]}, {color[1]}, {color[2]})")
        self.settings.set("pen_color", color)
        self.preview_widget.update_color(color)
        
        # 更新绘制管理器
        self._update_drawing_manager()
        
    def show_color_dialog(self):
        """
        废弃的方法，使用AnimatedColorPicker替代
        保留此方法是为了兼容性，避免调用错误
        """
        self.logger.debug("show_color_dialog方法已废弃，使用AnimatedColorPicker替代")
        pass
    
    def pen_width_changed(self, value):
        """笔尖粗细变化时的回调"""
        self.logger.debug(f"设置笔尖粗细: {value}")
        self.settings.set("pen_width", value)
        self.preview_widget.update_width(value)
        
        # 同步微调框的值
        if self.pen_width_spinner.value() != value:
            self.pen_width_spinner.setValue(value)
            
        # 更新绘制管理器
        self._update_drawing_manager()
        
    def pen_width_slider_sync(self, value):
        """微调框值变化时同步滑块的值"""
        if self.pen_width_slider.value() != value:
            self.pen_width_slider.setValue(value)
    
    def reset_settings(self):
        """重置为默认设置"""
        self.logger.info("重置为默认设置")
        self.settings.reset_to_default()
        
        # 更新UI显示
        self.pen_width_spinner.setValue(self.settings.get("pen_width"))
        self.preview_widget.update_width(self.settings.get("pen_width"))
        
        # 更新颜色按钮和预览
        color = self.settings.get("pen_color")
        self.color_picker.set_color(color)
        self.preview_widget.update_color(color)
        
        # 保存设置并应用
        if self.settings.save():
            self._update_drawing_manager()
            self.logger.info("默认设置已保存并应用")
            QMessageBox.information(self, "重置成功", "已重置为默认设置并应用")
        else:
            self.logger.error("保存默认设置失败")
            QMessageBox.warning(self, "重置失败", "无法保存默认设置")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 获取设置值
            pen_width = self.pen_width_spinner.value()
            
            # 直接从preview_widget获取颜色值
            pen_color = self.preview_widget.pen_color
            
            # 确保设置值更新
            self.settings.set("pen_width", pen_width)
            self.settings.set("pen_color", pen_color)
            
            # 检查是否真的有改变需要保存
            if not self.settings.has_changes():
                self.logger.info("设置未发生实际变化，无需保存")
                QMessageBox.information(self, "无需保存", "设置未发生实际变化，无需保存")
                return True
                
            # 保存设置
            success = self.settings.save()
            
            if success:
                self.logger.info("设置已保存")
                # 应用设置到绘制管理器
                self._update_drawing_manager()
                # 显示成功消息
                QMessageBox.information(self, "保存成功", "设置已保存并应用")
                return True
            else:
                self.logger.error("保存设置失败")
                QMessageBox.warning(self, "保存失败", "无法保存设置")
                return False
        except Exception as e:
            self.logger.error(f"保存设置时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存设置时出错: {str(e)}")
            return False
    
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
    
    def __init__(self, width=3, color=[0, 120, 255], parent=None):
        super().__init__(parent)
        self.pen_width = width
        self.pen_color = color
        self.setFixedSize(100, 50)
    
    def update_width(self, width):
        """更新笔尖粗细"""
        self.pen_width = width
        self.update()  # 触发重绘
    
    def update_color(self, color):
        """更新笔尖颜色"""
        self.pen_color = color
        self.update()  # 触发重绘
    
    def paintEvent(self, event):
        """绘制预览"""
        import math
        from PyQt5.QtGui import QPainter, QPen, QColor
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置画笔
        r, g, b = self.pen_color[0], self.pen_color[1], self.pen_color[2]
        pen = QPen(QColor(r, g, b))
        pen.setWidth(self.pen_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # 绘制水平线
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