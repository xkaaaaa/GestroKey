"""
设置页面主页面

包含应用设置、画笔设置、判断器设置三个子选项卡
"""

import os
import sys
from qtpy.QtCore import Qt, QTimer
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
        
        # 定时检查设置变更状态
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_settings_changes)
        self.check_timer.start(1000)  # 每秒检查一次

    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("设置")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        
        # 创建三个子选项卡
        self.application_tab = ApplicationSettingsTab(self)
        self.brush_tab = BrushSettingsTab(self)
        self.recognizer_tab = RecognizerSettingsTab(self)
        
        # 添加选项卡
        self.tab_widget.addTab(self.application_tab, "应用设置")
        self.tab_widget.addTab(self.brush_tab, "画笔设置")
        self.tab_widget.addTab(self.recognizer_tab, "判断器设置")
        
        # 选项卡切换事件
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        layout.addWidget(self.tab_widget)
        
        # 底部统一操作按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # 重置为默认按钮
        self.btn_reset = QPushButton("重置为默认")
        self.btn_reset.setMinimumSize(120, 35)
        self.btn_reset.clicked.connect(self._reset_settings)
        bottom_layout.addWidget(self.btn_reset)
        
        bottom_layout.addStretch()
        
        # 放弃修改按钮
        self.btn_discard = QPushButton("放弃修改")
        self.btn_discard.setMinimumSize(100, 35)
        self.btn_discard.clicked.connect(self._discard_changes)
        self.btn_discard.setEnabled(False)
        bottom_layout.addWidget(self.btn_discard)
        
        # 保存设置按钮
        self.btn_save = QPushButton("保存设置")
        self.btn_save.setMinimumSize(100, 35)
        self.btn_save.clicked.connect(self._save_settings)
        self.btn_save.setEnabled(False)
        bottom_layout.addWidget(self.btn_save)
        
        layout.addLayout(bottom_layout)

    def _on_tab_changed(self, index):
        """选项卡切换事件"""
        tab_names = ["应用设置", "画笔设置", "判断器设置"]
        if 0 <= index < len(tab_names):
            self.logger.debug(f"切换到设置选项卡: {tab_names[index]}")
            
    def _check_settings_changes(self):
        """检查设置是否有变更"""
        has_changes = self.has_unsaved_changes()
        self.btn_save.setEnabled(has_changes)
        self.btn_discard.setEnabled(has_changes)
        
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        try:
            # 检查前端UI更改
            has_frontend_changes = (
                self.application_tab.has_unsaved_changes() or
                self.brush_tab.has_unsaved_changes() or
                self.recognizer_tab.has_unsaved_changes()
            )
            
            # 检查后端设置更改
            has_backend_changes = self.settings.has_changes()
            
            return has_frontend_changes or has_backend_changes
        except Exception as e:
            self.logger.error(f"检查设置更改时出错: {e}")
            return False
    
    def _mark_changed(self):
        """标记设置已更改（由子选项卡调用）"""
        pass  # 变更检查由定时器自动处理
        
    def _save_settings(self):
        """保存设置"""
        try:
            # 应用所有子选项卡的设置
            if not self.application_tab.apply_settings():
                QMessageBox.critical(self, "错误", "应用设置失败")
                return
                
            if not self.brush_tab.apply_settings():
                QMessageBox.critical(self, "错误", "画笔设置失败")
                return
                
            if not self.recognizer_tab.apply_settings():
                QMessageBox.critical(self, "错误", "判断器设置失败")
                return
            
            # 保存到文件
            success = self.settings.save()
            if success:
                QMessageBox.information(self, "成功", "设置已保存")
                self.logger.info("设置已保存")
                
                # 重新加载所有选项卡
                self._reload_all()
            else:
                QMessageBox.critical(self, "错误", "保存设置失败")
                
        except Exception as e:
            self.logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
    
    def _reset_settings(self):
        """重置为默认设置"""
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
        """放弃所有未保存的更改"""
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
        """重新加载所有选项卡"""
        try:
            self.application_tab._load_settings()
            self.brush_tab._load_settings()
            self.recognizer_tab._load_settings()
            self.logger.debug("已重新加载所有设置选项卡")
        except Exception as e:
            self.logger.error(f"重新加载选项卡时出错: {e}")
    
    def _load_settings(self):
        """加载设置（兼容性方法）"""
        self._reload_all()
    
    def _apply_settings(self):
        """应用设置（兼容性方法）"""
        return (
            self.application_tab.apply_settings() and
            self.brush_tab.apply_settings() and
            self.recognizer_tab.apply_settings()
        )