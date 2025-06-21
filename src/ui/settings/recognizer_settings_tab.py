"""
判断器设置选项卡

处理手势识别相似度阈值等设置
"""

import os
import sys
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QDoubleSpinBox,
    QScrollArea,
)

try:
    from core.logger import get_logger
    from ui.settings.settings import get_settings
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger
    from ui.settings.settings import get_settings


class RecognizerSettingsTab(QWidget):
    """判断器设置选项卡"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("RecognizerSettingsTab")
        self.settings = get_settings()
        self.is_loading = False
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # 判断器设置组
        recognizer_group = self._create_recognizer_settings_group()
        content_layout.addWidget(recognizer_group)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def _create_recognizer_settings_group(self):
        """创建判断器设置组"""
        widget = QWidget()
        layout = QFormLayout(widget)

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
        
        layout.addRow("相似度阈值:", threshold_widget)

        return widget
    
    def _load_settings(self):
        """加载设置"""
        self.is_loading = True
        try:
            threshold = self.settings.get("gesture.similarity_threshold", 0.70)
            self.threshold_spinbox.setValue(threshold)
        except Exception as e:
            self.logger.error(f"加载判断器设置失败: {e}")
        finally:
            self.is_loading = False
    
    def _on_threshold_changed(self, value):
        """相似度阈值改变时的处理"""
        if not self.is_loading:
            self._mark_changed()
    
    def _mark_changed(self):
        """标记设置已更改"""
        parent = self.parent()
        if parent and hasattr(parent, 'parent') and hasattr(parent.parent(), '_mark_changed'):
            parent.parent()._mark_changed()
    
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        try:
            current_threshold = self.threshold_spinbox.value()
            saved_threshold = self.settings.get("gesture.similarity_threshold", 0.70)
            return current_threshold != saved_threshold
        except:
            return False
    
    def apply_settings(self):
        """应用设置"""
        try:
            threshold = self.threshold_spinbox.value()
            self.settings.set("gesture.similarity_threshold", threshold)
            return True
        except Exception as e:
            self.logger.error(f"应用判断器设置失败: {e}")
            return False
