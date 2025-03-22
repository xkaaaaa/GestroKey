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
    
    # 箭头符号转方向映射表
    ARROW_TO_DIRECTION = {
        '→': '右',
        '↗': '右上',
        '↑': '上',
        '↖': '左上',
        '←': '左',
        '↙': '左下',
        '↓': '下',
        '↘': '右下'
    }
    
    # 方向文本转箭头符号映射表
    DIRECTION_TO_ARROW = {
        '右': '→',
        '右上': '↗',
        '上': '↑',
        '左上': '↖',
        '左': '←',
        '左下': '↙',
        '下': '↓',
        '右下': '↘'
    }
    
    def __init__(self, trail_points: List[tuple], 
                 config_path: str = None, 
                 gestures_path: str = None):
        """
        初始化手势解析器
        :param trail_points: 轨迹点列表
        :param config_path: 配置文件路径
        :param gestures_path: 手势库文件路径
        """
        self.trail = trail_points
        
        # 如果没有指定路径，使用默认路径
        if config_path is None:
            config_path = os.path.expanduser("~/.gestrokey/settings.json")
        
        if gestures_path is None:
            gestures_path = os.path.expanduser("~/.gestrokey/gestures.json")
            
        self.config_path = config_path
        self.gestures_path = gestures_path
        
        self.min_points = 5           # 最小识别点数
        self.step_base = 3            # 动态步长基数
        self.merge_threshold = 25     # 合并阈值(px)
        self.noise_threshold = 15     # 噪音阈值(px)
        self.file_name = 'gesture_parser'
        
        # 记录文件修改时间
        self.config_mtime = 0
        self.gestures_mtime = 0

        log.info(f"{self.file_name} - 初始化解析器，轨迹点数: {len(trail_points)}，配置文件: {self.config_path}，手势库: {self.gestures_path}")
        # 加载手势库
        self.gesture_lib = self._load_gesture_lib()

    def parse(self) -> Optional[str]:
        """
        主解析流程
        :return: Base64编码的操作指令或None
        """
        # 检查文件是否有变化，有则重新加载
        self._check_file_changes()
        
        log.info(f"{self.file_name} - 开始解析手势...")
        if len(self.trail) < self.min_points:
            log.info(f"{self.file_name} - 轨迹点不足，需要至少{self.min_points}个点")
            return None
            
        # 核心处理流程
        raw_segments = self._parse_raw_strokes()
        optimized = self._optimize_strokes(raw_segments)
        result = self._match_gesture(optimized)
        log.info(f"{self.file_name} - 解析完成，结果: {result}")
        return result

    def _check_file_changes(self):
        """检查配置文件和手势库文件是否有更新"""
        try:
            # 检查配置文件
            if os.path.exists(self.config_path):
                current_config_mtime = os.path.getmtime(self.config_path)
                if current_config_mtime > self.config_mtime:
                    log.info(f"{self.file_name} - 检测到配置文件更新，重新加载")
                    self.config_mtime = current_config_mtime
                    self._reload_config()
            
            # 检查手势库文件
            if os.path.exists(self.gestures_path):
                current_gestures_mtime = os.path.getmtime(self.gestures_path)
                if current_gestures_mtime > self.gestures_mtime:
                    log.info(f"{self.file_name} - 检测到手势库文件更新，重新加载")
                    self.gestures_mtime = current_gestures_mtime
                    self.gesture_lib = self._load_gesture_lib()
        except Exception as e:
            log.error(f"{self.file_name} - 检查文件变化时出错: {str(e)}")

    def _reload_config(self):
        """重新加载配置文件中的相关设置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 从配置中更新相关参数
            if 'gesture_settings' in config:
                gs = config['gesture_settings']
                if 'min_points' in gs:
                    self.min_points = gs['min_points']
                if 'step_base' in gs:
                    self.step_base = gs['step_base']
                if 'merge_threshold' in gs:
                    self.merge_threshold = gs['merge_threshold']
                if 'noise_threshold' in gs:
                    self.noise_threshold = gs['noise_threshold']
                
                log.info(f"{self.file_name} - 已更新配置参数: min_points={self.min_points}, step_base={self.step_base}, merge_threshold={self.merge_threshold}, noise_threshold={self.noise_threshold}")
        except Exception as e:
            log.error(f"{self.file_name} - 重新加载配置时出错: {str(e)}")

    def _parse_raw_strokes(self) -> List[Dict]:
        """
        原始笔画分割算法
        :return: 未优化的笔画序列 [{'方向':str, '长度':float}, ...]
        """
        log.info(f"{self.file_name} - 开始原始笔画分割...")
        if len(self.trail) < 2:
            log.info(f"{self.file_name} - 轨迹点不足，无法分割")
            return []

        # 动态计算采样步长
        step = max(self.step_base, len(self.trail)//20)
        log.info(f"{self.file_name} - 计算采样步长: {step}")
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
                    log.info(f"{self.file_name} - 过滤微小移动: {vector}")
                    continue
                
            new_dir = self._vector_to_direction(vector)
            
            # 方向变化检测
            if current_dir:
                if self._direction_diff(current_dir, new_dir) > 45:
                    log.info(f"{self.file_name} - 检测到方向变化: {current_dir} -> {new_dir}")
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
            log.info(f"{self.file_name} - 添加最后一段: {current_dir}")
            segments.append({
                '方向': current_dir,
                '长度': np.linalg.norm(accum_vector)
            })
            
        log.info(f"{self.file_name} - 分割完成，共得到{len(segments)}段笔画")
        return segments

    def _optimize_strokes(self, segments: List[Dict]) -> List[str]:
        """
        优化笔画序列
        :param segments: 原始笔画数据
        :return: 优化后的方向序列 [方向1, 方向2, ...]
        """
        log.info(f"{self.file_name} - 开始优化笔画序列...")
        if not segments:
            log.info(f"{self.file_name} - 无有效笔画数据")
            return []
        
        # 第一步：合并短笔画
        length_median = np.median([s['长度'] for s in segments])
        log.info(f"{self.file_name} - 计算笔画长度中位数: {length_median}")
        merged = []
        temp = segments[0]
        
        for seg in segments[1:]:
            if temp['长度'] < self.merge_threshold and \
            self._direction_diff(temp['方向'], seg['方向']) < 90:
                log.info(f"{self.file_name} - 合并短笔画: {temp['方向']} + {seg['方向']}")
                temp['长度'] += seg['长度']
                temp['方向'] = self._vector_to_direction(
                    self._direction_to_vector(temp['方向']) * temp['长度'] +
                    self._direction_to_vector(seg['方向']) * seg['长度']
                )
            else:
                merged.append(temp)
                temp = seg
        merged.append(temp)
        log.info(f"{self.file_name} - 合并后剩余笔画数: {len(merged)}")
        
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
            log.info(f"{self.file_name} - 首尾强化后方向序列: {simplified}")

        log.info(f"{self.file_name} - 优化完成，最终方向序列: {simplified}")
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
        :param directions: 优化后的方向序列（箭头符号）
        :return: 匹配的操作指令或None
        """
        log.info(f"{self.file_name} - 开始手势匹配，输入方向序列: {directions}")
        
        # 确保输入的方向序列是标准化的（都是箭头符号）
        std_directions = []
        for d in directions:
            if d in self.ARROW_TO_DIRECTION:
                # 已经是箭头符号
                std_directions.append(d)
            elif d in self.DIRECTION_TO_ARROW:
                # 是方向文本，转换为箭头符号
                std_directions.append(self.DIRECTION_TO_ARROW[d])
            else:
                # 未知格式，保持原样
                std_directions.append(d)
                
        log.info(f"{self.file_name} - 标准化后的输入方向序列: {std_directions}")
        
        for gesture in self.gesture_lib:
            log.info(f"{self.file_name} - 尝试匹配手势: {gesture['name']}, 方向: {gesture['directions']}")
            
            if len(std_directions) != len(gesture['directions']):
                log.info(f"{self.file_name} - 方向序列长度不匹配，跳过 {gesture['name']}")
                continue
                
            # 标准化手势方向序列
            std_gesture_dirs = []
            for d in gesture['directions']:
                if d in self.ARROW_TO_DIRECTION:
                    # 已经是箭头符号
                    std_gesture_dirs.append(d)
                elif d in self.DIRECTION_TO_ARROW:
                    # 是方向文本，转换为箭头符号
                    std_gesture_dirs.append(self.DIRECTION_TO_ARROW[d])
                else:
                    # 未知格式，保持原样
                    std_gesture_dirs.append(d)
                    
            log.info(f"{self.file_name} - 标准化后的手势方向序列: {std_gesture_dirs}")
                
            match = True
            for i, (d1, d2) in enumerate(zip(std_directions, std_gesture_dirs)):
                if d1 != d2:
                    log.info(f"{self.file_name} - 方向不匹配：位置 {i}, 输入 '{d1}' != 手势 '{d2}'")
                    match = False
                    break
            
            if match:
                log.info(f"{self.file_name} - 匹配到手势: {gesture['name']}")
                return gesture['action']
        
        log.info(f"{self.file_name} - 未匹配到任何手势")
        return None

    def _load_gesture_lib(self) -> List[Dict]:
        """从手势库文件加载手势库"""
        # 从设置文件获取基本配置
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 更新配置文件修改时间
            self.config_mtime = os.path.getmtime(self.config_path)
                
            # 加载应用设置，此处不涉及手势库
            # 如果需要从settings.json中加载某些设置，可以在这里处理
            
            # 从手势库文件加载手势
            try:
                with open(self.gestures_path, 'r', encoding='utf-8') as f:
                    gestures_data = json.load(f)
                
                # 更新手势库文件修改时间
                self.gestures_mtime = os.path.getmtime(self.gestures_path)
                
                gestures = []
                if 'gestures' in gestures_data:
                    for name, gesture in gestures_data['gestures'].items():
                        directions_str = gesture['directions']
                        directions_list = []
                        
                        # 检查directions是字符串还是列表
                        if isinstance(directions_str, str):
                            # 如果是单个字符串，不需要分割
                            directions_list = [directions_str]
                        else:
                            # 如果已经是列表，直接使用
                            directions_list = directions_str
                        
                        gestures.append({
                            'name': name,
                            'directions': directions_list,
                            'action': gesture['action']
                        })
                    
                    log.info(f"{self.file_name} - 成功加载手势库，共加载{len(gestures)}个手势")
                    return gestures
                else:
                    log.error(f"{self.file_name} - 手势库文件格式错误：缺少'gestures'键")
                    return []
                    
            except FileNotFoundError:
                log.error(f"{self.file_name} - 手势库文件未找到: {self.gestures_path}")
                return []
            except json.JSONDecodeError:
                log.error(f"{self.file_name} - 手势库文件格式错误: {self.gestures_path}")
                return []
            except Exception as e:
                log.error(f"{self.file_name} - 加载手势库时发生未知错误: {str(e)}")
                return []
            
        except FileNotFoundError:
            log.error(f"{self.file_name} - 配置文件未找到: {self.config_path}")
            return []
        except json.JSONDecodeError:
            log.error(f"{self.file_name} - 配置文件格式错误: {self.config_path}")
            return []
        except Exception as e:
            log.error(f"{self.file_name} - 加载配置时发生未知错误: {str(e)}")
            return []

    def _vector_to_direction(self, vector: np.ndarray) -> str:
        """向量转8方向"""
        # 计算向量模长
        magnitude = np.linalg.norm(vector)
        if magnitude < 1e-6:  # 防止零向量
            return "→"  # 默认返回右箭头
        
        # 计算精确角度（0-360度）
        angle = math.degrees(math.atan2(-vector[1], vector[0])) % 360
        
        # 动态阈值计算（基于向量长度）
        # 降低阈值以减少方向模糊的可能性
        dynamic_threshold = 20.0 * (1 + 1/(1 + magnitude/50))  # 长度越大阈值越小
        
        # 判断是否在对角线方向
        is_diagonal = False
        diagonal_angles = [45, 135, 225, 315]  # 对角线的标准角度
        for diag_angle in diagonal_angles:
            if abs(angle - diag_angle) < 15:  # 如果非常接近对角线
                is_diagonal = True
                break
        
        # 对角线方向应该更容易被识别
        if is_diagonal:
            dynamic_threshold *= 1.2  # 增加对角线方向的阈值
            
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
            # 对于对角线方向，增加其优先级
            weight_factor = 1.0
            if i % 2 == 1 and is_diagonal:  # 对角线方向的索引是奇数
                weight_factor = 0.8  # 降低加权差异，增加优先级
                
            weighted_diff = diff * (1 - math.log1p(magnitude)/10) * weight_factor
            if weighted_diff < min_diff:
                min_diff = weighted_diff
                best_match = i
        
        # 添加更详细的日志，帮助调试
        direction_text = self.DIRECTION_MAP[best_match]
        arrow = self.DIRECTION_TO_ARROW.get(direction_text, "→")
        log.info(f"{self.file_name} - 向量角度: {angle:.2f}°, 最佳匹配: {direction_text} ({arrow}), 是否对角线: {is_diagonal}")
        
        return arrow  # 直接返回箭头符号

    def _direction_to_vector(self, direction: str) -> np.ndarray:
        """方向转单位向量"""
        # 如果输入是箭头符号，先转换为方向文本
        if direction in self.ARROW_TO_DIRECTION:
            direction = self.ARROW_TO_DIRECTION[direction]
            
        index = self.DIRECTION_MAP.index(direction)
        angle = math.radians(index * 45)
        return np.array([math.cos(angle), -math.sin(angle)])

    def _direction_diff(self, dir1: str, dir2: str) -> int:
        """计算两个方向的最小角度差"""
        # 如果输入是箭头符号，先转换为方向文本
        if dir1 in self.ARROW_TO_DIRECTION:
            dir1 = self.ARROW_TO_DIRECTION[dir1]
        if dir2 in self.ARROW_TO_DIRECTION:
            dir2 = self.ARROW_TO_DIRECTION[dir2]
            
        idx1 = self.DIRECTION_MAP.index(dir1)
        idx2 = self.DIRECTION_MAP.index(dir2)
        return min(abs(idx1 - idx2), 8 - abs(idx1 - idx2)) * 45

if __name__ == "__main__":
    print("请通过主程序运行。")