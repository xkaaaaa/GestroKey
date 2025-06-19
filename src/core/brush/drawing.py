"""
绘制模块

包含各种画笔的绘制逻辑
"""

import math
import time
import random
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


class CalligraphyBrush(BaseBrush):
    """毛笔画笔 - 模拟毛笔书法效果"""
    
    def __init__(self, width=2, color=None):
        super().__init__(width, color)
        self.name = "毛笔"
        self.last_point = None
        self.last_width = 0
        self.last_time = None
        
    def start_stroke(self, x, y, pressure=0.5):
        """开始一笔"""
        self.points = [[x, y, pressure, time.time()]]
        self.start_time = time.time()
        self.last_point = QPoint(x, y)
        self.last_width = self.width
        self.last_time = time.time()
        
    def add_point(self, x, y, pressure=0.5):
        """添加点到当前笔画"""
        if self.points:
            # 检查距离，避免过于密集的点
            last_point = self.points[-1]
            distance = math.sqrt((x - last_point[0])**2 + (y - last_point[1])**2)
            if distance >= 1.5:  # 毛笔点间距适中
                self.points.append([x, y, pressure, time.time()])
        else:
            self.points.append([x, y, pressure, time.time()])
        
    def end_stroke(self):
        """结束当前笔画"""
        pass
    
    def draw(self, painter, points=None):
        """绘制毛笔笔画"""
        draw_points = points or self.points
        if len(draw_points) < 1:
            return
            
        # 启用抗锯齿以获得平滑边缘
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        if len(draw_points) == 1:
            # 只有一个点，绘制圆点
            point = draw_points[0]
            x, y = point[0], point[1]
            pen = QPen(self.color)
            pen.setWidth(self.width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawPoint(int(x), int(y))
            return
        
        # 使用自定义绘制方法模拟毛笔效果
        self._draw_calligraphy_stroke(painter, draw_points)
    
    def _draw_calligraphy_stroke(self, painter, points):
        """绘制毛笔笔画的核心方法，参考brush_pyqt.py的算法"""
        if len(points) < 2:
            return
            
        for i in range(1, len(points)):
            from_point = points[i-1]
            to_point = points[i]
            
            from_p = QPoint(int(from_point[0]), int(from_point[1]))
            to_p = QPoint(int(to_point[0]), int(to_point[1]))
            
            # 计算绘制参数
            duration = 0.01
            if len(from_point) >= 4 and len(to_point) >= 4:
                duration = to_point[3] - from_point[3]
            
            distance = math.hypot(to_p.x() - from_p.x(), to_p.y() - from_p.y())
            
            # 动态笔画宽度
            base = self.width * 1.2
            delta = self.width * 0.2
            width = base + delta * (1 - 2/(1+math.exp(-0.3*(distance-5))))
            
            # 平滑处理
            if hasattr(self, 'last_width'):
                width = (width + self.last_width) / 2
            self.last_width = width
            
            self._draw_brush_segment(painter, from_p, to_p, width, duration)
    
    def _draw_brush_segment(self, painter, from_p, to_p, width, duration=0.01):
        """绘制毛笔笔画段，基于brush_pyqt.py的算法"""
        steps = max(1, int(math.hypot(to_p.x() - from_p.x(), to_p.y() - from_p.y()) / 2))
        angle = math.atan2(to_p.y() - from_p.y(), to_p.x() - from_p.x())
        angle_factor = 0.8 + 0.4 * abs(math.cos(angle))
        denom = max(0.001, duration * steps)
        
        # 随机决定本次笔画是深到浅还是浅到深
        gradient_reverse = random.random() < 0.5
        
        for i in range(steps):
            t = i / steps
            x = int(from_p.x() + (to_p.x() - from_p.x()) * t + (random.random()-0.5)*0.2*width)
            y = int(from_p.y() + (to_p.y() - from_p.y()) * t + (random.random()-0.5)*0.2*width)
            w = int(width * (0.95 + random.random()*0.1) * angle_factor)
            
            # 墨色渐变：t从0到1，深到浅或浅到深
            if gradient_reverse:
                ink_factor = 0.7 + 0.3 * (1-t)
            else:
                ink_factor = 0.7 + 0.3 * t
            
            # 基于原有颜色调整为墨色效果，保留用户设置的颜色倾向
            base_color = self.color
            if isinstance(base_color, (list, tuple)):
                r, g, b = base_color[:3]
            else:
                r, g, b = base_color.red(), base_color.green(), base_color.blue()
            
            # 应用墨色效果，但保留颜色倾向，而不是完全转换为灰度
            factor = ink_factor * 0.8  # 调整因子，让颜色不那么暗
            color = QColor(
                max(0, min(255, int(r * factor) + random.randint(-20, 20))),
                max(0, min(255, int(g * factor) + random.randint(-20, 20))), 
                max(0, min(255, int(b * factor) + random.randint(-20, 20)))
            )
            
            speed = max(0.01, math.hypot(to_p.x() - from_p.x(), to_p.y() - from_p.y()) / denom)
            opacity = max(0.35, min(1.0, 1.2 - speed*0.18 - duration*1.2))
            jump_prob = min(0.25, 0.08 + speed*0.12 + max(0, 10-width)*0.01)
            
            if random.random() < jump_prob:
                continue
                
            painter.save()
            painter.translate(x, y)
            painter.rotate(math.degrees(angle) + (random.random()-0.5)*8)
            painter.setOpacity(opacity)
            painter.fillRect(-w//2, -w//2, w, w, color)
            painter.restore()
            
            # 添加毛笔的毛丝效果，使用相似颜色
            if random.random() < 0.7:
                bend_len = w * (0.7 + random.random()*0.6)
                bend_angle = angle + (random.random()-0.5)*0.7
                bx = int(x + math.cos(bend_angle) * bend_len)
                by = int(y + math.sin(bend_angle) * bend_len)
                # 毛丝使用稍微暗一些的相同色调
                bend_color = QColor(
                    max(0, min(255, int(r * factor * 0.7) + random.randint(-15, 15))),
                    max(0, min(255, int(g * factor * 0.7) + random.randint(-15, 15))),
                    max(0, min(255, int(b * factor * 0.7) + random.randint(-15, 15)))
                )
                painter.save()
                painter.setPen(bend_color)
                painter.setOpacity(0.25 + random.random()*0.2)
                painter.drawLine(x, y, bx, by)
                painter.restore()
            
            # 随机墨滴效果，使用相同色调
            if random.random() < 0.18:
                zx = int(x + (random.random()-0.5)*w*1.5)
                zy = int(y + (random.random()-0.5)*w*1.5)
                zcolor = QColor(
                    max(0, min(255, int(r * factor * 0.9) + random.randint(-30, 30))),
                    max(0, min(255, int(g * factor * 0.9) + random.randint(-30, 30))),
                    max(0, min(255, int(b * factor * 0.9) + random.randint(-30, 30)))
                )
                painter.save()
                painter.setPen(zcolor)
                painter.setOpacity(0.18 + random.random()*0.18)
                painter.drawLine(x, y, zx, zy)
                painter.restore()
                
            # 墨晕效果，使用相同色调
            if random.random() < 0.15:
                painter.save()
                painter.translate(x + (random.random()-0.5)*w, y + (random.random()-0.5)*w)
                color2 = QColor(
                    max(0, min(255, int(r * factor * 0.8) + random.randint(-25, 25))),
                    max(0, min(255, int(g * factor * 0.8) + random.randint(-25, 25))),
                    max(0, min(255, int(b * factor * 0.8) + random.randint(-25, 25)))
                )
                painter.setOpacity(0.2 + random.random()*0.2)
                painter.fillRect(-w//4, -w//4, w//2, w//2, color2)
                painter.restore()


class DrawingModule:
    """绘制模块管理器"""
    
    def __init__(self):
        self.brushes = {
            "pencil": PencilBrush,
            "water": WaterBrush,
            "calligraphy": CalligraphyBrush
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