import copy
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, 
    QGroupBox, QMessageBox, QComboBox, QDialogButtonBox, QWidget, QProgressBar
)
from qtpy.QtGui import QPainter, QPen, QColor

from core.logger import get_logger
from ui.gestures.gestures import get_gesture_library
from ui.gestures.drawing_widget import GestureDrawingWidget
from core.path_analyzer import PathAnalyzer
from ui.settings.settings import get_settings


class TriggerPathEditDialog(QDialog):
    
    def __init__(self, path_key=None, parent=None):
        super().__init__(parent)
        self.logger = get_logger("TriggerPathEditDialog")
        self.gesture_library = get_gesture_library()
        
        self.path_key = path_key
        self.current_path = None
        self.is_editing = path_key is not None
        
        self.setWindowTitle("编辑触发路径" if self.is_editing else "添加触发路径")
        self.setFixedSize(600, 500)
        
        self.initUI()
        
        if self.is_editing:
            self._load_path_data()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        info_group = QGroupBox("基本信息")
        info_layout = QVBoxLayout(info_group)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("路径名称:"))
        self.edit_name = QLineEdit()
        name_layout.addWidget(self.edit_name)
        info_layout.addLayout(name_layout)
        
        layout.addWidget(info_group)
        
        drawing_group = QGroupBox("路径绘制")
        drawing_layout = QVBoxLayout(drawing_group)
        
        self.drawing_widget = GestureDrawingWidget()
        self.drawing_widget.current_tool = "brush"
        self.drawing_widget.pathCompleted.connect(self._on_path_completed)
        self.drawing_widget.pathUpdated.connect(self._on_path_updated)
        drawing_layout.addWidget(self.drawing_widget)
        
        layout.addWidget(drawing_group)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        
        self.btn_clear = QPushButton("清空绘制")
        self.btn_clear.clicked.connect(self._clear_drawing)
        button_box.addButton(self.btn_clear, QDialogButtonBox.ButtonRole.ActionRole)
        
        layout.addWidget(button_box)
        
    def _load_path_data(self):
        if not self.path_key:
            return
            
        path_data = self.gesture_library.trigger_paths.get(self.path_key)
        if not path_data:
            self.logger.error(f"找不到路径: {self.path_key}")
            return
            
        path_name = path_data.get('name', '')
        self.edit_name.setText(path_name)
        
        path = path_data.get('path')
        if path:
            self.current_path = copy.deepcopy(path)
            self.drawing_widget.load_path(self.current_path)
            
    def _on_path_completed(self, path):
        self.current_path = copy.deepcopy(path)
        
    def _on_path_updated(self):
        if self.drawing_widget.completed_paths:
            self.current_path = copy.deepcopy(self.drawing_widget.completed_paths[-1])
            
    def _clear_drawing(self):
        self.drawing_widget.clear_drawing()
        self.current_path = None
        
    def _save_and_accept(self):
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入路径名称")
            return
            
        try:
            if self.is_editing:
                path_data = self.gesture_library.trigger_paths[self.path_key]
                path_data['name'] = name
                if self.current_path:
                    path_data['path'] = self.current_path
            else:
                path_id = self.gesture_library._get_next_path_id()
                path_key = f"path_{path_id}"
                
                new_path_data = {
                    'id': path_id,
                    'name': name,
                    'path': self.current_path
                }
                
                self.gesture_library.trigger_paths[path_key] = new_path_data
                self.path_key = path_key
                
            self.gesture_library.mark_data_changed("trigger_paths")
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"保存路径时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存路径失败: {str(e)}")


