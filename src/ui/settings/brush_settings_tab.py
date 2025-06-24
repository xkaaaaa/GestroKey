"""
画笔设置选项卡

处理笔尖粗细、颜色、画笔类型等画笔相关设置
"""

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor, QPainter, QPen
from qtpy.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QRadioButton,
    QButtonGroup,
)

from core.logger import get_logger
from ui.settings.settings import get_settings
from .pen_preview_widget import PenPreviewWidget


class ColorPreviewWidget(QWidget):
    """颜色预览控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = [0, 120, 255]
        self.setMinimumSize(50, 30)

    def set_color(self, color):
        self.color = color[:]
        self.update()

    def get_color(self):
        return self.color[:]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setPen(QPen(QColor(128, 128, 128), 1))
        painter.setBrush(QColor(*self.color))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)


class BrushSettingsTab(QWidget):
    """画笔设置选项卡"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("BrushSettingsTab")
        self.settings = get_settings()
        self.is_loading = False
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()

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

        brush_type_layout = QHBoxLayout()
        
        self.brush_type_group = QButtonGroup()
        self.pencil_radio = QRadioButton("铅笔")
        self.water_radio = QRadioButton("水性笔")
        self.calligraphy_radio = QRadioButton("毛笔")
        
        self.brush_type_group.addButton(self.pencil_radio, 0)
        self.brush_type_group.addButton(self.water_radio, 1)
        self.brush_type_group.addButton(self.calligraphy_radio, 2)
        
        self.pencil_radio.toggled.connect(self._on_brush_type_changed)
        self.water_radio.toggled.connect(self._on_brush_type_changed)
        self.calligraphy_radio.toggled.connect(self._on_brush_type_changed)
        
        brush_type_layout.addWidget(self.pencil_radio)
        brush_type_layout.addWidget(self.water_radio)
        brush_type_layout.addWidget(self.calligraphy_radio)
        brush_type_layout.addStretch()
        
        brush_type_widget = QWidget()
        brush_type_widget.setLayout(brush_type_layout)
        brush_type_widget.setToolTip("选择画笔类型：铅笔为传统绘制效果，水性笔的线条会由细变粗，毛笔模拟书法效果")
        
        form_layout.addRow("画笔类型:", brush_type_widget)

        self.force_topmost_checkbox = QCheckBox("绘制时强制置顶")
        self.force_topmost_checkbox.setToolTip("开启后在绘制路径过程中会重复执行置顶命令，确保绘画窗口始终保持在最前面")
        self.force_topmost_checkbox.stateChanged.connect(self._on_force_topmost_changed)
        form_layout.addRow("绘制行为:", self.force_topmost_checkbox)

        layout.addLayout(form_layout)

        preview_layout = QVBoxLayout()
        preview_label = QLabel("预览:")
        preview_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
        preview_layout.addWidget(preview_label)
        
        self.pen_preview = PenPreviewWidget()
        self.pen_preview.setMinimumHeight(150)
        self.pen_preview.setMaximumHeight(300)
        preview_layout.addWidget(self.pen_preview)
        
        layout.addLayout(preview_layout)
        
        layout.addStretch()
    
    def _load_settings(self):
        self.is_loading = True
        try:
            pen_width = self.settings.get("brush.pen_width", 3)
            pen_color = self.settings.get("brush.pen_color", [0, 120, 255])
            brush_type = self.settings.get("brush.brush_type", "pencil")
            force_topmost = self.settings.get("brush.force_topmost", True)
            
            self.thickness_slider.setValue(pen_width)
            self.thickness_spinbox.setValue(pen_width)
            
            self.color_preview.set_color(pen_color)
            
            if brush_type == "water":
                self.water_radio.setChecked(True)
            elif brush_type == "calligraphy":
                self.calligraphy_radio.setChecked(True)
            else:
                self.pencil_radio.setChecked(True)
            
            self.pen_preview.update_pen(pen_width, pen_color, brush_type)
            
            self.force_topmost_checkbox.setChecked(force_topmost)
                
        except Exception as e:
            self.logger.error(f"加载画笔设置失败: {e}")
        finally:
            self.is_loading = False
    
    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'pen_preview'):
            self.pen_preview._start_animation()

    def _on_thickness_changed(self, value):
        if self.is_loading:
            return
            
        if self.thickness_spinbox.value() != value:
            self.thickness_spinbox.setValue(value)
        
        color = self.color_preview.get_color()
        brush_type = "water" if self.water_radio.isChecked() else ("calligraphy" if self.calligraphy_radio.isChecked() else "pencil")
        self.pen_preview.update_pen(value, color, brush_type)
        
        self._mark_changed()

    def _on_thickness_spinbox_changed(self, value):
        if self.is_loading:
            return
            
        if self.thickness_slider.value() != value:
            self.thickness_slider.setValue(value)
        
        self._mark_changed()

    def _on_color_button_clicked(self):
        current_color = QColor(*self.color_preview.get_color())
        color = QColorDialog.getColor(current_color, self, "选择笔尖颜色")
        
        if color.isValid():
            rgb = [color.red(), color.green(), color.blue()]
            self.color_preview.set_color(rgb)
            
            thickness = self.thickness_slider.value()
            brush_type = "water" if self.water_radio.isChecked() else ("calligraphy" if self.calligraphy_radio.isChecked() else "pencil")
            self.pen_preview.update_pen(thickness, rgb, brush_type)
            
            self._mark_changed()

    def _on_brush_type_changed(self):
        if not self.is_loading:
            thickness = self.thickness_slider.value()
            color = self.color_preview.get_color()
            brush_type = "water" if self.water_radio.isChecked() else ("calligraphy" if self.calligraphy_radio.isChecked() else "pencil")
            self.pen_preview.update_pen(thickness, color, brush_type)
            self._mark_changed()

    def _on_force_topmost_changed(self, state):
        if not self.is_loading:
            self._mark_changed()
    
    def _mark_changed(self):
        parent = self.parent()
        if parent and hasattr(parent, 'parent') and hasattr(parent.parent(), '_mark_changed'):
            parent.parent()._mark_changed()
    
    def has_unsaved_changes(self):
        try:
            if self.thickness_slider.value() != self.settings.get("brush.pen_width", 3):
                return True
            if self.color_preview.get_color() != self.settings.get("brush.pen_color", [0, 120, 255]):
                return True
            current_brush_type = "water" if self.water_radio.isChecked() else ("calligraphy" if self.calligraphy_radio.isChecked() else "pencil")
            if current_brush_type != self.settings.get("brush.brush_type", "pencil"):
                return True
            if self.force_topmost_checkbox.isChecked() != self.settings.get("brush.force_topmost", True):
                return True
            return False
        except:
            return False
    
    def apply_settings(self):
        try:
            thickness = self.thickness_slider.value()
            color = self.color_preview.get_color()
            brush_type = "water" if self.water_radio.isChecked() else ("calligraphy" if self.calligraphy_radio.isChecked() else "pencil")
            force_topmost = self.force_topmost_checkbox.isChecked()
            
            self.settings.set("brush.pen_width", thickness)
            self.settings.set("brush.pen_color", color)
            self.settings.set("brush.brush_type", brush_type)
            self.settings.set("brush.force_topmost", force_topmost)
            
            self._apply_pen_settings_to_drawing_module(thickness, color)
            
            return True
        except Exception as e:
            self.logger.error(f"应用画笔设置失败: {e}")
            return False
    
    def _apply_pen_settings_to_drawing_module(self, width, color):
        try:
            main_window = self._find_main_window()
            if main_window and hasattr(main_window, 'console_page'):
                console_page = main_window.console_page
                if hasattr(console_page, 'drawing_manager') and console_page.drawing_manager:
                    console_page.drawing_manager.update_settings()
                    self.logger.debug(f"已实时更新画笔设置: 粗细={width}, 颜色={color}")
        except Exception as e:
            self.logger.error(f"应用画笔设置失败: {e}")

    def _find_main_window(self):
        widget = self
        while widget:
            if hasattr(widget, 'console_page'):
                return widget
            widget = widget.parent()
        return None