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
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath

try:
    from .gesture_parser import GestureParser
    from .log import log
except ImportError:
    from gesture_parser import GestureParser
    from log import log

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

    def create_line(self, x1, y1, x2, y2, width, fill, capstyle, smooth, joinstyle):
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
        # 开启抗锯齿
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self.enable_hardware_acceleration:
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
            
            # 对于较长的线段，添加中间控制点以获得更平滑的曲线
            dist = math.hypot(x2-x1, y2-y1)
            if dist > 10:
                # 添加中间控制点，使线条更平滑
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                path.quadTo(mid_x, mid_y, x2, y2)
            else:
                path.lineTo(x2, y2)
                
            painter.drawPath(path)

class InkPainter:
    def __init__(self):
        # 硬件参数
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.file_name = "ink_painter"
        
        log(self.file_name, "绘画模块初始化")
        # 绘画参数
        self.load_drawing_settings()  # 加载绘画参数
        
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
        
        # 初始化系统
        self.load_gestures()               # 加载手势配置
        self.init_canvas()                 # 创建GUI界面
        self.start_listening()             # 启动鼠标监听循环

    def get_settings_path(self):
        """获取项目根目录的通用方法"""
        if getattr(sys, 'frozen', False):
            # 打包后使用exe所在目录的上二级目录
            return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'settings.json')
        else:
            # 开发时使用当前文件的上三级目录（src/app → 根目录）
            return os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'settings.json'
            )

    def init_canvas(self):
        """创建全屏透明画布窗口"""
        log(self.file_name, "开始初始化画布窗口")
        self.app = QApplication(sys.argv)
        self.root = QWidget()
        # 窗口不在任务栏显示（使用 Qt.Tool），窗口大小设为全屏尺寸-1
        # 同时设置 WA_ShowWithoutActivating 防止窗口夺取焦点
        self.root.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.root.setAttribute(Qt.WA_TranslucentBackground)
        self.root.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.root.setGeometry(0, 0, self.screen_width - 1, self.screen_height - 1)
        self.root.setWindowOpacity(0.85)
        
        self.canvas = Canvas(self.root)
        self.canvas.setGeometry(0, 0, self.screen_width - 1, self.screen_height - 1)
        self.canvas.enable_hardware_acceleration = self.enable_hardware_acceleration
        log(self.file_name, "画布窗口初始化完成")

    def load_drawing_settings(self):
        """从settings.json加载绘画参数"""
        log(self.file_name, "开始加载绘画参数")
        try:
            with open(self.get_settings_path(), 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            drawing_settings = config['drawing_settings']
            self.base_width = drawing_settings['base_width']                                                # 基础线宽
            self.min_width = drawing_settings['min_width']                                                  # 最小线宽
            self.max_width = drawing_settings['max_width']                                                  # 最大线宽
            self.speed_factor = drawing_settings['speed_factor']                                            # 速度敏感度
            self.fade_duration = drawing_settings['fade_duration']                                          # 渐隐时长（动画时间）
            self.antialias_layers = drawing_settings['antialias_layers']                                    # 抗锯齿层数
            self.min_distance = drawing_settings['min_distance']                                            # 最小触发距离
            self.line_color = drawing_settings['line_color']                                                # 线条颜色
            self.max_stroke_points = drawing_settings['max_stroke_points']                                  # 最绘制大节点数
            self.max_stroke_duration = drawing_settings['max_stroke_duration']                              # 最大绘制时长（秒）
            self.enable_advanced_brush = drawing_settings.get('enable_advanced_brush')                      # 高级画笔开关
            self.force_topmost = drawing_settings.get('force_topmost')                                      # 强制置顶开关
            self.enable_auto_smoothing = drawing_settings.get('enable_auto_smoothing')                      # 是否启用自动平滑（True/False）
            self.smoothing_factor = drawing_settings.get('smoothing_factor')                                # 自动平滑系数，控制平滑力度
            self.enable_hardware_acceleration = drawing_settings.get('enable_hardware_acceleration')        # 是否启用硬件加速（True/False）
            log(self.file_name, f"成功加载绘画参数: {drawing_settings}")
        except Exception as e:
            log(self.file_name, f"加载绘画参数失败: {str(e)}", level='error')
            raise

    def load_gestures(self):
        """从settings.json加载手势配置"""
        log(self.file_name, "开始加载手势配置")
        try:
            with open(self.get_settings_path(), 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.gesture_lib = []
            for name, gesture in config['gestures'].items():
                self.gesture_lib.append({
                    'name': name,
                    'directions': gesture['directions'],
                    'action': gesture['action']
                })
            log(self.file_name, f"成功加载{len(self.gesture_lib)}个手势")
        except Exception as e:
            log(self.file_name, f"加载手势配置失败: {str(e)}", level='error')
            raise

    def start_listening(self):
        """启动鼠标监听循环"""
        log(self.file_name, "启动鼠标监听循环")
        self.last_right_state = False
        QTimer.singleShot(5, self.listen_mouse)

    def listen_mouse(self):
        """核心监听逻辑"""
        if not self.running:
            return
        
        # 如果强制置顶开关开启，则重复调用raise_()，
        # 但不调用activateWindow()以免夺取焦点，从而确保窗口始终在顶层且不干扰其他窗口
        if self.force_topmost:
            try:
                self.root.raise_()
            except Exception as e:
                log(self.file_name, "强制置顶失败", level='error')
        
        right_pressed = win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0
        x, y = pyautogui.position()
        
        # 引入节流算法，减少点采样频率
        current_time = time.time()
        is_throttled = False
        
        if self.drawing and self.current_stroke:
            prev_x, prev_y, prev_time, _ = self.current_stroke[-1]
            # 如果距离上次记录点时间太短，且移动距离很小，则跳过本次更新
            dt = current_time - prev_time
            dist = math.hypot(x - prev_x, y - prev_y)
            
            # 提高渲染频率：减小间隔时间
            is_hovering = dist < 2
            min_interval = 0.001  # 统一使用1ms的最小间隔，提高响应速度
            # 停留时更敏感，移动时容许更大距离
            min_distance = 0.5 if is_hovering else 1.0
            
            if dt < min_interval and dist < min_distance:
                is_throttled = True
                
        # 状态切换处理
        if right_pressed and not self.last_right_state:
            self.start_point = (x, y)  # 记录起始点
            self.pending_points = [(x, y, time.time())]  # 初始化缓存
        elif right_pressed and not self.drawing and self.start_point:
            # 持续缓存轨迹点（即使未达触发距离）
            self.pending_points.append((x, y, time.time()))
            
            # 检查触发条件：提取元组中的坐标分量
            start_x, start_y = self.start_point
            dx = x - start_x
            dy = y - start_y
            if math.hypot(dx, dy) >= self.min_distance:
                self.start_drawing()  # 触发后开始绘制历史轨迹
        elif right_pressed and self.drawing and not is_throttled:
            self.update_drawing(x, y)
        elif not right_pressed and self.last_right_state:
            # 松开右键时清理
            if self.pending_points:
                log(self.file_name, "松开右键，清理未完成的轨迹")
                for line in self.active_lines:
                    try:
                        self.canvas.delete(line)
                    except Exception:
                        pass
                self.active_lines = []
                self.pending_points = []
            self.finish_drawing()
            self.start_point = None
        
        self.last_right_state = right_pressed
        
        # 减小监听间隔，提高响应速度
        next_interval = 1 if self.drawing else 5  # 绘制时用1ms以确保最大流畅度
        QTimer.singleShot(next_interval, self.listen_mouse)

    def start_drawing(self):
        """从缓存点开始初始化笔画"""
        if not self.pending_points:
            return
        
        log(self.file_name, "触发绘制条件，开始处理历史轨迹")
        
        # 转换缓存点并记录线条
        self.current_stroke = []
        if self.enable_auto_smoothing:
            self.smoothed_stroke = []
        active_lines = []  # 临时存储历史轨迹线条
        
        # 生成初始线宽
        base_width = self.base_width
        prev_width = base_width
        
        for i in range(len(self.pending_points)):
            x, y, t = self.pending_points[i]
            if i == 0:
                current_width = base_width
                self.current_stroke.append((x, y, t, current_width))
                if self.enable_auto_smoothing:
                    self.smoothed_stroke.append((x, y, t, current_width))
            else:
                # 计算动态线宽（与实时绘制相同逻辑）
                if self.enable_advanced_brush:
                    if self.enable_auto_smoothing:
                        prev_smoothed = self.smoothed_stroke[-1]
                        # 位置平滑
                        position_factor = min(0.7, self.smoothing_factor + 0.1)
                        new_x = position_factor * x + (1 - position_factor) * prev_smoothed[0]
                        new_y = position_factor * y + (1 - position_factor) * prev_smoothed[1]
                        
                        prev_x, prev_y, prev_t, _ = self.current_stroke[-1]
                        dt = t - prev_t
                        dx = x - prev_x
                        dy = y - prev_y
                        distance = math.hypot(dx, dy)
                        
                        # 判断停留状态
                        is_hovering = distance < 2
                        
                        # 基于停留状态确定线宽
                        if is_hovering:
                            # 停留状态下线性增长
                            hover_factor = min(1.0, max(0.1, dt * 5))
                            target_width = prev_width + hover_factor
                            if target_width > self.max_width:
                                target_width = self.max_width
                        else:
                            # 移动状态下基于速度计算
                            if dt > 0.0001:
                                speed = distance / dt
                                speed = min(3000, max(10, speed))
                                speed_log = math.log10(max(1, speed/50)) * self.speed_factor
                                width_factor = max(0.3, 1.0 - speed_log * 0.3)
                                target_width = self.base_width * width_factor
                            else:
                                target_width = prev_width
                                
                            target_width = max(self.min_width, min(self.max_width, target_width))
                        
                        # 平滑宽度变化
                        smooth_factor = 0.3 if is_hovering else 0.1
                        current_width = prev_width * (1 - smooth_factor) + target_width * smooth_factor
                        
                        # 限制宽度变化幅度
                        max_change = 1.0
                        if abs(current_width - prev_width) > max_change:
                            if current_width > prev_width:
                                current_width = prev_width + max_change
                            else:
                                current_width = prev_width - max_change
                        
                        self.current_stroke.append((x, y, t, current_width))
                        
                        # 宽度平滑
                        width_factor = min(0.8, self.smoothing_factor + 0.2)
                        new_width = width_factor * current_width + (1 - width_factor) * prev_smoothed[3]
                        
                        # 限制最小宽度
                        new_width = max(2.5, new_width)
                        smoothed_point = (new_x, new_y, t, new_width)
                        self.smoothed_stroke.append(smoothed_point)
                        
                        # 确定是否需要绘制
                        segment_length = math.hypot(new_x - prev_smoothed[0], new_y - prev_smoothed[1])
                        
                        # 对于停留和短线段的处理
                        if is_hovering:
                            force_draw = i % 2 == 0  # 每隔一个点绘制
                            if force_draw or segment_length >= 0.8:
                                lines = self.draw_single_line(prev_smoothed[0], prev_smoothed[1], new_x, new_y, new_width)
                                active_lines.extend(lines)
                        elif segment_length >= 0.5 or len(self.smoothed_stroke) <= 2:
                            lines = self.draw_single_line(prev_smoothed[0], prev_smoothed[1], new_x, new_y, new_width)
                            active_lines.extend(lines)
                        
                        prev_width = current_width
                    else:
                        # 无平滑模式的历史轨迹处理
                        prev_x, prev_y, prev_t, _ = self.current_stroke[-1]
                        dt = t - prev_t
                        dx = x - prev_x
                        dy = y - prev_y
                        distance = math.hypot(dx, dy)
                        
                        is_hovering = distance < 2
                        
                        # 基于停留状态确定线宽
                        if is_hovering:
                            hover_factor = min(1.0, max(0.1, dt * 5))
                            target_width = prev_width + hover_factor
                            if target_width > self.max_width:
                                target_width = self.max_width
                        else:
                            if dt > 0.0001:
                                speed = distance / dt
                                speed = min(3000, max(10, speed))
                                speed_log = math.log10(max(1, speed/50)) * self.speed_factor
                                width_factor = max(0.3, 1.0 - speed_log * 0.3)
                                target_width = self.base_width * width_factor
                            else:
                                target_width = prev_width
                                
                            target_width = max(self.min_width, min(self.max_width, target_width))
                        
                        smooth_factor = 0.3 if is_hovering else 0.1
                        current_width = prev_width * (1 - smooth_factor) + target_width * smooth_factor
                        
                        max_change = 1.0
                        if abs(current_width - prev_width) > max_change:
                            if current_width > prev_width:
                                current_width = prev_width + max_change
                            else:
                                current_width = prev_width - max_change
                        
                        self.current_stroke.append((x, y, t, current_width))
                        
                        segment_length = math.hypot(x - prev_x, y - prev_y)
                        
                        if is_hovering:
                            force_draw = i % 2 == 0
                            if force_draw or segment_length >= 0.8:
                                lines = self.draw_single_line(prev_x, prev_y, x, y, current_width)
                                active_lines.extend(lines)
                        elif segment_length >= 0.5 or len(self.current_stroke) <= 2:
                            lines = self.draw_single_line(prev_x, prev_y, x, y, current_width)
                            active_lines.extend(lines)
                            
                        prev_width = current_width
                else:
                    # 非高级画笔模式
                    prev_x, prev_y, prev_t, _ = self.current_stroke[-1]
                    dt = t - prev_t
                    dx = x - prev_x
                    dy = y - prev_y
                    
                    # 固定宽度
                    current_width = max(self.min_width, self.base_width)
                    self.current_stroke.append((x, y, t, current_width))
                    
                    # 使用单线条绘制
                    segment_length = math.hypot(x - prev_x, y - prev_y)
                    if segment_length >= 0.5 or len(self.current_stroke) <= 2:
                        lines = self.draw_single_line(prev_x, prev_y, x, y, current_width)
                        active_lines.extend(lines)
                    prev_width = current_width
        
        # 将历史轨迹线条加入动画队列
        self.active_lines.extend(active_lines)
        
        # 清空缓存
        self.pending_points = []
        self.drawing = True
        self.stroke_start_time = time.time()
        log(self.file_name, f"已加载 {len(self.current_stroke)} 个历史轨迹点")

    def update_drawing(self, x, y):
        """更新绘画轨迹"""
        log(self.file_name, f"更新绘画轨迹，当前点: ({x}, {y})", level='debug')
        
        # 检查是否超出最大节点数或最大绘制时长
        current_time = time.time()
        if (len(self.current_stroke) >= self.max_stroke_points or 
            current_time - self.stroke_start_time >= self.max_stroke_duration):
            log(self.file_name, "触发自动清理机制")
            self.finish_drawing()
            self.start_drawing()
            return
        
        # 获取上一个点的信息
        prev_x, prev_y, prev_time, prev_width = self.current_stroke[-1]
        
        # 计算动态线宽
        if self.enable_advanced_brush:
            dx = x - prev_x
            dy = y - prev_y
            distance = math.hypot(dx, dy)
            delta_time = current_time - prev_time
            
            # 判断是否为停留状态（距离很小视为停留）
            is_hovering = distance < 2
            
            # 基于停留状态确定线宽
            if is_hovering:
                # 停留状态下，线宽稳定增加到最大值
                hover_factor = min(1.0, max(0.1, delta_time * 5))  # 控制增长斜率
                target_width = prev_width + hover_factor  # 线性增长
                if target_width > self.max_width:
                    target_width = self.max_width
            else:
                # 移动状态下，基于速度计算目标线宽，并限制速度影响
                if delta_time > 0.0001:
                    speed = distance / delta_time
                    # 限制速度值范围，避免极端值
                    speed = min(3000, max(10, speed))
                    
                    # 使用对数缩放，减弱速度对宽度的影响
                    speed_log = math.log10(max(1, speed/50)) * self.speed_factor
                    
                    # 速度越快，线宽越细，但设置合理下限
                    width_factor = max(0.3, 1.0 - speed_log * 0.3)
                    target_width = self.base_width * width_factor
                else:
                    target_width = prev_width  # 保持宽度不变
                    
                # 确保宽度在最小值和最大值之间
                target_width = max(self.min_width, min(self.max_width, target_width))
            
            # 平滑宽度变化，避免突变
            # 停留状态时加速粗度变化，移动时保持平滑过渡
            smooth_factor = 0.3 if is_hovering else 0.1
            current_width = prev_width * (1 - smooth_factor) + target_width * smooth_factor
            
            # 确保宽度不会跳跃变化过大
            max_change = 1.0  # 每次最大变化宽度
            if abs(current_width - prev_width) > max_change:
                if current_width > prev_width:
                    current_width = prev_width + max_change
                else:
                    current_width = prev_width - max_change
        else:
            current_width = self.base_width
        
        # 记录轨迹点
        self.current_stroke.append((x, y, current_time, current_width))
        
        # 绘制方式：使用平滑曲线
        if self.enable_auto_smoothing:
            last_smoothed = self.smoothed_stroke[-1]
            
            # 位置平滑因子适当调整
            position_factor = min(0.7, self.smoothing_factor + 0.1)
            
            new_x = position_factor * x + (1 - position_factor) * last_smoothed[0]
            new_y = position_factor * y + (1 - position_factor) * last_smoothed[1]
            
            # 宽度也进行平滑
            width_factor = min(0.8, self.smoothing_factor + 0.2)
            new_width = width_factor * current_width + (1 - width_factor) * last_smoothed[3]
            
            # 限制最小宽度
            new_width = max(2.5, new_width)
            
            smoothed_point = (new_x, new_y, current_time, new_width)
            self.smoothed_stroke.append(smoothed_point)
            
            # 确定是否需要绘制新线段
            segment_length = math.hypot(new_x - last_smoothed[0], new_y - last_smoothed[1])
            
            # 对于停留点和短线段的处理策略
            if is_hovering:
                # 停留状态强制定期绘制，以显示粗细变化
                force_draw = len(self.smoothed_stroke) % 2 == 0  # 每隔一个点绘制
                if force_draw or segment_length >= 0.8:
                    lines = self.draw_single_line(last_smoothed[0], last_smoothed[1], new_x, new_y, new_width)
                    self.active_lines.extend(lines)
            elif segment_length >= 0.5 or len(self.smoothed_stroke) <= 2:
                # 移动状态下，控制最小段距离避免过度绘制
                lines = self.draw_single_line(last_smoothed[0], last_smoothed[1], new_x, new_y, new_width)
                self.active_lines.extend(lines)
        else:
            # 直接绘制模式
            segment_length = math.hypot(x - prev_x, y - prev_y)
            
            # 对于停留点和短线段的处理策略
            if distance < 2:  # 停留状态
                force_draw = len(self.current_stroke) % 2 == 0  # 每隔一个点绘制
                if force_draw or segment_length >= 0.8:
                    lines = self.draw_single_line(prev_x, prev_y, x, y, current_width)
                    self.active_lines.extend(lines)
            elif segment_length >= 0.5 or len(self.current_stroke) <= 2:
                lines = self.draw_single_line(prev_x, prev_y, x, y, current_width)
                self.active_lines.extend(lines)

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
        return [line]

    def finish_drawing(self):
        """结束并处理当前笔画"""
        log(self.file_name, "结束当前笔画")
        self.drawing = False
        
        # 合并所有轨迹点（包括触发前的缓存）
        full_stroke = self.current_stroke.copy()
        # 保存已结束的笔画，用于独立的手势识别（不影响其他笔画的识别）
        self.finished_strokes.append(full_stroke)
        
        # 触发渐隐动画：线条逐渐变透明（逐渐减小笔画的不透明度）
        if self.active_lines:
            log(self.file_name, f"触发渐隐动画，线条数: {len(self.active_lines)}")
            self.fade_animations.append({
                'lines': self.active_lines.copy(),  # 包含历史和实时线条
                'start_time': time.time(),
                'base_color': self.line_color
            })
            self.active_lines = []
            self.process_fade_animation()
        
        # 手势识别（使用完整轨迹），异步处理，不影响新笔画
        if len(full_stroke) >= 5:
            log(self.file_name, f"开始手势识别，轨迹点数: {len(full_stroke)}")
            trail_points = [(x, y) for x, y, *_ in full_stroke]
            parser = GestureParser(trail_points, config_path=self.get_settings_path())
            if operation := parser.parse():
                log(self.file_name, f"识别到手势，执行操作: {operation}")
                self.execute_operation(operation)
        
        # 清空数据
        self.current_stroke = []
        if self.enable_auto_smoothing:
            self.smoothed_stroke = []
        self.pending_points = []

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
            progress = min(elapsed / self.fade_duration, 1.0)
            
            # 动态计算颜色：保持原RGB，仅降低不透明度（alpha值）
            fade_color = self.calculate_fade_color(anim['base_color'], progress)
            
            # 批量收集更新
            for line_id in anim['lines']:
                batch_updates.append((line_id, fade_color))
            
            if progress >= 1.0:
                for line_id in anim['lines']:
                    self.canvas.delete(line_id)
                removals.append(anim)
        
        # 批量执行更新
        for line_id, color in batch_updates:
            try:
                self.canvas.itemconfig(line_id, fill=color)
            except Exception:
                pass
                
        # 清理已完成的渐隐动画
        for anim in removals:
            self.fade_animations.remove(anim)
        
        # 如果还有动画在运行，继续调度下一帧
        if self.fade_animations:
            QTimer.singleShot(max(1, int(min_interval * 1000)), self.process_fade_animation)

    def calculate_fade_color(self, base_color, progress):
        """根据进度计算渐隐颜色（线条逐渐变透明），返回格式为 #AARRGGBB
        说明：随着 progress 增大（0~1），alpha值逐渐减小，从而实现渐隐效果。
        """
        # 将HEX转RGB
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        a = int(255 * (1 - progress**0.8))  # 使用非线性衰减，让开始减淡更慢一些
        # 返回包含透明度信息的颜色，格式调整为 #AARRGGBB
        return "#{:02X}{:02X}{:02X}{:02X}".format(a, r, g, b)

    def execute_operation(self, encoded_cmd):
        """执行Base64编码的操作指令"""
        try:
            decoded = base64.b64decode(encoded_cmd).decode('utf-8')
            exec(decoded)
            log(self.file_name, f"成功执行操作: {decoded}")
        except Exception as e:
            log(self.file_name, f"操作执行失败: {str(e)}", level='error')

    def shutdown(self):
        """安全关闭资源"""
        log(self.file_name, "正在关闭绘画模块...")
        self.running = False
        self.root.close()
        self.canvas = None
        log(self.file_name, "绘画模块已关闭")

if __name__ == "__main__":
    print("建议通过主程序运行。")
    test_painter = InkPainter()
    test_painter.root.show()
    sys.exit(test_painter.app.exec_())
