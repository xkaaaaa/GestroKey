import sys
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QApplication, QFileDialog, 
                            QGroupBox, QCheckBox, QSlider, QColorDialog, QPushButton, QMessageBox,
                            QSizePolicy, QSpacerItem, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

try:
    from core.logger import get_logger
    from ui.settings.settings import get_settings
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.scrollbar import AnimatedScrollArea  # 导入自定义滚动区域
    from ui.components.slider import AnimatedSlider  # 导入自定义滑块组件
    from ui.components.color_picker import AnimatedColorPicker  # 导入自定义色彩选择器
    from ui.components.number_spinner import AnimatedNumberSpinner  # 导入自定义数字选择器
    from ui.components.toast_notification import show_info, show_error, show_warning, show_success, ensure_toast_system_initialized  # 导入Toast通知组件
    from version import APP_NAME  # 导入应用名称
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from core.logger import get_logger
    from ui.settings.settings import get_settings
    from ui.components.button import AnimatedButton  # 导入自定义动画按钮
    from ui.components.scrollbar import AnimatedScrollArea  # 导入自定义滚动区域
    from ui.components.slider import AnimatedSlider  # 导入自定义滑块组件
    from ui.components.color_picker import AnimatedColorPicker  # 导入自定义色彩选择器
    from ui.components.number_spinner import AnimatedNumberSpinner  # 导入自定义数字选择器
    from ui.components.toast_notification import show_info, show_error, show_warning, show_success, ensure_toast_system_initialized  # 导入Toast通知组件
    from version import APP_NAME  # 导入应用名称

