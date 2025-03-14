"""
手势解析模块
调用说明：
1. 初始化解析器：
   parser = GestureParser(trail_points, config_path='settings.json')
   - trail_points: 轨迹点列表，格式 [(x1,y1), (x2,y2), ...]
   - config_path: 手势配置文件路径（可选）

2. 执行解析：
   operation = parser.parse()
   - 返回匹配的操作指令（Base64字符串），若无匹配返回None

3. 方向定义：
   右(0°), 右上(45°), 上(90°), 左上(135°), 
   左(180°), 左下(225°), 下(270°), 右下(315°)
"""

import math
import json
import numpy as np
import time
import os
from typing import List, Dict, Optional

try:
    from .log import log
except ImportError:
    from log import log

class GestureParser:
    DIRECTION_MAP = ["右", "右上", "上", "左上", 
                    "左", "左下", "下", "右下"]
    
    def __init__(self, trail_points: List[tuple], config_path: str = None):
        """
        初始化手势解析器
        :param trail_points: 轨迹点序列 [(x,y), ...]
        :param config_path: 手势配置文件路径
        """
        self.trail = trail_points
        # 如果没有提供配置路径，使用项目根目录的settings.json
        if config_path is None:
            # 获取项目根目录
            current_dir = os.path.abspath(os.path.dirname(__file__))
            # 从当前目录向上两级找到项目根目录
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.config_path = os.path.join(project_root, 'settings.json')
        else:
            self.config_path = config_path
            
        self.min_points = 5           # 最小识别点数
        self.step_base = 3            # 动态步长基数
        self.merge_threshold = 25     # 合并阈值(px)
        self.noise_threshold = 15     # 噪音阈值(px)
        self.file_name = 'gesture_parser'

        log(self.file_name, f"初始化解析器，轨迹点数: {len(trail_points)}，配置文件: {self.config_path}")
        # 加载手势库
        self.gesture_lib = self._load_gesture_lib()

    def parse(self) -> Optional[str]:
        """
        主解析流程
        :return: Base64编码的操作指令或None
        """
        log(self.file_name, "开始解析手势...")
        if len(self.trail) < self.min_points:
            log(self.file_name, f"轨迹点不足，需要至少{self.min_points}个点")
            return None
            
        # 核心处理流程
        raw_segments = self._parse_raw_strokes()
        optimized = self._optimize_strokes(raw_segments)
        result = self._match_gesture(optimized)
        log(self.file_name, f"解析完成，结果: {result}")
        return result

    def _parse_raw_strokes(self) -> List[Dict]:
        """
        原始笔画分割算法
        :return: 未优化的笔画序列 [{'方向':str, '长度':float}, ...]
        """
        log(self.file_name, "开始原始笔画分割...")
        if len(self.trail) < 2:
            log(self.file_name, "轨迹点不足，无法分割")
            return []

        # 动态计算采样步长
        step = max(self.step_base, len(self.trail)//20)
        log(self.file_name, f"计算采样步长: {step}")
        segments = []
        current_dir = None
        accum_vector = np.array([0, 0])
        
        # 添加初始方向检测
        if len(self.trail) >= step:
            initial_vector = np.array(self.trail[step-1]) - np.array(self.trail[0])
            if np.linalg.norm(initial_vector) >= self.noise_threshold:
                current_dir = self._vector_to_direction(initial_vector)
                accum_vector = initial_vector
        
        for i in range(step, len(self.trail), step):
            prev = np.array(self.trail[i-step])
            curr = np.array(self.trail[i])
            vector = curr - prev
            
            # 调整过滤逻辑，保留初始方向
            if np.linalg.norm(vector) < self.noise_threshold:
                if not current_dir:  # 仅当没有初始方向时过滤
                    log(self.file_name, f"过滤微小移动: {vector}")
                    continue
                
            new_dir = self._vector_to_direction(vector)
            
            # 方向变化检测
            if current_dir:
                if self._direction_diff(current_dir, new_dir) > 45:
                    log(self.file_name, f"检测到方向变化: {current_dir} -> {new_dir}")
                    segments.append({
                        '方向': current_dir,
                        '长度': np.linalg.norm(accum_vector)
                    })
                    accum_vector = vector
                    current_dir = new_dir
                else:
                    accum_vector += vector
                    current_dir = self._vector_to_direction(accum_vector)
            else:
                accum_vector = vector
                current_dir = new_dir
        
        # 添加最后一段
        if current_dir:
            log(self.file_name, f"添加最后一段: {current_dir}")
            segments.append({
                '方向': current_dir,
                '长度': np.linalg.norm(accum_vector)
            })
            
        log(self.file_name, f"分割完成，共得到{len(segments)}段笔画")
        return segments

    def _optimize_strokes(self, segments: List[Dict]) -> List[str]:
        """
        优化笔画序列
        :param segments: 原始笔画数据
        :return: 优化后的方向序列 [方向1, 方向2, ...]
        """
        log(self.file_name, "开始优化笔画序列...")
        if not segments:
            log(self.file_name, "无有效笔画数据")
            return []
        
        # 第一步：合并短笔画
        length_median = np.median([s['长度'] for s in segments])
        log(self.file_name, f"计算笔画长度中位数: {length_median}")
        merged = []
        temp = segments[0]
        
        for seg in segments[1:]:
            if temp['长度'] < self.merge_threshold and \
            self._direction_diff(temp['方向'], seg['方向']) < 90:
                log(self.file_name, f"合并短笔画: {temp['方向']} + {seg['方向']}")
                temp['长度'] += seg['长度']
                temp['方向'] = self._vector_to_direction(
                    self._direction_to_vector(temp['方向']) * temp['长度'] +
                    self._direction_to_vector(seg['方向']) * seg['长度']
                )
            else:
                merged.append(temp)
                temp = seg
        merged.append(temp)
        log(self.file_name, f"合并后剩余笔画数: {len(merged)}")
        
        # 第二步：识别重复模式
        directions = [s['方向'] for s in merged]
        simplified = []
        i = 0
        while i < len(directions):
            # 查找重复模式
            pattern = self._find_repeating_pattern(directions[i:])
            if pattern:
                simplified.extend(pattern)
                i += len(pattern)  # 跳过已处理的模式
            else:
                simplified.append(directions[i])
                i += 1
        
        # 第三步：首尾强化
        if len(simplified) > 2:
            mid_dirs = simplified[1:-1]
            mid_dirs = [d for d in mid_dirs if 
                    self._direction_diff(d, simplified[0]) > 45 and
                    self._direction_diff(d, simplified[-1]) > 45]
            simplified = [simplified[0]] + mid_dirs + [simplified[-1]]
            log(self.file_name, f"首尾强化后方向序列: {simplified}")

        log(self.file_name, f"优化完成，最终方向序列: {simplified}")
        return simplified

    def _find_repeating_pattern(self, directions: List[str]) -> Optional[List[str]]:
        """查找重复模式"""
        if len(directions) < 4:
            return None
        
        # 查找最小重复单元
        for pattern_length in range(2, min(6, len(directions)//2)):
            pattern = directions[:pattern_length]
            next_pattern = directions[pattern_length:2*pattern_length]
            
            if pattern == next_pattern:
                # 检查是否还有更多重复
                i = 2 * pattern_length
                while i + pattern_length <= len(directions):
                    if directions[i:i+pattern_length] != pattern:
                        break
                    i += pattern_length
                
                # 返回完整的重复模式
                return directions[:i]
        
        return None

    def _match_gesture(self, directions: List[str]) -> Optional[str]:
        """
        匹配预定义手势
        :param directions: 优化后的方向序列
        :return: 匹配的操作指令或None
        """
        log(self.file_name, f"开始手势匹配，输入方向序列: {directions}")
        for gesture in self.gesture_lib:
            if len(directions) != len(gesture['directions']):
                continue
                
            match = True
            for d1, d2 in zip(directions, gesture['directions']):
                if d1 != d2:
                    match = False
                    break
            if match:
                log(self.file_name, f"匹配到手势: {gesture['name']}")
                return gesture['action']
        log(self.file_name, "未匹配到任何手势")
        return None

    def _load_gesture_lib(self) -> List[Dict]:
        """从配置文件加载手势库"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            gestures = []
            for name, gesture in config['gestures'].items():
                gestures.append({
                    'name': name,
                    'directions': gesture['directions'],
                    'action': gesture['action']
                })
            
            log(self.file_name, f"成功加载手势库，共加载{len(gestures)}个手势")
            return gestures
            
        except FileNotFoundError:
            log(self.file_name, f"配置文件未找到: {self.config_path}", level='error')
            raise
        except json.JSONDecodeError:
            log(self.file_name, f"配置文件格式错误: {self.config_path}", level='error')
            raise
        except KeyError as e:
            log(self.file_name, f"配置文件缺少必要字段: {str(e)}", level='error')
            raise
        except Exception as e:
            log(self.file_name, f"加载手势库时发生未知错误: {str(e)}", level='error')
            raise

    def _vector_to_direction(self, vector: np.ndarray) -> str:
        """向量转8方向"""
        # 计算向量模长
        magnitude = np.linalg.norm(vector)
        if magnitude < 1e-6:  # 防止零向量
            return "右"
        
        # 计算精确角度（0-360度）
        angle = math.degrees(math.atan2(-vector[1], vector[0])) % 360
        
        # 动态阈值计算（基于向量长度）
        dynamic_threshold = 22.5 * (1 + 1/(1 + magnitude/50))  # 长度越大阈值越小
        
        # 八个方向的角度范围计算
        direction_ranges = [
            (337.5 - dynamic_threshold, 22.5 + dynamic_threshold),   # 右
            (22.5 + dynamic_threshold, 67.5 + dynamic_threshold),   # 右上
            (67.5 + dynamic_threshold, 112.5 + dynamic_threshold),   # 上
            (112.5 + dynamic_threshold, 157.5 + dynamic_threshold), # 左上
            (157.5 + dynamic_threshold, 202.5 + dynamic_threshold), # 左
            (202.5 + dynamic_threshold, 247.5 + dynamic_threshold), # 左下
            (247.5 + dynamic_threshold, 292.5 + dynamic_threshold), # 下
            (292.5 + dynamic_threshold, 337.5 - dynamic_threshold)  # 右下
        ]
        
        # 寻找最匹配的方向
        best_match = 0
        min_diff = 360
        for i in range(8):
            # 计算角度差
            center_angle = i * 45
            diff = min(abs(angle - center_angle), 360 - abs(angle - center_angle))
            
            # 考虑向量长度权重（长向量优先）
            weighted_diff = diff * (1 - math.log1p(magnitude)/10)
            if weighted_diff < min_diff:
                min_diff = weighted_diff
                best_match = i
                
        return self.DIRECTION_MAP[best_match]

    def _direction_to_vector(self, direction: str) -> np.ndarray:
        """方向转单位向量"""
        index = self.DIRECTION_MAP.index(direction)
        angle = math.radians(index * 45)
        return np.array([math.cos(angle), -math.sin(angle)])

    def _direction_diff(self, dir1: str, dir2: str) -> int:
        """计算两个方向的最小角度差"""
        idx1 = self.DIRECTION_MAP.index(dir1)
        idx2 = self.DIRECTION_MAP.index(dir2)
        return min(abs(idx1 - idx2), 8 - abs(idx1 - idx2)) * 45

if __name__ == "__main__":
    print("请通过主程序运行。")