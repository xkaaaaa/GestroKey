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

try:
    from core.brush.drawing import DrawingModule
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
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
        self.animation_speed = 0.015
        self.is_playing = False
        
        try:
            self.drawing_module = DrawingModule()
        except Exception as e:
            self.drawing_module = None
        
        self._generate_gesture_path()
        
        self.drawing_buffer = None
        self.current_brush = None

    def _generate_gesture_path(self):
        self.gesture_points = []
        
        t_values = [i / 100.0 for i in range(101)]
        
        for t in t_values:
            x = t
            y = 0.5 + 0.3 * math.sin(t * math.pi * 2) * math.sin(t * math.pi)
            self.gesture_points.append((x, y))

    def update_pen(self, width, color, brush_type=None):
        self.pen_width = width
        self.pen_color = color[:]
        
        if self.drawing_module and brush_type:
            self.drawing_module.set_brush_type(brush_type)
        
        self._start_animation()

    def _start_animation(self):
        self.animation_progress = 0.0
        self.is_playing = True
        
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
        
        self.animation_timer.start(50)

    def _create_drawing_buffer(self):
        self.drawing_buffer = QPixmap(self.size())
        self.drawing_buffer.fill(Qt.GlobalColor.transparent)

    def _update_animation(self):
        if not self.is_playing:
            return
            
        self.animation_progress += self.animation_speed
        
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
            self._start_animation()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        if not self.is_playing and self.animation_progress == 0:
            painter.setPen(QPen(QColor(150, 150, 150)))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "点击开始预览")
            
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
        
        painter.setPen(QPen(QColor(60, 60, 60)))
        info_text = f"粗细: {self.pen_width}px  颜色: RGB({self.pen_color[0]}, {self.pen_color[1]}, {self.pen_color[2]})"
        painter.drawText(10, self.height() - 5, info_text)
        
        if self.is_playing:
            status_text = f"绘制中: {int(self.animation_progress * 100)}%"
        else:
            status_text = "点击重新预览"
        painter.drawText(self.width() - 120, self.height() - 5, status_text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.size().width() > 0 and self.size().height() > 0:
            self._create_drawing_buffer() 