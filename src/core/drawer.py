import sys
import time
import math
import os
import traceback
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath, QPixmap, QBrush, QPainterPathStroker
from pynput import mouse

# 导入笔画分析器
try:
    from logger import get_logger
    from stroke_analyzer import StrokeAnalyzer
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
    from ui.settings.settings import get_settings
    from ui.gestures.gestures import get_gesture_library  # 从ui.gestures导入手势库
    from core.gesture_executor import get_gesture_executor
except ImportError:
    from core.logger import get_logger
    from core.stroke_analyzer import StrokeAnalyzer
    from ui.settings.settings import get_settings
    from ui.gestures.gestures import get_gesture_library  # 从ui.gestures导入手势库
    from core.gesture_executor import get_gesture_executor

class DrawingSignals(QObject):
    """信号类，用于在线程间安全地传递信号"""
    start_drawing_signal = pyqtSignal(int, int, float)  # x, y, pressure
    continue_drawing_signal = pyqtSignal(int, int, float)  # x, y, pressure
    stop_drawing_signal = pyqtSignal()

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
        self.lines = []   # 存储完整线条，每条线由多个点组成
        self.current_line = []  # 当前正在绘制的线条
        self.current_stroke_id = 0  # 当前绘制的笔画ID
        
        # 笔画分析器
        self.stroke_analyzer = StrokeAnalyzer()
        
        # 绘制效果控制
        self.pen_color = QColor(0, 120, 255, 255)  # 线条颜色，设置完全不透明
        self.pen_width = 2  # 线条宽度，将由DrawingManager设置
        
        # 缓冲区和更新控制
        self.image = None  # 绘图缓冲
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(16)  # 约60fps
        
        # 渐变消失效果
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.fade_path)
        self.fade_timer.setInterval(20)  # 每20ms淡出一次
        self.fading = False  # 是否在淡出过程中
        self.fade_alpha = 255  # 当前淡出透明度
        self.fade_speed = 25  # 每次淡出减少的透明度
        
        self.initUI()
        self.logger.debug("绘制覆盖层初始化完成")
    
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
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)  # 完全透明，不影响鼠标事件
        
        # 获取屏幕尺寸
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.setGeometry(screen_geometry)
        
        # 创建绘图缓冲区
        self.image = QPixmap(screen_geometry.width(), screen_geometry.height())
        self.image.fill(Qt.GlobalColor.transparent)
        
        # 隐藏窗口，仅在绘制时显示
        self.hide()
        self.logger.debug(f"UI初始化完成，屏幕尺寸: {screen_geometry.width()}x{screen_geometry.height()}")
    
    def startDrawing(self, x, y, pressure=0.5):
        """开始绘制"""
        # 验证坐标有效性
        if x <= 0 or y <= 0:
            self.logger.warning(f"忽略无效的起始坐标: ({x}, {y})")
            return
        
        self.logger.debug(f"开始绘制，坐标: ({x}, {y}), 压力: {pressure}")
        
        # 停止任何正在进行的淡出效果
        if self.fading:
            self.logger.debug("检测到正在进行的淡出效果，正在停止")
            self.fade_timer.stop()
            self.fading = False
            self.fade_alpha = 255  # 重置透明度
            # 确保清除任何已有的淡出状态，避免影响新的绘制
            if self.image:
                painter = QPainter(self.image)
                painter.setOpacity(1.0)  # 设置完全不透明
                painter.end()
        
        # 确保创建新图像并清空画布（无论尺寸是否变化）
        if self.image is None or self.image.size() != self.size():
            self.image = QPixmap(self.size())
        # 始终清空画布，确保每次新绘制开始时没有旧内容
        self.image.fill(Qt.GlobalColor.transparent)
            
        # 记录起始点
        current_time = time.time()
        self.last_point = QPoint(x, y)
        self.current_stroke_id += 1  # 增加笔画ID
        self.current_line = [(x, y, pressure, current_time, self.current_stroke_id)]
        
        self.drawing = True
        
        # 停止更新计时器（如果正在运行）并重新启动
        if self.update_timer.isActive():
            self.update_timer.stop()
        
        # 显示窗口并启动更新计时器
        self.show()
        self.update_timer.start()
        self.update()
    
    def continueDrawing(self, x, y, pressure=0.5):
        """继续绘制轨迹"""
        if not self.drawing or not self.last_point:
            return
        
        # 验证坐标
        if x <= 0 or y <= 0:
            return
            
        current_point = QPoint(x, y)
        
        # 在图像上绘制新线段
        painter = QPainter(self.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # 设置画笔
        pen = QPen()
        pen.setColor(self.pen_color)
        pen.setWidth(self.pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        # 绘制线段
        painter.drawLine(self.last_point, current_point)
        
        # 记录当前点
        current_time = time.time()
        self.current_line.append((x, y, pressure, current_time, self.current_stroke_id))
        
        # 更新上一个点的位置
        self.last_point = current_point
        
        painter.end()
        
        # 更新显示
        self.update()
    
    def stopDrawing(self):
        """停止绘制并开始淡出效果"""
        if not self.drawing:
            return
            
        self.logger.debug("停止绘制，开始淡出")
        
        # 保存当前线条并分析方向
        if self.current_line:
            # 分析笔画方向
            direction_sequence, direction_details = self.stroke_analyzer.analyze_direction(self.current_line)
            direction_description = self.stroke_analyzer.get_direction_description(direction_sequence)
            
            # 记录本次绘制的点数据和方向
            self._log_stroke_data(self.current_line, direction_sequence, direction_description, direction_details)
            
            # 执行与方向匹配的手势动作
            if direction_sequence and direction_sequence not in ["无方向", "无明显方向"]:
                try:
                    gesture_executor = get_gesture_executor()
                    
                    # 执行手势
                    result = gesture_executor.execute_gesture(direction_sequence)
                    if result:
                        name = gesture_executor.gesture_library.get_gesture_by_direction(direction_sequence)[0]
                        self.logger.info(f"成功执行手势: {direction_sequence} -> {name if name else '未知手势'}")
                except Exception as e:
                    self.logger.error(f"执行手势动作时出错: {e}")
                    self.logger.debug(f"详细错误: {traceback.format_exc()}")
            
            # 保存线条数据
            self.lines.append(self.current_line.copy())
            self.points.extend(self.current_line)
            self.current_line = []
            
        # 开始淡出效果
        self.drawing = False
        self.fading = True
        self.fade_alpha = 255
        
        # 停止更新计时器，启动淡出计时器
        self.update_timer.stop()
        if self.fade_timer.isActive():
            self.fade_timer.stop()
        self.fade_timer.start()
    
    def _log_stroke_data(self, stroke_data, direction_sequence=None, direction_description=None, direction_details=None):
        """记录笔画数据到日志"""
        if not stroke_data or len(stroke_data) < 2:
            return
            
        stroke_id = stroke_data[0][4]  # 获取笔画ID
        point_count = len(stroke_data)
        start_time = stroke_data[0][3]
        end_time = stroke_data[-1][3]
        duration = end_time - start_time
        
        # 构建方向信息
        direction_info = ""
        if direction_sequence and direction_sequence not in ["无方向", "无明显方向"]:
            direction_info = f", 方向: {direction_sequence}"
            if direction_description:
                direction_info += f" ({direction_description})"
        
        # 计算统计数据
        total_distance = 0
        for i in range(1, len(stroke_data)):
            x1, y1 = stroke_data[i-1][0], stroke_data[i-1][1]
            x2, y2 = stroke_data[i][0], stroke_data[i][1]
            total_distance += math.sqrt((x2-x1)**2 + (y2-y1)**2)
            
        avg_speed = total_distance / duration if duration > 0 else 0
        
        # 记录主要信息
        self.logger.info(f"笔画 #{stroke_id}: {point_count}点, {duration:.2f}秒{direction_info}")
        self.logger.debug(f"笔画 #{stroke_id} 统计: 长度={total_distance:.1f}px, 速度={avg_speed:.1f}px/秒")
    
    def fade_path(self):
        """实现路径的淡出效果"""
        if not self.fading:
            self.fade_timer.stop()
            self.hide()
            self.logger.info(f"绘制会话完成: 记录了 {len(self.points)} 个点, {len(self.lines)} 条线")
            return
        
        # 如果已经重新开始绘制，则停止淡出效果
        if self.drawing:
            self.logger.debug("检测到新的绘制开始，停止淡出效果")
            self.fading = False
            self.fade_timer.stop()
            return
        
        # 更新透明度
        self.fade_alpha -= self.fade_speed
        
        if self.fade_alpha <= 0:
            # 淡出完成
            self.fade_alpha = 0
            self.fading = False
            self.fade_timer.stop()
            self.hide()
            self.logger.info(f"绘制会话完成: 记录了 {len(self.points)} 个点, {len(self.lines)} 条线")
            return
        
        # 重绘
        self.update()
    
    def paintEvent(self, event):
        """绘制事件处理"""
        if not self.image:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        if self.fading:
            # 绘制淡出效果
            painter.setOpacity(self.fade_alpha / 255.0)
        else:
            # 确保在正常绘制时完全不透明
            painter.setOpacity(1.0)
        
        # 绘制缓冲区内容
        painter.drawPixmap(0, 0, self.image)
    
    def resizeEvent(self, event):
        """窗口大小改变时调整画布大小"""
        if self.size().width() > 0 and self.size().height() > 0:
            new_image = QPixmap(self.size())
            new_image.fill(Qt.GlobalColor.transparent)
            
            if self.image:
                # 将原有内容绘制到新画布上
                painter = QPainter(new_image)
                painter.drawPixmap(0, 0, self.image)
                painter.end()
            
            self.image = new_image
            self.logger.debug(f"画布大小已调整: {self.size().width()}x{self.size().height()}")
            
    def get_stroke_direction(self, stroke_id=None):
        """获取指定笔画ID的方向，如不指定则获取最后一个笔画的方向"""
        if not self.lines:
            return "无笔画数据"
            
        if stroke_id is None:
            # 分析最后一个笔画
            stroke_data = self.lines[-1]
        else:
            # 查找匹配ID的笔画
            matching_strokes = [line for line in self.lines if line and line[0][4] == stroke_id]
            if not matching_strokes:
                return f"未找到ID为{stroke_id}的笔画"
            stroke_data = matching_strokes[0]
            
        direction_sequence, _ = self.stroke_analyzer.analyze_direction(stroke_data)
        return direction_sequence

class DrawingManager:
    """绘制管理器，只负责管理绘制功能"""
    
    def __init__(self):
        # 初始化日志记录器
        self.logger = get_logger("DrawingManager")
        self.logger.info("初始化绘制管理器")
        
        # 创建应用程序实例
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
            self.logger.debug("创建新的QApplication实例")
        else:
            self.logger.debug("使用现有的QApplication实例")
        
        # 创建信号对象，用于线程间通信
        self.signals = DrawingSignals()
        
        # 创建透明绘制覆盖层
        self.overlay = TransparentDrawingOverlay()
        
        # 连接信号到绘制方法
        self.signals.start_drawing_signal.connect(self.overlay.startDrawing)
        self.signals.continue_drawing_signal.connect(self.overlay.continueDrawing)
        self.signals.stop_drawing_signal.connect(self.overlay.stopDrawing)
        
        # 绘制状态
        self.is_active = False
        self.mouse_listener = None
        
        self.logger.info("绘制模块初始化完成")
    
    def start(self):
        """开始绘制功能 - 弹出绘制窗口并开始监听鼠标动作"""
        if self.is_active:
            self.logger.debug("绘制功能已经处于活动状态")
            return
            
        self.logger.info("启动绘制功能")
        
        # 从设置中读取笔尖粗细和颜色
        try:
            settings = get_settings()
            if settings:
                # 设置笔尖粗细
                pen_width = settings.get("pen_width")
                if pen_width:
                    self.overlay.set_pen_width(pen_width)
                    self.logger.debug(f"从设置中加载笔尖粗细: {pen_width}")
                
                # 设置笔尖颜色
                pen_color = settings.get("pen_color")
                if pen_color:
                    self.overlay.set_pen_color(pen_color)
                    self.logger.debug(f"从设置中加载笔尖颜色: {pen_color}")
            else:
                self.logger.warning("未能获取设置实例，使用当前默认值")
        except Exception as e:
            self.logger.error(f"加载笔尖设置失败: {e}，使用当前设置")
        
        # 初始化鼠标监听器
        self._init_mouse_hook()
        
        # 设置状态为活动
        self.is_active = True
        
        self.logger.debug("绘制功能已启动")
        
        return True
    
    def update_settings(self):
        """更新设置参数 - 无需重启绘制功能即可应用修改的参数"""
        self.logger.info("更新绘制参数")
        
        try:
            # 从设置中读取最新的参数
            settings = get_settings()
            if not settings:
                self.logger.warning("未能获取设置实例，无法更新设置")
                return False
                
            # 更新笔尖粗细
            pen_width = settings.get("pen_width")
            if pen_width:
                self.overlay.set_pen_width(pen_width)
                self.logger.debug(f"已更新笔尖粗细: {pen_width}")
            
            # 更新笔尖颜色
            pen_color = settings.get("pen_color")
            if pen_color:
                self.overlay.set_pen_color(pen_color)
                self.logger.debug(f"已更新笔尖颜色: {pen_color}")
            
            return True
        except Exception as e:
            self.logger.error(f"更新设置参数失败: {e}")
            return False
    
    def stop(self):
        """停止绘制功能 - 关闭绘制窗口并停止监听"""
        if not self.is_active:
            self.logger.debug("绘制功能已经停止")
            return
            
        self.logger.info("停止绘制功能")
        
        # 如果正在绘制中，先停止绘制
        if hasattr(self, 'right_mouse_down') and self.right_mouse_down:
            self.signals.stop_drawing_signal.emit()
            self.right_mouse_down = False
            self.last_position = None
        
        # 停止鼠标监听
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            self.logger.debug("鼠标监听器已停止")
        
        # 设置状态为非活动
        self.is_active = False
        
        self.logger.debug("绘制功能已停止")
        
        return True
    
    def _init_mouse_hook(self):
        """初始化全局鼠标监听（内部方法）"""
        try:
            self.right_mouse_down = False
            self.last_position = None
            self.last_pressure_time = 0
            self.simulated_pressure = 0.5
            
            def on_move(x, y):
                # 鼠标移动时，如果正在绘制，则通过信号更新绘制路径
                if self.right_mouse_down:
                    # 确保坐标有效
                    if x > 0 and y > 0:
                        # 模拟压力值
                        pressure = self._calculate_simulated_pressure(x, y)
                        self.signals.continue_drawing_signal.emit(x, y, pressure)
                        self.last_position = (x, y)
            
            def on_click(x, y, button, pressed):
                # 右键按下时开始绘制，松开时停止
                if button == mouse.Button.right:
                    if pressed:
                        # 确保坐标有效
                        if x > 0 and y > 0:
                            self.right_mouse_down = True
                            self.last_position = (x, y)
                            self.last_pressure_time = time.time()
                            self.simulated_pressure = 0.5  # 初始压力值
                            self.signals.start_drawing_signal.emit(x, y, self.simulated_pressure)
                            self.logger.info(f"开始绘制，坐标: ({x}, {y})")
                    else:
                        self.right_mouse_down = False
                        self.last_position = None
                        self.signals.stop_drawing_signal.emit()
                        self.logger.info("停止绘制")
            
            # 设置监听器
            self.mouse_listener = mouse.Listener(
                on_move=on_move,
                on_click=on_click
            )
            self.mouse_listener.start()
            self.logger.info("鼠标监听器已启动")
            
        except ImportError as e:
            self.logger.error(f"无法导入pynput库: {e}，请确保已安装: pip install pynput")
            self.is_active = False
            raise
        except Exception as e:
            self.logger.exception(f"初始化鼠标监听器时发生错误: {e}")
            self.is_active = False
            raise
    
    def _calculate_simulated_pressure(self, x, y):
        """根据鼠标移动速度计算模拟压力值"""
        if not self.last_position:
            return 0.5
            
        # 计算移动速度
        last_x, last_y = self.last_position
        distance = math.sqrt((x - last_x)**2 + (y - last_y)**2)
        current_time = time.time()
        time_diff = max(0.001, current_time - self.last_pressure_time)
        self.last_pressure_time = current_time
        
        # 计算速度并映射到压力值
        speed = distance / time_diff
        
        # 速度范围和对应的压力值
        min_speed, max_speed = 50, 2000
        min_pressure, max_pressure = 0.9, 0.3
        
        # 线性映射: 低速度对应高压力，高速度对应低压力
        if speed <= min_speed:
            pressure = max_pressure
        elif speed >= max_speed:
            pressure = min_pressure
        else:
            # 线性插值
            ratio = (speed - min_speed) / (max_speed - min_speed)
            pressure = max_pressure - ratio * (max_pressure - min_pressure)
        
        # 平滑压力变化
        self.simulated_pressure = self.simulated_pressure * 0.7 + pressure * 0.3
        
        return max(0.3, min(0.9, self.simulated_pressure))
    
    def get_last_direction(self):
        """获取最后一次绘制的方向序列"""
        return self.overlay.get_stroke_direction()


if __name__ == "__main__":
    try:
        # 示例用法
        drawer = DrawingManager()
        drawer.start()  # 开始绘制功能
        
        # 运行应用程序主循环
        app = QApplication.instance()
        sys.exit(app.exec())
    except Exception as e:
        # 获取一个独立的日志记录器记录主程序异常
        error_logger = get_logger("MainError")
        error_logger.exception(f"主程序发生未捕获的异常: {e}") 