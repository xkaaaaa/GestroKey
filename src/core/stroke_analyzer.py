import math
import numpy as np
from collections import deque
from scipy.signal import savgol_filter

# 动态导入日志模块
try:
    from logger import get_logger
except ImportError:
    from core.logger import get_logger

class StrokeAnalyzer:
    """笔画分析器，用于分析笔画的方向和特征"""
    
    # 定义方向常量
    UP = "上"
    DOWN = "下"
    LEFT = "左"
    RIGHT = "右"
    UP_LEFT = "左上"
    UP_RIGHT = "右上"
    DOWN_LEFT = "左下"
    DOWN_RIGHT = "右下"
    
    # 方向索引映射
    DIRECTIONS = [RIGHT, UP_RIGHT, UP, UP_LEFT, LEFT, DOWN_LEFT, DOWN, DOWN_RIGHT]
    
    def __init__(self):
        self.logger = get_logger("StrokeAnalyzer")
        self.min_segment_length = 10  # 最小分析段长度，小于此值的移动被视为噪声
        self.min_direction_change = 45  # 最小方向变化角度（度），大于此值视为方向改变
        self.min_segment_points = 5  # 一个方向段至少需要的点数
        
    def analyze_direction(self, points):
        """分析一系列点的主要方向
        
        Args:
            points: 点列表，每个点为(x, y, pressure, time, stroke_id)的元组
            
        Returns:
            tuple: (方向序列字符串, 方向细节字典)
        """
        if len(points) < 2:
            return "无方向", {}
            
        # 提取坐标信息
        coords = [(p[0], p[1]) for p in points]
        
        # 分段识别方向变化
        segments = self._segment_stroke(coords)
        
        if not segments:
            return "无明显方向", {}
            
        # 分析每个段的主方向
        segment_directions = []
        for segment in segments:
            if len(segment) < self.min_segment_points:
                continue
                
            # 计算段内各方向权重
            directions_weight = self._analyze_segment_directions(segment)
            
            # 获取主方向
            if directions_weight:
                main_dir = max(directions_weight.items(), key=lambda x: x[1])[0]
                segment_directions.append(main_dir)
        
        # 生成方向字符串
        if not segment_directions:
            return "无明显方向", {}
            
        # 合并连续相同方向
        merged_directions = []
        for dir in segment_directions:
            if not merged_directions or merged_directions[-1] != dir:
                merged_directions.append(dir)
        
        # 生成方向描述
        direction_str = "-".join(merged_directions)
        
        # 计算各方向的百分比统计
        flat_segments = [item for sublist in segments for item in sublist]
        overall_stats = self._analyze_segment_directions(flat_segments)
        
        # 返回方向序列和整体统计
        return direction_str, overall_stats
        
    def _segment_stroke(self, coords):
        """将笔画分割为具有不同方向的段
        
        Args:
            coords: 坐标点列表 [(x1,y1), (x2,y2), ...]
            
        Returns:
            list: 分割后的段列表，每个段是一个坐标点列表
        """
        if len(coords) < 3:
            return [coords]
            
        segments = []
        current_segment = [coords[0]]
        
        # 计算初始方向
        x1, y1 = coords[0]
        x2, y2 = coords[1]
        current_angle = math.degrees(math.atan2(y1 - y2, x2 - x1))  # y坐标反转
        
        # 初始化方向变化检测变量
        angle_history = deque(maxlen=5)  # 存储最近5个角度
        angle_history.append(current_angle)
        
        for i in range(1, len(coords)):
            current_segment.append(coords[i])
            
            # 不在最后两个点计算方向变化
            if i < len(coords) - 1:
                x1, y1 = coords[i]
                x2, y2 = coords[i+1]
                
                # 计算当前方向
                dx = x2 - x1
                dy = y1 - y2  # y坐标反转
                
                # 忽略太短的移动
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < 2:  # 微小移动忽略
                    continue
                    
                new_angle = math.degrees(math.atan2(dy, dx))
                
                # 规范化角度到0-360度
                if new_angle < 0:
                    new_angle += 360
                
                angle_history.append(new_angle)
                
                # 如果收集了足够多的角度，检查是否有方向变化
                if len(angle_history) >= 4:
                    # 计算平均角度
                    avg_old = sum(list(angle_history)[:-2]) / (len(angle_history) - 2)
                    avg_new = sum(list(angle_history)[-2:]) / 2
                    
                    # 计算角度差
                    angle_diff = abs(avg_new - avg_old)
                    if angle_diff > 180:
                        angle_diff = 360 - angle_diff
                        
                    # 如果角度变化足够大，且当前段足够长，则认为方向改变
                    if angle_diff > self.min_direction_change and len(current_segment) >= self.min_segment_points:
                        segments.append(current_segment)
                        current_segment = [coords[i]]
                        angle_history.clear()
                        angle_history.append(new_angle)
        
        # 添加最后一个段
        if current_segment:
            segments.append(current_segment)
            
        return segments
    
    def _analyze_segment_directions(self, coords):
        """分析一个段内的方向分布
        
        Args:
            coords: 坐标点列表 [(x1,y1), (x2,y2), ...]
            
        Returns:
            dict: 各方向的权重
        """
        if len(coords) < 2:
            return {}
            
        direction_weights = {}
        
        for i in range(1, len(coords)):
            x1, y1 = coords[i-1]
            x2, y2 = coords[i]
            
            dx = x2 - x1
            dy = y1 - y2  # y坐标反转（屏幕坐标系中y轴向下）
            
            # 计算段长度
            segment_length = math.sqrt(dx*dx + dy*dy)
            
            # 忽略太短的段（可能是噪声）
            if segment_length < self.min_segment_length / 5:  # 分段时使用更小的阈值
                continue
                
            # 确定此段的方向
            direction = self._determine_direction(dx, dy)
            direction_weights[direction] = direction_weights.get(direction, 0) + segment_length
            
        # 如果没有有效方向，返回空
        if not direction_weights:
            return {}
            
        # 计算每个方向的百分比
        total_length = sum(direction_weights.values())
        direction_percentages = {d: (w/total_length)*100 for d, w in direction_weights.items()}
        
        return direction_percentages
    
    def _determine_direction(self, dx, dy):
        """根据dx和dy确定方向"""
        # 计算角度（弧度）
        angle = math.atan2(dy, dx)
        
        # 将弧度转换为角度
        angle_deg = math.degrees(angle)
        
        # 角度范围从-180°到180°，将其规范化为0°到360°
        if angle_deg < 0:
            angle_deg += 360
            
        # 根据角度确定方向
        if 22.5 <= angle_deg < 67.5:
            return self.UP_RIGHT
        elif 67.5 <= angle_deg < 112.5:
            return self.UP
        elif 112.5 <= angle_deg < 157.5:
            return self.UP_LEFT
        elif 157.5 <= angle_deg < 202.5:
            return self.LEFT
        elif 202.5 <= angle_deg < 247.5:
            return self.DOWN_LEFT
        elif 247.5 <= angle_deg < 292.5:
            return self.DOWN
        elif 292.5 <= angle_deg < 337.5:
            return self.DOWN_RIGHT
        else:  # 337.5 <= angle_deg < 360 or 0 <= angle_deg < 22.5
            return self.RIGHT
    
    def get_direction_description(self, direction_str):
        """将方向字符串转换为人类可读的描述"""
        if not direction_str or direction_str == "无方向" or direction_str == "无明显方向":
            return "无明显方向"
            
        parts = direction_str.split("-")
        if len(parts) == 1:
            return f"单一{parts[0]}方向"
        else:
            return f"先{parts[0]}后{'再'.join(parts[1:])}" 