class ExecuteActionEditDialog(QDialog):
    def __init__(self, action_key=None, parent=None):
        super().__init__(parent)
        self.logger = get_logger("ExecuteActionEditDialog")
        self.gesture_library = get_gesture_library()
        
        self.action_key = action_key
        self.is_editing = action_key is not None
        
        self.setWindowTitle("编辑执行操作" if self.is_editing else "添加执行操作")
        self.setFixedSize(400, 300)
        
        self.initUI()
        
        if self.is_editing:
            self._load_action_data()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        info_group = QGroupBox("操作信息")
        info_layout = QVBoxLayout(info_group)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("操作名称:"))
        self.edit_name = QLineEdit()
        name_layout.addWidget(self.edit_name)
        info_layout.addLayout(name_layout)
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("操作类型:"))
        self.combo_type = QComboBox()
        self.combo_type.addItem("快捷键", "shortcut")
        type_layout.addWidget(self.combo_type)
        info_layout.addLayout(type_layout)
        
        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel("操作值:"))
        self.edit_value = QLineEdit()
        self.edit_value.setPlaceholderText("例如: Ctrl+C")
        value_layout.addWidget(self.edit_value)
        info_layout.addLayout(value_layout)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
    def _load_action_data(self):
        if not self.action_key:
            return
            
        action_data = self.gesture_library.execute_actions.get(self.action_key)
        if not action_data:
            self.logger.error(f"找不到操作: {self.action_key}")
            return
            
        action_name = action_data.get('name', '')
        action_type = action_data.get('type', 'shortcut')
        action_value = action_data.get('value', '')
        
        self.edit_name.setText(action_name)
        self.edit_value.setText(action_value)
        
        for i in range(self.combo_type.count()):
            if self.combo_type.itemData(i) == action_type:
                self.combo_type.setCurrentIndex(i)
                break
                
    def _save_and_accept(self):
        name = self.edit_name.text().strip()
        action_type = self.combo_type.currentData()
        value = self.edit_value.text().strip()
        
        if not name:
            QMessageBox.warning(self, "警告", "请输入操作名称")
            return
            
        if not value:
            QMessageBox.warning(self, "警告", "请输入操作值")
            return
            
        try:
            if self.is_editing:
                action_data = self.gesture_library.execute_actions[self.action_key]
                action_data['name'] = name
                action_data['type'] = action_type
                action_data['value'] = value
            else:
                action_id = self.gesture_library._get_next_action_id()
                action_key = f"action_{action_id}"
                
                new_action_data = {
                    'id': action_id,
                    'name': name,
                    'type': action_type,
                    'value': value
                }
                
                self.gesture_library.execute_actions[action_key] = new_action_data
                self.action_key = action_key
                
            self.gesture_library.mark_data_changed("execute_actions")
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"保存操作时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存操作失败: {str(e)}")

class TestSimilarityDialog(QDialog):
    def __init__(self, reference_path, parent=None):
        super().__init__(parent)
        self.reference_path = reference_path
        self.test_path = None
        self.similarity_score = 0.0
        self.threshold = 0.70
        
        self.path_analyzer = PathAnalyzer()
        
        try:
            settings = get_settings()
            self.threshold = settings.get("gesture.similarity_threshold", 0.70)
        except:
            self.threshold = 0.70
            
        self.setWindowTitle("测试手势相似度")
        self.setModal(True)
        self.resize(800, 600)
        self.setMinimumSize(700, 500)
        
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("手势相似度测试")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        left_panel = self._create_reference_panel()
        content_layout.addWidget(left_panel, 1)
        
        right_panel = self._create_test_panel()
        content_layout.addWidget(right_panel, 1)
        
        layout.addWidget(content_widget, 1)
        
        similarity_panel = self._create_similarity_panel()
        layout.addWidget(similarity_panel)
        
        button_layout = QHBoxLayout()
        
        clear_btn = QPushButton("清除测试")
        clear_btn.clicked.connect(self._clear_test)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def _create_reference_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #f8f9fa; border-radius: 8px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("参考路径")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #495057; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.reference_display = ReferencePathDisplay(self.reference_path)
        layout.addWidget(self.reference_display, 1)
        
        return panel
        
    def _create_test_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: #f8f9fa; border-radius: 8px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("绘制测试路径")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #495057; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.test_drawing = TestDrawingWidget()
        self.test_drawing.pathCompleted.connect(self._on_test_path_completed)
        layout.addWidget(self.test_drawing, 1)
        
        return panel
        
    def _create_similarity_panel(self):
        panel = QWidget()
        panel.setFixedHeight(120)
        panel.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 15, 20, 15)
        
        self.similarity_title = QLabel("等待绘制测试路径...")
        self.similarity_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #6c757d;")
        self.similarity_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.similarity_title)
        
        self.similarity_bar = QProgressBar()
        self.similarity_bar.setRange(0, 100)
        self.similarity_bar.setValue(0)
        self.similarity_bar.setTextVisible(True)
        self.similarity_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QProgressBar::chunk {
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.similarity_bar)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addStretch()
        
        self.threshold_label = QLabel(f"识别阈值: {self.threshold:.0%}")
        self.threshold_label.setStyleSheet("font-size: 12px; color: #6c757d;")
        threshold_layout.addWidget(self.threshold_label)
        
        layout.addLayout(threshold_layout)
        
        return panel
        
    def _on_test_path_completed(self, path):
        self.test_path = path
        self._calculate_similarity()
        
    def _calculate_similarity(self):
        if not self.test_path or not self.reference_path:
            return
            
        try:
            similarity = self.path_analyzer.calculate_similarity(
                self.reference_path, self.test_path
            )
            
            self.similarity_score = similarity
            self._update_similarity_display()
            
        except Exception as e:
            self.similarity_title.setText(f"计算相似度失败: {str(e)}")
            
    def _update_similarity_display(self):
        percentage = int(self.similarity_score * 100)
        self.similarity_bar.setValue(percentage)
        
        threshold_percentage = int(self.threshold * 100)
        
        if self.similarity_score >= self.threshold:
            color = "#28a745"
            status = "✓ 可识别"
            title_color = "#155724"
        elif self.similarity_score >= self.threshold * 0.8:
            color = "#ffc107"
            status = "⚠ 接近阈值"
            title_color = "#856404"
        else:
            color = "#dc3545"
            status = "✗ 无法识别"
            title_color = "#721c24"
            
        self.similarity_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 14px;
                color: white;
                background-color: #f8f9fa;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)
        
        self.similarity_title.setText(f"相似度: {percentage}% - {status}")
        self.similarity_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {title_color};")
        
    def _clear_test(self):
        self.test_drawing.clear_drawing()
        self.test_path = None
        self.similarity_score = 0.0
        self.similarity_bar.setValue(0)
        self.similarity_title.setText("等待绘制测试路径...")
        self.similarity_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #6c757d;")


