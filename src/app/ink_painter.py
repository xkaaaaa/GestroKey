"""
绘画模块
调用说明：
1. 初始化：painter = InkPainter()
   - 创建全屏透明画布（窗口尺寸为全屏尺寸减1，不显示在任务栏）
   - 自动加载手势配置
   - 启动鼠标监听线程

2. 关闭：painter.shutdown()
   - 安全销毁所有资源
   - 停止监听循环
"""

import time
import math
import base64
import json
import numpy as np
import pyautogui
import win32api
import win32con
import os
import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath

try:
    from .gesture_parser import GestureParser
    from .log import log
    from .operation_executor import execute as execute_operation
except ImportError:
    from gesture_parser import GestureParser
    from log import log
    from operation_executor import execute as execute_operation

class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []
        # 设置为透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        # 硬件加速开关（由设置控制）
        self.enable_hardware_acceleration = True
        # 减少不必要的重绘
        self.update_scheduled = False
        # 批量绘制队列
        self.batch_updates = []
        # 线条绘制方式：单线条模式
        self.single_line_mode = True

    def create_line(self, x1, y1, x2, y2, width, fill, capstyle=Qt.RoundCap, smooth=True, joinstyle=Qt.RoundJoin):
        """创建一条线段"""
        line = {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'width': width, 'color': fill}
        self.lines.append(line)
        # 不立即更新，而是加入批量队列
        self.batch_updates.append(line)
        self.schedule_update()
        return line

    def itemconfig(self, line, fill):
        line['color'] = fill
        self.schedule_update()

    def delete(self, line):
        try:
            self.lines.remove(line)
        except ValueError:
            pass
        self.schedule_update()
    
    def schedule_update(self):
        """智能调度更新，避免频繁重绘"""
        if not self.update_scheduled:
            self.update_scheduled = True
            QTimer.singleShot(2, self.do_update)  # 2ms延迟，合并多次更新但保持反应灵敏
    
    def do_update(self):
        """执行实际更新"""
        self.update_scheduled = False
        self.batch_updates.clear()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # 始终开启完整抗锯齿
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # 仅绘制可见区域内的线条
        visible_rect = event.rect()
        
        # 使用更适合线条绘制的合成模式
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        for line in self.lines:
            pen = QPen(QColor(line['color']))
            pen.setWidthF(line['width'])
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            
            # 将坐标转换为浮点数以实现更平滑的线条
            x1, y1 = float(line['x1']), float(line['y1'])
            x2, y2 = float(line['x2']), float(line['y2'])
            
            # 粗略判断线条是否在可见区域内（边界框检测）
            if (max(x1, x2) < visible_rect.left() or min(x1, x2) > visible_rect.right() or
                max(y1, y2) < visible_rect.top() or min(y1, y2) > visible_rect.bottom()):
                continue  # 不在可见区域内，跳过绘制
                
            painter.setPen(pen)
            
            # 使用路径绘制实现更平滑的线条效果
            path = QPainterPath()
            path.moveTo(x1, y1)
            
            # 始终使用贝塞尔曲线绘制，提高平滑度
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            path.quadTo(mid_x, mid_y, x2, y2)
                
            painter.drawPath(path)

