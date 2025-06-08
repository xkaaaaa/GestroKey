import sys
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor

try:
    from core.logger import get_logger
    from core.path_analyzer import PathAnalyzer
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger
    from core.path_analyzer import PathAnalyzer


class GestureDrawingWidget(QWidget):
    """手势绘制组件，用于在手势管理界面绘制手势路径"""
    
    pathCompleted = pyqtSignal(dict)  # 路径完成信号，发送格式化的路径
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger("GestureDrawingWidget")
        self.path_analyzer = PathAnalyzer()
        
        # 绘制状态
        self.drawing = False
        self.current_path = []
        self.completed_paths = []
        
        # 设置最小尺寸
        self.setMinimumSize(300, 200)
        self.setStyleSheet("background-color: white; border: 1px solid gray;")
        
        self.initUI()
        
    def initUI(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 顶部说明标签
        self.status_label = QLabel("在下方区域绘制手势（只能绘制一笔，新绘制会清除旧的）")
        self.status_label.setStyleSheet("color: blue; font-size: 12px; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("清除")
        self.clear_button.clicked.connect(self.clear_drawing)
        
        self.use_button = QPushButton("使用此路径")
        self.use_button.clicked.connect(self.use_current_path)
        self.use_button.setEnabled(False)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.use_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 绘图区域（使用widget自身）
        layout.addStretch()
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton and event.pos().y() > 60:
            # 如果已有完成的路径，先清除
            if self.completed_paths:
                self.clear_drawing()
            
            self.drawing = True
            self.current_path = [event.pos()]
            self.status_label.setText("正在绘制...")
            self.update()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.drawing and event.pos().y() > 60:
            self.current_path.append(event.pos())
            self.update()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            if len(self.current_path) > 1:
                # 格式化路径
                raw_points = [(p.x(), p.y(), 0.5, 0.0, 1) for p in self.current_path]
                formatted_path = self.path_analyzer.format_raw_path(raw_points)
                
                if formatted_path and formatted_path.get('points'):
                    self.completed_paths.append(formatted_path)
                    points_count = len(formatted_path.get('points', []))
                    connections_count = len(formatted_path.get('connections', []))
                    self.status_label.setText(f"路径已格式化：{points_count}个关键点，{connections_count}条连接（自动缩放显示）")
                    self.use_button.setEnabled(True)
                    self.logger.info(f"格式化路径完成：{points_count}个关键点")
                else:
                    self.status_label.setText("路径格式化失败，请重新绘制")
                    self.use_button.setEnabled(False)
            else:
                self.status_label.setText("绘制路径太短，请重新绘制")
                self.use_button.setEnabled(False)
            
            self.current_path = []
            self.update()
            
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制已完成的路径（蓝色）
        painter.setPen(QPen(QColor(0, 120, 255), 2))
        for path in self.completed_paths:
            self._draw_formatted_path(painter, path)
        
        # 绘制当前路径（红色）- 在绘制区域内
        if self.current_path:
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            # 确保绘制在合适的区域内（避免与按钮重叠）
            for i in range(len(self.current_path) - 1):
                start_pos = self.current_path[i]
                end_pos = self.current_path[i + 1]
                
                # 限制绘制区域，避免与顶部按钮重叠
                if start_pos.y() > 60 and end_pos.y() > 60:
                    painter.drawLine(start_pos, end_pos)
        
    def _draw_formatted_path(self, painter, path):
        """绘制格式化路径（自动缩放到最优大小）"""
        points = path.get('points', [])
        connections = path.get('connections', [])
        
        if not points or not connections:
            return
        
        # 计算路径的边界框
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        path_width = max_x - min_x
        path_height = max_y - min_y
        
        # 获取可用的绘制区域（减去边距）
        margin = 30  # 边距
        widget_width = self.width() - 2 * margin
        widget_height = self.height() - 100  # 上下留空间给按钮和标签
        
        # 确保最小显示区域
        if widget_width < 100:
            widget_width = 100
        if widget_height < 100:
            widget_height = 100
        
        # 计算缩放比例，充分利用显示区域
        if path_width > 0 and path_height > 0:
            scale_x = widget_width / path_width
            scale_y = widget_height / path_height
            scale = min(scale_x, scale_y)  # 保持宽高比，使用较小的缩放比例
        else:
            # 处理点或线的情况
            scale = 1.0
        
        # 如果路径太小，适当放大
        min_scale = 0.5  # 最小缩放比例
        max_scale = 10.0  # 最大缩放比例
        scale = max(min_scale, min(scale, max_scale))
        
        # 计算缩放后的尺寸和居中偏移
        scaled_width = path_width * scale
        scaled_height = path_height * scale
        offset_x = (self.width() - scaled_width) / 2
        offset_y = (self.height() - scaled_height) / 2 + 20  # 稍微向下偏移
        
        # 转换点坐标
        def transform_point(point):
            x = (point[0] - min_x) * scale + offset_x
            y = (point[1] - min_y) * scale + offset_y
            return QPoint(int(x), int(y))
        
        # 绘制连接线
        for conn in connections:
            from_idx = conn.get('from', 0)
            to_idx = conn.get('to', 0)
            
            if from_idx < len(points) and to_idx < len(points):
                start_point = transform_point(points[from_idx])
                end_point = transform_point(points[to_idx])
                painter.drawLine(start_point, end_point)
        
        # 绘制关键点（红色圆点）
        old_pen = painter.pen()
        painter.setPen(QPen(QColor(255, 0, 0), 4))
        for point in points:
            transformed_point = transform_point(point)
            painter.drawEllipse(transformed_point, 3, 3)
        painter.setPen(old_pen)
        
    def clear_drawing(self):
        """清除绘制内容"""
        self.current_path = []
        self.completed_paths = []
        self.use_button.setEnabled(False)
        self.status_label.setText("在下方区域绘制手势（只能绘制一笔，新绘制会清除旧的）")
        self.update()
        
    def use_current_path(self):
        """使用当前路径"""
        if self.completed_paths:
            # 使用最后一个完成的路径
            path = self.completed_paths[-1]
            self.pathCompleted.emit(path)
            self.logger.info("发送格式化路径给手势管理界面")
        
    def load_path(self, path):
        """加载并显示指定路径（用于编辑现有手势）"""
        if path and path.get('points'):
            self.clear_drawing()  # 先清除现有内容
            self.completed_paths = [path]
            self.use_button.setEnabled(True)
            points_count = len(path.get('points', []))
            connections_count = len(path.get('connections', []))
            self.status_label.setText(f"已加载路径：{points_count}个关键点，{connections_count}条连接（自动缩放显示）")
            self.update()
        else:
            self.clear_drawing() 