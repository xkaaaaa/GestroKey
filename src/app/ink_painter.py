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
            # 处理颜色 - 可能是元组(r,g,b)或字符串"#RRGGBB"
            color = line['color']
            if isinstance(color, tuple) and len(color) >= 3:
                # RGB元组
                r, g, b = color[0], color[1], color[2]
                qcolor = QColor(r, g, b)
            elif isinstance(color, str) and color.startswith('#'):
                # 十六进制字符串
                qcolor = QColor(color)
            else:
                # 默认颜色
                qcolor = QColor(0, 191, 255)  # 深天蓝色
                
            pen = QPen(qcolor)
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
    def __init__(self, config=None):
        """初始化笔画管理器
        
        Args:
            config: 配置信息字典
        """
        super().__init__()
        
        # 设置文件名用于日志标识
        self.file_name = "ink_painter: "
        
        # 加载配置
        self.config = config if config else {}
        
        # 状态变量
        self.is_drawing = False   # 是否处于绘画状态
        self.is_listening = False  # 是否正在监听鼠标
        self.is_active = False    # 组件是否处于激活状态
        
        # 默认绘画设置
        self.base_width = 6.0  # 基础线条宽度
        self.min_width = 3.0   # 最小线条宽度
        self.max_width = 15.0  # 最大线条宽度
        self.smoothing = 0.7   # 平滑度
        self.line_color = (0, 191, 255)  # 深天蓝色 RGB
        self.use_advanced_brush = True   # 使用高级笔刷
        self.auto_smoothing = True       # 自动平滑
        self.fade_duration = 0.5         # 渐隐持续时间（秒）
        self.speed_factor = 1.2          # 速度因子
        self.min_distance = 20           # 最小触发距离（像素）
        self.max_stroke_points = 200     # 最大笔画点数
        self.max_stroke_duration = 5     # 最大笔画持续时间（秒）
        
        # 状态变量
        self.right_button_pressed = False  # 右键是否按下
        self.start_point = None  # 起始点
        self.current_stroke = []  # 当前笔画的点
        self.smoothed_stroke = []  # 平滑后的笔画点
        self.active_lines = []  # 当前活动的线条
        self.point_buffer = []  # 点缓冲区
        self.fade_animations = []  # 渐隐动画列表
        self.line_width_history = []  # 线宽历史
        self.forced_end = False  # 是否强制结束笔画
        self.stroke_start_time = 0  # 笔画开始时间
        
        # 硬件参数
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        log.info("绘画模块初始化")
            
        # 状态控制
        self.running = True                # 运行状态标志
        self.current_stroke = []           # 当前笔画数据（原始数据，用于手势识别）
        self.smoothed_stroke = []          # 平滑后的笔画数据（用于绘图显示）
        self.active_lines = []             # 画布线条对象
        self.fade_animations = []          # 渐隐动画队列
        self.pending_points = []           # 存储达到触发条件前的轨迹点
        self.finished_strokes = []         # 已结束笔画，用于独立的手势识别
        self.forced_end = False            # 强制结束标志
        self.point_buffer = []             # 点缓冲区，用于高性能绘制
        
        # 初始化基本组件
        self.init_canvas()
        self.load_settings()
        self.load_gestures()
        self.init_gesture_parser()
        self.start_listening()
        
        log.info("绘画模块初始化完成")

    def get_config_path(self):
        """获取配置文件路径"""
        # 优先查找项目目录下的配置文件
        src_dir_config = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")
        
        if os.path.exists(src_dir_config):
            log.info(f"使用项目目录下的配置文件: {src_dir_config}")
            return src_dir_config
        
        # 使用用户主目录下的.gestrokey文件夹
        config_dir = os.path.expanduser("~/.gestrokey")
        return os.path.join(config_dir, "settings.json")
    
    def get_gesture_path(self):
        """获取手势库文件路径"""
        # 优先查找项目目录下的手势库文件
        src_dir_gestures = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gestures.json")
        
        if os.path.exists(src_dir_gestures):
            log.info(f"使用项目目录下的手势库文件: {src_dir_gestures}")
            return src_dir_gestures
        
        # 使用用户主目录下的.gestrokey文件夹
        config_dir = os.path.expanduser("~/.gestrokey")
        return os.path.join(config_dir, "gestures.json")

    def init_canvas(self):
        """初始化Canvas"""
        log.info(self.file_name + "初始化画布")
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
        log.info(self.file_name + "画布初始化完成")

    def load_settings(self):
        """从配置文件加载绘画设置"""
        log.info(self.file_name + "加载绘画设置")
        
        try:
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    drawing_settings = config.get('drawing', {})
                    
                    # 更新绘画设置
                    if drawing_settings:
                        # 基础宽度
                        if 'base_width' in drawing_settings:
                            self.base_width = float(drawing_settings['base_width'])
                            
                        # 最小宽度
                        if 'min_width' in drawing_settings:
                            self.min_width = float(drawing_settings['min_width'])
                            
                        # 最大宽度
                        if 'max_width' in drawing_settings:
                            self.max_width = float(drawing_settings['max_width'])
                            
                        # 平滑度
                        if 'smoothing' in drawing_settings:
                            self.smoothing = float(drawing_settings['smoothing'])
                            
                        # 颜色
                        if 'color' in drawing_settings:
                            color_hex = drawing_settings['color']
                            # 解析HEX颜色
                            if color_hex.startswith('#') and len(color_hex) in [4, 7, 9]:
                                try:
                                    r, g, b = self.hex_to_rgb(color_hex)
                                    # 设置颜色
                                    self.line_color = (r, g, b)
                                except Exception as e:
                                    log.error(f"颜色解析失败: {str(e)}")
                                    
                        # 高级笔刷
                        if 'advanced_brush' in drawing_settings:
                            self.use_advanced_brush = bool(drawing_settings['advanced_brush'])
                            
                        # 自动平滑
                        if 'auto_smoothing' in drawing_settings:
                            self.auto_smoothing = bool(drawing_settings['auto_smoothing'])
                            
                        # 淡出时间
                        if 'fade_time' in drawing_settings:
                            self.fade_duration = float(drawing_settings['fade_time'])
                            
                        # 速度因子
                        if 'speed_factor' in drawing_settings:
                            self.speed_factor = float(drawing_settings['speed_factor'])
                            
                    log.info(self.file_name + "成功加载绘画设置")
            else:
                log.warning(self.file_name + "配置文件不存在，使用默认设置")
        except Exception as e:
            log.error(self.file_name + "加载设置失败: " + str(e))

    def load_gestures(self):
        """加载手势库"""
        log.info(self.file_name + "加载手势库")
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
                            log.info(self.file_name + "成功加载手势: " + name + " - " + directions)
                        except Exception as e:
                            log.error("解析手势 " + name + " 失败: " + str(e))
                    
                    log.info(self.file_name + "成功加载手势库，共 " + str(len(self.gestures)) + " 个手势")
            else:
                log.warning(self.file_name + "手势库文件不存在，使用空手势库")
        except Exception as e:
            log.error("加载手势库失败: " + str(e))
            print("加载手势库失败: " + str(e))

    def init_gesture_parser(self):
        """初始化手势解析器"""
        log.info(self.file_name + "初始化手势解析器")
        # 使用空列表作为trail_points初始化
        # 这里只是初始化一个解析器实例，实际手势识别时会创建新的实例
        self.parser = GestureParser(trail_points=[])
        log.info(self.file_name + "手势解析器初始化完成")

    def start_listening(self):
        """开始监听鼠标事件"""
        log.info(self.file_name + "开始监听鼠标事件")
        # 设置监听状态为True
        self.is_listening = True
        
        # 创建专用线程处理绘画过程
        self.processing_thread = QTimer()
        self.processing_thread.timeout.connect(self.process_points)
        self.processing_thread.start(10)  # 10ms一次处理
        
        # 初始化鼠标状态
        self.last_right_state = False
        
        # 启动鼠标监听循环
        QTimer.singleShot(10, self.listen_mouse)
        log.info(self.file_name + "鼠标监听已启动")

    def listen_mouse(self):
        """监听鼠标状态"""
        # 如果不在监听状态，直接返回
        if not self.is_listening:
            return
            
        # 获取鼠标状态
        right_pressed = win32api.GetKeyState(win32con.VK_RBUTTON) < 0
        x, y = win32api.GetCursorPos()
        
        # 处理鼠标事件
        if right_pressed and not self.last_right_state:
            # 按下右键，记录起始点
            self.start_point = (x, y)
            self.pending_points = [(x, y)]
            log.info(self.file_name + f"右键按下，记录起始点: {self.start_point}")
        elif right_pressed and self.last_right_state:
            # 持续按下右键，处理移动
            if self.start_point:
                # 计算距离
                dx = x - self.start_point[0]
                dy = y - self.start_point[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                # 未开始绘画时，检查是否达到触发距离
                if not self.is_drawing and distance >= self.min_distance:
                    # 启动绘画
                    self.start_drawing(self.pending_points)
                
                # 已开始绘画或未达到触发距离，记录点
                if self.is_drawing:
                    # 添加到绘画缓冲
                    self.point_buffer.append((x, y))
                else:
                    # 添加到待处理点
                    self.pending_points.append((x, y))
                    
                if len(self.point_buffer) % 10 == 0:
                    log.debug(f"绘画中，已缓冲 {len(self.point_buffer)} 个点")
        elif not right_pressed and self.last_right_state:
            # 松开右键，结束绘画
            if self.pending_points and not self.is_drawing:
                # 清理未完成的轨迹
                log.info(self.file_name + f"松开右键，清理未触发的轨迹，点数: {len(self.pending_points)}")
                self.pending_points = []
                self.start_point = None
            
            # 如果正在绘画，结束当前笔画
            if self.is_drawing:
                log.info(self.file_name + f"松开右键，结束当前笔画，点数: {len(self.current_stroke) if self.current_stroke else 0}")
            self.finish_drawing()
        
        # 更新上一次右键状态
        self.last_right_state = right_pressed
        
        # 继续监听
        QTimer.singleShot(5, self.listen_mouse)  # 5ms更新一次，保证响应灵敏

    def process_points(self):
        """处理积累的点数据"""
        if not self.is_drawing or not self.point_buffer:
            return
        
        # 创建缓冲区副本并清空原缓冲区
        buffer_copy = self.point_buffer.copy()
        self.point_buffer = []
        
        # 处理缓冲区中的点
        for x, y in buffer_copy:
            current_time = time.time()
            
            # 添加到当前笔画
            self.update_drawing(x, y)

    def update_drawing(self, x, y):
        """更新绘画状态"""
        # 添加当前点到笔画数据
        if not self.is_drawing:
            return
        
        current_time = time.time()
            
        # 检查是否是新笔画的第一个点
        if not hasattr(self, 'stroke_start_time') or not self.current_stroke:
            # 开始新笔画
            log.info("开始新笔画")
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
            log.info("笔画超过最大点数限制(" + str(self.max_stroke_points) + ")，强制结束")
            self.forced_end = True  # 设置强制结束标志
            self.finish_drawing()
            return
        
        # 笔画时长保护
        if elapsed > self.max_stroke_duration:
            log.info("笔画超过最大时长限制(" + str(self.max_stroke_duration) + "秒)，强制结束")
            self.forced_end = True  # 设置强制结束标志
            self.finish_drawing()
            return
        
        # 应用平滑处理
        if self.auto_smoothing and len(self.current_stroke) >= 3:
            # 获取最后三个点
            points = self.current_stroke[-3:]
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            
            # 计算平滑点
            alpha = self.smoothing  # 平滑系数
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
                log.info(self.file_name + "发现距离较大的点，执行平滑连接: " + str(dist))
                
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
        if not self.use_advanced_brush:
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
        
        # 转换RGB元组为CSS格式颜色字符串
        if isinstance(self.line_color, tuple) and len(self.line_color) >= 3:
            r, g, b = self.line_color
            color_str = f"rgb({r},{g},{b})"
        else:
            color_str = self.line_color
        
        # 简化绘制逻辑，统一使用单个线条，减少绘制开销
        line = self.canvas.create_line(
            float(x1), float(y1), float(x2), float(y2),
            width=width,
            fill=color_str,
            capstyle=Qt.RoundCap,
            smooth=True,
            joinstyle=Qt.RoundJoin
        )
        
        # 将线添加到活动线条列表中 - 这对渐隐效果很重要
        return [line]

    def finish_drawing(self):
        """结束绘画过程并启动渐隐效果"""
        log.info("结束笔画，启动渐隐效果")
        if not self.is_drawing:
            return
        
        # 先保存当前状态用于手势识别
        current_stroke_copy = self.current_stroke.copy() if self.current_stroke else []
        
        # 重置绘画状态 - 放在前面以防止循环调用
        self.is_drawing = False
        
        # 如果是强制结束，则跳过手势识别
        is_forced_end = getattr(self, 'forced_end', False)
        
        # 添加到已完成笔画历史，并且进行手势识别（如果不是强制结束）
        if len(current_stroke_copy) > 5 and not is_forced_end:  # 至少需要5个点才能作为有效笔画
            self.finished_strokes.append(current_stroke_copy)
            
            # 尝试识别手势 - 直接处理，不使用线程
            try:
                log.info("进行手势识别")
                # 准备轨迹点数据
                trail_points = [(x, y) for x, y, _ in current_stroke_copy]
                
                # 直接调用手势识别方法
                self._process_gesture(trail_points)
            except Exception as e:
                log.error("手势识别失败: " + str(e))
        elif is_forced_end:
            log.info("强制结束笔画，跳过手势识别")
        
        # 重置强制结束标志
        self.forced_end = False
        
        # 确保有线条要进行渐隐效果
        if not self.active_lines:
            log.warning("没有活动线条需要渐隐")
            return
            
        # 启动渐隐效果
        if self.fade_duration > 0 and self.active_lines:
            log.info("启动渐隐效果，线条数量: " + str(len(self.active_lines)))
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
        log.info("笔画结束处理完成")
        
    def _process_gesture(self, trail_points):
        """处理手势识别"""
        try:
            log.info(f"开始手势识别，轨迹点数量: {len(trail_points)}")
            
            # 记录部分轨迹点位置，便于调试
            if len(trail_points) > 5:
                first_points = trail_points[:3]
                last_points = trail_points[-3:]
                log.debug(f"轨迹起始点: {first_points}, 结束点: {last_points}")
            
            # 创建新的GestureParser实例，传入轨迹点
            parser = GestureParser(trail_points)
            action = parser.parse()
            
            # 直接处理结果
            if action:
                log.info(f"识别到手势动作: {action}")
                self._handle_recognized_gesture(action)
            else:
                log.info("未识别到有效手势，检查轨迹是否符合预期")
                
        except Exception as e:
            log.error(f"手势识别出错: {str(e)}")
            import traceback
            log.error(f"异常堆栈: {traceback.format_exc()}")
            
    def _handle_recognized_gesture(self, action):
        """处理识别出的手势"""
        try:
            log.info("处理识别到的手势")
            
            # 清除线条显示
            if self.fade_animations:
                log.info("清除渐隐线条")
                fade_copy = self.fade_animations.copy()
                for anim in fade_copy:
                    for line in anim['lines']:
                        try:
                            self.canvas.delete(line)
                        except Exception:
                            pass
                self.fade_animations.clear()
            
            # 直接调用顶部导入的execute_operation函数
            log.info("执行手势动作")
            execute_operation(action)
            
        except Exception as e:
            log.error("处理手势失败: " + str(e))

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
            if isinstance(base_color, tuple) and len(base_color) >= 3:
                # 元组形式的RGB颜色
                r, g, b = base_color
            elif isinstance(base_color, str) and base_color.startswith("#"):
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
            elif isinstance(base_color, str):
                # 如果不是十六进制，假设是rgb格式
                color_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', base_color)
                if color_match:
                    r, g, b = map(int, color_match.groups())
                else:
                    r, g, b = 0, 191, 255  # 默认值
            else:
                # 无法识别的颜色格式，使用默认值
                r, g, b = 0, 191, 255  # 默认值
            
            # 计算alpha值 - 使用非线性衰减，让开始减淡更慢一些
            a = int(255 * (1 - progress**0.7))  # 降低幂次，使淡出更平滑
            
            # 返回包含透明度信息的颜色，格式调整为 #AARRGGBB
            return f"#{a:02X}{r:02X}{g:02X}{b:02X}"
        except Exception as e:
            log.error("计算渐隐颜色失败: " + str(e))
            return "#00BFFF"  # 返回默认颜色

    def shutdown(self):
        """安全关闭程序，释放资源"""
        log.info("关闭绘画模块，释放资源")
        self.running = False
        
        # 停止监听鼠标
        self.is_listening = False
        
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
        
        log.info("绘画模块已安全关闭")

    def start_drawing(self, points):
        """启动绘画模式"""
        log.info("启动绘画模式")
        # 避免重复启动
        if self.is_drawing:
            log.info("绘画模式已经处于激活状态")
            return
        
        # 设置绘画状态为True
        self.is_drawing = True
        
        # 显示画布
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.show()
            log.info("绘画窗口已显示")
        else:
            log.error("绘画窗口初始化失败")
        
        # 处理积累的轨迹点
        if points and len(points) > 0:
            log.info("处理之前积累的 " + str(len(points)) + " 个轨迹点")
            
            current_time = time.time()
            # 确保每个点都有时间戳信息
            formatted_points = []
            for point in points:
                if len(point) == 2:
                    # 只有x, y的情况，添加当前时间
                    formatted_points.append((point[0], point[1], current_time))
                else:
                    # 已经有三个元素，保持原样
                    formatted_points.append(point)
            
            # 初始化笔画状态
            self.current_stroke = formatted_points
            self.smoothed_stroke = self.current_stroke.copy()
            self.stroke_start_time = current_time
            self.line_width_history = []
            self.last_line_width = self.base_width
            
            # 绘制累积的轨迹
            if len(formatted_points) > 1:
                # 批量处理点数据，绘制线条
                for i in range(1, len(formatted_points)):
                    prev_x, prev_y, prev_time = formatted_points[i-1]
                    curr_x, curr_y, curr_time = formatted_points[i]
                    
                    # 计算线宽
                    line_width = self.calculate_line_width(prev_x, prev_y, curr_x, curr_y, prev_time, curr_time)
                    
                    # 绘制线段
                    new_lines = self.draw_single_line(prev_x, prev_y, curr_x, curr_y, line_width)
                    self.active_lines.extend(new_lines)
            
            # 清空待处理点列表，因为这些点已被处理
            self.pending_points = []
        
        log.info("绘画模式已启动")

    def stop_drawing(self):
        """停止绘画模式"""
        log.info("停止绘画模式")
        
        # 调用shutdown方法来处理资源释放
        self.shutdown()
        
        # 确保drawing状态被重置
        self.is_drawing = False
        log.info("绘画模式已停止")

    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB元组
        
        Args:
            hex_color: 十六进制颜色字符串，如'#FF0000'
            
        Returns:
            (r, g, b)元组，值范围0-255
        """
        # 去掉开头的'#'
        hex_color = hex_color.lstrip('#')
        
        # 处理缩写形式 #RGB
        if len(hex_color) == 3:
            r = int(hex_color[0] + hex_color[0], 16)
            g = int(hex_color[1] + hex_color[1], 16)
            b = int(hex_color[2] + hex_color[2], 16)
        # 处理完整形式 #RRGGBB
        elif len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        # 处理带透明度的形式 #RRGGBBAA（忽略透明度）
        elif len(hex_color) == 8:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            raise ValueError(f"无效的十六进制颜色格式: {hex_color}")
            
        return r, g, b

    def update_drawing_settings(self, settings):
        """更新绘画设置
        
        Args:
            settings: 包含绘画设置的字典
            
        Returns:
            成功返回True，失败返回False
        """
        log.info(self.file_name + "更新绘画设置")
        
        try:
            # 基础宽度
            if 'base_width' in settings:
                self.base_width = float(settings['base_width'])
                
            # 最小宽度
            if 'min_width' in settings:
                self.min_width = float(settings['min_width'])
                
            # 最大宽度
            if 'max_width' in settings:
                self.max_width = float(settings['max_width'])
                
            # 平滑度
            if 'smoothing' in settings:
                self.smoothing = float(settings['smoothing'])
                
            # 颜色
            if 'color' in settings:
                color_hex = settings['color']
                # 解析HEX颜色
                if color_hex.startswith('#') and len(color_hex) in [4, 7, 9]:
                    try:
                        r, g, b = self.hex_to_rgb(color_hex)
                        # 设置颜色
                        self.line_color = (r, g, b)
                    except Exception as e:
                        log.error(f"颜色解析失败: {str(e)}")
                        
            # 高级笔刷
            if 'advanced_brush' in settings:
                self.use_advanced_brush = bool(settings['advanced_brush'])
                
            # 自动平滑
            if 'auto_smoothing' in settings:
                self.auto_smoothing = bool(settings['auto_smoothing'])
                
            # 淡出时间
            if 'fade_time' in settings:
                self.fade_duration = float(settings['fade_time'])
                
            # 速度因子
            if 'speed_factor' in settings:
                self.speed_factor = float(settings['speed_factor'])
                
            log.info(self.file_name + "绘画设置已更新")
            return True
        except Exception as e:
            log.error(self.file_name + "更新绘画设置失败: " + str(e))
            return False

if __name__ == "__main__":
    print("建议通过主程序运行。")
    test_painter = InkPainter()
    # 启动Qt事件循环，保持程序运行
    sys.exit(test_painter.app.exec_())