class InkPainter:
    def __init__(self):
        # 硬件参数
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.file_name = "ink_painter"
        
        log(__name__, "绘画模块初始化")
            
        # 状态控制
        self.drawing = False               # 绘画状态标志
        self.running = True                # 运行状态标志
        self.current_stroke = []           # 当前笔画数据（原始数据，用于手势识别）
        self.smoothed_stroke = []          # 平滑后的笔画数据（用于绘图显示）
        self.active_lines = []             # 画布线条对象
        self.fade_animations = []          # 渐隐动画队列
        self.start_point = None            # 记录起始点
        self.pending_points = []           # 存储达到触发条件前的轨迹点
        self.finished_strokes = []         # 已结束笔画，用于独立的手势识别
        self.forced_end = False            # 强制结束标志
        self.point_buffer = []             # 点缓冲区，用于高性能绘制
        
        # 初始化基本组件
        self.init_canvas()
        self.load_drawing_settings()
        self.load_gestures()
        self.init_gesture_parser()
        self.start_listening()
        
        log(__name__, "绘画模块初始化完成")

    def get_settings_path(self):
        """获取设置文件路径"""
        # 与main.py中相同逻辑
        if getattr(sys, 'frozen', False):
            # 打包后使用exe所在目录的上二级目录
            return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'settings.json')
        else:
            # 开发时使用当前文件的上一级目录（src → 根目录）
            return os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'settings.json'
            )
    
    def get_gesture_path(self):
        """获取手势库文件路径"""
        # 与main.py中相同逻辑
        if getattr(sys, 'frozen', False):
            # 打包后使用exe所在目录的上二级目录
            return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'gestures.json')
        else:
            # 开发时使用项目根目录
            # 从当前文件向上两级找到项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return os.path.join(project_root, 'gestures.json')

    def init_canvas(self):
        """初始化Canvas"""
        log(self.file_name, "初始化画布")
        # 创建QApplication实例，如果不存在则创建
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # 创建透明全屏画布
        self.canvas = Canvas()
        self.canvas.resize(self.screen_width, self.screen_height)
        self.canvas.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.canvas.setAttribute(Qt.WA_TranslucentBackground)
        self.canvas.setAttribute(Qt.WA_ShowWithoutActivating)
        log(self.file_name, "画布初始化完成")

    def load_drawing_settings(self):
        """加载绘画设置"""
        log(self.file_name, "加载绘画设置")
        
        # 默认设置
        self.base_width = 6
        self.min_width = 3
        self.max_width = 15
        self.speed_factor = 1.2
        self.fade_duration = 0.5  # 渐隐效果持续时间（秒）
        self.antialias_layers = 2  # 抗锯齿层数
        self.min_distance = 20  # 最小绘制距离
        self.line_color = "#00BFFF"  # 深天蓝色
        self.max_stroke_points = 200  # 每次笔画最大点数
        self.max_stroke_duration = 5  # 每次笔画最大时长（秒）
        self.enable_advanced_brush = True  # 启用高级笔刷效果
        self.force_topmost = True  # 强制窗口保持在最前
        self.enable_auto_smoothing = True  # 启用自动平滑
        self.smoothing_factor = 0.6  # 平滑因子
        self.enable_hardware_acceleration = True  # 启用硬件加速
        
        try:
            settings_path = self.get_settings_path()
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    settings = config.get('drawing_settings', {})
                    
                    # 更新设置
                    self.base_width = settings.get('base_width', self.base_width)
                    self.min_width = settings.get('min_width', self.min_width)
                    self.max_width = settings.get('max_width', self.max_width)
                    self.speed_factor = settings.get('speed_factor', self.speed_factor)
                    self.fade_duration = settings.get('fade_duration', self.fade_duration)
                    self.antialias_layers = settings.get('antialias_layers', self.antialias_layers)
                    self.min_distance = settings.get('min_distance', self.min_distance)
                    self.line_color = settings.get('line_color', self.line_color)
                    self.max_stroke_points = settings.get('max_stroke_points', self.max_stroke_points)
                    self.max_stroke_duration = settings.get('max_stroke_duration', self.max_stroke_duration)
                    self.enable_advanced_brush = settings.get('enable_advanced_brush', self.enable_advanced_brush)
                    self.force_topmost = settings.get('force_topmost', self.force_topmost)
                    self.enable_auto_smoothing = settings.get('enable_auto_smoothing', self.enable_auto_smoothing)
                    self.smoothing_factor = settings.get('smoothing_factor', self.smoothing_factor)
                    self.enable_hardware_acceleration = settings.get('enable_hardware_acceleration', self.enable_hardware_acceleration)
                    
                    log(self.file_name, "成功加载绘画设置")
            else:
                log(self.file_name, "设置文件不存在，使用默认设置")
        except Exception as e:
            log(self.file_name, f"加载设置失败: {str(e)}", level="error")
            print(f"加载设置失败: {str(e)}")
        
        # 更新Canvas的硬件加速设置
        if hasattr(self, 'canvas'):
            self.canvas.enable_hardware_acceleration = self.enable_hardware_acceleration

    def load_gestures(self):
        """加载手势库"""
        log(self.file_name, "加载手势库")
        self.gestures = {}
        gesture_path = self.get_gesture_path()
        
        try:
            if os.path.exists(gesture_path):
                with open(gesture_path, 'r', encoding='utf-8') as f:
                    gesture_data = json.load(f)
                    gestures_dict = gesture_data.get('gestures', {})
                    
                    # 处理手势数据
                    for name, gesture in gestures_dict.items():
                        directions = gesture.get('directions', '')
                        action_base64 = gesture.get('action', '')
                        
                        try:
                            # Base64解码操作
                            action = base64.b64decode(action_base64).decode('utf-8')
                            
                            # 添加到手势库
                            self.gestures[directions] = {
                    'name': name,
                                'action': action
                            }
                            log(self.file_name, f"成功加载手势: {name} - {directions}")
                        except Exception as e:
                            log(self.file_name, f"解析手势 {name} 失败: {str(e)}", level="error")
                    
                    log(self.file_name, f"成功加载手势库，共 {len(self.gestures)} 个手势")
            else:
                log(self.file_name, "手势库文件不存在，使用空手势库", level="warning")
        except Exception as e:
            log(self.file_name, f"加载手势库失败: {str(e)}", level="error")
            print(f"加载手势库失败: {str(e)}")

    def init_gesture_parser(self):
        """初始化手势解析器"""
        log(self.file_name, "初始化手势解析器")
        # 使用空列表作为trail_points初始化
        # 这里只是初始化一个解析器实例，实际手势识别时会创建新的实例
        self.parser = GestureParser(trail_points=[])
        log(self.file_name, "手势解析器初始化完成")

    def start_listening(self):
        """开始监听鼠标事件"""
        log(self.file_name, "开始监听鼠标事件")
        # 创建专用线程处理绘画过程
        self.processing_thread = QTimer()
        self.processing_thread.timeout.connect(self.process_points)
        self.processing_thread.start(10)  # 10ms一次处理
        
        # 初始化鼠标状态
        self.last_right_state = False
        
        # 启动鼠标监听循环
        QTimer.singleShot(10, self.listen_mouse)
        log(self.file_name, "鼠标监听已启动")

    def listen_mouse(self):
        """核心鼠标监听逻辑"""
        if not self.running:
            return
        
        # 如果强制置顶开关开启，确保窗口始终在顶层
        if hasattr(self, 'canvas') and self.canvas and self.force_topmost:
            try:
                self.canvas.raise_()
            except Exception as e:
                log(self.file_name, f"强制置顶失败: {str(e)}", level="error")
        
        # 获取鼠标状态和位置
        right_pressed = win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0
        x, y = pyautogui.position()
        
        # 状态切换处理
        if right_pressed and not self.last_right_state:
            # 刚按下右键，记录起始点
            if not self.drawing:
                self.start_point = (x, y)
                current_time = time.time()
                self.pending_points = [(x, y, current_time)]
                log(self.file_name, f"右键按下，记录起始点: ({x}, {y})")
        elif right_pressed and not self.drawing and self.start_point:
            # 持续按住右键但还未开始绘画，记录轨迹点
            current_time = time.time()
            self.pending_points.append((x, y, current_time))
            
            # 检查触发条件
            start_x, start_y = self.start_point
            dx = x - start_x
            dy = y - start_y
            distance = math.hypot(dx, dy)
            
            if distance >= self.min_distance:
                # 达到触发距离，开始绘画
                self.start_drawing()
                log(self.file_name, f"达到触发距离({distance:.1f}px >= {self.min_distance}px)，开始绘画")
        elif right_pressed and self.drawing:
            # 已在绘画中，添加点到缓冲区
            if not hasattr(self, 'last_point') or self.last_point != (x, y):
                self.point_buffer.append((x, y))
                self.last_point = (x, y)
        elif not right_pressed and self.last_right_state:
            # 松开右键，结束绘画
            if self.pending_points and not self.drawing:
                # 清理未完成的轨迹
                log(self.file_name, "松开右键，清理未触发的轨迹")
                self.pending_points = []
                self.start_point = None
            
            # 如果正在绘画，结束当前笔画
            if self.drawing:
                log(self.file_name, "松开右键，结束当前笔画")
            self.finish_drawing()
        
        # 更新上一次右键状态
        self.last_right_state = right_pressed
        
        # 继续监听
        QTimer.singleShot(5, self.listen_mouse)  # 5ms更新一次，保证响应灵敏

    def process_points(self):
        """处理积累的点数据"""
        if not self.drawing or not self.point_buffer:
            return
            
        # 批量处理缓冲区内的点，限制每次处理的点数量
        points_to_process = self.point_buffer[:20]  # 每次最多处理20个点
        if points_to_process:
            del self.point_buffer[:len(points_to_process)]
            
            # 批量处理绘制点
            for point in points_to_process:
                self.update_drawing(point[0], point[1])

    def update_drawing(self, x, y):
        """更新绘画状态"""
        # 添加当前点到笔画数据
        if not self.drawing:
            return
        
        current_time = time.time()
            
        # 检查是否是新笔画的第一个点
        if not hasattr(self, 'stroke_start_time') or not self.current_stroke:
            # 开始新笔画
            log(__name__, "开始新笔画")
            self.start_point = (x, y)
            self.current_stroke = [(x, y, current_time)]
            self.smoothed_stroke = [(x, y, current_time)]
            self.pending_points = []
            self.forced_end = False  # 重置强制结束标志
            
            # 添加线宽历史记录属性用于平滑处理
            self.line_width_history = []
            self.last_line_width = self.base_width
            
            # 重置笔画保护计时器
            self.stroke_start_time = current_time
            return
        
        # 防止与前一个点完全重合造成的零长度线段
        if self.current_stroke and len(self.current_stroke) > 0:
            prev_x, prev_y, prev_time = self.current_stroke[-1]
            if abs(x - prev_x) < 0.1 and abs(y - prev_y) < 0.1:
                return
        
        # 更新笔画数据
        elapsed = current_time - self.stroke_start_time
        
        # 添加新点
        self.current_stroke.append((x, y, current_time))
        
        # 笔画点数保护
        if len(self.current_stroke) > self.max_stroke_points:
            log(__name__, f"笔画超过最大点数限制({self.max_stroke_points})，强制结束")
            self.forced_end = True  # 设置强制结束标志
            self.finish_drawing()
            return
        
        # 笔画时长保护
        if elapsed > self.max_stroke_duration:
            log(__name__, f"笔画超过最大时长限制({self.max_stroke_duration}秒)，强制结束")
            self.forced_end = True  # 设置强制结束标志
            self.finish_drawing()
            return
        
        # 应用平滑处理
        if self.enable_auto_smoothing and len(self.current_stroke) >= 3:
            # 获取最后三个点
            points = self.current_stroke[-3:]
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            
            # 计算平滑点
            alpha = self.smoothing_factor  # 平滑系数
            smooth_x = alpha * (x_vals[0] + x_vals[2]) / 2 + (1 - alpha) * x_vals[1]
            smooth_y = alpha * (y_vals[0] + y_vals[2]) / 2 + (1 - alpha) * y_vals[1]
            
            # 替换中间点为平滑点
            self.smoothed_stroke.append((smooth_x, smooth_y, current_time))
        else:
            # 不应用平滑，直接添加原始点
            self.smoothed_stroke.append((x, y, current_time))
        
        # 计算线宽
        if len(self.smoothed_stroke) > 1:
            prev_x, prev_y, prev_time = self.smoothed_stroke[-2]
            curr_x, curr_y, curr_time = self.smoothed_stroke[-1]
            
            # 计算移动距离和时间差
            dist = math.sqrt((curr_x - prev_x) ** 2 + (curr_y - prev_y) ** 2)
            
            # 即使距离较大也进行连接，但需要处理大距离情况
            if dist > 100:
                log(self.file_name, f"发现距离较大的点，执行平滑连接: {dist:.1f}")
                
                # 对于特别大的距离，插入中间点
                if dist > 200:
                    # 计算需要插入多少个中间点
                    insert_count = min(10, int(dist / 30))
                    
                    # 最后绘制的坐标点
                    last_drawn_x, last_drawn_y = prev_x, prev_y
                    
                    # 计算高级画笔的线宽
                    line_width = self.calculate_line_width(prev_x, prev_y, curr_x, curr_y, prev_time, curr_time)
                    
                    # 创建插值点绘制线条
                    for i in range(1, insert_count + 1):
                        t = i / (insert_count + 1)
                        mid_x = prev_x + t * (curr_x - prev_x)
                        mid_y = prev_y + t * (curr_y - prev_y)
                        
                        # 绘制连接线段
                        new_lines = self.draw_single_line(
                            last_drawn_x, last_drawn_y, mid_x, mid_y, line_width)
                        self.active_lines.extend(new_lines)
                        
                        # 更新最后绘制点
                        last_drawn_x, last_drawn_y = mid_x, mid_y
                    
                    # 绘制最后一段到实际点
                    new_lines = self.draw_single_line(
                        last_drawn_x, last_drawn_y, curr_x, curr_y, line_width)
                    self.active_lines.extend(new_lines)
                    return
            
            # 计算并应用高级画笔线宽
            line_width = self.calculate_line_width(prev_x, prev_y, curr_x, curr_y, prev_time, curr_time)
            
            # 绘制线段
            new_lines = self.draw_single_line(prev_x, prev_y, curr_x, curr_y, line_width)
            self.active_lines.extend(new_lines)
            
    def calculate_line_width(self, prev_x, prev_y, curr_x, curr_y, prev_time, curr_time):
        """根据绘制速度计算线宽"""
        # 如果高级画笔功能被禁用，直接返回基础线宽
        if not self.enable_advanced_brush:
            return self.base_width
            
        # 计算移动距离和时间差
        dist = math.sqrt((curr_x - prev_x) ** 2 + (curr_y - prev_y) ** 2)
        time_diff = max(0.001, curr_time - prev_time)  # 防止除零
        
        # 计算速度
        speed = dist / time_diff
        
        # 速度映射到线宽调整系数，速度越大线条越细
        raw_speed_multiplier = max(0.5, min(1.5, 1.5 - (speed / (200 * self.speed_factor))))
        
        # 添加线宽平滑处理 - 使用移动平均来平滑线宽变化
        # 保留最近8个线宽值进行平均
        if not hasattr(self, 'line_width_history'):
            self.line_width_history = []
            
        self.line_width_history.append(raw_speed_multiplier)
        if len(self.line_width_history) > 8:
            self.line_width_history.pop(0)
        
        # 计算平滑后的线宽调整系数 - 使用加权移动平均
        weights = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]  # 越新的值权重越高
        trimmed_weights = weights[-len(self.line_width_history):]
        
        # 计算加权平均
        weighted_sum = sum(w * v for w, v in zip(trimmed_weights, self.line_width_history))
        weight_sum = sum(trimmed_weights)
        smooth_speed_multiplier = weighted_sum / weight_sum
        
        # 平滑处理：让当前值与上一个值之间有平滑过渡
        if hasattr(self, 'last_line_width'):
            # 在上一个值和当前计算值之间进行插值 - 60%上一个，40%当前
            transition_factor = 0.6  # 平滑因子，越大越平滑
            final_multiplier = (transition_factor * self.last_line_width/self.base_width + 
                              (1-transition_factor) * smooth_speed_multiplier)
            
            # 计算实际线宽
            line_width = max(self.min_width, min(self.max_width, self.base_width * final_multiplier))
            self.last_line_width = line_width  # 保存当前线宽用于下次平滑
        else:
            # 第一个点，直接使用计算值
            line_width = max(self.min_width, min(self.max_width, self.base_width * smooth_speed_multiplier))
            self.last_line_width = line_width
            
        return line_width

    def draw_single_line(self, x1, y1, x2, y2, width):
        """使用单线条模式绘制线段，简化实现，避免重叠描边"""
        # 确保线宽值不会太小
        width = max(2.5, width)
        
        # 简化绘制逻辑，统一使用单个线条，减少绘制开销
        line = self.canvas.create_line(
            float(x1), float(y1), float(x2), float(y2),
            width=width,
            fill=self.line_color,
            capstyle=Qt.RoundCap,
            smooth=True,
            joinstyle=Qt.RoundJoin
        )
        
        # 将线添加到活动线条列表中 - 这对渐隐效果很重要
        return [line]

    def finish_drawing(self):
        """结束绘画过程并启动渐隐效果"""
        log(__name__, "结束笔画，启动渐隐效果")
        if not self.drawing:
            return
        
        # 先保存当前状态用于手势识别
        current_stroke_copy = self.current_stroke.copy() if self.current_stroke else []
        
        # 重置绘画状态 - 放在前面以防止循环调用
        self.drawing = False
        
        # 如果是强制结束，则跳过手势识别
        is_forced_end = getattr(self, 'forced_end', False)
        
        # 添加到已完成笔画历史，并且进行手势识别（如果不是强制结束）
        if len(current_stroke_copy) > 5 and not is_forced_end:  # 至少需要5个点才能作为有效笔画
            self.finished_strokes.append(current_stroke_copy)
            
            # 尝试识别手势 - 直接处理，不使用线程
            try:
                log(__name__, "进行手势识别")
                # 准备轨迹点数据
                trail_points = [(x, y) for x, y, _ in current_stroke_copy]
                
                # 直接调用手势识别方法
                self._process_gesture(trail_points)
            except Exception as e:
                log(__name__, f"手势识别失败: {str(e)}", level="error")
        elif is_forced_end:
            log(__name__, "强制结束笔画，跳过手势识别")
        
        # 重置强制结束标志
        self.forced_end = False
        
        # 确保有线条要进行渐隐效果
        if not self.active_lines:
            log(__name__, "没有活动线条需要渐隐", level="warning")
            return
            
        # 启动渐隐效果
        if self.fade_duration > 0 and self.active_lines:
            log(__name__, f"启动渐隐效果，线条数量: {len(self.active_lines)}")
            fade_start = time.time()
            fade_end = fade_start + self.fade_duration
            
            # 设置渐隐动画
            self.fade_animations.append({
                'lines': self.active_lines.copy(),
                'start_color': self.line_color,
                'start_time': fade_start,
                'end_time': fade_end
            })
            
            # 启动渐隐处理定时器
            if not hasattr(self, 'fade_timer') or not self.fade_timer:
                self.fade_timer = QTimer()
                self.fade_timer.timeout.connect(self.process_fade_animation)
                self.fade_timer.start(20)  # 50 FPS
            elif not self.fade_timer.isActive():
                self.fade_timer.start(20)  # 如果定时器已存在但不活跃，重新启动
                
            # 清空当前笔画的线条引用，但不从画布删除（由渐隐过程负责）
            self.active_lines = []
        else:
            # 没有渐隐效果，直接清除线条
            for line in self.active_lines:
                self.canvas.delete(line)
            self.active_lines = []
        
        # 重置状态
        self.current_stroke = []
        self.smoothed_stroke = []
        self.line_width_history = []
        self.point_buffer = []  # 清空点缓冲区
        # 强制清除最后绘制点记录，避免连线bug
        if hasattr(self, 'last_drawn_point'):
            delattr(self, 'last_drawn_point')
        log(__name__, "笔画结束处理完成")
        
    def _process_gesture(self, trail_points):
        """处理手势识别"""
        try:
            log(__name__, "开始手势识别")
            
            # 创建新的GestureParser实例，传入轨迹点
            parser = GestureParser(trail_points)
            action = parser.parse()
            
            # 直接处理结果
            if action:
                log(__name__, f"识别到手势动作: {action}")
                self._handle_recognized_gesture(action)
            else:
                log(__name__, "未识别到有效手势")
                
        except Exception as e:
            log(__name__, f"手势识别出错: {str(e)}", level="error")
            
    def _handle_recognized_gesture(self, action):
        """处理识别出的手势"""
        try:
            log(__name__, "处理识别到的手势")
            
            # 清除线条显示
            if self.fade_animations:
                log(__name__, "清除渐隐线条")
                fade_copy = self.fade_animations.copy()
                for anim in fade_copy:
                    for line in anim['lines']:
                        try:
                            self.canvas.delete(line)
                        except Exception:
                            pass
                self.fade_animations.clear()
            
            # 直接调用顶部导入的execute_operation函数
            log(__name__, "执行手势动作")
            execute_operation(action)
            
        except Exception as e:
            log(__name__, f"处理手势失败: {str(e)}", level="error")

    def process_fade_animation(self):
        """处理渐隐动画帧"""
        current_time = time.time()
        removals = []
        
        # 每秒最多30帧动画更新
        min_interval = 1/30
        if hasattr(self, 'last_animation_time'):
            if current_time - self.last_animation_time < min_interval:
                # 如果距离上次更新不足1/30秒，跳过本次更新
                QTimer.singleShot(int((min_interval - (current_time - self.last_animation_time)) * 1000), 
                                self.process_fade_animation)
                return
                
        self.last_animation_time = current_time
        
        # 批量处理动画
        batch_updates = []
        
        for anim in self.fade_animations:
            elapsed = current_time - anim['start_time']
            duration = anim['end_time'] - anim['start_time'] if 'end_time' in anim else self.fade_duration
            progress = min(elapsed / duration, 1.0)
            
            # 动态计算颜色：保持原RGB，仅降低不透明度（alpha值）
            fade_color = self.calculate_fade_color(anim['start_color'], progress)
            
            # 批量收集更新
            for line_id in anim['lines']:
                batch_updates.append((line_id, fade_color))
            
            if progress >= 1.0:
                for line_id in anim['lines']:
                    self.canvas.delete(line_id)
                removals.append(anim)
        
        # 批量执行更新
        for line_id, color in batch_updates:
            self.canvas.itemconfig(line_id, color)
        
        # 移除已完成的动画
        for anim in removals:
            self.fade_animations.remove(anim)
        
        # 如果还有活动的动画，继续定时器
        if self.fade_animations:
            # 不需要重新启动定时器，会自动继续
            pass
        else:
            # 没有活动动画了，停止定时器
            if hasattr(self, 'fade_timer') and self.fade_timer:
                self.fade_timer.stop()

    def calculate_fade_color(self, base_color, progress):
        """计算渐隐过程中的颜色（保持RGB不变，仅降低alpha值）"""
        try:
            # 解析原始颜色
            if base_color.startswith("#"):
                # 十六进制颜色
                if len(base_color) == 7:  # #RRGGBB
                    r = int(base_color[1:3], 16)
                    g = int(base_color[3:5], 16)
                    b = int(base_color[5:7], 16)
                elif len(base_color) == 9:  # #AARRGGBB
                    r = int(base_color[3:5], 16)
                    g = int(base_color[5:7], 16)
                    b = int(base_color[7:9], 16)
                else:
                    r, g, b = 0, 191, 255  # 默认值
            else:
                # 如果不是十六进制，假设是rgb格式
                color_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', base_color)
                if color_match:
                    r, g, b = map(int, color_match.groups())
                else:
                    r, g, b = 0, 191, 255  # 默认值
            
            # 计算alpha值 - 使用非线性衰减，让开始减淡更慢一些
            a = int(255 * (1 - progress**0.7))  # 降低幂次，使淡出更平滑
            
        # 返回包含透明度信息的颜色，格式调整为 #AARRGGBB
            return f"#{a:02X}{r:02X}{g:02X}{b:02X}"
        except Exception as e:
            log(__name__, f"计算渐隐颜色失败: {str(e)}", level="error")
            return "#00BFFF"  # 返回默认颜色

    def shutdown(self):
        """安全关闭程序，释放资源"""
        log(__name__, "关闭绘画模块，释放资源")
        self.running = False
        
        # 停止所有定时器
        if hasattr(self, 'fade_timer') and self.fade_timer:
            self.fade_timer.stop()
            
        if hasattr(self, 'processing_thread') and self.processing_thread:
            self.processing_thread.stop()
        
        # 清空所有线条
        if hasattr(self, 'canvas') and self.canvas:
            for line in self.active_lines:
                self.canvas.delete(line)
                
            for anim in self.fade_animations:
                for line in anim['lines']:
                    self.canvas.delete(line)
        
        # 关闭窗口
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.hide()
        self.canvas.close()
        
        log(__name__, "绘画模块已安全关闭")

    def start_drawing(self):
        """启动绘画模式"""
        log(__name__, "启动绘画模式")
        # 避免重复启动
        if self.drawing:
            log(__name__, "绘画模式已经处于激活状态")
            return
        
        # 设置绘画状态为True
        self.drawing = True
        
        # 显示画布
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.show()
            log(__name__, "绘画窗口已显示")
        else:
            log(__name__, "绘画窗口初始化失败", level="error")
        
        # 处理积累的轨迹点
        if self.pending_points and len(self.pending_points) > 0:
            log(__name__, f"处理之前积累的 {len(self.pending_points)} 个轨迹点")
            
            # 初始化笔画状态
            self.current_stroke = self.pending_points.copy()
            self.smoothed_stroke = self.current_stroke.copy()
            self.stroke_start_time = self.pending_points[0][2]  # 使用第一个点的时间
            self.line_width_history = []
            self.last_line_width = self.base_width
            
            # 绘制累积的轨迹
            if len(self.pending_points) > 1:
                # 批量处理点数据，绘制线条
                for i in range(1, len(self.pending_points)):
                    prev_x, prev_y, prev_time = self.pending_points[i-1]
                    curr_x, curr_y, curr_time = self.pending_points[i]
                    
                    # 计算线宽
                    line_width = self.calculate_line_width(prev_x, prev_y, curr_x, curr_y, prev_time, curr_time)
                    
                    # 绘制线段
                    new_lines = self.draw_single_line(prev_x, prev_y, curr_x, curr_y, line_width)
                    self.active_lines.extend(new_lines)
            
            # 清空待处理点列表，因为这些点已被处理
            self.pending_points = []
        
        log(__name__, "绘画模式已启动")

    def stop_drawing(self):
        """停止绘画模式"""
        log(__name__, "停止绘画模式")
        
        # 调用shutdown方法来处理资源释放
        self.shutdown()
        
        # 确保drawing状态被重置
        self.drawing = False
        log(__name__, "绘画模式已停止")

if __name__ == "__main__":
    print("建议通过主程序运行。")
    test_painter = InkPainter()
    # 启动Qt事件循环，保持程序运行
    sys.exit(test_painter.app.exec_())