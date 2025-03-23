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
    from .log import log, setup_logger
    from .operation_executor import execute as execute_operation
except ImportError:
    from gesture_parser import GestureParser
    from log import log, setup_logger
    from operation_executor import execute as execute_operation

# 全局变量，控制是否在调试模式
IS_DEBUG_MODE = False
# 添加手势解析器懒加载标志
_GESTURE_PARSER_INITIALIZED = False
# 添加配置文件缓存
_CONFIG_CACHE = {}
_CONFIG_CACHE_TIME = 0
_GESTURES_CACHE = {}
_GESTURES_CACHE_TIME = 0
# 添加线条对象池，减少内存分配
_LINE_OBJECT_POOL = []
_MAX_POOL_SIZE = 1000  # 最大对象池大小

# 设置调试模式的函数
def set_debug_mode(debug=False):
    global IS_DEBUG_MODE
    IS_DEBUG_MODE = debug
    setup_logger(debug)  # 设置日志记录器的级别

# 线条对象池管理函数
def get_line_from_pool():
    """从对象池获取一个线条对象"""
    global _LINE_OBJECT_POOL
    if _LINE_OBJECT_POOL:
        line = _LINE_OBJECT_POOL.pop()
        # 确保对象是完全空的，没有残留属性
        line.clear()
        # 预初始化所有必需的键，设置默认值
        line['x1'] = 0
        line['y1'] = 0
        line['x2'] = 0 
        line['y2'] = 0
        line['width'] = 1.0
        line['color'] = "rgb(0,0,0)"
        return line
    else:
        # 池为空，创建新对象，包含所有必需的键
        return {
            'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0,
            'width': 1.0, 'color': "rgb(0,0,0)"
        }

