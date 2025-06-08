import sys
import os
import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QPolygon

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
        # 设置为简洁布局，无按钮无提示文字
        self.setLayout(QVBoxLayout())
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 每次新绘制都自动清除之前的内容
            self.clear_drawing()
            
            self.drawing = True
            self.current_path = [event.pos()]
            self.update()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.drawing:
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
                    # 自动使用此路径
                    self.pathCompleted.emit(formatted_path)
                    self.logger.info(f"自动使用格式化路径：{len(formatted_path.get('points', []))}个关键点")
            
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
        
        # 绘制当前路径（红色）
        if self.current_path:
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            for i in range(len(self.current_path) - 1):
                painter.drawLine(self.current_path[i], self.current_path[i + 1])
        
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
        
        # 绘制连接线和方向箭头
        painter.setPen(QPen(QColor(0, 120, 255), 2))
        for conn in connections:
            from_idx = conn.get('from', 0)
            to_idx = conn.get('to', 0)
            
            if from_idx < len(points) and to_idx < len(points):
                start_point = transform_point(points[from_idx])
                end_point = transform_point(points[to_idx])
                painter.drawLine(start_point, end_point)
                
                # 在线条中间绘制方向箭头
                self._draw_direction_arrow(painter, start_point, end_point)
        
        # 绘制关键点 - 起点、终点、中间点用不同颜色
        old_pen = painter.pen()
        
        for i, point in enumerate(points):
            transformed_point = transform_point(point)
            
            if i == 0:
                # 起点 - 绿色，较大
                painter.setPen(QPen(QColor(0, 200, 0), 3))
                painter.setBrush(QColor(0, 200, 0))
                painter.drawEllipse(transformed_point.x() - 6, transformed_point.y() - 6, 12, 12)
            elif i == len(points) - 1:
                # 终点 - 红色
                if len(points) == 1:
                    # 只有一个点时，绘制一个小一点的红色圆点在绿色内部
                    painter.setPen(QPen(QColor(255, 0, 0), 2))
                    painter.setBrush(QColor(255, 0, 0))
                    painter.drawEllipse(transformed_point.x() - 3, transformed_point.y() - 3, 6, 6)
                else:
                    # 有多个点时，终点稍微小一点
                    painter.setPen(QPen(QColor(255, 0, 0), 3))
                    painter.setBrush(QColor(255, 0, 0))
                    painter.drawEllipse(transformed_point.x() - 4, transformed_point.y() - 4, 8, 8)
            else:
                # 中间点 - 蓝色，最小
                painter.setPen(QPen(QColor(0, 120, 255), 2))
                painter.setBrush(QColor(0, 120, 255))
                painter.drawEllipse(transformed_point.x() - 2, transformed_point.y() - 2, 4, 4)
        
        painter.setPen(old_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)  # 重置画刷
    
    def _draw_direction_arrow(self, painter, start_point, end_point):
        """在线条中间绘制方向箭头"""
        # 计算中点
        mid_x = (start_point.x() + end_point.x()) / 2
        mid_y = (start_point.y() + end_point.y()) / 2
        mid_point = QPoint(int(mid_x), int(mid_y))
        
        # 计算方向向量
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        
        # 如果线条太短，不画箭头
        length = math.sqrt(dx * dx + dy * dy)
        if length < 20:
            return
        
        # 标准化方向向量
        dx /= length
        dy /= length
        
        # 箭头大小
        arrow_length = 8
        arrow_width = 4
        
        # 计算箭头的三个点
        # 箭头顶点（指向前进方向）
        arrow_tip_x = mid_x + dx * arrow_length / 2
        arrow_tip_y = mid_y + dy * arrow_length / 2
        
        # 箭头两侧的点
        # 垂直向量 (-dy, dx)
        arrow_left_x = mid_x - dx * arrow_length / 2 - dy * arrow_width
        arrow_left_y = mid_y - dy * arrow_length / 2 + dx * arrow_width
        
        arrow_right_x = mid_x - dx * arrow_length / 2 + dy * arrow_width
        arrow_right_y = mid_y - dy * arrow_length / 2 - dx * arrow_width
        
        # 创建箭头多边形
        arrow_polygon = QPolygon([
            QPoint(int(arrow_tip_x), int(arrow_tip_y)),
            QPoint(int(arrow_left_x), int(arrow_left_y)),
            QPoint(int(arrow_right_x), int(arrow_right_y))
        ])
        
        # 绘制箭头
        old_pen = painter.pen()
        old_brush = painter.brush()
        painter.setPen(QPen(QColor(255, 100, 0), 1))  # 橙色箭头
        painter.setBrush(QColor(255, 100, 0))
        painter.drawPolygon(arrow_polygon)
        painter.setPen(old_pen)
        painter.setBrush(old_brush)
    
    def clear_drawing(self):
        """清除绘制内容"""
        self.current_path = []
        self.completed_paths = []
        self.update()
        
    def load_path(self, path):
        """加载并显示指定路径（用于编辑现有手势）"""
        if path and path.get('points'):
            self.clear_drawing()  # 先清除现有内容
            self.completed_paths = [path]
            self.update()
        else:
            self.clear_drawing() 