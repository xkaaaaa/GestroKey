"""
设置页面主页面

包含应用设置、画笔设置、判断器设置三个子选项卡
"""

import os
from qtpy.QtCore import Qt, QTimer, QSize
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

from core.logger import get_logger
from ui.settings.settings import get_settings
from .application_settings_tab import ApplicationSettingsTab
from .brush_settings_tab import BrushSettingsTab
from .recognizer_settings_tab import RecognizerSettingsTab


class SettingsPage(QWidget):
    """设置页面主页面，包含三个子选项卡"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("SettingsPage")
        self.settings = get_settings()
        
        self._init_ui()
        
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_settings_changes)
        self.check_timer.start(1000)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("设置")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.tab_widget = QTabWidget()
        
        self.application_tab = ApplicationSettingsTab(self)
        self.brush_tab = BrushSettingsTab(self)
        self.recognizer_tab = RecognizerSettingsTab(self)
        
        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "assets", "images", "ui"
        )
        
        # 添加选项卡
        tabs_config = [
            (self.application_tab, "app-settings.svg", "应用设置"),
            (self.brush_tab, "brush-settings.svg", "画笔设置"),
            (self.recognizer_tab, "recognizer-settings.svg", "判断器设置")
        ]
        
        for tab, icon_name, label in tabs_config:
            icon_path = os.path.join(assets_dir, icon_name)
            if os.path.exists(icon_path):
                self.tab_widget.addTab(tab, QIcon(icon_path), label)
            else:
                self.tab_widget.addTab(tab, label)
        
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        self.btn_reset = QPushButton("重置为默认")
        self.btn_reset.setMinimumSize(120, 35)
        self.btn_reset.clicked.connect(self._reset_settings)
        reset_icon_path = os.path.join(assets_dir, "reset.svg")
        if os.path.exists(reset_icon_path):
            self.btn_reset.setIcon(QIcon(reset_icon_path))
            self.btn_reset.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_reset)
        
        bottom_layout.addStretch()
        
        self.btn_discard = QPushButton("放弃修改")
        self.btn_discard.setMinimumSize(100, 35)
        self.btn_discard.clicked.connect(self._discard_changes)
        self.btn_discard.setEnabled(False)
        cancel_icon_path = os.path.join(assets_dir, "cancel.svg")
        if os.path.exists(cancel_icon_path):
            self.btn_discard.setIcon(QIcon(cancel_icon_path))
            self.btn_discard.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_discard)
        
        self.btn_save = QPushButton("保存设置")
        self.btn_save.setMinimumSize(100, 35)
        self.btn_save.clicked.connect(self._save_settings)
        self.btn_save.setEnabled(False)
        save_icon_path = os.path.join(assets_dir, "save.svg")
        if os.path.exists(save_icon_path):
            self.btn_save.setIcon(QIcon(save_icon_path))
            self.btn_save.setIconSize(QSize(18, 18))
        bottom_layout.addWidget(self.btn_save)
        
        layout.addLayout(bottom_layout)

    def _on_tab_changed(self, index):
        tab_names = ["应用设置", "画笔设置", "判断器设置"]
        if 0 <= index < len(tab_names):
            self.logger.debug(f"切换到设置选项卡: {tab_names[index]}")
            
    def _check_settings_changes(self):
        has_changes = self.has_unsaved_changes()
        self.btn_save.setEnabled(has_changes)
        self.btn_discard.setEnabled(has_changes)
        
    def has_unsaved_changes(self):
        try:
            has_frontend_changes = (
                self.application_tab.has_unsaved_changes() or
                self.brush_tab.has_unsaved_changes() or
                self.recognizer_tab.has_unsaved_changes()
            )
            
            has_backend_changes = self.settings.has_changes()
            
            return has_frontend_changes or has_backend_changes
        except Exception as e:
            self.logger.error(f"检查设置更改时出错: {e}")
            return False
    
    def _mark_changed(self):
        pass
        
    def _save_settings(self):
        try:
            if not self.application_tab.apply_settings():
                QMessageBox.critical(self, "错误", "应用设置失败")
                return
                
            if not self.brush_tab.apply_settings():
                QMessageBox.critical(self, "错误", "画笔设置失败")
                return
                
            if not self.recognizer_tab.apply_settings():
                QMessageBox.critical(self, "错误", "判断器设置失败")
                return
            
            success = self.settings.save()
            if success:
                QMessageBox.information(self, "成功", "设置已保存")
                self.logger.info("设置已保存")
                self._reload_all()
            else:
                QMessageBox.critical(self, "错误", "保存设置失败")
                
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
    
    def _reset_settings(self):
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要将所有设置重置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.settings.reset_to_default()
                if success:
                    QMessageBox.information(self, "成功", "设置已重置为默认值")
                    self.logger.info("设置已重置为默认值")
                    self._reload_all()
                else:
                    QMessageBox.critical(self, "错误", "重置设置失败")
            except Exception as e:
                self.logger.error(f"重置设置失败: {e}")
                QMessageBox.critical(self, "错误", f"重置设置失败: {str(e)}")

    def _discard_changes(self):
        reply = QMessageBox.question(
            self, "确认放弃", 
            "确定要放弃所有修改吗？这将丢失所有未保存的更改。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.settings.load()
                QMessageBox.information(self, "成功", "所有未保存的更改已放弃")
                self.logger.info("已放弃所有修改")
                self._reload_all()
            except Exception as e:
                self.logger.error(f"放弃更改失败: {e}")
                QMessageBox.critical(self, "错误", f"放弃更改失败: {str(e)}")
    
    def _reload_all(self):
        try:
            self.application_tab._load_settings()
            self.brush_tab._load_settings()
            self.recognizer_tab._load_settings()
            self.logger.debug("已重新加载所有设置选项卡")
        except Exception as e:
            self.logger.error(f"重新加载选项卡时出错: {e}")
    
    def _load_settings(self):
        self._reload_all()
    
    def _apply_settings(self):
        return (
            self.application_tab.apply_settings() and
            self.brush_tab.apply_settings() and
            self.recognizer_tab.apply_settings()
        )