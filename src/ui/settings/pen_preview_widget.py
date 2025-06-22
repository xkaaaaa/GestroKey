"""
动态笔尖预览控件

用于在设置页面预览不同画笔效果的动态组件
"""

import os
import sys
import math
import time
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QColor, QPainter, QPen, QPixmap
from qtpy.QtWidgets import QWidget

from core.brush.drawing import DrawingModule


class PenPreviewWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pen_width = 3
        self.pen_color = [0, 120, 255]
        self.setMinimumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        
        self.animation_progress = 0.0
        self.animation_speed = 0.04
        self.is_playing = False
        
        try:
            self.drawing_module = DrawingModule()
        except Exception as e:
            self.drawing_module = None
        
        self._generate_gesture_path()
        
        self.drawing_buffer = None
        self.previous_buffer = None
        self.fade_progress = 0.0
        self.fade_duration = 0.5
        self.current_brush = None

    def _generate_gesture_path(self):
        """根据画笔粗细生成合适的随机形状"""
        import random
        
        if self.pen_width <= 3:
            shape_types = ['wave', 'spiral', 'heart', 'star', 'circle', 'triangle', 'diamond', 'infinity', 
                          'sine_wave', 'cosine_wave', 's_curve', 'flower', 'butterfly', 'figure_eight', 'zigzag']
        elif self.pen_width <= 8:
            shape_types = ['wave', 'circle', 'triangle', 'diamond', 'simple_star', 'oval', 
                          'sine_wave', 's_curve', 'simple_flower', 'figure_eight']
        else:
            shape_types = ['line', 'simple_wave', 'large_circle', 'square', 'simple_sine']
        
        shape_type = random.choice(shape_types)
        self.gesture_points = []
        
        t_values = [i / 100.0 for i in range(101)]
        
        if shape_type == 'wave':
            for t in t_values:
                x = t
                y = 0.5 + 0.3 * math.sin(t * math.pi * 2) * math.sin(t * math.pi)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'simple_wave':
            for t in t_values:
                x = t
                y = 0.5 + 0.2 * math.sin(t * math.pi * 1.5)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'line':
            for t in t_values:
                x = t
                y = 0.5
                self.gesture_points.append((x, y))
                
        elif shape_type == 'circle':
            for t in t_values:
                angle = t * 2 * math.pi
                x = 0.5 + 0.3 * math.cos(angle)
                y = 0.5 + 0.3 * math.sin(angle)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'large_circle':
            for t in t_values:
                angle = t * 2 * math.pi
                x = 0.5 + 0.25 * math.cos(angle)
                y = 0.5 + 0.25 * math.sin(angle)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'triangle':
            for t in t_values:
                if t <= 0.33:
                    x = 0.2 + t * 1.8
                    y = 0.8
                elif t <= 0.66:
                    progress = (t - 0.33) / 0.33
                    x = 0.8 - progress * 0.3
                    y = 0.8 - progress * 0.6
                else:
                    progress = (t - 0.66) / 0.34
                    x = 0.5 - progress * 0.3
                    y = 0.2 + progress * 0.6
                self.gesture_points.append((x, y))
                
        elif shape_type == 'square':
            for t in t_values:
                if t <= 0.25:
                    x = 0.2 + t * 2.4
                    y = 0.2
                elif t <= 0.5:
                    x = 0.8
                    y = 0.2 + (t - 0.25) * 2.4
                elif t <= 0.75:
                    x = 0.8 - (t - 0.5) * 2.4
                    y = 0.8
                else:
                    x = 0.2
                    y = 0.8 - (t - 0.75) * 2.4
                self.gesture_points.append((x, y))
                
        elif shape_type == 'heart':
            for t in t_values:
                angle = t * 2 * math.pi
                x = 0.5 + 0.2 * (16 * math.sin(angle)**3) / 16
                y = 0.4 - 0.15 * (13 * math.cos(angle) - 5 * math.cos(2*angle) - 2 * math.cos(3*angle) - math.cos(4*angle)) / 16
                self.gesture_points.append((x, y))
                
        elif shape_type == 'star':
            for t in t_values:
                angle = t * 2 * math.pi
                if int(t * 10) % 2 == 0:
                    radius = 0.3
                else:
                    radius = 0.15
                x = 0.5 + radius * math.cos(angle - math.pi/2)
                y = 0.5 + radius * math.sin(angle - math.pi/2)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'simple_star':
            for t in t_values:
                angle = t * 2 * math.pi
                if int(t * 5) % 2 == 0:
                    radius = 0.25
                else:
                    radius = 0.15
                x = 0.5 + radius * math.cos(angle - math.pi/2)
                y = 0.5 + radius * math.sin(angle - math.pi/2)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'diamond':
            for t in t_values:
                if t <= 0.25:
                    x = 0.5 + t * 1.2
                    y = 0.5 + t * 1.2
                elif t <= 0.5:
                    progress = t - 0.25
                    x = 0.8 - progress * 1.2
                    y = 0.8 - progress * 1.2
                elif t <= 0.75:
                    progress = t - 0.5
                    x = 0.5 - progress * 1.2
                    y = 0.5 - progress * 1.2
                else:
                    progress = t - 0.75
                    x = 0.2 + progress * 1.2
                    y = 0.2 + progress * 1.2
                self.gesture_points.append((x, y))
                
        elif shape_type == 'spiral':
            for t in t_values:
                angle = t * 4 * math.pi
                radius = 0.05 + t * 0.25
                x = 0.5 + radius * math.cos(angle)
                y = 0.5 + radius * math.sin(angle)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'infinity':
            for t in t_values:
                angle = t * 2 * math.pi
                x = 0.5 + 0.3 * math.cos(angle) / (1 + math.sin(angle)**2)
                y = 0.5 + 0.2 * math.sin(angle) * math.cos(angle) / (1 + math.sin(angle)**2)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'oval':
            for t in t_values:
                angle = t * 2 * math.pi
                x = 0.5 + 0.35 * math.cos(angle)
                y = 0.5 + 0.2 * math.sin(angle)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'sine_wave':
            for t in t_values:
                x = t
                y = 0.5 + 0.25 * math.sin(t * 2 * math.pi)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'simple_sine':
            for t in t_values:
                x = t
                y = 0.5 + 0.15 * math.sin(t * math.pi)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'cosine_wave':
            for t in t_values:
                x = t
                y = 0.5 + 0.25 * math.cos(t * 2 * math.pi)
                self.gesture_points.append((x, y))
                
        elif shape_type == 's_curve':
            for t in t_values:
                x = t
                y = 0.5 + 0.3 * math.sin(t * math.pi)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'flower':
            for t in t_values:
                angle = t * 2 * math.pi
                radius = 0.2 + 0.1 * math.cos(5 * angle)
                x = 0.5 + radius * math.cos(angle)
                y = 0.5 + radius * math.sin(angle)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'simple_flower':
            for t in t_values:
                angle = t * 2 * math.pi
                radius = 0.15 + 0.08 * math.cos(3 * angle)
                x = 0.5 + radius * math.cos(angle)
                y = 0.5 + radius * math.sin(angle)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'butterfly':
            for t in t_values:
                angle = t * 2 * math.pi
                radius = math.exp(math.cos(angle)) - 2 * math.cos(4 * angle) + math.sin(angle/12)**5
                radius = radius * 0.05 + 0.1
                x = 0.5 + radius * math.cos(angle)
                y = 0.5 + radius * math.sin(angle)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'figure_eight':
            for t in t_values:
                angle = t * 2 * math.pi
                x = 0.5 + 0.25 * math.sin(angle)
                y = 0.5 + 0.2 * math.sin(2 * angle)
                self.gesture_points.append((x, y))
                
        elif shape_type == 'zigzag':
            for t in t_values:
                x = t
                y = 0.5 + 0.2 * (2 * (t * 4 - math.floor(t * 4)) - 1)
                self.gesture_points.append((x, y))

    def update_pen(self, width, color, brush_type=None):
        self.pen_width = width
        self.pen_color = color[:]
        
        if self.drawing_module and brush_type:
            self.drawing_module.set_brush_type(brush_type)
        
        self._generate_gesture_path()
        self._start_animation()

    def _start_animation(self):
        self.animation_progress = 0.0
        self.is_playing = True
        
        if self.drawing_buffer:
            self.previous_buffer = QPixmap(self.drawing_buffer)
        self.fade_progress = 0.0
        
        self.animation_start_time = time.time()
        
        self._create_drawing_buffer()
        
        if self.drawing_module:
            color = QColor(*self.pen_color)
            self.current_brush = self.drawing_module.create_brush(self.pen_width, color)
            
            screen_points = self._convert_to_screen_coords(self.gesture_points)
            if screen_points and self.current_brush:
                x, y = screen_points[0]
                self.current_brush.start_stroke(x, y, 0.5)
        
        self.current_point_index = 0
        
        self.animation_timer.start(30)

    def _create_drawing_buffer(self):
        self.drawing_buffer = QPixmap(self.size())
        self.drawing_buffer.fill(Qt.GlobalColor.transparent)

    def _update_animation(self):
        if not self.is_playing:
            return
            
        self.animation_progress += self.animation_speed
        
        self.fade_progress = min(1.0, self.fade_progress + self.animation_speed * 5)
        
        screen_points = self._convert_to_screen_coords(self.gesture_points)
        total_points = len(screen_points)
        
        target_point_index = int(self.animation_progress * total_points)
        
        if self.current_brush and screen_points:
            while self.current_point_index < target_point_index and self.current_point_index < len(screen_points) - 1:
                self.current_point_index += 1
                x, y = screen_points[self.current_point_index]
                self.current_brush.add_point(x, y, 0.5)
                
                if self.drawing_buffer:
                    buffer_painter = QPainter(self.drawing_buffer)
                    buffer_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    
                    if self.current_point_index > 0:
                        prev_x, prev_y = screen_points[self.current_point_index - 1]
                        
                        brush_type = self.drawing_module.get_current_brush_type()
                        
                        if brush_type == "pencil":
                            pen = QPen(QColor(*self.pen_color))
                            pen.setWidth(self.pen_width)
                            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                            buffer_painter.setPen(pen)
                            buffer_painter.drawLine(prev_x, prev_y, x, y)
                            
                        elif brush_type == "calligraphy":
                            if hasattr(self.current_brush, '_draw_brush_segment'):
                                from qtpy.QtCore import QPoint
                                from_p = QPoint(int(prev_x), int(prev_y))
                                to_p = QPoint(int(x), int(y))
                                
                                distance = math.hypot(to_p.x() - from_p.x(), to_p.y() - from_p.y())
                                base = self.pen_width * 1.2
                                delta = self.pen_width * 0.2
                                width = base + delta * (1 - 2/(1+math.exp(-0.3*(distance-5))))
                                
                                self.current_brush._draw_brush_segment(buffer_painter, from_p, to_p, width, 0.01)
                            else:
                                pen = QPen(QColor(*self.pen_color))
                                pen.setWidth(self.pen_width)
                                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                                buffer_painter.setPen(pen)
                                buffer_painter.drawLine(prev_x, prev_y, x, y)
                                
                        elif brush_type == "water":
                            self.drawing_buffer.fill(Qt.GlobalColor.transparent)
                            current_points = []
                            
                            current_time = time.time()
                            animation_duration = current_time - self.animation_start_time
                            
                            for i in range(self.current_point_index + 1):
                                px, py = screen_points[i]
                                progress_ratio = i / max(1, self.current_point_index)
                                point_time = self.animation_start_time + animation_duration * progress_ratio
                                current_points.append([px, py, 0.5, point_time])
                            
                            temp_brush = self.drawing_module.create_brush(self.pen_width, QColor(*self.pen_color))
                            temp_brush.draw(buffer_painter, current_points, current_time, False)
                    
                    buffer_painter.end()
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.is_playing = False
            self.animation_timer.stop()
            
            if self.current_brush:
                self.current_brush.end_stroke()
                
            if self.fade_progress >= 1.0:
                self.previous_buffer = None
        
        self.update()

    def _convert_to_screen_coords(self, relative_points):
        margin = 30
        available_width = self.width() - 2 * margin
        available_height = self.height() - 40
        
        screen_points = []
        for x_rel, y_rel in relative_points:
            x = margin + x_rel * available_width
            y = 30 + y_rel * available_height
            screen_points.append((int(x), int(y)))
        
        return screen_points

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._generate_gesture_path()
            self._start_animation()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        # 绘制淡出的上一个笔画
        if self.previous_buffer and self.fade_progress < 1.0:
            fade_opacity = 1.0 - self.fade_progress
            painter.setOpacity(fade_opacity)
            painter.drawPixmap(0, 0, self.previous_buffer)
            painter.setOpacity(1.0)
            
        if self.drawing_buffer:
            painter.drawPixmap(0, 0, self.drawing_buffer)
        
        if self.is_playing:
            screen_points = self._convert_to_screen_coords(self.gesture_points)
            total_points = len(screen_points)
            current_point_index = int(self.animation_progress * total_points)
            
            if current_point_index < len(screen_points) - 1:
                segment_progress = (self.animation_progress * total_points) - current_point_index
                
                start_point = screen_points[current_point_index]
                end_point = screen_points[current_point_index + 1]
                
                partial_x = start_point[0] + (end_point[0] - start_point[0]) * segment_progress
                partial_y = start_point[1] + (end_point[1] - start_point[1]) * segment_progress
                
                cursor_pen = QPen(QColor(255, 100, 100))
                cursor_pen.setWidth(max(1, self.pen_width // 2))
                painter.setPen(cursor_pen)
                painter.drawEllipse(int(partial_x) - 2, int(partial_y) - 2, 4, 4)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.size().width() > 0 and self.size().height() > 0:
            self._create_drawing_buffer()