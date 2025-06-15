import os
import sys
from qtpy.QtCore import Qt, QTimer
from qtpy.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QGroupBox,
    QFormLayout,
    QDoubleSpinBox,
    QTabWidget,
    QDoubleSpinBox,
    QTabWidget,
    QFrame,
    QDialog,
)

try:
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
    from ui.gestures.drawing_widget import GestureDrawingWidget
    from ui.settings.settings import get_settings
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    from core.logger import get_logger
    from ui.gestures.gestures import get_gesture_library
    from ui.gestures.drawing_widget import GestureDrawingWidget
    from ui.settings.settings import get_settings


class GesturesPage(QWidget):
    """手势管理主页面，包含三个子选项卡"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GesturesPage")
        self.gesture_library = get_gesture_library()
        
        self.initUI()
        
    def initUI(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("手势管理")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        
        # 导入并创建三个子选项卡
        from ui.gestures.trigger_paths_tab import TriggerPathsTab
        from ui.gestures.execute_actions_tab import ExecuteActionsTab  
        from ui.gestures.gesture_mappings_tab import GestureMappingsTab
        
        self.trigger_paths_tab = TriggerPathsTab(self)
        self.execute_actions_tab = ExecuteActionsTab(self)
        self.gesture_mappings_tab = GestureMappingsTab(self)
        
        # 添加选项卡
        self.tab_widget.addTab(self.trigger_paths_tab, "触发路径")
        self.tab_widget.addTab(self.execute_actions_tab, "执行操作")
        self.tab_widget.addTab(self.gesture_mappings_tab, "手势映射")
        
        # 选项卡切换事件
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        layout.addWidget(self.tab_widget)
        
        # 底部统一操作按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        # 重置为默认手势库按钮
        self.btn_reset = QPushButton("重置为默认")
        self.btn_reset.setMinimumSize(120, 35)
        self.btn_reset.clicked.connect(self._reset_to_default)
        bottom_layout.addWidget(self.btn_reset)
        
        bottom_layout.addStretch()
        
        # 保存手势库按钮
        self.btn_save_library = QPushButton("保存设置")
        self.btn_save_library.setMinimumSize(100, 35)
        self.btn_save_library.clicked.connect(self._save_gesture_library)
        self.btn_save_library.setEnabled(False)
        bottom_layout.addWidget(self.btn_save_library)
        
        layout.addLayout(bottom_layout)
        
        # 定时检查手势库变更状态
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_library_changes)
        self.check_timer.start(1000)  # 每秒检查一次
        
    def _on_tab_changed(self, index):
        """选项卡切换事件"""
        tab_names = ["触发路径", "执行操作", "手势映射"]
        if 0 <= index < len(tab_names):
            self.logger.debug(f"切换到选项卡: {tab_names[index]}")
            
    def _check_library_changes(self):
        """检查手势库是否有变更"""
        has_changes = self.gesture_library.has_changes()
        self.btn_save_library.setEnabled(has_changes)
        
    def _save_gesture_library(self):
        """保存手势库"""
        try:
            success = self.gesture_library.save()
            if success:
                QMessageBox.information(self, "成功", "设置已保存")
                self.logger.info("手势库已保存")
                
                # 刷新所有选项卡
                self._refresh_all()
            else:
                QMessageBox.critical(self, "错误", "保存设置失败")
                    
        except Exception as e:
            self.logger.error(f"保存手势库时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
            
    def _refresh_all(self):
        """刷新所有选项卡"""
        try:
            self.trigger_paths_tab.refresh_list()
            self.execute_actions_tab.refresh_list()
            self.gesture_mappings_tab.refresh_list()
            self.logger.debug("已刷新所有选项卡")
        except Exception as e:
            self.logger.error(f"刷新选项卡时出错: {e}")
            
    def _reset_to_default(self):
        """重置为默认手势库"""
        reply = QMessageBox.question(
            self, "确认重置", 
            "确定要重置为默认手势库吗？这将丢失所有自定义的手势设置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 重新加载默认手势库
                default_gestures = self.gesture_library._load_default_gestures()
                
                # 根据操作系统调整快捷键格式
                import sys
                if sys.platform != "win32":
                    self.gesture_library._convert_actions_for_current_platform()
                
                # 重置手势库数据
                self.gesture_library.trigger_paths = default_gestures.get("trigger_paths", {}).copy()
                self.gesture_library.execute_actions = default_gestures.get("execute_actions", {}).copy()
                self.gesture_library.gesture_mappings = default_gestures.get("gesture_mappings", {}).copy()
                
                # 保存到文件
                success = self.gesture_library.save()
                if success:
                    QMessageBox.information(self, "成功", "已重置为默认手势库")
                    self.logger.info("手势库已重置为默认")
                    
                    # 刷新所有选项卡
                    self._refresh_all()
                else:
                    QMessageBox.critical(self, "错误", "重置手势库失败")
                    
            except Exception as e:
                self.logger.error(f"重置手势库时出错: {e}")
                QMessageBox.critical(self, "错误", f"重置手势库失败: {str(e)}")


class SimilarityTestDialog(QDialog):
    """相似度测试对话框"""
    
    def __init__(self, reference_path, parent=None):
        super().__init__(parent)
        self.reference_path = reference_path
        self.test_path = None
        
        try:
            from core.path_analyzer import PathAnalyzer
            self.path_analyzer = PathAnalyzer()
        except ImportError:
            self.path_analyzer = None
        
        self.setWindowTitle("相似度测试")
        self.setFixedSize(800, 600)
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 上半部分：两个画板
        canvas_group = QGroupBox("路径对比")
        canvas_layout = QHBoxLayout(canvas_group)
        
        # 左侧：显示参考路径
        left_group = QGroupBox("当前编辑的路径")
        left_layout = QVBoxLayout(left_group)
        
        self.reference_widget = GestureDrawingWidget()
        self.reference_widget.setFixedHeight(250)
        # 隐藏工具栏
        self.reference_widget.toolbar.setVisible(False)
        # 禁用所有工具，但保持显示功能
        self.reference_widget.current_tool = None
        self.reference_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # 加载参考路径
        self.reference_widget.load_path(self.reference_path)
        left_layout.addWidget(self.reference_widget)
        
        # 延迟重置视图，确保widget已完全显示
        QTimer.singleShot(100, self.reference_widget._reset_view)
        
        canvas_layout.addWidget(left_group)
        
        # 右侧：用户绘制测试路径
        right_group = QGroupBox("绘制测试路径")
        right_layout = QVBoxLayout(right_group)
        
        self.test_widget = GestureDrawingWidget()
        self.test_widget.setFixedHeight(250)
        # 隐藏工具栏
        self.test_widget.toolbar.setVisible(False)
        # 设置为画笔工具
        self.test_widget.current_tool = "brush"
        # 连接路径完成信号
        self.test_widget.pathCompleted.connect(self._on_test_path_completed)
        # 重写鼠标按下事件以在开始绘画时清空画布
        self._setup_test_widget_events()
        right_layout.addWidget(self.test_widget)
        
        canvas_layout.addWidget(right_group)
        
        layout.addWidget(canvas_group)
        
        # 下半部分：相似度显示
        result_group = QGroupBox("相似度结果")
        result_layout = QVBoxLayout(result_group)
        
        self.similarity_label = QLabel("请在右侧画板绘制测试路径")
        self.similarity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.similarity_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 20px;")
        result_layout.addWidget(self.similarity_label)
        
        layout.addWidget(result_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.btn_close = QPushButton("关闭")
        self.btn_close.clicked.connect(self.close)
        button_layout.addWidget(self.btn_close)
        
        layout.addLayout(button_layout)
    
    def _on_test_path_completed(self, path):
        """测试路径绘制完成"""
        self.test_path = path
        self._calculate_similarity()
    
    def _setup_test_widget_events(self):
        """设置测试组件的事件处理"""
        # 保存原始的鼠标按下事件
        original_mouse_press = self.test_widget.mousePressEvent
        
        def custom_mouse_press(event):
            # 如果是左键按下且不是在拖拽状态，表示开始新的绘画
            if (event.button() == Qt.MouseButton.LeftButton and 
                self.test_widget.current_tool == "brush" and
                not self.test_widget.space_pressed and
                self.test_widget._is_in_drawing_area(event.pos())):
                
                # 清空画布并重置视图
                self.test_widget.clear_drawing()
                self.test_widget._reset_view()
                self.test_path = None
                self.similarity_label.setText("请在右侧画板绘制测试路径")
            
            # 调用原始的事件处理
            original_mouse_press(event)
        
        # 替换鼠标按下事件
        self.test_widget.mousePressEvent = custom_mouse_press
    
    def _calculate_similarity(self):
        """计算相似度"""
        if not self.test_path or not self.path_analyzer:
            self.similarity_label.setText("无法计算相似度")
            return
        
        try:
            # 归一化路径
            normalized_ref = self.path_analyzer.normalize_path_scale(self.reference_path)
            normalized_test = self.path_analyzer.normalize_path_scale(self.test_path)
            
            # 计算相似度
            similarity = self.path_analyzer.calculate_similarity(normalized_ref, normalized_test)
            
            # 显示结果
            percentage = similarity * 100
            if percentage >= 70:
                color = "green"
                status = "很相似"
            elif percentage >= 50:
                color = "orange"
                status = "较相似"
            else:
                color = "red"
                status = "不相似"
            
            result_text = f"相似度: <span style='color: {color}; font-size: 24px;'>{percentage:.1f}%</span> ({status})"
            self.similarity_label.setText(result_text)
            
        except Exception as e:
            self.similarity_label.setText(f"计算错误: {str(e)}")
    



if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    widget = GesturesPage()
    widget.show()
    sys.exit(app.exec()) 