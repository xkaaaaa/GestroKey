"""
绘制模块

包含各种画笔的绘制逻辑
"""

import math
import time
from abc import ABC, abstractmethod
from qtpy.QtCore import QPoint, Qt
from qtpy.QtGui import QColor, QPainter, QPainterPath, QPen


class BaseBrush(ABC):
    """画笔基类"""
    
    def __init__(self, width=2, color=None):
        self.width = width
        self.color = color or QColor(0, 120, 255, 255)
        self.points = []  # 当前笔画的点
        self.start_time = 0
        
    @abstractmethod
    def start_stroke(self, x, y, pressure=0.5):
        """开始一笔"""
        pass
        
    @abstractmethod
    def add_point(self, x, y, pressure=0.5):
        """添加点到当前笔画"""
        pass
        
    @abstractmethod
    def end_stroke(self):
        """结束当前笔画"""
        pass
        
    @abstractmethod
    def draw(self, painter, points=None):
        """绘制笔画"""
        pass


class PencilBrush(BaseBrush):
    """铅笔画笔 - 原有的绘制效果"""
    
    def __init__(self, width=2, color=None):
        super().__init__(width, color)
        self.name = "铅笔"
        
    def start_stroke(self, x, y, pressure=0.5):
        """开始一笔"""
        self.points = [[x, y, pressure, time.time()]]
        self.start_time = time.time()
        
    def add_point(self, x, y, pressure=0.5):
        """添加点到当前笔画"""
        if self.points:
            # 检查距离，避免过于密集的点
            last_point = self.points[-1]
            distance = math.sqrt((x - last_point[0])**2 + (y - last_point[1])**2)
            if distance >= 2.0:  # 最小距离阈值
                self.points.append([x, y, pressure, time.time()])
        else:
            self.points.append([x, y, pressure, time.time()])
        
    def end_stroke(self):
        """结束当前笔画"""
        pass
        
    def draw(self, painter, points=None):
        """绘制铅笔笔画"""
        draw_points = points or self.points
        if len(draw_points) < 1:
            return
            
        # 启用抗锯齿以获得平滑边缘
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # 设置画笔
        pen = QPen(self.color)
        pen.setWidth(self.width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        if len(draw_points) == 1:
            # 只有一个点，绘制圆点
            painter.drawPoint(int(draw_points[0][0]), int(draw_points[0][1]))
        else:
            # 绘制连续路径
            path = QPainterPath()
            path.moveTo(draw_points[0][0], draw_points[0][1])
            
            for point in draw_points[1:]:
                path.lineTo(point[0], point[1])
                
            painter.drawPath(path)


class WaterBrush(BaseBrush):
    """水性笔画笔 - 新出现的点由小变大，直到预设粗细"""
    
    def __init__(self, width=2, color=None):
        super().__init__(width, color)
        self.name = "水性笔"
        self.growth_duration = 0.15  # 点从小到大的时间（秒），加快变粗速度
        self.min_size_ratio = 0.1  # 最小尺寸比例，让变化更明显
        
    def start_stroke(self, x, y, pressure=0.5):
        """开始一笔"""
        self.points = [[x, y, pressure, time.time()]]
        self.start_time = time.time()
        
    def add_point(self, x, y, pressure=0.5):
        """添加点到当前笔画"""
        if self.points:
            # 检查距离，避免过于密集的点
            last_point = self.points[-1]
            distance = math.sqrt((x - last_point[0])**2 + (y - last_point[1])**2)
            if distance >= 1.0:  # 水性笔更密集，提高流畅度
                self.points.append([x, y, pressure, time.time()])
        else:
            self.points.append([x, y, pressure, time.time()])
        
    def end_stroke(self):
        """结束当前笔画"""
        pass
        
    def _calculate_point_size(self, point_time, current_time, is_stroke_ended=False):
        """计算点的大小"""
        if is_stroke_ended:
            # 笔画结束后，所有点都保持最大尺寸
            return self.width
            
        # 计算点存在的时间
        age = current_time - point_time
        
        if age >= self.growth_duration:
            # 已经达到最大尺寸
            return self.width
        else:
            # 线性增长
            growth_ratio = age / self.growth_duration
            min_size = self.width * self.min_size_ratio
            return min_size + (self.width - min_size) * growth_ratio
        
    def draw(self, painter, points=None, current_time=None, is_stroke_ended=False):
        """绘制水性笔笔画"""
        draw_points = points or self.points
        if not draw_points:
            return
            
        if current_time is None:
            current_time = time.time()
            
        # 启用抗锯齿以获得平滑边缘
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        if len(draw_points) == 1:
            # 只有一个点，绘制圆点
            point = draw_points[0]
            x, y = point[0], point[1]
            point_time = point[3] if len(point) >= 4 else current_time
            
            point_size = self._calculate_point_size(point_time, current_time, is_stroke_ended)
            pen = QPen(self.color)
            pen.setWidth(max(1, int(point_size)))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawPoint(int(x), int(y))
            return
        
        if is_stroke_ended:
            # 笔画结束后，绘制为统一的连续路径（用于消失效果）
            path = QPainterPath()
            path.moveTo(draw_points[0][0], draw_points[0][1])
            
            for point in draw_points[1:]:
                path.lineTo(point[0], point[1])
            
            # 使用最大粗细绘制
            pen = QPen(self.color)
            pen.setWidth(self.width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)
        else:
            # 绘制过程中，使用动态效果，让点持续变粗
            for i in range(1, len(draw_points)):
                current_point = draw_points[i]
                prev_point = draw_points[i-1]
                
                # 计算当前点和前一个点的大小
                current_time_point = current_point[3] if len(current_point) >= 4 else current_time
                prev_time_point = prev_point[3] if len(prev_point) >= 4 else current_time
                
                current_size = self._calculate_point_size(current_time_point, current_time, is_stroke_ended)
                prev_size = self._calculate_point_size(prev_time_point, current_time, is_stroke_ended)
                
                # 使用平均大小绘制这段线条
                avg_size = (current_size + prev_size) / 2
                
                # 设置画笔属性
                pen = QPen(self.color)
                pen.setWidth(max(1, int(avg_size)))
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                
                # 绘制线段
                painter.drawLine(
                    int(prev_point[0]), int(prev_point[1]),
                    int(current_point[0]), int(current_point[1])
                )


class DrawingModule:
    """绘制模块管理器"""
    
    def __init__(self):
        self.brushes = {
            "pencil": PencilBrush,
            "water": WaterBrush
        }
        self.current_brush_type = "pencil"
        self.current_brush = None
        
    def set_brush_type(self, brush_type):
        """设置画笔类型"""
        if brush_type in self.brushes:
            self.current_brush_type = brush_type
            return True
        return False
        
    def get_brush_types(self):
        """获取所有画笔类型"""
        return list(self.brushes.keys())
        
    def create_brush(self, width=2, color=None):
        """创建当前类型的画笔实例"""
        brush_class = self.brushes[self.current_brush_type]
        return brush_class(width, color)
        
    def get_current_brush_type(self):
        """获取当前画笔类型"""
        return self.current_brush_type 