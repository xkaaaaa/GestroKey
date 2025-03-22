from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QGroupBox, QFrame, QSpacerItem, QSizePolicy, QGridLayout,
                              QSlider, QCheckBox, QScrollArea, QColorDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

import os
import sys

try:
    from app.log import log
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.log import log

class SettingsPageHeader(QWidget):
    """设置页头部组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 10)
        
        # 标题
        title = QLabel("设置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2D3748;")
        layout.addWidget(title)
        
        # 描述
        description = QLabel("自定义GestroKey的各项设置")
        description.setStyleSheet("font-size: 14px; color: #4A5568; margin-top: 5px;")
        layout.addWidget(description)
        
        # 分割线
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #E2E8F0;")
        layout.addWidget(divider)

class SliderSetting(QWidget):
    """滑块设置组件"""
    
    # 定义信号
    valueChanged = pyqtSignal(str, float)  # 值变更信号，参数为(键名, 值)
    
    def __init__(self, key, title, min_value, max_value, step, default_value, parent=None):
        super().__init__(parent)
        self.key = key
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 15)
        
        # 标题和值
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2D3748;")
        header_layout.addWidget(title_label)
        
        # 值
        self.value_label = QLabel(str(default_value))
        self.value_label.setStyleSheet("font-size: 14px; color: #4A90E2; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(self.value_label)
        
        # 滑块
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_value / step))
        self.slider.setMaximum(int(max_value / step))
        if default_value is None:
            default_value = min_value
        self.slider.setValue(int(default_value / step))
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #E2E8F0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
                background: #4A90E2;
            }
            
            QSlider::sub-page:horizontal {
                background: #4A90E2;
                border-radius: 4px;
            }
        """)
        
        # 步长和值
        self.step = step
        
        # 连接信号
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        
        # 添加组件到布局
        layout.addWidget(header)
        layout.addWidget(self.slider)
        
    def on_slider_value_changed(self, value):
        """滑块值变更处理"""
        # 计算实际值
        actual_value = value * self.step
        
        # 更新值标签，格式化数字，限制小数位数
        if actual_value.is_integer():
            # 如果是整数，不显示小数部分
            formatted_value = str(int(actual_value))
        else:
            # 如果是小数，最多显示2位小数，并移除尾部的0
            formatted_value = f"{actual_value:.2f}".rstrip('0').rstrip('.')
        
        self.value_label.setText(formatted_value)
        
        # 发送值变更信号
        self.valueChanged.emit(self.key, actual_value)
        
    def set_value(self, value):
        """设置滑块值"""
        self.slider.setValue(int(value / self.step))

class CheckboxSetting(QWidget):
    """复选框设置组件"""
    
    # 定义信号
    valueChanged = pyqtSignal(str, bool)  # 值变更信号，参数为(键名, 值)
    
    def __init__(self, key, title, default_value, parent=None):
        super().__init__(parent)
        self.key = key
        
        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # 复选框
        self.checkbox = QCheckBox(title)
        if default_value is None:
            default_value = False
        self.checkbox.setChecked(default_value)
        self.checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #2D3748;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #CBD5E0;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4A90E2;
                border: 1px solid #4A90E2;
                image: url(checkmark.png);
            }
            
            QCheckBox::indicator:unchecked:hover {
                border: 1px solid #4A90E2;
            }
        """)
        
        # 连接信号
        self.checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        
        # 添加组件到布局
        layout.addWidget(self.checkbox)
        layout.addStretch()
        
    def on_checkbox_state_changed(self, state):
        """复选框状态变更处理"""
        checked = (state == Qt.Checked)
        
        # 发送值变更信号
        self.valueChanged.emit(self.key, checked)
        
    def set_checked(self, checked):
        """设置复选框状态"""
        self.checkbox.setChecked(checked)

class ColorPickerSetting(QWidget):
    """颜色选择器设置组件"""
    
    # 定义信号
    valueChanged = pyqtSignal(str, str)  # 值变更信号，参数为(键名, 颜色值)
    
    def __init__(self, key, title, default_value, parent=None):
        super().__init__(parent)
        self.key = key
        
        # 设置默认值
        if default_value is None:
            default_value = "#4299E1"  # 默认蓝色
        self.current_color = default_value
        
        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2D3748;")
        layout.addWidget(title_label)
        
        # 创建颜色预览框
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet(f"background-color: {default_value}; border: 1px solid #CBD5E0; border-radius: 3px;")
        layout.addWidget(self.color_preview)
        
        # 创建颜色值标签
        self.color_value = QLabel(default_value)
        self.color_value.setStyleSheet("font-size: 14px; color: #4A5568; margin-left: 5px;")
        layout.addWidget(self.color_value)
        
        # 创建选择按钮
        self.select_button = QPushButton("选择")
        self.select_button.setCursor(Qt.PointingHandCursor)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #4A5568;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #CBD5E0;
            }
            
            QPushButton:pressed {
                background-color: #A0AEC0;
            }
        """)
        self.select_button.clicked.connect(self.show_color_dialog)
        layout.addWidget(self.select_button)
        
        # 添加弹性空间
        layout.addStretch()
        
    def show_color_dialog(self):
        """显示颜色选择对话框"""
        initial_color = QColor(self.current_color)
        color = QColorDialog.getColor(initial_color, self, "选择颜色")
        
        if color.isValid():
            # 获取十六进制颜色值
            hex_color = color.name()
            
            # 更新预览和标签
            self.color_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #CBD5E0; border-radius: 3px;")
            self.color_value.setText(hex_color)
            
            # 保存当前颜色
            self.current_color = hex_color
            
            # 发送值变更信号
            self.valueChanged.emit(self.key, hex_color)
            
    def set_color(self, color):
        """设置颜色值"""
        self.current_color = color
        self.color_preview.setStyleSheet(f"background-color: {color}; border: 1px solid #CBD5E0; border-radius: 3px;")
        self.color_value.setText(color)

