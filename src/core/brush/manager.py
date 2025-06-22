"""
绘制管理器

管理绘制功能的启动、停止和设置更新
"""

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

        # 性能优化 - 鼠标事件限流
        self.last_move_time = 0
        self.move_throttle_ms = 5  # 限制鼠标移动事件处理频率

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
                pen_width = settings.get("brush.pen_width")
                if pen_width:
                    self.overlay.set_pen_width(pen_width)
                    self.logger.debug(f"从设置中加载笔尖粗细: {pen_width}")

                # 设置笔尖颜色
                pen_color = settings.get("brush.pen_color")
                if pen_color:
                    self.overlay.set_pen_color(pen_color)
                    self.logger.debug(f"从设置中加载笔尖颜色: {pen_color}")

                # 设置画笔类型
                brush_type = settings.get("brush.brush_type", "pencil")
                self.overlay.set_brush_type(brush_type)
                self.logger.debug(f"从设置中加载画笔类型: {brush_type}")

                # 设置强制置顶
                force_topmost = settings.get("brush.force_topmost", True)
                self.overlay.set_force_topmost(force_topmost)
                self.logger.debug(f"从设置中加载强制置顶设置: {force_topmost}")
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
            pen_width = settings.get("brush.pen_width")
            if pen_width:
                self.overlay.set_pen_width(pen_width)
                self.logger.debug(f"已更新笔尖粗细: {pen_width}")

            # 更新笔尖颜色
            pen_color = settings.get("brush.pen_color")
            if pen_color:
                self.overlay.set_pen_color(pen_color)
                self.logger.debug(f"已更新笔尖颜色: {pen_color}")

            # 更新画笔类型
            brush_type = settings.get("brush.brush_type", "pencil")
            self.overlay.set_brush_type(brush_type)
            self.logger.debug(f"已更新画笔类型: {brush_type}")

            # 更新强制置顶设置
            force_topmost = settings.get("brush.force_topmost", True)
            self.overlay.set_force_topmost(force_topmost)
            self.logger.debug(f"已更新强制置顶设置: {force_topmost}")

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
        if hasattr(self, "right_mouse_down") and self.right_mouse_down:
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
                        # 限流处理，减少处理频率
                        current_time = time.time() * 1000  # 转换为毫秒
                        if current_time - self.last_move_time < self.move_throttle_ms:
                            return
                        self.last_move_time = current_time

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
                            self.signals.start_drawing_signal.emit(
                                x, y, self.simulated_pressure
                            )
                            self.logger.info(f"开始绘制，坐标: ({x}, {y})")
                    else:
                        self.right_mouse_down = False
                        self.last_position = None
                        self.signals.stop_drawing_signal.emit()
                        self.logger.info("停止绘制")

            # 设置监听器
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
        """计算模拟压力值（内部方法）"""
        try:
            current_time = time.time()
            
            # 基于移动速度计算压力
            if self.last_position and self.last_pressure_time:
                # 计算移动距离和时间差
                dx = x - self.last_position[0]
                dy = y - self.last_position[1]
                distance = (dx**2 + dy**2) ** 0.5
                time_delta = current_time - self.last_pressure_time
                
                if time_delta > 0:
                    # 计算速度（像素/秒）
                    speed = distance / time_delta
                    
                    # 速度越快，压力越小（模拟快速移动时压力减小的效果）
                    # 速度范围大致在 0-2000 像素/秒
                    max_speed = 2000
                    speed_ratio = min(speed / max_speed, 1.0)
                    
                    # 压力值在 0.2-0.8 之间变化，速度越快压力越小
                    pressure = 0.8 - (speed_ratio * 0.6)
                    
                    # 平滑处理，避免压力值变化过于剧烈
                    smooth_factor = 0.3
                    self.simulated_pressure = (
                        self.simulated_pressure * (1 - smooth_factor) + 
                        pressure * smooth_factor
                    )
                else:
                    # 时间差为0，保持当前压力
                    pass
            else:
                # 首次计算，使用默认压力
                self.simulated_pressure = 0.5
            
            # 更新时间记录
            self.last_pressure_time = current_time
            
            # 确保压力值在合理范围内
            self.simulated_pressure = max(0.1, min(1.0, self.simulated_pressure))
            
            return self.simulated_pressure
            
        except Exception as e:
            self.logger.warning(f"计算模拟压力值时出错: {e}")
            return 0.5  # 返回默认压力值

    def get_last_direction(self):
        """获取最后一次绘制的方向信息"""
        try:
            return self.overlay.get_stroke_direction()
        except Exception as e:
            self.logger.error(f"获取绘制方向失败: {e}")
            return "获取方向信息失败"