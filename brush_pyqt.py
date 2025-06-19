import sys
import random
import math
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPainter, QColor, QMouseEvent, QPaintEvent, QPixmap, QTouchEvent
from PyQt6.QtCore import Qt, QPoint

class BrushCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)
        self.setFixedSize(1200, 700)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)
        self.last_point = None
        self.last_width = 10
        self.drawing = False
        self.last_time = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.last_width = 10
            self.last_time = time.time()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing:
            curr_point = event.position().toPoint()
            now = time.time()
            duration = now - self.last_time if self.last_time else 0.01
            dist = math.hypot(curr_point.x() - self.last_point.x(), curr_point.y() - self.last_point.y())
            base = 15
            delta = 3
            width = base + delta * (1 - 2/(1+math.exp(-0.3*(dist-5))))
            width = (width + self.last_width) / 2
            self.draw_brush(self.last_point, curr_point, width, duration)
            self.last_point = curr_point
            self.last_width = width
            self.last_time = now
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.last_point is not None:
                # 收尾效果
                end_point = self.last_point
                for i in range(1, 8):
                    fade = 1 - i / 8
                    width = max(2, self.last_width * fade)
                    duration = 0.03 * i
                    offset = int(2 * i * (random.random()-0.5))
                    to_p = QPoint(end_point.x() + offset, end_point.y() + offset)
                    self.draw_brush(end_point, to_p, width, duration)
                    end_point = to_p
            self.drawing = False

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def clear(self):
        self.pixmap.fill(Qt.GlobalColor.white)
        self.update()

    def draw_brush(self, from_p: QPoint, to_p: QPoint, width, duration=0.01):
        painter = QPainter(self.pixmap)
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
            base_gray = int(30 * ink_factor)
            color = QColor(
                base_gray + random.randint(-15, 15),
                base_gray + random.randint(-15, 15),
                base_gray + random.randint(-15, 15)
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
            if random.random() < 0.7:
                bend_len = w * (0.7 + random.random()*0.6)
                bend_angle = angle + (random.random()-0.5)*0.7
                bx = int(x + math.cos(bend_angle) * bend_len)
                by = int(y + math.sin(bend_angle) * bend_len)
                bend_color = QColor(40 + random.randint(-20, 20), 40 + random.randint(-20, 20), 40 + random.randint(-20, 20))
                painter.save()
                painter.setPen(bend_color)
                painter.setOpacity(0.25 + random.random()*0.2)
                painter.drawLine(x, y, bx, by)
                painter.restore()
            if random.random() < 0.18:
                zx = int(x + (random.random()-0.5)*w*1.5)
                zy = int(y + (random.random()-0.5)*w*1.5)
                zcolor = QColor(80 + random.randint(-60, 60), 80 + random.randint(-60, 60), 80 + random.randint(-60, 60))
                painter.save()
                painter.setPen(zcolor)
                painter.setOpacity(0.18 + random.random()*0.18)
                painter.drawLine(x, y, zx, zy)
                painter.restore()
            if random.random() < 0.15:
                painter.save()
                painter.translate(x + (random.random()-0.5)*w, y + (random.random()-0.5)*w)
                color2 = QColor(60 + random.randint(-40, 40), 60 + random.randint(-40, 40), 60 + random.randint(-40, 40))
                painter.setOpacity(0.2 + random.random()*0.2)
                painter.fillRect(-w//4, -w//4, w//2, w//2, color2)
                painter.restore()
        painter.end()

    def touchEvent(self, event: QTouchEvent):
        if event.type() == event.Type.TouchBegin:
            self.drawing = True
            self.last_point = event.points()[0].position().toPoint()
            self.last_width = 15
            self.last_time = time.time()
        elif event.type() == event.Type.TouchUpdate and self.drawing:
            curr_point = event.points()[0].position().toPoint()
            now = time.time()
            duration = now - self.last_time if self.last_time else 0.01
            dist = math.hypot(curr_point.x() - self.last_point.x(), curr_point.y() - self.last_point.y())
            base = 15
            delta = 3
            width = base + delta * math.exp(-dist/4)
            width = (width + self.last_width) / 2
            self.draw_brush(self.last_point, curr_point, width, duration)
            self.last_point = curr_point
            self.last_width = width
            self.last_time = now
            self.update()
        elif event.type() == event.Type.TouchEnd:
            if self.last_point is not None:
                end_point = self.last_point
                for i in range(1, 8):
                    fade = 1 - i / 8
                    width = max(2, self.last_width * fade)
                    duration = 0.03 * i
                    offset = int(2 * i * (random.random()-0.5))
                    to_p = QPoint(end_point.x() + offset, end_point.y() + offset)
                    self.draw_brush(end_point, to_p, width, duration)
                    end_point = to_p
            self.drawing = False
        event.accept()

    def event(self, event):
        if event.type() in [event.Type.TouchBegin, event.Type.TouchUpdate, event.Type.TouchEnd]:
            return self.touchEvent(event)
        return super().event(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('毛笔画笔模拟')
        self.canvas = BrushCanvas()
        btn_clear = QPushButton('清空画布 (快捷键C)')
        btn_clear.clicked.connect(self.canvas.clear)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(btn_clear)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_C:
            self.canvas.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())