class ReferencePathDisplay(QWidget):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setMinimumSize(250, 200)
        self.setStyleSheet("background-color: white; border-radius: 4px;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        if not self.path or not self.path.get('points'):
            painter.setPen(QColor(108, 117, 125))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "无路径数据")
            return
            
        points = self.path['points']
        if not points:
            return
            
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        margin = 20
        width = self.width() - 2 * margin
        height = self.height() - 2 * margin
        
        path_width = max_x - min_x
        path_height = max_y - min_y
        
        if path_width == 0 or path_height == 0:
            scale = 1.0
        else:
            scale = min(width / path_width, height / path_height) * 0.8
        
        offset_x = margin + (width - path_width * scale) / 2 - min_x * scale
        offset_y = margin + (height - path_height * scale) / 2 - min_y * scale
        
        pen = QPen(QColor(0, 123, 255), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        connections = self.path.get('connections', [])
        for conn in connections:
            from_idx = conn['from']
            to_idx = conn['to']
            
            if 0 <= from_idx < len(points) and 0 <= to_idx < len(points):
                from_point = points[from_idx]
                to_point = points[to_idx]
                
                x1 = from_point[0] * scale + offset_x
                y1 = from_point[1] * scale + offset_y
                x2 = to_point[0] * scale + offset_x
                y2 = to_point[1] * scale + offset_y
                
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        painter.setPen(QPen(QColor(220, 53, 69), 2))
        painter.setBrush(QColor(255, 255, 255))
        
        for i, point in enumerate(points):
            x = point[0] * scale + offset_x
            y = point[1] * scale + offset_y
            painter.drawEllipse(int(x) - 4, int(y) - 4, 8, 8)


class TestDrawingWidget(QWidget):
    pathCompleted = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.path_analyzer = PathAnalyzer()
        
        self.drawing = False
        self.current_path = []
        self.completed_path = None
        
        self.setMinimumSize(250, 200)
        self.setStyleSheet("background-color: white; border-radius: 4px;")
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.current_path = [event.pos()]
            self.completed_path = None
            self.update()
            
    def mouseMoveEvent(self, event):
        if self.drawing:
            self.current_path.append(event.pos())
            self.update()
            
    def mouseReleaseEvent(self, event):
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            
            if len(self.current_path) > 5:
                raw_points = [(p.x(), p.y(), 0.5, 0.0, 1) for p in self.current_path]
                formatted_path = self.path_analyzer.format_raw_path(raw_points)
                
                if formatted_path and formatted_path.get('points'):
                    self.completed_path = formatted_path
                    self.pathCompleted.emit(formatted_path)
                    
            self.current_path = []
            self.update()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        if not self.completed_path and not self.current_path:
            painter.setPen(QColor(108, 117, 125))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "在此区域绘制测试手势")
            return
            
        if self.current_path:
            pen = QPen(QColor(108, 117, 125), 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            for i in range(1, len(self.current_path)):
                painter.drawLine(self.current_path[i-1], self.current_path[i])
                
        if self.completed_path:
            self._draw_completed_path(painter)
            
    def _draw_completed_path(self, painter):
        points = self.completed_path.get('points', [])
        if not points:
            return
            
        pen = QPen(QColor(40, 167, 69), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        connections = self.completed_path.get('connections', [])
        for conn in connections:
            from_idx = conn['from']
            to_idx = conn['to']
            
            if 0 <= from_idx < len(points) and 0 <= to_idx < len(points):
                from_point = points[from_idx]
                to_point = points[to_idx]
                painter.drawLine(int(from_point[0]), int(from_point[1]), 
                               int(to_point[0]), int(to_point[1]))
        
        painter.setPen(QPen(QColor(220, 53, 69), 2))
        painter.setBrush(QColor(255, 255, 255))
        
        for point in points:
            painter.drawEllipse(int(point[0]) - 4, int(point[1]) - 4, 8, 8)
            
    def clear_drawing(self):
        self.current_path = []
        self.completed_path = None
        self.drawing = False
        self.update()