import sys
import os
import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QPolygon, QTransform

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
        
        # 视图变换属性
        self.view_scale = 1.0  # 缩放因子
        self.view_offset = QPoint(0, 0)  # 视图偏移
        self.min_scale = 0.1  # 最小缩放
        self.max_scale = 5.0  # 最大缩放
        
        # 标准视图（用于双击重置）
        self.standard_scale = 1.0
        self.standard_offset = QPoint(0, 0)
        
        # 拖拽状态
        self.panning = False
        self.last_pan_point = QPoint()
        self.space_pressed = False
        
        # 双击检测
        self.click_timer = QTimer()
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._single_click_timeout)
        self.click_count = 0
        
        # 设置最小尺寸
        self.setMinimumSize(300, 200)
        self.setStyleSheet("background-color: white; border: 1px solid gray;")
        
        # 启用键盘焦点和滚轮事件
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.initUI()
        
    def initUI(self):
        """初始化UI"""
        # 设置为简洁布局，无按钮无提示文字
        self.setLayout(QVBoxLayout())
        
    def keyPressEvent(self, event):
        """键盘按下事件"""
        if event.key() == Qt.Key.Key_Space:
            self.space_pressed = True
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
        """键盘释放事件"""
        if event.key() == Qt.Key.Key_Space:
            self.space_pressed = False
            if not self.panning:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().keyReleaseEvent(event)
        
    def wheelEvent(self, event):
        """滚轮事件 - Alt+滚轮缩放"""
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            # 计算缩放中心点（鼠标位置）
            try:
                zoom_center = event.position().toPoint()
            except:
                # 兼容性处理
                zoom_center = event.pos()
            
            # 计算缩放因子 - 使用angleDelta().y()或pixelDelta().y()
            angle_delta = event.angleDelta()
            pixel_delta = event.pixelDelta()
            
            # 获取滚动增量 - 通常在y()，但在某些情况下可能在x()
            if not angle_delta.isNull():
                delta = angle_delta.y() if angle_delta.y() != 0 else angle_delta.x()
            elif not pixel_delta.isNull():
                delta = pixel_delta.y() if pixel_delta.y() != 0 else pixel_delta.x()
            else:
                delta = 0
            
            # 如果没有有效的delta值，跳过处理
            if delta == 0:
                event.accept()
                return
            
            # 修正缩放方向：向上滚动(delta>0)放大，向下滚动(delta<0)缩小
            if delta > 0:
                scale_factor = 1.2  # 放大
            else:
                scale_factor = 1.0 / 1.2  # 缩小
            new_scale = self.view_scale * scale_factor
            
            # 限制缩放范围
            new_scale = max(self.min_scale, min(self.max_scale, new_scale))
            
            if new_scale != self.view_scale:
                # 计算缩放后的偏移调整，使缩放围绕鼠标位置进行
                # 将鼠标位置转换为视图坐标
                view_center_x = (zoom_center.x() - self.view_offset.x()) / self.view_scale
                view_center_y = (zoom_center.y() - self.view_offset.y()) / self.view_scale
                
                # 更新缩放
                self.view_scale = new_scale
                
                # 调整偏移以保持鼠标位置不变
                new_offset_x = zoom_center.x() - view_center_x * self.view_scale
                new_offset_y = zoom_center.y() - view_center_y * self.view_scale
                self.view_offset = QPoint(int(new_offset_x), int(new_offset_y))
                
                self.update()
                
            event.accept()
        else:
            super().wheelEvent(event)
            
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.setFocus()  # 获取键盘焦点
        
        if event.button() == Qt.MouseButton.MiddleButton:
            # 中键双击检测
            self.click_count += 1
            if self.click_count == 1:
                self.click_timer.start(300)  # 300ms内等待第二次点击
            elif self.click_count == 2:
                self.click_timer.stop()
                self._reset_view()  # 双击中键归位
                self.click_count = 0
                return
                
            # 开始拖拽
            self.panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
        elif event.button() == Qt.MouseButton.LeftButton:
            if self.space_pressed:
                # 空格+左键拖拽
                self.panning = True
                self.last_pan_point = event.pos()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            else:
                # 正常绘制
                self.clear_drawing()
                self.drawing = True
                # 将屏幕坐标转换为视图坐标
                view_pos = self._screen_to_view(event.pos())
                self.current_path = [view_pos]
                self.update()
                
    def _single_click_timeout(self):
        """单击超时"""
        self.click_count = 0
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.panning:
            # 拖拽画布
            delta = event.pos() - self.last_pan_point
            self.view_offset += delta
            self.last_pan_point = event.pos()
            self.update()
        elif self.drawing:
            # 绘制手势
            view_pos = self._screen_to_view(event.pos())
            self.current_path.append(view_pos)
            self.update()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.panning and (event.button() == Qt.MouseButton.MiddleButton or 
                           (event.button() == Qt.MouseButton.LeftButton and self.space_pressed)):
            self.panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor if self.space_pressed else Qt.CursorShape.ArrowCursor)
            
        elif self.drawing and event.button() == Qt.MouseButton.LeftButton and not self.space_pressed:
            self.drawing = False
            if len(self.current_path) > 1:
                # 格式化路径 - 注意这里current_path已经是视图坐标
                raw_points = [(p.x(), p.y(), 0.5, 0.0, 1) for p in self.current_path]
                formatted_path = self.path_analyzer.format_raw_path(raw_points)
                
                if formatted_path and formatted_path.get('points'):
                    self.completed_paths.append(formatted_path)
                    # 自动使用此路径
                    self.pathCompleted.emit(formatted_path)
                    self.logger.info(f"自动使用格式化路径：{len(formatted_path.get('points', []))}个关键点")
            
            self.current_path = []
            self.update()
            
    def _screen_to_view(self, screen_pos):
        """将屏幕坐标转换为视图坐标"""
        view_x = (screen_pos.x() - self.view_offset.x()) / self.view_scale
        view_y = (screen_pos.y() - self.view_offset.y()) / self.view_scale
        return QPoint(int(view_x), int(view_y))
        

    def _reset_view(self):
        """重置视图到标准视图状态"""
        self.view_scale = self.standard_scale
        self.view_offset = QPoint(self.standard_offset)
        self.update()
        self.logger.info("视图已重置到标准状态")
            
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 应用视图变换
        transform = QTransform()
        transform.translate(self.view_offset.x(), self.view_offset.y())
        transform.scale(self.view_scale, self.view_scale)
        painter.setTransform(transform)
        
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
        # 重置到默认视图
        self.view_scale = 1.0
        self.view_offset = QPoint(0, 0)
        self.standard_scale = 1.0
        self.standard_offset = QPoint(0, 0)
        self.update()
        

    def load_path(self, path):
        """加载并显示指定路径（用于编辑现有手势）"""
        if path and path.get('points'):
            self.clear_drawing()  # 先清除现有内容
            self.completed_paths = [path]
            # 重置到标准视图（1:1）让自动缩放生效
            self.view_scale = 1.0
            self.view_offset = QPoint(0, 0)
            self.standard_scale = 1.0
            self.standard_offset = QPoint(0, 0)
            self.update()
        else:
            self.clear_drawing() 