"""
绘画模块
调用说明：
1. 初始化：painter = InkPainter()
   - 创建全屏透明画布
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
import tkinter as tk
import pyautogui
import win32api
import win32con
import os
import sys
import colorsys
from .gesture_parser import GestureParser
from .log import log

class InkPainter:
    def __init__(self):
        # 硬件参数
        self.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.file_name = "ink_painter"
        
        log(self.file_name, "绘画模块初始化")
        # 绘画参数
        self.load_drawing_settings()  # 加载绘画参数
        
        # 抗锯齿预计算
        log(self.file_name, "开始抗锯齿颜色预计算")
        self.antialias_colors = []
        base_color = np.array([int(self.line_color[1:3], 16), 
                              int(self.line_color[3:5], 16), 
                              int(self.line_color[5:7], 16)])
        for i in range(self.antialias_layers):
            ratio = i / self.antialias_layers
            fade = 0.8 * (1 - ratio**0.3)
            blend = ratio * 0.1
            color = base_color * fade + (255 - base_color) * blend
            self.antialias_colors.append("#{:02X}{:02X}{:02X}".format(*np.clip(color, 0, 255).astype(int)))
        log(self.file_name, f"完成抗锯齿颜色预计算，共生成{len(self.antialias_colors)}种颜色")
            
        # 状态控制
        self.drawing = False               # 绘画状态标志
        self.running = True                # 运行状态标志
        self.current_stroke = []           # 当前笔画数据
        self.active_lines = []             # 画布线条对象
        self.fade_animations = []          # 渐隐动画队列
        self.start_point = None            # 记录起始点
        self.pending_points = []           # 存储达到触发条件前的轨迹点
        
        # 初始化系统
        self.load_gestures()               # 加载手势配置
        self.init_canvas()                 # 创建GUI界面
        self.start_listening()             # 启动监听循环

    def get_settings_path(self):
        """获取项目根目录的通用方法"""
        if getattr(sys, 'frozen', False):
            # 打包后使用exe所在目录的上二级目录
            return os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'settings.json')
        else:
            # 开发时使用当前文件的上三级目录（src/app → 根目录）
            return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'settings.json')


    def init_canvas(self):
        """创建全屏透明画布窗口"""
        log(self.file_name, "开始初始化画布窗口")
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.attributes("-alpha", 0.85)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "white")
        
        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        log(self.file_name, "画布窗口初始化完成")

    def load_drawing_settings(self):
        """从settings.json加载绘画参数"""
        log(self.file_name, "开始加载绘画参数")
        try:
            with open(self.get_settings_path(), 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            drawing_settings = config['drawing_settings']
            self.base_width = drawing_settings['base_width']                                  # 基础线宽
            self.min_width = drawing_settings['min_width']                                    # 最小线宽
            self.max_width = drawing_settings['max_width']                                    # 最大线宽
            self.speed_factor = drawing_settings['speed_factor']                              # 速度敏感度
            self.fade_duration = drawing_settings['fade_duration']                            # 渐隐时长
            self.antialias_layers = drawing_settings['antialias_layers']                      # 抗锯齿层数
            self.min_distance = drawing_settings['min_distance']                              # 最小触发距离
            self.line_color = drawing_settings['line_color']                                  # 线条颜色
            self.max_stroke_points = drawing_settings['max_stroke_points']                    # 最绘制大节点数
            self.max_stroke_duration = drawing_settings['max_stroke_duration']                # 最大绘制时长（秒）
            self.enable_advanced_brush = drawing_settings.get('enable_advanced_brush', True)  # 高级画笔开关
            self.fade_color = drawing_settings.get('fade_color', '#0000FF')                   # 渐隐动画颜色
            self.force_topmost = drawing_settings.get('force_topmost', True)                  # 强制置顶开关
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
        self.root.after(5, self.listen_mouse)

    def listen_mouse(self):
        """核心监听逻辑"""
        if not self.running:
            return
        
        # 强制置顶
        if self.force_topmost:
            try:
                self.root.attributes("-topmost", True)
            except tk.TclError:
                log(self.file_name, "强制置顶失败", level='error')
        
        right_pressed = win32api.GetAsyncKeyState(win32con.VK_RBUTTON) < 0
        x, y = pyautogui.position()
        
        # 状态切换处理
        if right_pressed and not self.last_right_state:
            self.start_point = (x, y)  # 记录起始点
            self.pending_points = [(x, y, time.time())]  # 初始化缓存
        elif right_pressed and not self.drawing and self.start_point:
            # 持续缓存轨迹点（即使未达触发距离）
            self.pending_points.append((x, y, time.time()))
            
            # 检查触发条件
            # 修复代码：提取元组中的坐标分量
            start_x, start_y = self.start_point
            dx = x - start_x
            dy = y - start_y
            if math.hypot(dx, dy) >= self.min_distance:
                self.start_drawing()  # 触发后开始绘制历史轨迹
        elif right_pressed and self.drawing:
            self.update_drawing(x, y)
        elif not right_pressed and self.last_right_state:
            # 松开右键时清理
            if self.pending_points:
                log(self.file_name, "松开右键，清理未完成的轨迹")
                for line in self.active_lines:
                    try:
                        self.canvas.delete(line)
                    except tk.TclError:
                        pass
                self.active_lines = []
                self.pending_points = []
            self.finish_drawing()
            self.start_point = None
        
        self.last_right_state = right_pressed
        self.root.after(5, self.listen_mouse)

    def start_drawing(self):
        """从缓存点开始初始化笔画"""
        if not self.pending_points:
            return
        
        log(self.file_name, "触发绘制条件，开始处理历史轨迹")
        
        # 转换缓存点并记录线条
        self.current_stroke = []
        active_lines = []  # 临时存储历史轨迹线条
        
        # 生成初始线宽
        base_width = self.base_width
        for i in range(len(self.pending_points)):
            x, y, t = self.pending_points[i]
            if i == 0:
                current_width = base_width
            else:
                # 计算动态线宽（与实时绘制相同逻辑）
                prev_x, prev_y, prev_t = self.pending_points[i-1]
                dx = x - prev_x
                dy = y - prev_y
                dt = t - prev_t
                speed = math.hypot(dx, dy) / dt if dt > 0 else 0
                target_width = base_width / (1 + self.speed_factor * speed**0.7) if self.enable_advanced_brush else base_width
                target_width = max(self.min_width, min(self.max_width, target_width))
                
                # 平滑过渡到目标宽度
                smooth_factor = 0.3  # 与实时绘制一致
                current_width = prev_width * (1 - smooth_factor) + target_width * smooth_factor
            
            self.current_stroke.append((x, y, t, current_width))
            prev_width = current_width  # 记录当前线宽
            
            # 绘制线段
            if i > 0:
                prev_x, prev_y, prev_t, prev_width = self.current_stroke[i-1]
                lines = self.draw_antialiased_line(prev_x, prev_y, x, y, prev_width, current_width)
                active_lines.extend(lines)
        
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
            self.start_drawing()  # 移除非法的坐标参数
            return
        
        # 原有逻辑
        current_time = time.time()
        prev_x, prev_y, prev_time, prev_width = self.current_stroke[-1]
        
        # 计算动态线宽
        dx = x - prev_x
        dy = y - prev_y
        distance = math.hypot(dx, dy)
        delta_time = current_time - prev_time
        if delta_time > 0.001:
            speed = distance / delta_time
        else:
            speed = 0
        
        # 计算目标宽度
        target_width = self.base_width / (1 + self.speed_factor * speed**0.7)
        target_width = max(self.min_width, min(self.max_width, target_width))
        
        # 平滑过渡到目标宽度
        if len(self.current_stroke) > 1:
            # 使用加权平均实现平滑过渡
            smooth_factor = 0.3  # 调整这个值可以控制过渡速度
            current_width = prev_width * (1 - smooth_factor) + target_width * smooth_factor
        else:
            current_width = target_width
        
        # 记录轨迹点
        self.current_stroke.append((x, y, current_time, current_width))
        
        # 抗锯齿绘制
        lines = self.draw_antialiased_line(prev_x, prev_y, x, y, prev_width, current_width)
        self.active_lines.extend(lines)


    def draw_antialiased_line(self, x1, y1, x2, y2, w1, w2):
        """生成抗锯齿线条，并返回线条对象列表"""
        line_group = []
        
        # 先绘制最外层的抗锯齿层
        for i in reversed(range(self.antialias_layers)):
            ratio = i / self.antialias_layers
            width = w1 * (1 - ratio) + w2 * ratio
            expand = 1 + 1.0 * (1 - ratio**0.5)
            
            # 计算抗锯齿颜色
            base_color = np.array([int(self.line_color[1:3], 16), 
                                int(self.line_color[3:5], 16), 
                                int(self.line_color[5:7], 16)])
            fade = 0.85 * (1 - ratio**0.3)
            blend = ratio * 0.1
            color = base_color * fade + (255 - base_color) * blend
            antialias_color = "#{:02X}{:02X}{:02X}".format(*np.clip(color, 0, 255).astype(int))
            
            layer = self.canvas.create_line(
                x1, y1, x2, y2,
                width=width * expand,
                fill=antialias_color,
                capstyle=tk.ROUND,
                smooth=True,
                joinstyle=tk.ROUND
            )
            line_group.append(layer)
        
        # 最后绘制主线条
        main_line = self.canvas.create_line(
            x1, y1, x2, y2,
            width=w2,
            fill=self.line_color,
            capstyle=tk.ROUND,
            smooth=True,
            joinstyle=tk.ROUND
        )
        line_group.append(main_line)
        
        return line_group

    def finish_drawing(self):
        """结束并处理当前笔画"""
        log(self.file_name, "结束当前笔画")
        self.drawing = False
        
        # 合并所有轨迹点（包括触发前的缓存）
        full_stroke = self.current_stroke.copy()
        
        # 触发渐隐动画
        if self.active_lines:
            log(self.file_name, f"触发渐隐动画，线条数: {len(self.active_lines)}")
            self.fade_animations.append({
                'lines': self.active_lines.copy(),  # 包含历史和实时线条
                'start_time': time.time(),
                'base_color': self.line_color
            })
            self.active_lines = []
            self.process_fade_animation()
        
        # 手势识别（使用完整轨迹）
        if len(full_stroke) >= 5:
            log(self.file_name, f"开始手势识别，轨迹点数: {len(full_stroke)}")
            trail_points = [(x, y) for x, y, *_ in full_stroke]
            parser = GestureParser(trail_points, config_path=self.get_settings_path())
            if operation := parser.parse():
                log(self.file_name, f"识别到手势，执行操作: {operation}")
                self.execute_operation(operation)
        
        # 清空数据
        self.current_stroke = []
        self.pending_points = []

    def process_fade_animation(self):
        """处理渐隐动画帧"""
        current_time = time.time()
        removals = []
        
        for anim in self.fade_animations:
            elapsed = current_time - anim['start_time']
            progress = min(elapsed / self.fade_duration, 1.0)
            
            # 动态计算颜色
            fade_color = self.calculate_fade_color(anim['base_color'], progress)
            
            # 更新颜色
            for line_id in anim['lines']:
                try:
                    self.canvas.itemconfig(line_id, fill=fade_color)
                except tk.TclError:
                    pass
            
            if progress >= 1.0:
                for line_id in anim['lines']:
                    self.canvas.delete(line_id)
                removals.append(anim)
            
            # 清理并保持循环
            for anim in removals:
                self.fade_animations.remove(anim)
            
            if self.fade_animations:
                self.root.after(10, self.process_fade_animation)

    def calculate_fade_color(self, base_color, progress):
        """根据进度计算渐隐颜色（HSV明度调整）"""
        # 将HEX转RGB
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        
        # 转HSV并调整明度
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        v = v * (1 - progress)  # 明度随进度降低
        r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)
        
        # 转回HEX
        return "#{:02X}{:02X}{:02X}".format(
            int(r_new*255), 
            int(g_new*255), 
            int(b_new*255)
        )

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
        self.root.destroy()
        self.canvas = None
        log(self.file_name, "绘画模块已关闭")

if __name__ == "__main__":
    print("额，非常不建议您这么启动")
    print("不过也不是不行，就是会报错《而已》。你只需要修改一下开头即可")
    time.sleep(1)
    test_painter = InkPainter()
    test_painter.root.mainloop()