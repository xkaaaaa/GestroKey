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
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
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
        
        log(__name__, "绘画模块初始化")
        
        # 确保settings.json存在
        self.ensure_settings_file()
        
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
        self.forced_end = False            # 强制结束标志
        
        # 初始化系统
        self.load_gestures()               # 加载手势配置
        self.init_canvas()                 # 创建GUI界面
        self.init_gesture_parser()         # 初始化手势识别器
        self.start_listening()             # 启动鼠标监听循环
        
        log(__name__, "绘画模块初始化完成")

    def ensure_settings_file(self):
        """确保settings.json存在，如果不存在则创建一个默认配置"""
        settings_path = self.get_settings_path()
        
        if os.path.exists(settings_path):
            log(self.file_name, f"配置文件已存在: {settings_path}")
            return
            
        log(self.file_name, f"配置文件不存在，创建默认配置: {settings_path}")
        
        # 确保目录存在
        settings_dir = os.path.dirname(settings_path)
        os.makedirs(settings_dir, exist_ok=True)
        
        # 创建默认配置
        default_settings = {
            "drawing_settings": {
                "base_width": 6,
                "min_width": 3,
                "max_width": 15,
                "speed_factor": 1.2,
                "fade_duration": 0.5,
                "antialias_layers": 2,
                "min_distance": 20,
                "line_color": "#00BFFF",
                "max_stroke_points": 200,
                "max_stroke_duration": 5,
                "enable_advanced_brush": True,
                "force_topmost": True,
                "enable_auto_smoothing": True,
                "smoothing_factor": 0.6,
                "enable_hardware_acceleration": True
            },
            "gestures": {
                "上": {
                    "directions": "↑",
                    "action": "cGFzc2FwcC5taW5pbWl6ZV9hbGwoKQ=="  # base64编码的"passapp.minimize_all()"
                },
                "下": {
                    "directions": "↓",
                    "action": "cGFzc2FwcC5yZXN0b3JlX2FsbCgp"  # base64编码的"passapp.restore_all()"
                },
                "左": {
                    "directions": "←",
                    "action": "cGFzc2FwcC5wcmV2X3dpbmRvdygp"  # base64编码的"passapp.prev_window()"
                },
                "右": {
                    "directions": "→",
                    "action": "cGFzc2FwcC5uZXh0X3dpbmRvdygp"  # base64编码的"passapp.next_window()"
                }
            }
        }
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, ensure_ascii=False, indent=4)
            log(self.file_name, "成功创建默认配置文件")
        except Exception as e:
            log(self.file_name, f"创建默认配置文件失败: {str(e)}", level="error")

    def get_settings_path(self):
        """获取项目根目录的通用方法"""
        if getattr(sys, 'frozen', False):
            # 打包后使用exe所在目录的上二级目录
            return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'settings.json')
        else:
            # 开发时直接指向根目录下的settings.json
            # 更可靠的方法：先获取当前文件的绝对路径，然后向上找3层到根目录
            curr_path = os.path.abspath(__file__)
            # src/app/ink_painter.py 向上3层到根目录
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(curr_path)))
            return os.path.join(root_dir, 'settings.json')

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
        
        # 设置默认值，以防配置文件不存在或读取失败
        self.base_width = 6
        self.min_width = 3
        self.max_width = 15
        self.speed_factor = 1.2
        self.fade_duration = 0.5
        self.antialias_layers = 2
        self.min_distance = 20
        self.line_color = '#00BFFF'
        self.max_stroke_points = 200
        self.max_stroke_duration = 5
        self.enable_advanced_brush = True
        self.force_topmost = True
        self.enable_auto_smoothing = True
        self.smoothing_factor = 0.6
        self.enable_hardware_acceleration = True
        
        try:
            settings_path = self.get_settings_path()
            if not os.path.exists(settings_path):
                log(self.file_name, f"找不到配置文件: {settings_path}，使用默认设置", level="warning")
                return
                
            log(self.file_name, f"从 {settings_path} 加载配置")
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'drawing_settings' not in config:
                log(self.file_name, "配置文件中不存在drawing_settings部分，使用默认设置", level="warning")
                return
                
            drawing_settings = config['drawing_settings']
            
            # 使用get方法安全获取值，如果键不存在则使用默认值
            self.base_width = drawing_settings.get('base_width', self.base_width)
            self.min_width = drawing_settings.get('min_width', self.min_width)
            self.max_width = drawing_settings.get('max_width', self.max_width)
            self.speed_factor = drawing_settings.get('speed_factor', self.speed_factor)
            self.fade_duration = drawing_settings.get('fade_duration', self.fade_duration)
            self.antialias_layers = drawing_settings.get('antialias_layers', self.antialias_layers)
            self.min_distance = drawing_settings.get('min_distance', self.min_distance)
            self.line_color = drawing_settings.get('line_color', self.line_color)
            self.max_stroke_points = drawing_settings.get('max_stroke_points', self.max_stroke_points)
            self.max_stroke_duration = drawing_settings.get('max_stroke_duration', self.max_stroke_duration)
            self.enable_advanced_brush = drawing_settings.get('enable_advanced_brush', self.enable_advanced_brush)
            self.force_topmost = drawing_settings.get('force_topmost', self.force_topmost)
            self.enable_auto_smoothing = drawing_settings.get('enable_auto_smoothing', self.enable_auto_smoothing)
            self.smoothing_factor = drawing_settings.get('smoothing_factor', self.smoothing_factor)
            self.enable_hardware_acceleration = drawing_settings.get('enable_hardware_acceleration', self.enable_hardware_acceleration)
            
            log(self.file_name, f"成功加载绘画参数: {drawing_settings}")
        except json.JSONDecodeError as e:
            log(self.file_name, f"解析配置文件失败: {str(e)}，使用默认设置", level='error')
        except Exception as e:
            log(self.file_name, f"加载绘画参数失败: {str(e)}，使用默认设置", level='error')

    def load_gestures(self):
        """从settings.json加载手势配置"""
        log(self.file_name, "开始加载手势配置")
        try:
            settings_path = self.get_settings_path()
            if not os.path.exists(settings_path):
                log(self.file_name, f"找不到配置文件: {settings_path}", level="error")
                self.gesture_lib = []
                return
                
            log(self.file_name, f"从 {settings_path} 加载配置")
            with open(settings_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'gestures' not in config:
                log(self.file_name, "配置文件中不存在gestures部分", level="error")
                self.gesture_lib = []
                return
                
            self.gesture_lib = []
            for name, gesture in config['gestures'].items():
                if 'directions' not in gesture or 'action' not in gesture:
                    log(self.file_name, f"手势 {name} 格式不正确，跳过", level="warning")
                    continue
                    
                self.gesture_lib.append({
                    'name': name,
                    'directions': gesture['directions'],
                    'action': gesture['action']
                })
                
            if not self.gesture_lib:
                log(self.file_name, "没有加载到有效的手势配置", level="warning")
            else:
                log(self.file_name, f"成功加载{len(self.gesture_lib)}个手势")
        except json.JSONDecodeError as e:
            log(self.file_name, f"解析配置文件失败: {str(e)}", level='error')
            self.gesture_lib = []
        except Exception as e:
            log(self.file_name, f"加载手势配置失败: {str(e)}", level='error')
            self.gesture_lib = []

    def init_gesture_parser(self):
        """初始化手势识别器"""
        try:
            # 确认settings.json路径存在
            settings_path = self.get_settings_path()
            if not os.path.exists(settings_path):
                log(self.file_name, f"找不到手势配置文件: {settings_path}", level="error")
                self.gesture_parser = None
                return
                
            # 初始化手势识别器 - 使用空的trail_points列表，实际使用时会重新创建解析器
            empty_trail = []
            self.gesture_parser = GestureParser(empty_trail)
            log(self.file_name, "手势识别器初始化完成")
        except Exception as e:
            log(self.file_name, f"手势识别器初始化失败: {str(e)}", level="error")
            self.gesture_parser = None

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
            prev_x, prev_y, prev_time = self.current_stroke[-1]
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
            # 只在没有绘画状态时记录起始点
            if not self.drawing:
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
                # 只有未在绘画状态时才调用start_drawing
                self.start_drawing()  # 触发后开始绘制历史轨迹
        elif right_pressed and self.drawing and not is_throttled:
            # 已经在绘画状态时更新绘图
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
            # 结束当前笔画
            if self.drawing:
                self.finish_drawing()
            self.start_point = None
        
        self.last_right_state = right_pressed
        
        # 减小监听间隔，提高响应速度
        next_interval = 1 if self.drawing else 5  # 绘制时用1ms以确保最大流畅度
        QTimer.singleShot(next_interval, self.listen_mouse)

    def start_drawing(self):
        """启动绘画模式"""
        log(__name__, "启动绘画模式")
        # 避免重复启动
        if self.drawing:
            log(__name__, "绘画模式已经处于激活状态")
            return
            
        # 设置绘画状态为True
        self.drawing = True
        
        # 显示全屏透明窗口
        if hasattr(self, 'root') and self.root:
            self.root.show()
            log(__name__, "绘画窗口已显示")
        else:
            log(__name__, "绘画窗口初始化失败", level="error")
            
        # 处理收集的pending_points，避免出现意外长连线
        if self.pending_points and len(self.pending_points) > 0:
            # 使用收集到的第一个点作为起点
            first_x, first_y, first_time = self.pending_points[0]
            # 初始化笔画数据
            self.current_stroke = [(first_x, first_y, first_time)]
            self.smoothed_stroke = [(first_x, first_y, first_time)]
            self.stroke_start_time = first_time
            self.line_width_history = []
            self.last_line_width = self.base_width
            
            # 处理其余点
            if len(self.pending_points) > 1:
                for i in range(1, len(self.pending_points)):
                    x, y, t = self.pending_points[i]
                    # 更新点数据
                    self.current_stroke.append((x, y, t))
                    self.smoothed_stroke.append((x, y, t))
                    
                    # 计算并绘制线段
                    if len(self.smoothed_stroke) > 1:
                        prev_x, prev_y, _ = self.smoothed_stroke[-2]
                        curr_x, curr_y, _ = self.smoothed_stroke[-1]
                        line_width = self.base_width  # 初始点使用基础线宽
                        new_lines = self.draw_single_line(prev_x, prev_y, curr_x, curr_y, line_width)
                        self.active_lines.extend(new_lines)
            
            # 清空pending_points
            self.pending_points = []

    def stop_drawing(self):
        """停止绘画模式"""
        log(__name__, "停止绘画模式")
        
        # 调用现有的shutdown方法来处理资源释放
        self.shutdown()
        
        # 确保drawing状态被重置
        self.drawing = False
        log(__name__, "绘画模式已停止")

    def update_drawing(self, x, y):
        """更新绘画状态"""
        # 添加当前点到笔画数据
        if not self.drawing:
            # 已修改start_drawing方法，所以这里可以直接返回
            return
            
        # 检查是否是新笔画的第一个点
        if not hasattr(self, 'stroke_start_time') or not self.current_stroke:
            # 开始新笔画
            log(__name__, "开始新笔画")
            self.start_point = (x, y)
            self.current_stroke = [(x, y, time.time())]
            self.smoothed_stroke = [(x, y, time.time())]
            self.pending_points = []
            self.forced_end = False  # 重置强制结束标志
            
            # 添加线宽历史记录属性用于平滑处理
            self.line_width_history = []
            self.last_line_width = self.base_width
            
            # 重置笔画保护计时器
            self.stroke_start_time = time.time()
            return
        
        current_time = time.time()
        
        # 防止与前一个点完全重合造成的零长度线段
        if self.current_stroke and len(self.current_stroke) > 0:
            prev_x, prev_y, _ = self.current_stroke[-1]
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
            time_diff = max(0.001, curr_time - prev_time)  # 防止除零
            
            # 计算速度
            speed = dist / time_diff
            
            # 速度映射到线宽调整系数，速度越大线条越细
            raw_speed_multiplier = max(0.5, min(1.5, 1.5 - (speed / (200 * self.speed_factor))))
            
            # 添加线宽平滑处理 - 使用移动平均来平滑线宽变化
            # 保留最近8个线宽值进行平均
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
            
            # 绘制线段
            new_lines = self.draw_single_line(prev_x, prev_y, curr_x, curr_y, line_width)
            self.active_lines.extend(new_lines)

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
            
            # 尝试识别手势 - 使用新方法创建GestureParser实例
            try:
                log(__name__, "尝试识别手势")
                # 提取轨迹点坐标（去掉时间戳）
                trail_points = [(x, y) for x, y, _ in current_stroke_copy]
                
                # 创建新的GestureParser实例
                parser = GestureParser(trail_points)
                action = parser.parse()
                
                if action:
                    log(__name__, f"识别到手势动作: {action}")
                    # 执行手势动作
                    self.execute_operation(action)
                    
                    # 对于已识别的手势，清空线条（立即消失）
                    for line in self.active_lines:
                        self.canvas.delete(line)
                    self.active_lines = []
                    # 重置强制结束标志
                    self.forced_end = False
                    return
                else:
                    log(__name__, "未识别到有效手势")
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
            
        # 如果没有识别为手势，启动渐隐效果
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
        log(__name__, "笔画结束处理完成")

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
            try:
                self.canvas.itemconfig(line_id, fill=color)
            except Exception as e:
                log(__name__, f"更新线条颜色失败: {str(e)}", level="error")
        
        # 清理已完成的渐隐动画
        for anim in removals:
            self.fade_animations.remove(anim)
        
        # 如果还有动画在运行，继续调度下一帧
        if self.fade_animations:
            QTimer.singleShot(max(1, int(min_interval * 1000)), self.process_fade_animation)
        else:
            # 没有更多动画，停止定时器
            if hasattr(self, 'fade_timer') and self.fade_timer.isActive():
                self.fade_timer.stop()
                log(__name__, "渐隐动画完成，停止定时器")

    def calculate_fade_color(self, base_color, progress):
        """根据进度计算渐隐颜色（线条逐渐变透明），返回格式为 #AARRGGBB
        说明：随着 progress 增大（0~1），alpha值逐渐减小，从而实现渐隐效果。
        """
        try:
            # 将HEX转RGB
            if base_color.startswith('#'):
                if len(base_color) == 7:  # #RRGGBB
                    r = int(base_color[1:3], 16)
                    g = int(base_color[3:5], 16)
                    b = int(base_color[5:7], 16)
                elif len(base_color) == 9:  # #AARRGGBB
                    # 已经带透明度的颜色
                    a_orig = int(base_color[1:3], 16)
                    r = int(base_color[3:5], 16)
                    g = int(base_color[5:7], 16)
                    b = int(base_color[7:9], 16)
            else:
                # 默认使用蓝色
                r, g, b = 0, 191, 255  # 默认蓝色 #00BFFF
            
            # 计算alpha值 - 使用非线性衰减，让开始减淡更慢一些
            a = int(255 * (1 - progress**0.7))  # 降低幂次，使淡出更平滑
            
            # 返回包含透明度信息的颜色，格式调整为 #AARRGGBB
            return f"#{a:02X}{r:02X}{g:02X}{b:02X}"
        except Exception as e:
            log(__name__, f"计算渐隐颜色失败: {str(e)}", level="error")
            return "#00BFFF"  # 返回默认颜色

    def execute_operation(self, encoded_cmd):
        """执行Base64编码的操作指令"""
        try:
            decoded = base64.b64decode(encoded_cmd).decode('utf-8')
            exec(decoded)
            log(self.file_name, f"成功执行操作: {decoded}")
        except Exception as e:
            log(self.file_name, f"操作执行失败: {str(e)}", level='error')

    def shutdown(self):
        """安全关闭程序，释放资源"""
        log(__name__, "关闭绘画模块，释放资源")
        self.running = False
        
        # 停止所有定时器
        if hasattr(self, 'fade_timer') and self.fade_timer:
            self.fade_timer.stop()
        
        # 清空所有线条
        if hasattr(self, 'canvas') and self.canvas:
            for line in self.active_lines:
                self.canvas.delete(line)
                
            for anim in self.fade_animations:
                for line in anim['lines']:
                    self.canvas.delete(line)
        
        # 关闭窗口
        if hasattr(self, 'root') and self.root:
            self.root.hide()
            self.root.close()
        
        log(__name__, "绘画模块已安全关闭")

if __name__ == "__main__":
    print("建议通过主程序运行。")
    test_painter = InkPainter()
    test_painter.root.show()
    sys.exit(test_painter.app.exec_())