class SettingsPage(QWidget):
    """设置页面"""
    
    # 定义信号
    settingChanged = pyqtSignal(str, object)  # 单个设置变更信号，参数为(键名, 值)
    saveSettingsClicked = pyqtSignal(dict)    # 保存设置信号，参数为设置字典
    resetSettingsClicked = pyqtSignal()       # 重置设置信号
    hasUnsavedChanges = pyqtSignal(bool)      # 未保存更改状态信号
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.settings = {}            # 当前已保存的设置
        self.pending_settings = {}    # 未保存的临时设置
        self.settings_controls = {}
        self.has_unsaved_changes = False
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 页头
        self.header = SettingsPageHeader()
        main_layout.addWidget(self.header)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(20)
        
        # 添加设置分组
        
        # 绘画设置组
        drawing_group = QGroupBox("绘画设置")
        drawing_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        drawing_layout = QVBoxLayout(drawing_group)
        drawing_layout.setContentsMargins(15, 20, 15, 15)
        
        # 添加绘画设置控件
        
        # 速度因子
        speed_slider = SliderSetting(
            "speed_factor", "速度因子", 0.1, 3.0, 0.1, 
            self.settings_manager.get_setting("drawing", "speed_factor", 1.2)
        )
        speed_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(speed_slider)
        self.settings_controls["drawing/speed_factor"] = speed_slider
        
        # 基本宽度
        base_width_slider = SliderSetting(
            "base_width", "基本宽度", 1, 15, 0.5, 
            self.settings_manager.get_setting("drawing", "base_width", 6.0)
        )
        base_width_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(base_width_slider)
        self.settings_controls["drawing/base_width"] = base_width_slider
        
        # 最小宽度
        min_width_slider = SliderSetting(
            "min_width", "最小宽度", 1, 10, 0.5, 
            self.settings_manager.get_setting("drawing", "min_width", 3.0)
        )
        min_width_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(min_width_slider)
        self.settings_controls["drawing/min_width"] = min_width_slider
        
        # 最大宽度
        max_width_slider = SliderSetting(
            "max_width", "最大宽度", 5, 30, 0.5, 
            self.settings_manager.get_setting("drawing", "max_width", 15.0)
        )
        max_width_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(max_width_slider)
        self.settings_controls["drawing/max_width"] = max_width_slider
        
        # 平滑度
        smoothing_slider = SliderSetting(
            "smoothing", "平滑度", 0.0, 1.0, 0.05, 
            self.settings_manager.get_setting("drawing", "smoothing", 0.7)
        )
        smoothing_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(smoothing_slider)
        self.settings_controls["drawing/smoothing"] = smoothing_slider
        
        # 笔画颜色
        color_picker = ColorPickerSetting(
            "color", "笔画颜色", 
            self.settings_manager.get_setting("drawing", "color", "#4299E1")
        )
        color_picker.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(color_picker)
        self.settings_controls["drawing/color"] = color_picker
        
        # 渐隐时间
        fade_time_slider = SliderSetting(
            "fade_time", "渐隐时间(秒)", 0.1, 2.0, 0.1, 
            self.settings_manager.get_setting("drawing", "fade_time", 0.5)
        )
        fade_time_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(fade_time_slider)
        self.settings_controls["drawing/fade_time"] = fade_time_slider
        
        # 最小触发距离
        min_distance_slider = SliderSetting(
            "min_distance", "最小触发距离(像素)", 5, 50, 1, 
            self.settings_manager.get_setting("drawing", "min_distance", 20)
        )
        min_distance_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(min_distance_slider)
        self.settings_controls["drawing/min_distance"] = min_distance_slider
        
        # 最大笔画点数
        max_points_slider = SliderSetting(
            "max_stroke_points", "最大笔画点数", 50, 500, 10, 
            self.settings_manager.get_setting("drawing", "max_stroke_points", 200)
        )
        max_points_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(max_points_slider)
        self.settings_controls["drawing/max_stroke_points"] = max_points_slider
        
        # 最大笔画持续时间
        max_duration_slider = SliderSetting(
            "max_stroke_duration", "最大笔画持续时间(秒)", 1, 10, 1, 
            self.settings_manager.get_setting("drawing", "max_stroke_duration", 5)
        )
        max_duration_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(max_duration_slider)
        self.settings_controls["drawing/max_stroke_duration"] = max_duration_slider
        
        # 启用高级画笔
        advanced_brush_checkbox = CheckboxSetting(
            "advanced_brush", "启用高级画笔", 
            self.settings_manager.get_setting("drawing", "advanced_brush", True)
        )
        advanced_brush_checkbox.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(advanced_brush_checkbox)
        self.settings_controls["drawing/advanced_brush"] = advanced_brush_checkbox
        
        # 启用自动平滑
        auto_smoothing_checkbox = CheckboxSetting(
            "auto_smoothing", "启用自动平滑", 
            self.settings_manager.get_setting("drawing", "auto_smoothing", True)
        )
        auto_smoothing_checkbox.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(auto_smoothing_checkbox)
        self.settings_controls["drawing/auto_smoothing"] = auto_smoothing_checkbox
        
        # 启用硬件加速
        hardware_accel_checkbox = CheckboxSetting(
            "hardware_acceleration", "启用硬件加速", 
            self.settings_manager.get_setting("drawing", "hardware_acceleration", True)
        )
        hardware_accel_checkbox.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(hardware_accel_checkbox)
        self.settings_controls["drawing/hardware_acceleration"] = hardware_accel_checkbox
        
        # 最小点数
        min_points_slider = SliderSetting(
            "min_points", "最小点数", 5, 30, 1, 
            self.settings_manager.get_setting("drawing", "min_points", 10)
        )
        min_points_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(min_points_slider)
        self.settings_controls["drawing/min_points"] = min_points_slider
        
        # 最大暂停时间
        max_pause_slider = SliderSetting(
            "max_pause_ms", "最大暂停时间(毫秒)", 100, 1000, 50, 
            self.settings_manager.get_setting("drawing", "max_pause_ms", 300)
        )
        max_pause_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(max_pause_slider)
        self.settings_controls["drawing/max_pause_ms"] = max_pause_slider
        
        # 最小长度
        min_length_slider = SliderSetting(
            "min_length", "最小长度(像素)", 10, 100, 5, 
            self.settings_manager.get_setting("drawing", "min_length", 50)
        )
        min_length_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(min_length_slider)
        self.settings_controls["drawing/min_length"] = min_length_slider
        
        # 灵敏度
        sensitivity_slider = SliderSetting(
            "sensitivity", "灵敏度", 0.1, 1.0, 0.05, 
            self.settings_manager.get_setting("drawing", "sensitivity", 0.8)
        )
        sensitivity_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(sensitivity_slider)
        self.settings_controls["drawing/sensitivity"] = sensitivity_slider
        
        # 画布边框大小
        canvas_border_slider = SliderSetting(
            "canvas_border", "画布边框大小(像素)", 0, 10, 1, 
            self.settings_manager.get_setting("drawing", "canvas_border", 1)
        )
        canvas_border_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(canvas_border_slider)
        self.settings_controls["drawing/canvas_border"] = canvas_border_slider
        
        # 添加绘画设置组到滚动区域
        scroll_layout.addWidget(drawing_group)
        
        # 应用设置组
        app_group = QGroupBox("应用设置")
        app_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 16px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        app_layout = QVBoxLayout(app_group)
        app_layout.setContentsMargins(15, 20, 15, 15)
        
        # 添加应用设置控件
        
        # 窗口置顶
        topmost_checkbox = CheckboxSetting(
            "force_topmost", "强制窗口置顶", 
            self.settings_manager.get_setting("app", "force_topmost", True)
        )
        topmost_checkbox.valueChanged.connect(self.on_setting_changed)
        app_layout.addWidget(topmost_checkbox)
        self.settings_controls["app/force_topmost"] = topmost_checkbox
        
        # 开机自启动
        autostart_checkbox = CheckboxSetting(
            "start_with_system", "开机自启动", 
            self.settings_manager.get_setting("app", "start_with_windows", False)
        )
        autostart_checkbox.valueChanged.connect(self.on_setting_changed)
        app_layout.addWidget(autostart_checkbox)
        self.settings_controls["app/start_with_windows"] = autostart_checkbox
        
        # 硬件加速
        hardware_accel_checkbox = CheckboxSetting(
            "enable_hardware_acceleration", "启用硬件加速", 
            self.settings_manager.get_setting("app", "enable_hardware_acceleration", True)
        )
        hardware_accel_checkbox.valueChanged.connect(self.on_setting_changed)
        app_layout.addWidget(hardware_accel_checkbox)
        self.settings_controls["app/enable_hardware_acceleration"] = hardware_accel_checkbox
        
        # 添加应用设置组到滚动区域
        scroll_layout.addWidget(app_group)
        
        # 按钮组
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        # 重置按钮
        reset_btn = QPushButton("恢复默认设置")
        reset_btn.setFixedWidth(150)
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #F56565;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #E53E3E;
            }
            
            QPushButton:pressed {
                background-color: #C53030;
            }
        """)
        reset_btn.clicked.connect(self.on_reset_clicked)
        self.reset_button = reset_btn  # 保存为类属性
        
        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.setFixedWidth(150)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4299E1;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #3182CE;
            }
            
            QPushButton:pressed {
                background-color: #2B6CB0;
            }
        """)
        save_btn.clicked.connect(self.on_save_clicked)
        self.save_button = save_btn  # 保存为类属性
        
        # 添加按钮到布局
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        
        # 添加按钮组到滚动区域
        scroll_layout.addWidget(button_container)
        
        # 添加弹性空间
        scroll_layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        
        # 添加滚动区域到主布局
        main_layout.addWidget(scroll_area)
        
        # 加载设置
        self.load_settings()
        
    def load_settings(self, settings=None):
        """从设置管理器加载设置
        
        Args:
            settings: 可选的设置字典，如果不提供则从设置管理器获取
        """
        if settings is None:
            self.settings = self.settings_manager.get_settings()
        else:
            self.settings = settings
            
        # 重置未保存的设置
        self.pending_settings = {}
        self.has_unsaved_changes = False
        self.hasUnsavedChanges.emit(False)
        
        # 更新控件值
        for key, control in self.settings_controls.items():
            if "/" in key:
                category, setting_key = key.split("/", 1)
                if category in self.settings and setting_key in self.settings[category]:
                    if isinstance(control, SliderSetting):
                        control.set_value(self.settings[category][setting_key])
                    elif isinstance(control, CheckboxSetting):
                        control.set_checked(self.settings[category][setting_key])
                    elif isinstance(control, ColorPickerSetting):
                        control.set_color(self.settings[category][setting_key])

    def on_setting_changed(self, key, value):
        """设置值变更处理 - 仅更新临时设置，不立即应用
        
        Args:
            key: 设置键名
            value: 设置值
        """
        log.debug(f"设置变更(未保存): {key} = {value}")
        
        # 解析键名 - 格式：分类/键名，例如: "drawing/speed_factor"
        if "/" in key:
            category, setting_key = key.split("/", 1)
            
            # 特殊处理某些设置键名映射
            if category == "app" and setting_key == "start_with_system":
                setting_key = "start_with_windows"
                log.debug(f"设置键名映射: start_with_system -> start_with_windows")
            
            # 更新未保存的设置
            if category not in self.pending_settings:
                self.pending_settings[category] = {}
            self.pending_settings[category][setting_key] = value
            
            # 标记有未保存的更改
            self.has_unsaved_changes = True
            self.hasUnsavedChanges.emit(True)
        else:
            # 尝试确定正确的类别
            if key == "start_with_system":
                if "app" not in self.pending_settings:
                    self.pending_settings["app"] = {}
                self.pending_settings["app"]["start_with_windows"] = value
                log.debug(f"设置键名映射: start_with_system -> app/start_with_windows")
            else:
                # 直接更新设置（无分类）
                self.pending_settings[key] = value
            
            # 标记有未保存的更改
            self.has_unsaved_changes = True
            self.hasUnsavedChanges.emit(True)
        
    def on_save_clicked(self):
        """保存按钮点击处理 - 应用所有待处理的设置"""
        if not self.has_unsaved_changes:
            return
            
        # 合并待处理的设置到当前设置
        for category, settings in self.pending_settings.items():
            if category not in self.settings:
                self.settings[category] = {}
            
            if isinstance(settings, dict):
                # 分类设置
                for key, value in settings.items():
                    self.settings[category][key] = value
            else:
                # 根级别设置
                self.settings[category] = settings
        
        # 发出保存设置信号
        self.saveSettingsClicked.emit(self.settings)
        
        # 清除未保存的标记
        self.pending_settings = {}
        self.has_unsaved_changes = False
        self.hasUnsavedChanges.emit(False)
        
    def on_reset_clicked(self):
        """重置按钮点击处理"""
        self.resetSettingsClicked.emit()
        
        # 清除未保存的标记
        self.pending_settings = {}
        self.has_unsaved_changes = False
        self.hasUnsavedChanges.emit(False)
        
    def get_current_settings(self):
        """获取当前设置
        
        Returns:
            当前设置字典
        """
        # 如果有未保存的更改，返回包含未保存更改的设置
        if self.has_unsaved_changes:
            # 创建当前设置的副本
            result = {}
            
            # 添加当前已保存的设置
            for category, settings in self.settings.items():
                if isinstance(settings, dict):
                    result[category] = settings.copy()
                else:
                    result[category] = settings
            
            # 合并未保存的设置
            for category, settings in self.pending_settings.items():
                if isinstance(settings, dict):
                    if category not in result:
                        result[category] = {}
                    for key, value in settings.items():
                        result[category][key] = value
                else:
                    result[category] = settings
                    
            return result
            
        # 否则直接返回当前已保存的设置
        return self.settings

    def update_settings(self, settings):
        """更新设置控件的值
        
        Args:
            settings: 设置字典
        """
        self.settings = settings
        
        # 清除未保存的标记
        self.pending_settings = {}
        self.has_unsaved_changes = False
        self.hasUnsavedChanges.emit(False)
        
        # 更新控件值
        for key, control in self.settings_controls.items():
            if "/" in key:
                category, setting_key = key.split("/", 1)
                if category in settings and setting_key in settings[category]:
                    if isinstance(control, SliderSetting):
                        control.set_value(settings[category][setting_key])
                    elif isinstance(control, CheckboxSetting):
                        control.set_checked(settings[category][setting_key])
                        
    def has_pending_changes(self):
        """检查是否有未保存的设置更改
        
        Returns:
            布尔值，表示是否有未保存的更改
        """
        return self.has_unsaved_changes

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from ui.utils.settings_manager import SettingsManager
    import tempfile
    
    # 创建临时设置文件
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
        temp_path = temp.name
        
    app = QApplication(sys.argv)
    
    # 初始化设置管理器
    settings_manager = SettingsManager(temp_path)
    
    # 创建设置页面
    settings_page = SettingsPage(settings_manager)
    settings_page.show()
    
    # 运行应用
    ret = app.exec_()
    
    # 清理
    os.unlink(temp_path)
    
    sys.exit(ret) 