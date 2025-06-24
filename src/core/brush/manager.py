import os
import sys
import time
import traceback

from pynput import mouse
from qtpy.QtWidgets import QApplication

from .overlay import DrawingSignals, TransparentDrawingOverlay

from core.logger import get_logger
from ui.settings.settings import get_settings


class DrawingManager:
    """绘制管理器"""

    def __init__(self):
        self.logger = get_logger("DrawingManager")
        self.logger.info("初始化绘制管理器")

        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
            self.logger.debug("创建新的QApplication实例")
        else:
            self.logger.debug("使用现有的QApplication实例")

        self.signals = DrawingSignals()
        self.overlay = TransparentDrawingOverlay()

        self.signals.start_drawing_signal.connect(self.overlay.startDrawing)
        self.signals.continue_drawing_signal.connect(self.overlay.continueDrawing)
        self.signals.stop_drawing_signal.connect(self.overlay.stopDrawing)

        self.is_active = False
        self.mouse_listener = None

        self.last_move_time = 0
        self.move_throttle_ms = 5

        self.logger.info("绘制模块初始化完成")

    def start(self):
        """开始绘制功能"""
        if self.is_active:
            self.logger.debug("绘制功能已经处于活动状态")
            return

        self.logger.info("启动绘制功能")

        try:
            settings = get_settings()
            if settings:
                pen_width = settings.get("brush.pen_width")
                if pen_width:
                    self.overlay.set_pen_width(pen_width)
                    self.logger.debug(f"从设置中加载笔尖粗细: {pen_width}")

                pen_color = settings.get("brush.pen_color")
                if pen_color:
                    self.overlay.set_pen_color(pen_color)
                    self.logger.debug(f"从设置中加载笔尖颜色: {pen_color}")

                brush_type = settings.get("brush.brush_type", "pencil")
                self.overlay.set_brush_type(brush_type)
                self.logger.debug(f"从设置中加载画笔类型: {brush_type}")

                force_topmost = settings.get("brush.force_topmost", True)
                self.overlay.set_force_topmost(force_topmost)
                self.logger.debug(f"从设置中加载强制置顶设置: {force_topmost}")
            else:
                self.logger.warning("未能获取设置实例，使用当前默认值")
        except Exception as e:
            self.logger.error(f"加载笔尖设置失败: {e}，使用当前设置")

        self._init_mouse_hook()
        self.is_active = True
        self.logger.debug("绘制功能已启动")

        return True

    def update_settings(self):
        """更新设置参数"""
        self.logger.info("更新绘制参数")

        try:
            settings = get_settings()
            if not settings:
                self.logger.warning("未能获取设置实例，无法更新设置")
                return False

            pen_width = settings.get("brush.pen_width")
            if pen_width:
                self.overlay.set_pen_width(pen_width)
                self.logger.debug(f"已更新笔尖粗细: {pen_width}")

            pen_color = settings.get("brush.pen_color")
            if pen_color:
                self.overlay.set_pen_color(pen_color)
                self.logger.debug(f"已更新笔尖颜色: {pen_color}")

            brush_type = settings.get("brush.brush_type", "pencil")
            self.overlay.set_brush_type(brush_type)
            self.logger.debug(f"已更新画笔类型: {brush_type}")

            force_topmost = settings.get("brush.force_topmost", True)
            self.overlay.set_force_topmost(force_topmost)
            self.logger.debug(f"已更新强制置顶设置: {force_topmost}")

            return True
        except Exception as e:
            self.logger.error(f"更新设置参数失败: {e}")
            return False

    def stop(self):
        """停止绘制功能"""
        if not self.is_active:
            self.logger.debug("绘制功能已经停止")
            return

        self.logger.info("停止绘制功能")

        if hasattr(self, "right_mouse_down") and self.right_mouse_down:
            self.signals.stop_drawing_signal.emit()
            self.right_mouse_down = False
            self.last_position = None

        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            self.logger.debug("鼠标监听器已停止")

        self.is_active = False
        self.logger.debug("绘制功能已停止")

        return True

    def _init_mouse_hook(self):
        """初始化全局鼠标监听"""
        try:
            self.right_mouse_down = False
            self.last_position = None
            self.last_pressure_time = 0
            self.simulated_pressure = 0.5

            def on_move(x, y):
                if self.right_mouse_down:
                    if x > 0 and y > 0:
                        current_time = time.time() * 1000
                        if current_time - self.last_move_time < self.move_throttle_ms:
                            return
                        self.last_move_time = current_time

                        pressure = self._calculate_simulated_pressure(x, y)
                        self.signals.continue_drawing_signal.emit(x, y, pressure)
                        self.last_position = (x, y)

            def on_click(x, y, button, pressed):
                if button == mouse.Button.right:
                    if pressed:
                        if x > 0 and y > 0:
                            self.right_mouse_down = True
                            self.last_position = (x, y)
                            self.last_pressure_time = time.time()
                            self.simulated_pressure = 0.5
                            self.signals.start_drawing_signal.emit(
                                x, y, self.simulated_pressure
                            )
                            self.logger.info(f"开始绘制，坐标: ({x}, {y})")
                    else:
                        self.right_mouse_down = False
                        self.last_position = None
                        self.signals.stop_drawing_signal.emit()
                        self.logger.info("停止绘制")

            self.mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
            self.mouse_listener.start()
            self.logger.info("鼠标监听器已启动")

        except ImportError as e:
            self.logger.error(f"无法导入pynput库: {e}，请确保已安装: pip install pynput")
            self.is_active = False
            raise
        except Exception as e:
            self.logger.error(f"初始化鼠标监听器失败: {e}")
            self.logger.error(traceback.format_exc())
            self.is_active = False
            raise

    def _calculate_simulated_pressure(self, x, y):
        """计算模拟压力值"""
        try:
            current_time = time.time()
            
            if self.last_position and self.last_pressure_time:
                dx = x - self.last_position[0]
                dy = y - self.last_position[1]
                distance = (dx**2 + dy**2) ** 0.5
                time_delta = current_time - self.last_pressure_time
                
                if time_delta > 0:
                    speed = distance / time_delta
                    max_speed = 2000
                    speed_ratio = min(speed / max_speed, 1.0)
                    pressure = 0.8 - (speed_ratio * 0.6)
                    
                    smooth_factor = 0.3
                    self.simulated_pressure = (
                        self.simulated_pressure * (1 - smooth_factor) + 
                        pressure * smooth_factor
                    )
            else:
                self.simulated_pressure = 0.5
            
            self.last_pressure_time = current_time
            self.simulated_pressure = max(0.1, min(1.0, self.simulated_pressure))
            
            return self.simulated_pressure
            
        except Exception as e:
            self.logger.warning(f"计算模拟压力值时出错: {e}")
            return 0.5

    def get_last_direction(self):
        """获取最后一次绘制的方向信息"""
        try:
            return self.overlay.get_stroke_direction()
        except Exception as e:
            self.logger.error(f"获取绘制方向失败: {e}")
            return "获取方向信息失败"