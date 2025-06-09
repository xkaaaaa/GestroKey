import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QRadioButton,
    QButtonGroup,
)

try:
    from core.logger import get_logger
    from ui.settings.settings import get_settings
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger
    from ui.settings.settings import get_settings


class SettingsPage(QWidget):
    """设置页面 - 重新设计版本"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("SettingsPage")
        self.settings = get_settings()
        
        # 状态变量
        self.is_loading = False
        
        self._init_ui()
        self._load_settings()
        self.logger.info("设置页面初始化完成")

    def _init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("设置")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # 设置内容
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # 画笔设置组
        brush_group = self._create_brush_settings_group()
        content_layout.addWidget(brush_group)

        # 应用设置组
        app_group = self._create_app_settings_group()
        content_layout.addWidget(app_group)

        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # 底部按钮
        button_layout = self._create_button_layout()
        main_layout.addLayout(button_layout)

    def _create_brush_settings_group(self):
        """创建画笔设置组"""
        group = QGroupBox("画笔设置")
        layout = QVBoxLayout(group)

        form_layout = QFormLayout()

        # 笔尖粗细
        thickness_layout = QHBoxLayout()
        
        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.thickness_slider.setRange(1, 20)
        self.thickness_slider.setMinimumWidth(200)
        self.thickness_slider.valueChanged.connect(self._on_thickness_changed)
        
        self.thickness_spinbox = QSpinBox()
        self.thickness_spinbox.setRange(1, 20)
        self.thickness_spinbox.setMinimumWidth(60)
        self.thickness_spinbox.valueChanged.connect(self._on_thickness_spinbox_changed)
        
        thickness_layout.addWidget(self.thickness_slider)
        thickness_layout.addWidget(self.thickness_spinbox)
        
        form_layout.addRow("笔尖粗细:", thickness_layout)

        # 笔尖颜色
        color_layout = QHBoxLayout()
        
        self.color_button = QPushButton("选择颜色")
        self.color_button.setMinimumSize(100, 30)
        self.color_button.clicked.connect(self._on_color_button_clicked)
        
        self.color_preview = ColorPreviewWidget()
        self.color_preview.setMinimumSize(100, 30)
        
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()
        
        form_layout.addRow("笔尖颜色:", color_layout)

        layout.addLayout(form_layout)

        # 预览区域
        preview_layout = QVBoxLayout()
        preview_label = QLabel("预览:")
        preview_layout.addWidget(preview_label)
        
        self.pen_preview = PenPreviewWidget()
        self.pen_preview.setMinimumHeight(80)
        preview_layout.addWidget(self.pen_preview)
        
        layout.addLayout(preview_layout)

        return group

    def _create_app_settings_group(self):
        """创建应用设置组"""
        group = QGroupBox("应用设置")
        layout = QFormLayout(group)

        # 开机自启动
        self.autostart_checkbox = QCheckBox("开机自启动")
        self.autostart_checkbox.setToolTip("设置应用程序是否在系统启动时自动运行（将以静默模式启动，自动开始监听并最小化到托盘）")
        self.autostart_checkbox.stateChanged.connect(self._on_autostart_changed)
        layout.addRow("启动选项:", self.autostart_checkbox)

        # 退出确认对话框
        self.show_exit_dialog_checkbox = QCheckBox("显示退出确认对话框")
        self.show_exit_dialog_checkbox.setToolTip("关闭程序时是否显示确认对话框")
        self.show_exit_dialog_checkbox.stateChanged.connect(self._on_exit_dialog_changed)
        layout.addRow("退出行为:", self.show_exit_dialog_checkbox)

        # 默认关闭行为
        close_behavior_layout = QVBoxLayout()
        
        self.close_behavior_group = QButtonGroup()
        self.minimize_radio = QRadioButton("最小化到托盘")
        self.exit_radio = QRadioButton("退出程序")
        
        self.close_behavior_group.addButton(self.minimize_radio, 0)
        self.close_behavior_group.addButton(self.exit_radio, 1)
        
        self.minimize_radio.toggled.connect(self._on_close_behavior_changed)
        self.exit_radio.toggled.connect(self._on_close_behavior_changed)
        
        close_behavior_layout.addWidget(self.minimize_radio)
        close_behavior_layout.addWidget(self.exit_radio)
        
        close_behavior_widget = QWidget()
        close_behavior_widget.setLayout(close_behavior_layout)
        close_behavior_widget.setToolTip("当不显示退出对话框时的默认行为")
        
        layout.addRow("默认关闭行为:", close_behavior_widget)

        # 手势相似度阈值
        threshold_layout = QHBoxLayout()
        
        self.threshold_spinbox = QDoubleSpinBox()
        self.threshold_spinbox.setRange(0.0, 1.0)
        self.threshold_spinbox.setSingleStep(0.05)
        self.threshold_spinbox.setDecimals(2)
        self.threshold_spinbox.setValue(0.7)
        self.threshold_spinbox.setMinimumWidth(80)
        self.threshold_spinbox.setToolTip("手势识别的相似度阈值，值越高要求越严格")
        self.threshold_spinbox.valueChanged.connect(self._on_threshold_changed)
        
        threshold_layout.addWidget(self.threshold_spinbox)
        threshold_layout.addStretch()
        
        threshold_widget = QWidget()
        threshold_widget.setLayout(threshold_layout)
        
        layout.addRow("手势相似度阈值:", threshold_widget)

        return group

    def _create_button_layout(self):
        """创建底部按钮布局"""
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.reset_button = QPushButton("重置为默认")
        self.reset_button.setMinimumSize(120, 35)
        self.reset_button.clicked.connect(self._reset_settings)
        
        self.save_button = QPushButton("保存设置")
        self.save_button.setMinimumSize(100, 35)
        self.save_button.clicked.connect(self._save_settings)

        layout.addWidget(self.reset_button)
        layout.addStretch()
        layout.addWidget(self.save_button)

        return layout

    def _load_settings(self):
        """从设置中加载数据"""
        self.is_loading = True
        
        try:
            pen_width = self.settings.get("pen_width", 3)
            pen_color = self.settings.get("pen_color", [0, 120, 255])
            
            self.thickness_slider.setValue(pen_width)
            self.thickness_spinbox.setValue(pen_width)
            
            self.color_preview.set_color(pen_color)
            self.pen_preview.update_pen(pen_width, pen_color)
            
            is_autostart = self.settings.is_autostart_enabled()
            self.autostart_checkbox.setChecked(is_autostart)
            
            # 加载应用设置
            show_exit_dialog = self.settings.get("app.show_exit_dialog", True)
            self.show_exit_dialog_checkbox.setChecked(show_exit_dialog)
            
            default_close_action = self.settings.get("app.default_close_action", "minimize")
            if default_close_action == "minimize":
                self.minimize_radio.setChecked(True)
            else:
                self.exit_radio.setChecked(True)
            
            # 加载手势相似度阈值
            threshold = self.settings.get("gesture.similarity_threshold", 0.70)
            self.threshold_spinbox.setValue(threshold)
            
            self.logger.debug("设置已加载到界面")
            
        except Exception as e:
            self.logger.error(f"加载设置失败: {e}")
            QMessageBox.critical(self, "错误", f"加载设置失败: {str(e)}")
        finally:
            self.is_loading = False
            self._update_button_states()

    def _on_thickness_changed(self, value):
        """笔尖粗细滑块变化"""
        if self.is_loading:
            return
            
        if self.thickness_spinbox.value() != value:
            self.thickness_spinbox.setValue(value)
        
        color = self.color_preview.get_color()
        self.pen_preview.update_pen(value, color)
        
        # 只在视觉上预览，不立即应用到后端
        self._mark_changed()

    def _on_thickness_spinbox_changed(self, value):
        """笔尖粗细数字框变化"""
        if self.is_loading:
            return
            
        if self.thickness_slider.value() != value:
            self.thickness_slider.setValue(value)
        
        # 只在视觉上预览，不立即应用到后端
        self._mark_changed()

    def _on_color_button_clicked(self):
        """颜色按钮点击"""
        current_color = QColor(*self.color_preview.get_color())
        color = QColorDialog.getColor(current_color, self, "选择笔尖颜色")
        
        if color.isValid():
            rgb = [color.red(), color.green(), color.blue()]
            self.color_preview.set_color(rgb)
            
            thickness = self.thickness_slider.value()
            self.pen_preview.update_pen(thickness, rgb)
            
            # 只在视觉上预览，不立即应用到后端
            self._mark_changed()

    def _on_autostart_changed(self, state):
        """开机自启状态变化"""
        if not self.is_loading:
            self._mark_changed()

    def _on_exit_dialog_changed(self, state):
        """退出对话框设置变化"""
        if not self.is_loading:
            self._mark_changed()

    def _on_close_behavior_changed(self):
        """默认关闭行为变化"""
        if not self.is_loading:
            self._mark_changed()

    def _on_threshold_changed(self, value):
        """手势相似度阈值变化"""
        if not self.is_loading:
            self._mark_changed()

    def _mark_changed(self):
        """标记设置已更改"""
        if not self.is_loading:
            self._update_button_states()

    def _has_frontend_changes(self):
        """检查前端UI是否有未应用的更改"""
        try:
            # 检查笔刷设置
            current_thickness = self.thickness_slider.value()
            current_color = self.color_preview.get_color()
            
            saved_thickness = self.settings.get("brush.pen_width", 3)
            saved_color = self.settings.get("brush.pen_color", [0, 120, 255])
            
            if current_thickness != saved_thickness:
                self.logger.debug(f"笔尖粗细有变化: {current_thickness} != {saved_thickness}")
                return True
                
            if current_color != saved_color:
                self.logger.debug(f"笔尖颜色有变化: {current_color} != {saved_color}")
                return True
            
            # 检查应用设置
            current_autostart = self.autostart_checkbox.isChecked()
            saved_autostart = self.settings.is_autostart_enabled()
            
            if current_autostart != saved_autostart:
                self.logger.debug(f"开机自启动有变化: {current_autostart} != {saved_autostart}")
                return True
            
            current_show_exit_dialog = self.show_exit_dialog_checkbox.isChecked()
            saved_show_exit_dialog = self.settings.get("app.show_exit_dialog", True)
            
            if current_show_exit_dialog != saved_show_exit_dialog:
                self.logger.debug(f"退出对话框设置有变化: {current_show_exit_dialog} != {saved_show_exit_dialog}")
                return True
            
            current_close_action = "minimize" if self.minimize_radio.isChecked() else "exit"
            saved_close_action = self.settings.get("app.default_close_action", "exit")
            
            if current_close_action != saved_close_action:
                self.logger.debug(f"默认关闭行为有变化: {current_close_action} != {saved_close_action}")
                return True
            
            # 检查手势相似度阈值
            current_threshold = self.threshold_spinbox.value()
            saved_threshold = self.settings.get("gesture.similarity_threshold", 0.70)
            
            if current_threshold != saved_threshold:
                self.logger.debug(f"手势相似度阈值有变化: {current_threshold} != {saved_threshold}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"检查前端更改时出错: {e}")
            return False

    def _update_button_states(self):
        """更新按钮状态"""
        # 检查是否有未保存的更改
        has_changes = self._has_frontend_changes() or self.settings.has_changes()
        self.save_button.setEnabled(has_changes)

    def _apply_pen_settings_to_drawing_module(self, width, color):
        """实时应用画笔设置到绘制模块"""
        try:
            self.settings.set("pen_width", width)
            self.settings.set("pen_color", color)
            
            main_window = self._find_main_window()
            if main_window and hasattr(main_window, 'console_page'):
                console_page = main_window.console_page
                if hasattr(console_page, 'drawing_manager') and console_page.drawing_manager:
                    console_page.drawing_manager.update_settings()
                    self.logger.debug(f"已实时更新画笔设置: 粗细={width}, 颜色={color}")
            
        except Exception as e:
            self.logger.error(f"应用画笔设置失败: {e}")

    def _find_main_window(self):
        """查找主窗口"""
        widget = self
        while widget:
            if hasattr(widget, 'console_page'):
                return widget
            widget = widget.parent()
        return None

    def _apply_settings(self):
        """应用当前设置"""
        try:
            thickness = self.thickness_slider.value()
            color = self.color_preview.get_color()
            self._apply_pen_settings_to_drawing_module(thickness, color)
            
            is_autostart = self.autostart_checkbox.isChecked()
            current_autostart = self.settings.is_autostart_enabled()
            
            if is_autostart != current_autostart:
                success = self.settings.set_autostart(is_autostart)
                if success:
                    self.logger.info(f"开机自启动设置已更新: {is_autostart}")
                else:
                    QMessageBox.warning(self, "警告", "更新开机自启动设置失败")
            
            # 应用应用设置
            show_exit_dialog = self.show_exit_dialog_checkbox.isChecked()
            self.settings.set("app.show_exit_dialog", show_exit_dialog)
            
            default_close_action = "minimize" if self.minimize_radio.isChecked() else "exit"
            self.settings.set("app.default_close_action", default_close_action)
            
            # 应用手势相似度阈值
            threshold = self.threshold_spinbox.value()
            self.settings.set("gesture.similarity_threshold", threshold)
            
            self._update_button_states()
            QMessageBox.information(self, "成功", "设置已应用")
            
        except Exception as e:
            self.logger.error(f"应用设置失败: {e}")
            QMessageBox.critical(self, "错误", f"应用设置失败: {str(e)}")



    def _save_settings(self):
        """应用并保存设置到文件"""
        try:
            # 先应用所有设置
            thickness = self.thickness_slider.value()
            color = self.color_preview.get_color()
            self._apply_pen_settings_to_drawing_module(thickness, color)
            
            is_autostart = self.autostart_checkbox.isChecked()
            current_autostart = self.settings.is_autostart_enabled()
            
            if is_autostart != current_autostart:
                success = self.settings.set_autostart(is_autostart)
                if not success:
                    QMessageBox.warning(self, "警告", "更新开机自启动设置失败")
                    return
            
            # 应用应用设置
            show_exit_dialog = self.show_exit_dialog_checkbox.isChecked()
            self.settings.set("app.show_exit_dialog", show_exit_dialog)
            
            default_close_action = "minimize" if self.minimize_radio.isChecked() else "exit"
            self.settings.set("app.default_close_action", default_close_action)
            
            # 应用手势相似度阈值
            threshold = self.threshold_spinbox.value()
            self.settings.set("gesture.similarity_threshold", threshold)
            
            # 保存到文件
            success = self.settings.save()
            if success:
                QMessageBox.information(self, "成功", "设置已保存")
                self.logger.info("设置已保存到文件")
            else:
                QMessageBox.critical(self, "错误", "保存设置失败")
                
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")

    def _reset_settings(self):
        result = QMessageBox.question(
            self, "确认重置", 
            "确定要将所有设置重置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            try:
                success = self.settings.reset_to_default()
                if success:
                    self._load_settings()
                    
                    # 重置后需要应用画笔设置到绘制模块
                    thickness = self.thickness_slider.value()
                    color = self.color_preview.get_color()
                    self._apply_pen_settings_to_drawing_module(thickness, color)
                    
                    QMessageBox.information(self, "成功", "设置已重置为默认值")
                    self.logger.info("设置已重置为默认值")
                else:
                    QMessageBox.critical(self, "错误", "重置设置失败")
            except Exception as e:
                self.logger.error(f"重置设置失败: {e}")
                QMessageBox.critical(self, "错误", f"重置设置失败: {str(e)}")

    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        has_frontend_changes = self._has_frontend_changes()
        has_backend_changes = self.settings.has_changes()
        total_changes = has_frontend_changes or has_backend_changes
        
        self.logger.debug(f"设置页面检查未保存更改: 前端变化={has_frontend_changes}, 后端变化={has_backend_changes}, 总变化={total_changes}")
        return total_changes


class ColorPreviewWidget(QWidget):
    """颜色预览控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = [0, 120, 255]
        self.setMinimumSize(50, 30)

    def set_color(self, color):
        """设置颜色"""
        self.color = color[:]
        self.update()

    def get_color(self):
        """获取颜色"""
        return self.color[:]

    def paintEvent(self, event):
        """绘制颜色预览"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setPen(QPen(QColor(128, 128, 128), 1))
        painter.setBrush(QColor(*self.color))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)


class PenPreviewWidget(QWidget):
    """笔尖预览控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pen_width = 3
        self.pen_color = [0, 120, 255]
        self.setMinimumHeight(60)

    def update_pen(self, width, color):
        """更新笔尖参数"""
        self.pen_width = width
        self.pen_color = color[:]
        self.update()

    def paintEvent(self, event):
        """绘制笔尖预览"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        pen = QPen(QColor(*self.pen_color))
        pen.setWidth(self.pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        y = self.height() // 2
        start_x = 20
        end_x = self.width() - 20
        
        if end_x > start_x:
            import math
            points = []
            for x in range(start_x, end_x, 2):
                wave_y = y + int(10 * math.sin((x - start_x) * 0.1))
                points.append((x, wave_y))
            
            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        
        painter.setPen(QPen(QColor(60, 60, 60)))
        info_text = f"粗细: {self.pen_width}px  颜色: RGB({self.pen_color[0]}, {self.pen_color[1]}, {self.pen_color[2]})"
        painter.drawText(10, self.height() - 5, info_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SettingsPage()
    widget.show()
    sys.exit(app.exec())