class SettingsTab(QWidget):
    """设置选项卡，提供应用程序设置管理功能"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("SettingsTab")
        self.settings = get_settings()
        
        # 预加载通知系统
        ensure_toast_system_initialized()
        self.logger.debug("通知组件已预加载")
        
        self.initUI()
        self.logger.debug("设置选项卡初始化完成")
    
    def initUI(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # 创建滚动区域，以便在窗口较小时可以滚动查看所有设置
        # 使用自定义动画滚动区域替代标准滚动区域
        scroll_area = AnimatedScrollArea()
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建内容部件
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题标签
        title_label = QLabel("设置")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        content_layout.addWidget(title_label)
        
        # 添加顶部间距
        content_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # 绘制设置组
        drawing_group = QGroupBox("绘制设置")
        drawing_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        drawing_layout = QVBoxLayout()
        
        # 笔尖粗细设置
        pen_layout = QHBoxLayout()
        pen_label = QLabel("笔尖粗细:")
        pen_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        # 使用自定义动画滑块替代普通SpinBox
        self.pen_width_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.pen_width_slider.setRange(1, 20)
        self.pen_width_slider.setValue(self.settings.get("pen_width"))
        self.pen_width_slider.valueChanged.connect(self.pen_width_changed)
        self.pen_width_slider.setMinimumWidth(200)
        self.pen_width_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # 使用自定义数字选择器替代普通SpinBox
        self.pen_width_spinner = AnimatedNumberSpinner(
            min_value=1, 
            max_value=20, 
            step=1, 
            value=self.settings.get("pen_width"),
            primary_color=[52, 152, 219]  # 蓝色主题
        )
        self.pen_width_spinner.valueChanged.connect(self.pen_width_spinner_sync)
        self.pen_width_spinner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        pen_layout.addWidget(pen_label)
        pen_layout.addWidget(self.pen_width_slider)
        pen_layout.addWidget(self.pen_width_spinner)
        drawing_layout.addLayout(pen_layout)
        
        # 笔尖颜色设置
        color_layout = QVBoxLayout()  # 改为垂直布局
        color_label = QLabel("笔尖颜色:")
        color_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        # 使用自定义色彩选择器组件替代简单的按钮
        self.color_picker = AnimatedColorPicker()
        self.color_picker.set_color(self.settings.get("pen_color"))
        self.color_picker.colorChanged.connect(self.color_changed)
        self.color_picker.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_picker)
        drawing_layout.addLayout(color_layout)
        
        # 绘制预览框
        preview_layout = QHBoxLayout()
        preview_label = QLabel("笔尖预览:")
        preview_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        
        self.preview_widget = PenPreviewWidget(
            self.settings.get("pen_width"), 
            self.settings.get("pen_color")
        )
        self.preview_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.preview_widget)
        preview_layout.addStretch()
        drawing_layout.addLayout(preview_layout)
        
        drawing_group.setLayout(drawing_layout)
        content_layout.addWidget(drawing_group)
        
        # 添加中间间距
        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # 重置和保存按钮
        buttons_layout = QHBoxLayout()
        
        # 使用自定义动画按钮替换标准按钮
        reset_button = AnimatedButton("重置为默认设置", primary_color=[108, 117, 125])  # 灰色
        reset_button.setMinimumSize(140, 36)  # 设置最小大小而不是固定大小
        reset_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        reset_button.clicked.connect(self.reset_settings)
        
        save_button = AnimatedButton("保存设置", primary_color=[41, 128, 185])  # 蓝色
        save_button.setMinimumSize(120, 36)  # 设置最小大小而不是固定大小
        save_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        save_button.clicked.connect(self.save_settings)
        
        buttons_layout.addWidget(reset_button)
        buttons_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        buttons_layout.addWidget(save_button)
        
        content_layout.addLayout(buttons_layout)
        
        # 底部弹性空间
        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # 设置内容部件
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area)
        
        # 设置布局和大小策略
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
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
        
        # 不再立即更新绘制管理器，只在保存或重置时更新
        # self._update_drawing_manager()
    
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
        # 更新微调框
        if self.pen_width_spinner.value() != value:
            self.pen_width_spinner.setValue(value)
        
        # 更新预览
        self.preview_widget.update_width(value)
        
        # 不再立即更新绘制管理器，只在保存或重置时更新
        # self._update_drawing_manager()
    
    def pen_width_spinner_sync(self, value):
        """微调框值变化时同步滑块的值"""
        if self.pen_width_slider.value() != value:
            self.pen_width_slider.setValue(value)
            # 设置值（通过滑块的valueChanged信号间接调用pen_width_changed）
    
    def reset_settings(self):
        """重置为默认设置"""
        # 弹出确认对话框
        reply = QMessageBox.question(
            self, 
            f"{APP_NAME} - 确认重置", 
            "是否确定将所有设置重置为默认值？", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logger.info("用户选择重置所有设置为默认值")
            
            # 重置设置
            self.settings.reset_to_default()
            
            # 更新UI
            pen_width = self.settings.get("pen_width")
            pen_color = self.settings.get("pen_color")
            
            # 更新笔尖粗细控件
            self.pen_width_slider.setValue(pen_width)
            self.pen_width_spinner.setValue(pen_width)
            
            # 更新笔尖颜色
            self.color_picker.set_color(pen_color)
            
            # 更新预览
            self.preview_widget.update_width(pen_width)
            self.preview_widget.update_color(pen_color)
            
            # 更新绘制管理器
            self._update_drawing_manager()
            
            # 显示成功消息
            show_success(self, "已成功将所有设置重置为默认值。")
            self.logger.info("设置已重置为默认值")
    
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
                show_info(self, "设置未发生实际变化，无需保存")
                return True
                
            # 保存设置
            success = self.settings.save()
            
            if success:
                self.logger.info("设置已保存")
                # 应用设置到绘制管理器
                self._update_drawing_manager()
                # 显示成功消息
                show_success(self, "设置已保存并应用")
                return True
            else:
                self.logger.error("保存设置失败")
                show_warning(self, "无法保存设置")
                return False
        except Exception as e:
            self.logger.error(f"保存设置时出错: {e}")
            show_error(self, f"保存设置时出错: {str(e)}")
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
    
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        try:
            return self.settings.has_changes()
        except Exception as e:
            self.logger.error(f"检查设置更改状态时出错: {e}")
            return False


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
        from PyQt6.QtGui import QPainter, QPen, QColor
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置画笔
        r, g, b = self.pen_color[0], self.pen_color[1], self.pen_color[2]
        pen = QPen(QColor(r, g, b))
        pen.setWidth(self.pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
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
    sys.exit(app.exec()) 