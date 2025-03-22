from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QGroupBox, QFrame, QSpacerItem, QSizePolicy, QGridLayout,
                              QSlider, QCheckBox, QScrollArea)
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
        
        # 更新值标签
        self.value_label.setText(str(actual_value))
        
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

class SettingsPage(QWidget):
    """设置页面"""
    
    # 定义信号
    settingChanged = pyqtSignal(str, object)  # 单个设置变更信号，参数为(键名, 值)
    saveSettingsClicked = pyqtSignal(dict)    # 保存设置信号，参数为设置字典
    resetSettingsClicked = pyqtSignal()       # 重置设置信号
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.settings = {}
        self.settings_controls = {}
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
            "speed_factor", "速度因子", 0.1, 2.0, 0.1, 
            self.settings_manager.get_setting("speed_factor", 1.0)
        )
        speed_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(speed_slider)
        self.settings_controls["speed_factor"] = speed_slider
        
        # 基本宽度
        base_width_slider = SliderSetting(
            "base_width", "基本宽度", 1, 10, 0.5, 
            self.settings_manager.get_setting("base_width", 5)
        )
        base_width_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(base_width_slider)
        self.settings_controls["base_width"] = base_width_slider
        
        # 最小宽度
        min_width_slider = SliderSetting(
            "min_width", "最小宽度", 1, 10, 0.5, 
            self.settings_manager.get_setting("min_width", 3)
        )
        min_width_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(min_width_slider)
        self.settings_controls["min_width"] = min_width_slider
        
        # 最大宽度
        max_width_slider = SliderSetting(
            "max_width", "最大宽度", 2, 20, 0.5, 
            self.settings_manager.get_setting("max_width", 12)
        )
        max_width_slider.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(max_width_slider)
        self.settings_controls["max_width"] = max_width_slider
        
        # 启用高级画笔
        advanced_brush_checkbox = CheckboxSetting(
            "enable_advanced_brush", "启用高级画笔", 
            self.settings_manager.get_setting("enable_advanced_brush", True)
        )
        advanced_brush_checkbox.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(advanced_brush_checkbox)
        self.settings_controls["enable_advanced_brush"] = advanced_brush_checkbox
        
        # 启用自动平滑
        auto_smoothing_checkbox = CheckboxSetting(
            "enable_auto_smoothing", "启用自动平滑", 
            self.settings_manager.get_setting("enable_auto_smoothing", True)
        )
        auto_smoothing_checkbox.valueChanged.connect(self.on_setting_changed)
        drawing_layout.addWidget(auto_smoothing_checkbox)
        self.settings_controls["enable_auto_smoothing"] = auto_smoothing_checkbox
        
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
            self.settings_manager.get_setting("force_topmost", True)
        )
        topmost_checkbox.valueChanged.connect(self.on_setting_changed)
        app_layout.addWidget(topmost_checkbox)
        self.settings_controls["force_topmost"] = topmost_checkbox
        
        # 开机自启动
        autostart_checkbox = CheckboxSetting(
            "start_with_system", "开机自启动", 
            self.settings_manager.get_setting("start_with_system", False)
        )
        autostart_checkbox.valueChanged.connect(self.on_setting_changed)
        app_layout.addWidget(autostart_checkbox)
        self.settings_controls["start_with_system"] = autostart_checkbox
        
        # 硬件加速
        hardware_accel_checkbox = CheckboxSetting(
            "enable_hardware_acceleration", "启用硬件加速", 
            self.settings_manager.get_setting("enable_hardware_acceleration", True)
        )
        hardware_accel_checkbox.valueChanged.connect(self.on_setting_changed)
        app_layout.addWidget(hardware_accel_checkbox)
        self.settings_controls["enable_hardware_acceleration"] = hardware_accel_checkbox
        
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
        
        # 更新控件值
        for key, control in self.settings_controls.items():
            if key in self.settings:
                if isinstance(control, SliderSetting):
                    control.set_value(self.settings[key])
                elif isinstance(control, CheckboxSetting):
                    control.set_checked(self.settings[key])
        
    def on_setting_changed(self, key, value):
        """设置变更处理"""
        self.settings[key] = value
        self.settingChanged.emit(key, value)
        
    def on_save_clicked(self):
        """保存按钮点击处理"""
        self.saveSettingsClicked.emit(self.settings)
        
    def on_reset_clicked(self):
        """重置按钮点击处理"""
        self.resetSettingsClicked.emit()
        
    def update_settings(self, settings):
        """更新设置控件的值
        
        Args:
            settings: 设置字典
        """
        self.settings = settings
        
        # 更新控件值
        for key, control in self.settings_controls.items():
            if key in settings:
                if isinstance(control, SliderSetting):
                    control.set_value(settings[key])
                elif isinstance(control, CheckboxSetting):
                    control.set_checked(settings[key])
        
    def get_current_settings(self):
        """获取当前设置
        
        Returns:
            dict: 当前的设置字典
        """
        return self.settings
        
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