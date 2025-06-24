"""
应用设置选项卡

处理开机自启动、退出行为等应用相关设置
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QCheckBox,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QRadioButton,
    QButtonGroup,
)

from core.logger import get_logger
from ui.settings.settings import get_settings


class ApplicationSettingsTab(QWidget):
    """应用设置选项卡"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ApplicationSettingsTab")
        self.settings = get_settings()
        self.is_loading = False
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()

        self.autostart_checkbox = QCheckBox("开机自启动")
        self.autostart_checkbox.setToolTip("设置应用程序是否在系统启动时自动运行（将以静默模式启动，自动开始监听并最小化到托盘）")
        self.autostart_checkbox.stateChanged.connect(self._on_autostart_changed)
        form_layout.addRow("启动选项:", self.autostart_checkbox)

        self.show_exit_dialog_checkbox = QCheckBox("显示退出确认对话框")
        self.show_exit_dialog_checkbox.setToolTip("关闭程序时是否显示确认对话框")
        self.show_exit_dialog_checkbox.stateChanged.connect(self._on_exit_dialog_changed)
        form_layout.addRow("退出行为:", self.show_exit_dialog_checkbox)

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
        
        form_layout.addRow("默认关闭行为:", close_behavior_widget)

        layout.addLayout(form_layout)
        layout.addStretch()
    
    def _load_settings(self):
        self.is_loading = True
        try:
            is_autostart = self.settings.is_autostart_enabled()
            self.autostart_checkbox.setChecked(is_autostart)
            
            show_exit_dialog = self.settings.get("app.show_exit_dialog", True)
            self.show_exit_dialog_checkbox.setChecked(show_exit_dialog)
            
            default_close_action = self.settings.get("app.default_close_action", "minimize")
            if default_close_action == "minimize":
                self.minimize_radio.setChecked(True)
            else:
                self.exit_radio.setChecked(True)
                
        except Exception as e:
            self.logger.error(f"加载应用设置失败: {e}")
        finally:
            self.is_loading = False
    
    def _on_autostart_changed(self, state):
        if not self.is_loading:
            self._mark_changed()
    
    def _on_exit_dialog_changed(self, state):
        if not self.is_loading:
            self._mark_changed()
    
    def _on_close_behavior_changed(self):
        if not self.is_loading:
            self._mark_changed()
    
    def _mark_changed(self):
        parent = self.parent()
        if parent and hasattr(parent, 'parent') and hasattr(parent.parent(), '_mark_changed'):
            parent.parent()._mark_changed()
    
    def has_unsaved_changes(self):
        try:
            current_autostart = self.autostart_checkbox.isChecked()
            saved_autostart = self.settings.is_autostart_enabled()
            if current_autostart != saved_autostart:
                return True
            
            current_exit_dialog = self.show_exit_dialog_checkbox.isChecked()
            saved_exit_dialog = self.settings.get("app.show_exit_dialog", True)
            if current_exit_dialog != saved_exit_dialog:
                return True
            
            current_close_action = "minimize" if self.minimize_radio.isChecked() else "exit"
            saved_close_action = self.settings.get("app.default_close_action", "minimize")
            if current_close_action != saved_close_action:
                return True
            
            return False
        except:
            return False
    
    def apply_settings(self):
        try:
            is_autostart = self.autostart_checkbox.isChecked()
            current_autostart = self.settings.is_autostart_enabled()
            
            if is_autostart != current_autostart:
                success = self.settings.set_autostart(is_autostart)
                if not success:
                    return False
            
            show_exit_dialog = self.show_exit_dialog_checkbox.isChecked()
            self.settings.set("app.show_exit_dialog", show_exit_dialog)
            
            default_close_action = "minimize" if self.minimize_radio.isChecked() else "exit"
            self.settings.set("app.default_close_action", default_close_action)
            
            return True
        except Exception as e:
            self.logger.error(f"应用设置失败: {e}")
            return False