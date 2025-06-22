"""
透明绘制覆盖层

处理绘制界面的显示和交互
"""

import sys
import os
import math
import time

from qtpy.QtCore import QObject, QPoint, QRect, Qt, QTimer, Signal
from qtpy.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPixmap,
    QSurfaceFormat,
)
from qtpy.QtWidgets import QApplication, QWidget

# 导入画笔模块
from .drawing import DrawingModule
from .fading import FadingModule

from core.logger import get_logger
from core.path_analyzer import PathAnalyzer


class DrawingSignals(QObject):
    """信号类，用于在线程间安全地传递信号"""

    start_drawing_signal = Signal(int, int, float)  # x, y, pressure
    continue_drawing_signal = Signal(int, int, float)  # x, y, pressure
    stop_drawing_signal = Signal()


class TransparentDrawingOverlay(QWidget):
    """透明绘制覆盖层，用于捕获鼠标移动并绘制轨迹"""

    def __init__(self):
        super().__init__()
        self.logger = get_logger("DrawingOverlay")

        # 绘制状态
        self.drawing = False
        self.last_point = None

        # 点和压力数据
        self.points = []  # 存储所有轨迹点，每个元素为 [x, y, pressure, timestamp]
        self.lines = []  # 存储完整线条，每条线由多个点组成
        self.current_line = []  # 当前正在绘制的线条
        self.current_stroke_id = 0  # 当前绘制的笔画ID

        # 路径分析器
        self.path_analyzer = PathAnalyzer()

        # 画笔模块
        self.drawing_module = DrawingModule()
        self.current_brush = None

        # 绘制效果控制
        self.pen_color = QColor(0, 120, 255, 255)  # 线条颜色，设置完全不透明
        self.pen_width = 2  # 线条宽度

        # 缓冲区和更新控制
        self.image = None  # 绘图缓冲
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(10)
        
        # 水性笔持续更新定时器
        self.water_update_timer = QTimer(self)
        self.water_update_timer.timeout.connect(self._update_water_brush)
        self.water_update_timer.setInterval(16)  # 约60FPS

        # 消失模块
        self.fading_module = FadingModule(self)
        self.fading_module.fade_update.connect(self.update)
        self.fading_module.fade_complete.connect(self._on_fade_complete)
        self.fading = False

        # 绘制优化参数
        self.min_drawing_distance = 2.0  # 最小绘制距离阈值，防止过于频繁绘制
        self.last_drawing_points = []  # 存储最近的几个绘制点，用于平滑处理
        self.max_drawing_points = 3  # 最大存储点数

        # 性能优化 - 预创建画笔和批量绘制
        self.painter_pen = QPen()
        self.painter_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.painter_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        self._batch_painter = None  # 批量绘制的QPainter实例

        # 强制置顶定时器
        self.force_topmost_timer = QTimer(self)
        self.force_topmost_timer.timeout.connect(self._force_window_topmost)
        self.force_topmost_enabled = True  # 默认启用强制置顶

        self.initUI()
        self.logger.debug("绘制覆盖层初始化完成")

    def set_brush_type(self, brush_type):
        """设置画笔类型"""
        if self.drawing_module.set_brush_type(brush_type):
            self.logger.debug(f"画笔类型已设置为: {brush_type}")
            return True
        else:
            self.logger.warning(f"无效的画笔类型: {brush_type}")
            return False

    def get_brush_types(self):
        """获取所有画笔类型"""
        return self.drawing_module.get_brush_types()

    def get_current_brush_type(self):
        """获取当前画笔类型"""
        return self.drawing_module.get_current_brush_type()

    def set_force_topmost(self, enabled):
        """设置是否启用强制置顶"""
        self.force_topmost_enabled = enabled
        self.logger.debug(f"强制置顶已设置为: {enabled}")

    def _force_window_topmost(self):
        """强制窗口置顶"""
        if self.force_topmost_enabled and self.isVisible():
            self.raise_()
            self.activateWindow()
            # 确保窗口始终在最顶层
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
            )
            self.show()

    def set_pen_width(self, width):
        """设置笔尖粗细"""
        if width > 0:
            self.pen_width = width
            self.logger.debug(f"笔尖粗细已设置为: {width}")

    def set_pen_color(self, color):
        """设置笔尖颜色"""
        if isinstance(color, list) and len(color) >= 3:
            r, g, b = color[0], color[1], color[2]
            # 设置完全不透明
            alpha = 255
            self.pen_color = QColor(r, g, b, alpha)
            self.logger.debug(f"笔尖颜色已设置为: RGB({r},{g},{b})")
            return True
        else:
            self.logger.warning(f"无效的颜色值: {color}")
            return False

    def initUI(self):
        # 创建一个全屏、透明、无边框的窗口，用于绘制
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )  # 完全透明，不影响鼠标事件

        # 启用图形硬件加速
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        # 有选择性地启用硬件加速，避免与QPainter冲突
        try:
            # 设置高质量渲染格式
            format = QSurfaceFormat()
            format.setSamples(4)  # 启用多重采样抗锯齿
            format.setSwapInterval(1)  # 垂直同步

            # 在支持的环境中使用OpenGL
            QSurfaceFormat.setDefaultFormat(format)

            # 启用Qt的合成器提示以获得更好的硬件加速
            self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
            self.setAutoFillBackground(False)  # 禁用自动填充背景以提高性能

            self.logger.debug("成功配置图形硬件加速")
        except ImportError:
            self.logger.warning("无法导入QSurfaceFormat，图形硬件加速可能不可用")
        except Exception as e:
            self.logger.warning(f"配置图形硬件加速时出错: {e}")

        # 获取屏幕尺寸
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.setGeometry(screen_geometry)

        # 创建绘图缓冲区
        self.image = QPixmap(screen_geometry.width(), screen_geometry.height())
        self.image.fill(Qt.GlobalColor.transparent)

        # 隐藏窗口，仅在绘制时显示
        self.hide()
        self.logger.debug(
            f"UI初始化完成，屏幕尺寸: {screen_geometry.width()}x{screen_geometry.height()}"
        )

    def startDrawing(self, x, y, pressure=0.5):
        """开始绘制"""
        # 验证坐标有效性
        if x <= 0 or y <= 0:
            return

        self.logger.debug(f"开始绘制，坐标: ({x}, {y}), 压力: {pressure}")

        # 如果正在消失过程中，立即停止消失并清除
        if self.fading:
            self.logger.debug("检测到消失过程中开始新绘制，停止消失效果")
            self.fading_module.stop_fade()
            self.fading = False
            # 清除所有旧数据
            self.points = []
            self.lines = []
            self.current_line = []

        # 创建全新的图像，彻底清除之前的内容
        self.image = QPixmap(self.size())
        self.image.fill(Qt.GlobalColor.transparent)

        # 记录起始点
        current_time = time.time()
        self.last_point = QPoint(x, y)
        self.current_stroke_id += 1
        self.current_line = [[x, y, pressure, current_time, self.current_stroke_id]]
        self.points.append([x, y, pressure, current_time])

        # 重置绘制优化参数
        self.last_drawing_points = [(x, y)]

        self.drawing = True

        # 创建新画笔
        self.current_brush = self.drawing_module.create_brush(self.pen_width, self.pen_color)
        if self.current_brush:
            self.current_brush.start_stroke(x, y, pressure)

        # 停止更新计时器（如果正在运行）
        if self.update_timer.isActive():
            self.update_timer.stop()

        # 显示窗口
        self.show()

        # 启动强制置顶定时器
        if self.force_topmost_enabled:
            self.force_topmost_timer.start(100)

        # 如果是水性笔，启动持续更新定时器
        if self.drawing_module.get_current_brush_type() == "water":
            self.water_update_timer.start()

        # 立即更新显示以确保新绘制可见
        self.update()

    def continueDrawing(self, x, y, pressure=0.5):
        """继续绘制"""
        if not self.drawing or not self.last_point:
            return

        # 验证坐标有效性
        if x <= 0 or y <= 0:
            return

        current_point = QPoint(x, y)

        # 计算与上一个点的距离，如果太近，则忽略以减轻CPU负担
        last_x, last_y = self.last_point.x(), self.last_point.y()
        distance = math.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)

        if distance < self.min_drawing_distance:
            return

        # 添加到历史点队列，保持队列长度
        self.last_drawing_points.append((x, y))
        if len(self.last_drawing_points) > self.max_drawing_points:
            self.last_drawing_points.pop(0)

        # 根据画笔类型选择绘制方式
        brush_type = self.drawing_module.get_current_brush_type()
        
        if brush_type == "pencil" or brush_type == "calligraphy":
            # 铅笔和毛笔使用批量绘制优化，直接绘制到image上
            if not hasattr(self, "_batch_painter") or self._batch_painter is None:
                self._batch_painter = QPainter(self.image)
                self._batch_painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            if brush_type == "pencil":
                # 设置铅笔画笔
                self.painter_pen.setColor(self.pen_color)
                self.painter_pen.setWidth(self.pen_width)
                self._batch_painter.setPen(self.painter_pen)
                # 绘制线段
                self._batch_painter.drawLine(self.last_point, current_point)
            else:  # calligraphy
                # 使用毛笔绘制方法
                if self.current_brush:
                    self.current_brush.add_point(x, y, pressure)
                    # 只绘制最新的线段
                    if len(self.current_brush.points) >= 2:
                        from_point = self.current_brush.points[-2]
                        to_point = self.current_brush.points[-1]
                        from_p = QPoint(int(from_point[0]), int(from_point[1]))
                        to_p = QPoint(int(to_point[0]), int(to_point[1]))
                        
                        # 计算绘制参数
                        duration = 0.01
                        if len(from_point) >= 4 and len(to_point) >= 4:
                            duration = to_point[3] - from_point[3]
                        
                        distance = math.hypot(to_p.x() - from_p.x(), to_p.y() - from_p.y())
                        
                        # 动态笔画宽度
                        base = self.pen_width * 1.2
                        delta = self.pen_width * 0.2
                        width = base + delta * (1 - 2/(1+math.exp(-0.3*(distance-5))))
                        
                        # 平滑处理
                        if hasattr(self.current_brush, 'last_width'):
                            width = (width + self.current_brush.last_width) / 2
                        self.current_brush.last_width = width
                        
                        # 绘制这一段
                        self.current_brush._draw_brush_segment(self._batch_painter, from_p, to_p, width, duration)
            
            # 计算需要更新的区域（只更新绘制的线段区域）
            update_rect = QRect(self.last_point, current_point).normalized()
            padding = self.pen_width + 5  # 毛笔需要更大的padding
            update_rect.adjust(-padding, -padding, padding, padding)
            
            # 仅更新需要重绘的区域
            self.update(update_rect)
        else:
            # 水性笔等其他画笔类型使用原有方式保持动态效果
            if self.current_brush:
                self.current_brush.add_point(x, y, pressure)
            
            # 全屏更新以保持动态效果
            self.update()

        # 记录当前点
        current_time = time.time()
        self.current_line.append([x, y, pressure, current_time, self.current_stroke_id])
        self.points.append([x, y, pressure, current_time])

        # 更新上一个点的位置
        self.last_point = current_point

    def stopDrawing(self):
        """停止绘制"""
        if not self.drawing:
            return

        self._fade_pixmap = QPixmap(self.size())
        self._fade_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self._fade_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setOpacity(1.0)
        painter.drawPixmap(0, 0, self.image)
        brush_type = self.drawing_module.get_current_brush_type()
        if brush_type == "water":
            # 只有水性笔需要重新绘制到fade_pixmap，因为它的效果是动态的
            # 毛笔和铅笔已经绘制到image上了，不需要重复绘制
            current_time = time.time()
            for line in self.lines:
                if line:
                    temp_brush = self.drawing_module.create_brush(self.pen_width, self.pen_color)
                    temp_brush.draw(painter, line, current_time, False)
            if self.current_line:
                temp_brush = self.drawing_module.create_brush(self.pen_width, self.pen_color)
                temp_brush.draw(painter, self.current_line, current_time, False)
        painter.end()
        self.logger.debug("停止绘制")

        # 结束批量绘制
        if hasattr(self, "_batch_painter") and self._batch_painter is not None:
            self._batch_painter.end()
            self._batch_painter = None

        # 结束当前笔画
        if self.current_brush:
            self.current_brush.end_stroke()

        # 保存当前线条
        if self.current_line:
            self.lines.append(self.current_line.copy())
            self.current_line = []

        # 重置绘制状态
        self.drawing = False
        self.last_point = None
        self.current_brush = None

        # 停止强制置顶和更新定时器
        self.force_topmost_timer.stop()
        self.update_timer.stop()
        self.water_update_timer.stop()

        # 第一步：分析路径并发送给手势执行器
        if self.points:
            try:
                formatted_path = self.path_analyzer.format_raw_path(self.points)
                if formatted_path and formatted_path.get('points'):
                    self.logger.info(f"绘制完成，路径包含 {len(formatted_path.get('points', []))} 个关键点")
                    try:
                        from core.gesture_executor import get_gesture_executor
                        executor = get_gesture_executor()
                        if executor:
                            result = executor.execute_gesture_by_path(formatted_path)
                            if result:
                                self.logger.info("手势识别并执行成功")
                            else:
                                self.logger.debug("未识别到匹配的手势")
                        else:
                            self.logger.warning("无法获取手势执行器实例")
                    except Exception as exec_error:
                        self.logger.error(f"手势执行失败: {exec_error}")
                else:
                    self.logger.debug("路径格式化后为空，不执行手势识别")
            except Exception as e:
                self.logger.error(f"路径分析失败: {e}")

        self.logger.debug("开始整体淡出效果")
        self.fading_module.start_fade()
        self.fading = True

    def _on_fade_complete(self):
        """淡出完成回调"""
        self.logger.debug("淡出完成，清除所有笔迹并隐藏窗口")
        
        # 清除所有笔迹数据
        self.points = []
        self.lines = []
        self.current_line = []
        
        # 重置状态
        self.fading = False
        self.drawing = False
        self.last_point = None
        self.current_brush = None
        
        # 清空画布
        if self.image:
            self.image.fill(Qt.GlobalColor.transparent)
        
        # 隐藏窗口
        self.hide()

    def paintEvent(self, event):
        """绘制事件处理"""
        if not self.image:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 清除整个绘制区域（确保不会有残留）
        if not self.fading:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        if self.fading:
            # 整体淡出像素
            if hasattr(self, '_fade_pixmap') and self._fade_pixmap:
                painter.setOpacity(self.fading_module.get_fade_alpha() / 255.0)
                painter.drawPixmap(0, 0, self._fade_pixmap)
        else:
            # 正常绘制
            painter.setOpacity(1.0)
            painter.drawPixmap(0, 0, self.image)
            # 动态绘制水性笔类型（毛笔和铅笔已经绘制到image上了）
            brush_type = self.drawing_module.get_current_brush_type()
            if brush_type == "water":
                # 只有水性笔需要重新绘制到fade_pixmap，因为它的效果是动态的
                # 毛笔和铅笔已经绘制到image上了，不需要重复绘制
                current_time = time.time()
                for line in self.lines:
                    if line:
                        temp_brush = self.drawing_module.create_brush(self.pen_width, self.pen_color)
                        temp_brush.draw(painter, line, current_time, False)
                if self.current_line:
                    temp_brush = self.drawing_module.create_brush(self.pen_width, self.pen_color)
                    temp_brush.draw(painter, self.current_line, current_time, False)

    def resizeEvent(self, event):
        """窗口大小改变时调整画布大小"""
        if self.size().width() > 0 and self.size().height() > 0:
            if (
                self.image is None
                or self.image.size().width() < self.size().width()
                or self.image.size().height() < self.size().height()
            ):
                new_image = QPixmap(self.size())
                new_image.fill(Qt.GlobalColor.transparent)

                if self.image:
                    # 将原有内容绘制到新画布上
                    painter = QPainter(new_image)
                    painter.drawPixmap(0, 0, self.image)
                    painter.end()

                self.image = new_image
                self.logger.debug(
                    f"画布大小已调整: {self.size().width()}x{self.size().height()}"
                )

    def get_stroke_direction(self, stroke_id=None):
        """获取指定笔画的基本信息，如不指定则获取最后一个笔画"""
        if not self.lines:
            return "无笔画数据"

        if stroke_id is None:
            # 获取最后一个笔画
            stroke_data = self.lines[-1]
        else:
            # 查找匹配ID的笔画
            matching_strokes = [
                line for line in self.lines if line and line[0][4] == stroke_id
            ]
            if not matching_strokes:
                return f"未找到ID为{stroke_id}的笔画"
            stroke_data = matching_strokes[0]

        # 返回笔画基本信息
        if stroke_data:
            return f"笔画#{stroke_data[0][4]}: {len(stroke_data)}个点"
        return "无效的笔画数据"

    def _clear_all_strokes(self):
        """清除所有笔迹"""
        self.drawing = False
        self.last_point = None
        self.current_brush = None
        self.points = []
        self.lines = []
        self.current_line = []
        self.current_stroke_id = 0
        self.fading = False
        self.fading_module.stop_fade()
        self.force_topmost_timer.stop()
        self.update_timer.stop()
        self.water_update_timer.stop()
        if self.image:
            self.image.fill(Qt.GlobalColor.transparent)
        self.hide()

    def _update_water_brush(self):
        """水性笔持续更新，让停留的点也能逐渐变粗"""
        if not self.drawing or self.drawing_module.get_current_brush_type() != "water":
            return
            
        # 只要在绘制水性笔，就持续更新以显示变粗效果
        self.update()