def return_line_to_pool(line):
    """将线条对象归还到对象池"""
    global _LINE_OBJECT_POOL, _MAX_POOL_SIZE
    # 安全检查：确保是有效的线条对象
    if not isinstance(line, dict):
        return
    
    # 清空对象数据，但保留基本结构
    line.clear()
    # 重新初始化基本键，防止下次使用时出现KeyError
    line['x1'] = 0
    line['y1'] = 0
    line['x2'] = 0
    line['y2'] = 0
    line['width'] = 1.0
    line['color'] = "rgb(0,0,0)"
    
    # 如果池未满，归还对象
    if len(_LINE_OBJECT_POOL) < _MAX_POOL_SIZE:
        _LINE_OBJECT_POOL.append(line)

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
        # 从对象池获取线条对象
        line = get_line_from_pool()
        
        # 确保颜色值在添加到线条字典前是有效格式
        if isinstance(fill, str) and (fill.startswith('rgb(') or fill.startswith('#')):
            color = fill  # 保持字符串格式
        elif isinstance(fill, tuple) and len(fill) >= 3:
            # 处理元组，转换为CSS字符串格式
            r, g, b = fill[0], fill[1], fill[2]
            color = f"rgb({r},{g},{b})"
            log.debug(f"在create_line中将颜色元组 {fill} 转换为CSS字符串: {color}")
        else:
            # 无效颜色格式，使用默认值并记录
            color = "rgb(170,85,255)"  # 默认紫色
            log.error(f"无效的颜色格式 {fill}，使用默认紫色")
        
        # 设置线条属性
        line['x1'] = x1
        line['y1'] = y1
        line['x2'] = x2
        line['y2'] = y2
        line['width'] = width
        line['color'] = color
        
        self.lines.append(line)
        # 不立即更新，而是加入批量队列
        self.batch_updates.append(line)
        self.schedule_update()
        return line

    def itemconfig(self, line, fill):
        # 确保颜色值在更新线条颜色时是有效格式
        if isinstance(fill, str) and (fill.startswith('rgb(') or fill.startswith('#')):
            color = fill  # 保持字符串格式
        elif isinstance(fill, tuple) and len(fill) >= 3:
            # 处理元组，转换为CSS字符串格式
            r, g, b = fill[0], fill[1], fill[2]
            color = f"rgb({r},{g},{b})"
            log.debug(f"在itemconfig中将颜色元组 {fill} 转换为CSS字符串: {color}")
        else:
            # 无效颜色格式，使用默认值并记录
            color = "rgb(170,85,255)"  # 默认紫色
            log.error(f"itemconfig: 无效的颜色格式 {fill}，使用默认紫色")
        
        line['color'] = color
        self.schedule_update()

    def delete(self, line):
        try:
            self.lines.remove(line)
            # 归还对象到池
            return_line_to_pool(line)
        except ValueError:
            pass
        self.schedule_update()
    
    def batch_update_lines(self, line_updates):
        """批量更新多条线的颜色
        
        Args:
            line_updates: 包含(line, color)元组的列表
        """
        if not line_updates:
            return
            
        for line, color in line_updates:
            self.itemconfig(line, color)
        
        # 一次性触发更新，而不是为每条线单独更新
        self.schedule_update()
    
    def batch_delete_lines(self, lines_to_delete):
        """批量删除多条线
        
        Args:
            lines_to_delete: 要删除的线条对象列表
        """
        if not lines_to_delete:
            return
            
        # 记录删除前的线条数量
        lines_count_before = len(self.lines)
        
        # 字典是不可哈希的，不能直接使用集合
        # 使用列表推导式直接过滤掉要删除的线条
        # 这种方法对于少量线条高效，对大量线条可能性能较低
        if len(lines_to_delete) < 10:
            # 过滤并记录要返回池的对象
            to_delete = []
            self.lines = [line for line in self.lines if (line not in lines_to_delete or to_delete.append(line) is None)]
            
            # 归还删除的对象到池
            for line in to_delete:
                return_line_to_pool(line)
        else:
            # 对于大量线条，使用id作为标识符进行高效过滤
            # 创建一个删除列表中对象的id集合
            lines_to_delete_ids = {id(line) for line in lines_to_delete}
            
            # 创建保留和删除的两个列表
            lines_to_keep = []
            actual_deleted = []
            
            for line in self.lines:
                if id(line) not in lines_to_delete_ids:
                    lines_to_keep.append(line)
                else:
                    actual_deleted.append(line)
                    
            # 更新线条列表
            self.lines = lines_to_keep
            
            # 归还删除的对象到池
            for line in actual_deleted:
                return_line_to_pool(line)
        
        # 记录实际删除的线条数量
        deleted_count = lines_count_before - len(self.lines)
        if IS_DEBUG_MODE and deleted_count > 0:
            log.debug(f"批量删除了 {deleted_count} 条线")
        
        # 一次性触发更新
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
        
        # 根据硬件加速设置调整渲染选项
        if hasattr(self, 'enable_hardware_acceleration') and self.enable_hardware_acceleration:
            # 启用完整硬件加速渲染选项
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            
            # 使用更适合硬件加速的合成模式
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        else:
            # 在软件渲染模式下，只使用基本抗锯齿以提高性能
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        # 仅渲染可见区域内的线条以提高性能
        visible_rect = event.rect()
        
        # 使用视口裁剪来进一步优化渲染
        painter.setClipRect(visible_rect)
        
        # 计算屏幕上需要渲染的线条
        visible_lines = []
        
        for line in self.lines:
            # 添加安全检查，确保线条包含所有必需的键
            required_keys = ['x1', 'y1', 'x2', 'y2', 'width', 'color']
            if not all(key in line for key in required_keys):
                # 跳过无效线条，并记录错误
                if IS_DEBUG_MODE:
                    log.error(f"发现无效线条对象: {line}")
                continue
            
            # 提取线条坐标
            try:
                x1, y1 = float(line['x1']), float(line['y1'])
                x2, y2 = float(line['x2']), float(line['y2'])
            except (ValueError, KeyError) as e:
                # 捕获所有可能的转换错误
                log.error(f"处理线条坐标时出错: {e}, 线条: {line}")
                continue
            
            # 快速边界框检测，跳过不在可见区域的线条
            if (max(x1, x2) < visible_rect.left() or min(x1, x2) > visible_rect.right() or
                max(y1, y2) < visible_rect.top() or min(y1, y2) > visible_rect.bottom()):
                continue  # 不在可见区域内，跳过绘制
            
            visible_lines.append(line)
        
        # 如果启用了硬件加速并且有足够多的线条，使用批量绘制优化
        if hasattr(self, 'enable_hardware_acceleration') and self.enable_hardware_acceleration and len(visible_lines) > 10:
            # 按颜色分组线条，减少画笔切换次数
            color_groups = {}
            for line in visible_lines:
                color = line['color']
                if color not in color_groups:
                    color_groups[color] = []
                color_groups[color].append(line)
            
            # 对每个颜色组批量绘制
            for color, lines in color_groups.items():
                # 处理颜色
                if isinstance(color, str):
                    if color.startswith('rgb('):
                        rgb_values = color.strip('rgb()').split(',')
                        if len(rgb_values) >= 3:
                            try:
                                r = int(rgb_values[0].strip())
                                g = int(rgb_values[1].strip())
                                b = int(rgb_values[2].strip())
                                qcolor = QColor(r, g, b)
                            except ValueError:
                                qcolor = QColor(170, 85, 255)  # 默认紫色
                        else:
                            qcolor = QColor(170, 85, 255)  # 默认紫色
                    elif color.startswith('#'):
                        qcolor = QColor(color)
                    else:
                        qcolor = QColor(170, 85, 255)  # 默认紫色
                else:
                    qcolor = QColor(170, 85, 255)  # 默认紫色
                
                # 设置画笔 - 只设置一次颜色
                pen = QPen(qcolor)
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pen)
                
                # 批量绘制相同颜色的线条
                for line in lines:
                    try:
                        x1, y1 = float(line['x1']), float(line['y1'])
                        x2, y2 = float(line['x2']), float(line['y2'])
                        pen.setWidthF(line['width'])
                        painter.setPen(pen)
                        
                        # 使用路径绘制实现更平滑的线条效果
                        path = QPainterPath()
                        path.moveTo(x1, y1)
                        
                        # 使用贝塞尔曲线绘制，提高平滑度
                        mid_x = (x1 + x2) / 2
                        mid_y = (y1 + y2) / 2
                        path.quadTo(mid_x, mid_y, x2, y2)
                        painter.drawPath(path)
                    except (ValueError, KeyError) as e:
                        # 捕获所有可能的绘制错误
                        log.error(f"批量绘制线条时出错: {e}, 线条: {line}")
                        continue
        else:
            # 普通逐条绘制模式
            for line in visible_lines:
                try:
                    # 处理颜色 - create_line 方法已经确保 line['color'] 是有效的颜色格式
                    color = line['color']
                    
                    if isinstance(color, str):
                        if color.startswith('rgb('):
                            # 解析RGB格式
                            rgb_values = color.strip('rgb()').split(',')
                            if len(rgb_values) >= 3:
                                try:
                                    r = int(rgb_values[0].strip())
                                    g = int(rgb_values[1].strip())
                                    b = int(rgb_values[2].strip())
                                    qcolor = QColor(r, g, b)
                                except ValueError:
                                    qcolor = QColor(170, 85, 255)  # 默认紫色
                            else:
                                qcolor = QColor(170, 85, 255)  # 默认紫色
                        elif color.startswith('#'):
                            # 十六进制字符串
                            qcolor = QColor(color)
                        else:
                            # 无法识别的字符串格式，使用默认值
                            qcolor = QColor(170, 85, 255)  # 默认紫色
                    else:
                        # 默认颜色 - 使用紫色代替红色，与设置中的默认颜色一致
                        qcolor = QColor(170, 85, 255)  # 默认紫色
                        
                    pen = QPen(qcolor)
                    pen.setWidthF(line['width'])
                    pen.setCapStyle(Qt.RoundCap)
                    pen.setJoinStyle(Qt.RoundJoin)
                    
                    # 将坐标转换为浮点数以实现更平滑的线条
                    x1, y1 = float(line['x1']), float(line['y1'])
                    x2, y2 = float(line['x2']), float(line['y2'])
                        
                    painter.setPen(pen)
                    
                    # 使用路径绘制实现更平滑的线条效果
                    path = QPainterPath()
                    path.moveTo(x1, y1)
                    
                    # 贝塞尔曲线绘制，提高平滑度
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    path.quadTo(mid_x, mid_y, x2, y2)
                        
                    painter.drawPath(path)
                except (ValueError, KeyError) as e:
                    # 捕获所有可能的绘制错误
                    log.error(f"绘制线条时出错: {e}, 线条: {line}")
                    continue

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
        if IS_DEBUG_MODE:
            log.debug(f"InkPainter初始化，配置信息：{self.config}")
        
        # 状态变量
        self.is_drawing = False   # 是否处于绘画状态
        self.is_listening = False  # 是否正在监听鼠标
        self.is_active = False    # 组件是否处于激活状态
        
        # 默认绘画设置
        self.base_width = 6.0  # 基础线条宽度
        self.min_width = 3.0   # 最小线条宽度
        self.max_width = 15.0  # 最大线条宽度
        self.smoothing = 0.7   # 平滑度
        self._line_color = (255, 0, 0)  # 纯红色 - 如果看到这个颜色，说明设置没有生效
        self._color_str = "rgb(255,0,0)"  # 预处理的CSS颜色字符串
        log.error(f"初始化使用临时颜色值: {self._line_color} - 应该很快被设置中的值覆盖")
        
        self.use_advanced_brush = True   # 使用高级笔刷
        self.auto_smoothing = True       # 自动平滑
        self.fade_duration = 0.5         # 渐隐持续时间（秒）
        self.speed_factor = 1.2          # 速度因子
        self.min_distance = 20           # 最小触发距离（像素）
        self.max_stroke_points = 200     # 最大笔画点数
        self.max_stroke_duration = 5     # 最大笔画持续时间（秒）
        self.canvas_border = 1           # 画布边框大小（像素）
        
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
        # 不再立即初始化手势解析器，而是在需要时才初始化
        # self.init_gesture_parser()  
        self.start_listening()
        
        # 确保颜色已从配置加载（不是默认红色）
        if self._line_color == (255, 0, 0):
            log.error("初始化后颜色仍然是默认红色，强制重新从配置加载颜色")
            try:
                config_path = self.get_config_path()
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        drawing_settings = config.get('drawing', {})
                        if drawing_settings and 'color' in drawing_settings:
                            color_hex = drawing_settings['color']
                            if color_hex.startswith('#') and len(color_hex) in [4, 7, 9]:
                                log.info(f"强制加载颜色: {color_hex}")
                                r, g, b = self.hex_to_rgb(color_hex)
                                self._line_color = (r, g, b)
                                log.info(f"强制加载颜色后: {self._line_color}")
            except Exception as e:
                log.error(f"强制加载颜色失败: {str(e)}")
        
        log.info(f"绘画模块初始化完成，当前颜色: {self._line_color}")

    # 添加属性访问器，确保每次获取颜色时都使用最新的值
    @property
    def line_color(self):
        return self._line_color
    
    @line_color.setter
    def line_color(self, value):
        """设置线条颜色，并同时更新CSS颜色字符串缓存"""
        try:
            old_value = self._line_color
            self._line_color = value
            
            # 预处理并缓存CSS颜色字符串格式
            if isinstance(value, tuple) and len(value) >= 3:
                r, g, b = value
                # 确保RGB值在有效范围内
                r = max(0, min(255, int(r)))
                g = max(0, min(255, int(g)))
                b = max(0, min(255, int(b)))
                self._color_str = f"rgb({r},{g},{b})"
            elif isinstance(value, str) and (value.startswith('rgb(') or value.startswith('#')):
                self._color_str = value  # 如果已经是字符串格式，直接使用
            else:
                # 无效颜色格式，使用默认紫色
                log.error(f"无效的颜色格式: {value}，使用默认紫色")
                self._line_color = (170, 85, 255)  # 默认紫色
                self._color_str = "rgb(170,85,255)"
            
            if IS_DEBUG_MODE:
                log.debug(f"线条颜色已从 {old_value} 更新为: {value}")
            
            # 如果有活动的线条，批量更新它们的颜色
            if hasattr(self, 'active_lines') and self.active_lines:
                self._update_active_lines_color()
        except Exception as e:
            log.error(f"设置线条颜色时出错: {e}")
            import traceback
            log.error(f"设置线条颜色错误堆栈: {traceback.format_exc()}")
            # 确保有有效的默认值
            self._line_color = (170, 85, 255)  # 默认紫色
            self._color_str = "rgb(170,85,255)"
    
    def _update_active_lines_color(self):
        """更新所有活动线条的颜色 - 抽取为单独方法以提高可维护性"""
        try:
            if IS_DEBUG_MODE:
                log.debug(f"批量更新 {len(self.active_lines)} 条活动线条颜色为: {self._color_str}")
            
            # 收集要更新的线条，一次性批量更新
            batch_updates = []
            for line in self.active_lines:
                if isinstance(line, dict):  # 确保是有效的线条对象
                    batch_updates.append((line, self._color_str))
            
            # 如果有Canvas实例且支持批量操作，使用批量更新
            if hasattr(self, 'canvas'):
                if hasattr(self.canvas, 'batch_update_lines') and batch_updates:
                    self.canvas.batch_update_lines(batch_updates)
                else:
                    # 否则使用普通更新方式
                    for line, color in batch_updates:
                        try:
                            self.canvas.itemconfig(line, fill=color)
                        except Exception as e:
                            log.error(f"更新单个线条颜色失败: {e}")
                            continue
            
            if IS_DEBUG_MODE:
                log.debug(f"批量更新完成，共 {len(batch_updates)} 条线")
        except Exception as e:
            log.error(f"更新活动线条颜色整体失败: {e}")
            import traceback
            log.error(f"更新线条颜色错误堆栈: {traceback.format_exc()}")

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

    def get_cached_config(self):
        """获取缓存的配置，如果配置文件有变化则重新读取"""
        global _CONFIG_CACHE, _CONFIG_CACHE_TIME
        
        config_path = self.get_config_path()
        
        # 检查文件是否存在
        if not os.path.exists(config_path):
            log.warning(f"配置文件不存在: {config_path}")
            return {}
        
        # 获取文件的最后修改时间
        mod_time = os.path.getmtime(config_path)
        
        # 如果缓存为空或文件有更新，则重新读取
        if not _CONFIG_CACHE or mod_time > _CONFIG_CACHE_TIME:
            try:
                if IS_DEBUG_MODE:
                    log.debug(f"配置文件已变化或未缓存，重新读取: {config_path}")
                with open(config_path, 'r', encoding='utf-8') as f:
                    _CONFIG_CACHE = json.load(f)
                    _CONFIG_CACHE_TIME = mod_time
                    log.info(f"已重新加载配置文件: {config_path}")
            except Exception as e:
                log.error(f"读取配置文件失败: {str(e)}")
                return {}
        else:
            if IS_DEBUG_MODE:
                log.debug(f"使用缓存的配置文件: {config_path}")
            
        return _CONFIG_CACHE

    def get_cached_gestures(self):
        """获取缓存的手势库，如果手势库文件有变化则重新读取"""
        global _GESTURES_CACHE, _GESTURES_CACHE_TIME
        
        gesture_path = self.get_gesture_path()
        
        # 检查文件是否存在
        if not os.path.exists(gesture_path):
            log.warning(f"手势库文件不存在: {gesture_path}")
            return {}
        
        # 获取文件的最后修改时间
        mod_time = os.path.getmtime(gesture_path)
        
        # 如果缓存为空或文件有更新，则重新读取
        if not _GESTURES_CACHE or mod_time > _GESTURES_CACHE_TIME:
            try:
                if IS_DEBUG_MODE:
                    log.debug(f"手势库文件已变化或未缓存，重新读取: {gesture_path}")
                with open(gesture_path, 'r', encoding='utf-8') as f:
                    _GESTURES_CACHE = json.load(f)
                    _GESTURES_CACHE_TIME = mod_time
                    log.info(f"已重新加载手势库文件: {gesture_path}")
            except Exception as e:
                log.error(f"读取手势库文件失败: {str(e)}")
                return {}
        else:
            if IS_DEBUG_MODE:
                log.debug(f"使用缓存的手势库文件: {gesture_path}")
            
        return _GESTURES_CACHE

    def init_canvas(self):
        """初始化Canvas"""
        if IS_DEBUG_MODE:
            log.info(self.file_name + "初始化画布")
        else:
            log.info(self.file_name + "初始化画布")  # 保留关键初始化日志
        # 创建QApplication实例，如果不存在则创建
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # 创建透明全屏画布
        self.canvas = Canvas()
        
        # 获取画布边框大小（从设置中获取，默认为1像素）
        canvas_border = self.canvas_border if hasattr(self, 'canvas_border') else 1
        
        # 获取屏幕尺寸并调整画布大小，根据边框设置减少相应像素
        log.info(f"{self.file_name}设置画布大小: 宽 {self.screen_width - canvas_border*2}px, 高 {self.screen_height - canvas_border*2}px, 边框 {canvas_border}px")
        self.canvas.resize(self.screen_width - canvas_border*2, self.screen_height - canvas_border*2)
        
        # 设置窗口位置，考虑边框大小
        self.canvas.move(canvas_border, canvas_border)
        
        self.canvas.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.canvas.setAttribute(Qt.WA_TranslucentBackground)
        self.canvas.setAttribute(Qt.WA_ShowWithoutActivating)
        log.info(self.file_name + "画布初始化完成")

    def load_settings(self):
        """从配置文件加载绘画设置"""
        log.info(self.file_name + "从配置文件加载绘画设置")
        try:
            # 使用缓存获取配置
            config = self.get_cached_config()
            
            # 检查是否有drawing部分
            if 'drawing' in config:
                drawing_settings = config['drawing']
                
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
                
                # 颜色 - 添加更详细的日志
                if 'color' in drawing_settings:
                    color_hex = drawing_settings['color']
                    log.info(f"从配置中读取到颜色值: {color_hex}")
                    # 解析HEX颜色
                    if color_hex.startswith('#') and len(color_hex) in [4, 7, 9]:
                        try:
                            if IS_DEBUG_MODE:
                                log.info(f"尝试解析HEX颜色: {color_hex}")
                            r, g, b = self.hex_to_rgb(color_hex)
                            log.info(f"HEX颜色 {color_hex} 解析为RGB: ({r}, {g}, {b})")
                            old_color = self.line_color
                            self.line_color = (r, g, b)
                            log.info(f"成功加载颜色: {color_hex} -> RGB: {self.line_color}")
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
                log.warning(self.file_name + "配置文件中无绘画设置部分，使用默认设置")
                if IS_DEBUG_MODE:
                    log.debug(f"默认线条颜色: {self.line_color}")
        except Exception as e:
            log.error(self.file_name + "加载设置失败: " + str(e))

    def load_gestures(self):
        """加载手势库"""
        log.info(self.file_name + "加载手势库")
        self.gestures = {}
        
        try:
            # 使用缓存获取手势库
            gesture_data = self.get_cached_gestures()
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
        except Exception as e:
            log.error("加载手势库失败: " + str(e))
            print("加载手势库失败: " + str(e))

    def init_gesture_parser(self):
        """初始化手势解析器"""
        # 仅在真正需要时才初始化，使用懒加载模式
        global _GESTURE_PARSER_INITIALIZED
        if _GESTURE_PARSER_INITIALIZED:
            if IS_DEBUG_MODE:
                log.debug(self.file_name + "手势解析器已初始化，跳过重复初始化")
            return
        
        log.info(self.file_name + "初始化手势解析器")
        # 使用空列表作为trail_points初始化
        # 这里只是初始化一个解析器实例，实际手势识别时会创建新的实例
        self.parser = GestureParser(trail_points=[])
        _GESTURE_PARSER_INITIALIZED = True
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
            
        # 记录当前时间，用于实现事件节流
        current_time = time.time()
        
        # 节流逻辑：每次处理至少间隔3ms
        if hasattr(self, 'last_mouse_event_time') and current_time - self.last_mouse_event_time < 0.003:
            # 如果距离上次处理不足3ms，稍后再尝试
            QTimer.singleShot(1, self.listen_mouse)
            return
        
        # 更新最后处理时间
        self.last_mouse_event_time = current_time
        
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
                # 计算距离（使用平方距离，避免开平方）
                dx = x - self.start_point[0]
                dy = y - self.start_point[1]
                squared_distance = dx*dx + dy*dy
                
                # 未开始绘画时，检查是否达到触发距离
                # 400 = 20*20 (最小触发距离的平方)
                min_distance_squared = self.min_distance * self.min_distance
                if not self.is_drawing and squared_distance >= min_distance_squared:
                    # 启动绘画
                    self.start_drawing(self.pending_points)
                
                # 已开始绘画或未达到触发距离，记录点
                if self.is_drawing:
                    # 添加到绘画缓冲 - 使用点过滤减少冗余点
                    last_point = self.point_buffer[-1] if self.point_buffer else None
                    if not last_point or self._should_add_point(last_point, (x, y)):
                        self.point_buffer.append((x, y))
                else:
                    # 添加到待处理点，也使用过滤
                    last_point = self.pending_points[-1] if self.pending_points else None
                    if not last_point or self._should_add_point(last_point, (x, y)):
                        self.pending_points.append((x, y))
                    
                # 减少不必要的日志
                if len(self.point_buffer) % 50 == 0 and IS_DEBUG_MODE:
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
        
        # 继续监听，使用自适应间隔
        # 如果正在绘画，使用更短的间隔以提高响应性
        interval = 3 if self.is_drawing else 5
        QTimer.singleShot(interval, self.listen_mouse)  # 间隔时间，保证响应灵敏

    def _should_add_point(self, last_point, new_point):
        """判断是否应该添加新点，避免记录过于密集的点"""
        # 计算点之间的平方距离
        dx = new_point[0] - last_point[0]
        dy = new_point[1] - last_point[1]
        squared_dist = dx*dx + dy*dy
        
        # 如果距离太小，不添加新点，阈值可根据需要调整
        # 使用3像素作为最小距离，平方后为9
        min_record_dist_squared = 9
        
        # 如果绘制速度很快，可以适当增加记录点的频率
        if hasattr(self, 'last_point_time'):
            time_diff = time.time() - self.last_point_time
            # 如果移动速度快（时间短距离大），降低阈值
            if time_diff < 0.03 and squared_dist > 25:  # 5*5=25，5像素且小于30ms
                self.last_point_time = time.time()
                return True
        else:
            self.last_point_time = time.time()
        
        # 正常判断
        if squared_dist >= min_record_dist_squared:
            self.last_point_time = time.time()
            return True
            
        return False

    def process_points(self):
        """处理积累的点数据"""
        if not self.is_drawing or not self.point_buffer:
            return
        
        # 如果缓冲点太少，等待更多点积累
        if len(self.point_buffer) < 2:
            return
        
        # 创建缓冲区副本并清空原缓冲区
        buffer_copy = self.point_buffer.copy()
        self.point_buffer = []
        
        # 对缓冲中的点进行平滑和简化，减少不必要的点
        smoothed_points = self._smooth_and_simplify_points(buffer_copy)
        
        # 处理精简后的点
        for x, y in smoothed_points:
            current_time = time.time()
            self.update_drawing(x, y)

    def _smooth_and_simplify_points(self, points):
        """平滑和简化点序列，减少冗余点"""
        if len(points) <= 2:
            return points
            
        # 结果列表，始终包含起点
        result = [points[0]]
        
        # 使用道格拉斯-普克算法简化点序列
        # 这是一个递归算法，找到一系列点中最大偏差点
        def douglas_peucker(start_index, end_index, epsilon_squared):
            # 找到距离start和end连线最远的点
            max_dist_squared = 0
            max_index = start_index
            
            start_point = points[start_index]
            end_point = points[end_index]
            
            # 如果起点和终点相邻，无需简化
            if end_index - start_index <= 1:
                return
                
            # 计算线段
            line_dx = end_point[0] - start_point[0]
            line_dy = end_point[1] - start_point[1]
            line_length_squared = line_dx*line_dx + line_dy*line_dy
            
            # 如果线段长度为0，所有点都共线
            if line_length_squared == 0:
                max_dist_squared = 0
                for i in range(start_index+1, end_index):
                    point = points[i]
                    dx = point[0] - start_point[0]
                    dy = point[1] - start_point[1]
                    dist_squared = dx*dx + dy*dy
                    if dist_squared > max_dist_squared:
                        max_dist_squared = dist_squared
                        max_index = i
            else:
                # 计算每个点到线段的距离
                for i in range(start_index+1, end_index):
                    point = points[i]
                    
                    # 计算点到线的距离
                    px = point[0] - start_point[0]
                    py = point[1] - start_point[1]
                    
                    # 计算投影比例
                    proj = (px*line_dx + py*line_dy) / line_length_squared
                    
                    # 限制投影在线段范围内
                    proj = max(0, min(1, proj))
                    
                    # 计算投影点
                    proj_x = start_point[0] + proj * line_dx
                    proj_y = start_point[1] + proj * line_dy
                    
                    # 计算距离的平方
                    dx = point[0] - proj_x
                    dy = point[1] - proj_y
                    dist_squared = dx*dx + dy*dy
                    
                    if dist_squared > max_dist_squared:
                        max_dist_squared = dist_squared
                        max_index = i
            
            # 如果最大距离大于阈值，递归处理两个子部分
            if max_dist_squared > epsilon_squared:
                douglas_peucker(start_index, max_index, epsilon_squared)
                result.append(points[max_index])
                douglas_peucker(max_index, end_index, epsilon_squared)
            
        # 调用递归函数简化点序列
        # 使用3像素作为阈值 (3*3=9)
        epsilon_squared = 9
        douglas_peucker(0, len(points)-1, epsilon_squared)
        
        # 确保终点被包含
        if result[-1] != points[-1]:
            result.append(points[-1])
        
        return result

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
            # 使用平方距离比较，避免开平方运算
            dx = x - prev_x
            dy = y - prev_y
            squared_dist = dx*dx + dy*dy
            if squared_dist < 0.01:  # 0.1 * 0.1 = 0.01
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
            
            # 计算移动距离的平方 - 避免开平方运算
            dx = curr_x - prev_x
            dy = curr_y - prev_y
            squared_dist = dx*dx + dy*dy
            
            # 即使距离较大也进行连接，但需要处理大距离情况
            # 10000 = 100*100, 40000 = 200*200
            if squared_dist > 10000:  # 距离大于100像素
                # 只在调试模式下输出详细日志
                if IS_DEBUG_MODE:
                    log.info(self.file_name + f"发现距离较大的点，执行平滑连接: {math.sqrt(squared_dist):.2f}像素")
                else:
                    # 非调试模式下只记录一次日志，使用非精确值
                    log.info(self.file_name + "发现距离较大的点，执行平滑连接")
                
                # 对于特别大的距离，插入中间点
                if squared_dist > 40000:  # 距离大于200像素
                    # 计算需要插入多少个中间点 - 基于实际距离
                    dist = math.sqrt(squared_dist)  # 这里需要开平方
                    insert_count = min(10, int(dist / 30))
                    
                    # 最后绘制的坐标点
                    last_drawn_x, last_drawn_y = prev_x, prev_y
                    
                    # 计算高级画笔的线宽 - 只计算一次
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
            
        # 计算移动距离和时间差 - 使用平方距离优化
        dx = curr_x - prev_x
        dy = curr_y - prev_y
        squared_dist = dx*dx + dy*dy
        # 只有在真正需要时才计算开平方
        dist = math.sqrt(squared_dist)
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
        
        # 计算平滑后的线宽调整系数 - 使用加权移动平均，优化计算
        weights = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]  # 越新的值权重越高
        num_values = len(self.line_width_history)
        trimmed_weights = weights[-num_values:]
        
        # 优化计算加权平均
        weighted_sum = 0
        weight_sum = 0
        for i in range(num_values):
            weighted_sum += trimmed_weights[i] * self.line_width_history[i]
            weight_sum += trimmed_weights[i]
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
        
        # 直接使用预处理好的颜色字符串，避免重复转换
        if IS_DEBUG_MODE:
            log.info(f"绘制线条时使用的颜色: {self.line_color}")
            log.info(f"最终用于绘制线条的CSS颜色: {self._color_str}")
        
        # 简化绘制逻辑，统一使用单个线条，减少绘制开销
        line = self.canvas.create_line(
            float(x1), float(y1), float(x2), float(y2),
            width=width,
            fill=self._color_str,  # 使用预处理的颜色字符串
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
            # 限制已完成笔画历史大小，防止内存无限增长
            max_finished_strokes = 10
            self.finished_strokes.append(current_stroke_copy)
            # 保持最近的10个笔画
            if len(self.finished_strokes) > max_finished_strokes:
                self.finished_strokes = self.finished_strokes[-max_finished_strokes:]
            
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
            
            # 过滤有效的线条对象
            valid_lines = [line for line in self.active_lines if isinstance(line, dict)]
            if len(valid_lines) < len(self.active_lines):
                log.warning(f"过滤掉了 {len(self.active_lines) - len(valid_lines)} 个无效线条对象")
            
            # 设置渐隐动画
            self.fade_animations.append({
                'lines': valid_lines,
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
            try:
                valid_lines = [line for line in self.active_lines if isinstance(line, dict)]
                if hasattr(self.canvas, 'batch_delete_lines') and valid_lines:
                    self.canvas.batch_delete_lines(valid_lines)
                else:
                    for line in valid_lines:
                        self.canvas.delete(line)
            except Exception as e:
                log.error(f"清除线条时出错: {e}")
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
            
            # 确保手势解析器已初始化
            if not _GESTURE_PARSER_INITIALIZED:
                self.init_gesture_parser()
            
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
                            # 确保是字典对象
                            if isinstance(line, dict):
                                self.canvas.delete(line)
                        except Exception as e:
                            log.error(f"删除手势渐隐线条时出错: {e}")
                self.fade_animations.clear()
            
            # 直接调用顶部导入的execute_operation函数
            log.info("执行手势动作")
            execute_operation(action)
            
        except Exception as e:
            log.error("处理手势失败: " + str(e))
            import traceback
            log.error(f"处理手势错误堆栈: {traceback.format_exc()}")

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
        lines_to_remove = []
        
        for anim in self.fade_animations:
            elapsed = current_time - anim['start_time']
            duration = anim['end_time'] - anim['start_time'] if 'end_time' in anim else self.fade_duration
            progress = min(elapsed / duration, 1.0)
            
            # 动态计算颜色：保持原RGB，仅降低不透明度（alpha值）
            fade_color = self.calculate_fade_color(anim['start_color'], progress)
            
            # 批量收集更新
            for line_id in anim['lines']:
                # 确保是有效线条对象
                if isinstance(line_id, dict) and 'color' in line_id:
                    batch_updates.append((line_id, fade_color))
            
            if progress >= 1.0:
                for line_id in anim['lines']:
                    # 只添加有效的线条对象到删除列表
                    if isinstance(line_id, dict):
                        lines_to_remove.append(line_id)
                removals.append(anim)
        
        # 批量执行更新（如果Canvas支持批量更新）
        if hasattr(self.canvas, 'batch_update_lines') and batch_updates:
            self.canvas.batch_update_lines(batch_updates)
        else:
            # 否则普通方式逐条更新
            for line_id, color in batch_updates:
                try:
                    self.canvas.itemconfig(line_id, color)
                except Exception as e:
                    if IS_DEBUG_MODE:
                        log.error(f"更新线条颜色失败: {e}, line_id: {line_id}")
        
        # 批量删除已完成的线条
        if lines_to_remove:
            try:
                if hasattr(self.canvas, 'batch_delete_lines'):
                    self.canvas.batch_delete_lines(lines_to_remove)
                else:
                    for line_id in lines_to_remove:
                        self.canvas.delete(line_id)
            except Exception as e:
                log.error(f"删除渐隐完成线条时出错: {e}")
        
        # 移除已完成的动画
        for anim in removals:
            try:
                self.fade_animations.remove(anim)
            except ValueError:
                log.error(f"尝试移除不存在的动画: {anim}")
                
        # 恢复定时器管理代码
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
            # 进行安全检查，避免空值或无效值
            if base_color is None:
                log.error("计算渐隐颜色失败: 基础颜色为空")
                return "#80AAAAAA"  # 返回一个安全的半透明灰色

            # 解析原始颜色
            r, g, b = 170, 85, 255  # 默认值：紫色，避免使用初始的红色
            
            if isinstance(base_color, tuple) and len(base_color) >= 3:
                # 元组形式的RGB颜色
                r, g, b = base_color
            elif isinstance(base_color, str) and base_color.startswith("#"):
                # 十六进制颜色
                if len(base_color) == 7:  # #RRGGBB
                    try:
                        r = int(base_color[1:3], 16)
                        g = int(base_color[3:5], 16)
                        b = int(base_color[5:7], 16)
                    except ValueError:
                        log.error(f"解析十六进制颜色失败: {base_color}")
                elif len(base_color) == 9:  # #AARRGGBB
                    try:
                        r = int(base_color[3:5], 16)
                        g = int(base_color[5:7], 16)
                        b = int(base_color[7:9], 16)
                    except ValueError:
                        log.error(f"解析带透明度的十六进制颜色失败: {base_color}")
                else:
                    # 无法识别的颜色格式，使用默认值
                    log.error(f"计算渐隐颜色时使用默认紫色 - 颜色格式识别失败: {base_color}")
            elif isinstance(base_color, str):
                # 如果不是十六进制，假设是rgb格式
                color_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', base_color)
                if color_match:
                    try:
                        r, g, b = map(int, color_match.groups())
                    except ValueError:
                        log.error(f"解析RGB格式颜色失败: {base_color}")
                else:
                    # 无法识别的字符串格式，使用默认值
                    log.error(f"计算渐隐颜色时使用默认紫色 - 颜色格式识别失败: {base_color}")
            else:
                # 无法识别的颜色格式，使用默认值
                log.error(f"计算渐隐颜色时使用默认紫色 - 颜色格式类型错误: {type(base_color)}")
            
            # 确保RGB值在有效范围内
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # 计算alpha值 - 使用非线性衰减，让开始减淡更慢一些
            # 确保progress在有效范围内
            progress = max(0.0, min(1.0, progress))
            a = int(255 * (1 - progress**0.7))  # 降低幂次，使淡出更平滑
            a = max(0, min(255, a))  # 确保透明度在有效范围
            
            # 返回包含透明度信息的颜色，格式调整为 #AARRGGBB
            return f"#{a:02X}{r:02X}{g:02X}{b:02X}"
        except Exception as e:
            log.error(f"计算渐隐颜色失败: {e}")
            import traceback
            log.error(f"计算渐隐颜色错误堆栈: {traceback.format_exc()}")
            return "#80AAAAAA"  # 返回一个安全的半透明灰色

    def shutdown(self):
        """安全关闭程序，释放资源"""
        log.info("关闭绘画模块，释放资源")
        self.running = False
        
        # 停止监听鼠标
        self.is_listening = False
        
        # 停止所有定时器
        if hasattr(self, 'fade_timer') and self.fade_timer:
            try:
                self.fade_timer.stop()
            except Exception as e:
                log.error(f"停止渐隐定时器时出错: {e}")
            
        if hasattr(self, 'processing_thread') and self.processing_thread:
            try:
                self.processing_thread.stop()
            except Exception as e:
                log.error(f"停止处理线程时出错: {e}")
        
        # 清空所有线条
        if hasattr(self, 'canvas') and self.canvas:
            # 处理活动线条
            for line in self.active_lines:
                try:
                    if isinstance(line, dict):
                        self.canvas.delete(line)
                except Exception as e:
                    log.error(f"删除活动线条时出错: {e}")
                    
            # 处理渐隐动画中的线条
            for anim in self.fade_animations:
                for line in anim['lines']:
                    try:
                        if isinstance(line, dict):
                            self.canvas.delete(line)
                    except Exception as e:
                        log.error(f"删除渐隐动画线条时出错: {e}")
        
        # 关闭窗口
        if hasattr(self, 'canvas') and self.canvas:
            try:
                self.canvas.hide()
                self.canvas.close()
            except Exception as e:
                log.error(f"关闭画布窗口时出错: {e}")
        
        log.info("绘画模块已安全关闭")

    def start_drawing(self, points):
        """启动绘画模式"""
        log.info("启动绘画模式")
        # 避免重复启动
        if self.is_drawing:
            log.info("绘画模式已经处于激活状态")
            return
        
        # 刷新设置，确保使用最新配置
        self.reset_painter()
        log.debug(f"绘画开始时使用的颜色设置: {self.line_color}")
        
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
        log.info(self.file_name + "更新绘画设置: " + str(settings))
        
        try:
            updated_settings = []
            needs_redraw = False
            old_line_color = self.line_color
            
            # 基础宽度
            if 'base_width' in settings:
                self.base_width = float(settings['base_width'])
                updated_settings.append(f"base_width={self.base_width}")
                
            # 最小宽度
            if 'min_width' in settings:
                self.min_width = float(settings['min_width'])
                updated_settings.append(f"min_width={self.min_width}")
                
            # 最大宽度
            if 'max_width' in settings:
                self.max_width = float(settings['max_width'])
                updated_settings.append(f"max_width={self.max_width}")
                
            # 平滑度
            if 'smoothing' in settings:
                self.smoothing = float(settings['smoothing'])
                updated_settings.append(f"smoothing={self.smoothing}")
                
            # 颜色
            if 'color' in settings:
                color_hex = settings['color']
                # 解析HEX颜色
                if color_hex.startswith('#') and len(color_hex) in [4, 7, 9]:
                    try:
                        log.info(f"正在从配置文件加载颜色: {color_hex}")
                        r, g, b = self.hex_to_rgb(color_hex)
                        # 设置颜色
                        log.debug(f"更新颜色设置: {color_hex} -> RGB: ({r},{g},{b}) 旧值: {old_line_color}")
                        self.line_color = (r, g, b)
                        updated_settings.append(f"color={color_hex}")
                        needs_redraw = True
                        
                        # 额外检查颜色设置是否成功应用
                        log.debug(f"更新后的颜色: {self.line_color}")
                    except Exception as e:
                        log.error(f"颜色解析失败: {str(e)}")
                        
            # 高级笔刷
            if 'advanced_brush' in settings:
                self.use_advanced_brush = bool(settings['advanced_brush'])
                updated_settings.append(f"advanced_brush={self.use_advanced_brush}")
                
            # 自动平滑
            if 'auto_smoothing' in settings:
                self.auto_smoothing = bool(settings['auto_smoothing'])
                updated_settings.append(f"auto_smoothing={self.auto_smoothing}")
                
            # 淡出时间
            if 'fade_time' in settings:
                self.fade_duration = float(settings['fade_time'])
                updated_settings.append(f"fade_time={self.fade_duration}")
                
            # 速度因子
            if 'speed_factor' in settings:
                self.speed_factor = float(settings['speed_factor'])
                updated_settings.append(f"speed_factor={self.speed_factor}")
                
            # 最小触发距离
            if 'min_distance' in settings:
                self.min_distance = int(float(settings['min_distance']))
                updated_settings.append(f"min_distance={self.min_distance}")
                
            # 最大笔画点数
            if 'max_stroke_points' in settings:
                self.max_stroke_points = int(float(settings['max_stroke_points']))
                updated_settings.append(f"max_stroke_points={self.max_stroke_points}")
                
            # 最大笔画持续时间
            if 'max_stroke_duration' in settings:
                self.max_stroke_duration = int(float(settings['max_stroke_duration']))
                updated_settings.append(f"max_stroke_duration={self.max_stroke_duration}")

            # 如果颜色发生变化，立即更新已绘制的活动线条
            if needs_redraw and hasattr(self, 'active_lines') and self.active_lines:
                log.info("颜色设置已更改，更新活动线条颜色")
                try:
                    # 将RGB元组转换为CSS颜色字符串
                    if isinstance(self.line_color, tuple) and len(self.line_color) >= 3:
                        r, g, b = self.line_color
                        color_str = f"rgb({r},{g},{b})"
                    else:
                        color_str = self.line_color
                    
                    log.debug(f"更新活动线条颜色为: {color_str}")
                    
                    # 更新所有活动线条的颜色
                    for line in self.active_lines:
                        self.canvas.itemconfig(line, fill=color_str)
                    
                    # 更新当前渐隐动画中的开始颜色
                    for anim in self.fade_animations:
                        anim['start_color'] = self.line_color
                except Exception as e:
                    log.error(f"更新活动线条颜色失败: {str(e)}")
            
            # 硬件加速
            if 'hardware_acceleration' in settings and hasattr(self, 'canvas'):
                hardware_accel = bool(settings['hardware_acceleration'])
                self.canvas.enable_hardware_acceleration = hardware_accel
                updated_settings.append(f"hardware_acceleration={hardware_accel}")
                
            # 画布边框大小
            if 'canvas_border' in settings:
                old_border = self.canvas_border if hasattr(self, 'canvas_border') else 1
                self.canvas_border = int(settings['canvas_border'])
                updated_settings.append(f"canvas_border={self.canvas_border}")
                
                # 如果边框大小改变且画布已创建，则重新调整画布大小
                if hasattr(self, 'canvas') and old_border != self.canvas_border:
                    log.info(f"{self.file_name}重新调整画布大小: 宽 {self.screen_width - self.canvas_border*2}px, 高 {self.screen_height - self.canvas_border*2}px, 边框 {self.canvas_border}px")
                    self.canvas.resize(self.screen_width - self.canvas_border*2, self.screen_height - self.canvas_border*2)
                    # 更新画布位置
                    self.canvas.move(self.canvas_border, self.canvas_border)
            
            # 打印所有更新的设置
            if updated_settings:
                log.info(self.file_name + "已更新以下设置: " + ", ".join(updated_settings))
            else:
                log.info(self.file_name + "未更新任何设置，使用现有配置")
            
            return True
        except Exception as e:
            log.error(self.file_name + "更新绘画设置失败: " + str(e))
            import traceback
            log.error(self.file_name + "错误堆栈: " + traceback.format_exc())
            return False

    # 添加重置方法，确保设置被完全刷新
    def reset_painter(self):
        """重置绘图器状态，应用最新设置"""
        log.info("重置绘图器状态，应用最新设置")
        old_color = self.line_color
        # 重新加载设置
        self.load_settings()
        log.info(f"重置后颜色从 {old_color} 变为 {self.line_color}")
        
        # 重置绘画状态变量
        self.current_stroke = []
        self.smoothed_stroke = []
        self.pending_points = []
        self.line_width_history = []
        self.last_line_width = self.base_width

if __name__ == "__main__":
    print("建议通过主程序运行。")
    # 测试时启用调试模式
    set_debug_mode(True)
    test_painter = InkPainter()
    # 启动Qt事件循环，保持程序运行
    sys.exit(test_painter.app.exec_())