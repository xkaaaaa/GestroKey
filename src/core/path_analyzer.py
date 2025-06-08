import math
import sys
import os

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger


class PathAnalyzer:
    """路径分析器，用于格式化路径和计算相似度"""
    
    def __init__(self):
        self.logger = get_logger("PathAnalyzer")
    
    def format_raw_path(self, raw_points):
        """将原始绘制点转换为格式化路径
        
        Args:
            raw_points: 原始点列表，每个点为(x, y, pressure, time, stroke_id)的元组
            
        Returns:
            dict: 格式化的路径 {'points': [(x,y)], 'connections': [{'from': i, 'to': j, 'type': 'line'}]}
        """
        if len(raw_points) < 2:
            return {'points': [], 'connections': []}
        
        # 提取坐标
        coords = [(int(p[0]), int(p[1])) for p in raw_points]
        
        # 简化路径，提取关键点
        key_points = self._extract_key_points(coords)
        
        # 生成连接信息（默认都是直线连接）
        connections = []
        for i in range(len(key_points) - 1):
            connections.append({
                'from': i,
                'to': i + 1,
                'type': 'line'
            })
        
        return {
            'points': key_points,
            'connections': connections
        }
    
    def _extract_key_points(self, coords):
        """提取关键点"""
        if len(coords) <= 2:
            return coords
        
        key_points = [coords[0]]  # 起点
        
        i = 0
        while i < len(coords) - 1:
            line_end = self._find_line_segment(coords, i)
            if line_end > i + 2:
                # 找到直线段，添加终点
                if coords[line_end] not in key_points:
                    key_points.append(coords[line_end])
                i = line_end
            else:
                # 没找到长直线，跳过一些点
                i += max(1, len(coords) // 10)  # 动态步长
                if i < len(coords):
                    if coords[i] not in key_points:
                        key_points.append(coords[i])
        
        # 确保终点被包含
        if len(key_points) == 0 or key_points[-1] != coords[-1]:
            key_points.append(coords[-1])
        
        # 去除重复点
        unique_points = []
        for point in key_points:
            if not unique_points or (point[0] != unique_points[-1][0] or point[1] != unique_points[-1][1]):
                unique_points.append(point)
        
        return unique_points
    
    def _find_line_segment(self, points, start_idx):
        """寻找从起始点开始的最长直线段"""
        if start_idx >= len(points) - 2:
            return start_idx
        
        threshold = 8.0  # 偏离直线的阈值
        end_idx = start_idx + 1
        
        for i in range(start_idx + 2, len(points)):
            # 检查点是否在直线上
            if self._distance_to_line(points[start_idx], points[i], points[end_idx]) < threshold:
                end_idx = i
            else:
                break
        
        return end_idx if end_idx > start_idx + 3 else start_idx
    
    def _distance_to_line(self, p1, p2, point):
        """计算点到直线的距离"""
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        x0, y0 = point[0], point[1]
        
        # 直线长度
        line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if line_length == 0:
            return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
        
        # 点到直线距离
        distance = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / line_length
        return distance
    
    def calculate_similarity(self, path1, path2):
        """计算两个路径的相似度
        
        Args:
            path1: 第一个路径 {'points': [...], 'connections': [...]}
            path2: 第二个路径 {'points': [...], 'connections': [...]}
            
        Returns:
            float: 相似度 (0.0 到 1.0)
        """
        if not path1 or not path2:
            return 0.0
        
        # 提取点和连接
        points1 = path1.get('points', [])
        points2 = path2.get('points', [])
        connections1 = path1.get('connections', [])
        connections2 = path2.get('connections', [])
        
        if not points1 or not points2:
            return 0.0
        
        score = 0.0
        total_weight = 0.0
        
        # 1. 段数相似度 (20%权重)
        seg_count_diff = abs(len(connections1) - len(connections2))
        max_segments = max(len(connections1), len(connections2))
        if max_segments > 0:
            seg_similarity = max(0, 1 - (seg_count_diff / max_segments) * 2)  # 更严格的惩罚
            score += seg_similarity * 0.2
            total_weight += 0.2
        
        # 2. 路径类型序列相似度 (30%权重)
        type_similarity = self._compare_path_types(connections1, connections2)
        score += type_similarity * 0.3
        total_weight += 0.3
        
        # 3. 形状相似度 (25%权重)
        shape_similarity = self._compare_detailed_shape(points1, points2)
        score += shape_similarity * 0.25
        total_weight += 0.25
        
        # 4. 路径方向相似度 (25%权重)
        direction_similarity = self._compare_path_directions(points1, points2)
        score += direction_similarity * 0.25
        total_weight += 0.25
        
        final_score = score / total_weight if total_weight > 0 else 0.0
        
        # 应用非线性变换，让差异更明显
        final_score = final_score ** 1.5  # 让低分更低，高分相对保持
        
        return final_score
    
    def _compare_path_types(self, connections1, connections2):
        """比较路径类型序列的相似度"""
        types1 = [conn.get('type', 'line') for conn in connections1]
        types2 = [conn.get('type', 'line') for conn in connections2]
        
        # 使用编辑距离算法
        max_len = max(len(types1), len(types2), 1)
        edit_dist = self._edit_distance(types1, types2)
        return max(0, 1 - (edit_dist / max_len))
    
    def _edit_distance(self, seq1, seq2):
        """计算编辑距离"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        return dp[m][n]
    
    def _compare_detailed_shape(self, points1, points2):
        """详细的形状比较"""
        bbox1 = self._get_path_bbox(points1)
        bbox2 = self._get_path_bbox(points2)
        
        if not bbox1 or not bbox2:
            return 0.0
        
        # 比较宽高比
        ratio1 = bbox1['width'] / max(bbox1['height'], 1)
        ratio2 = bbox2['width'] / max(bbox2['height'], 1)
        ratio_diff = abs(ratio1 - ratio2) / max(ratio1, ratio2, 0.1)
        ratio_similarity = max(0, 1 - ratio_diff)
        
        # 比较相对大小
        area1 = bbox1['width'] * bbox1['height']
        area2 = bbox2['width'] * bbox2['height']
        if area1 > 0 and area2 > 0:
            size_ratio = min(area1, area2) / max(area1, area2)
        else:
            size_ratio = 0
        
        return (ratio_similarity * 0.7 + size_ratio * 0.3)
    
    def _compare_path_directions(self, points1, points2):
        """比较路径的整体方向趋势"""
        dir1 = self._get_path_direction_vector(points1)
        dir2 = self._get_path_direction_vector(points2)
        
        if not dir1 or not dir2:
            return 0.5
        
        # 计算方向向量的余弦相似度
        dot_product = dir1[0] * dir2[0] + dir1[1] * dir2[1]
        magnitude1 = math.sqrt(dir1[0]**2 + dir1[1]**2)
        magnitude2 = math.sqrt(dir2[0]**2 + dir2[1]**2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.5
        
        cosine_similarity = dot_product / (magnitude1 * magnitude2)
        return (cosine_similarity + 1) / 2  # 转换到[0,1]范围
    
    def _get_path_direction_vector(self, points):
        """获取路径的整体方向向量"""
        if len(points) < 2:
            return None
        
        start_point = points[0]
        end_point = points[-1]
        
        return (end_point[0] - start_point[0], end_point[1] - start_point[1])
    
    def _get_path_bbox(self, points):
        """获取路径的边界框"""
        if not points:
            return None
        
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        
        return {
            'min_x': min(xs), 'max_x': max(xs),
            'min_y': min(ys), 'max_y': max(ys),
            'width': max(xs) - min(xs),
            'height': max(ys) - min(ys)
        }
    
    def normalize_path_scale(self, path, target_size=100):
        """将路径归一化到指定尺寸，用于提高相似度比较的准确性
        
        Args:
            path: 路径字典
            target_size: 目标尺寸
            
        Returns:
            dict: 归一化后的路径
        """
        points = path.get('points', [])
        if not points:
            return path
        
        # 获取边界框
        bbox = self._get_path_bbox(points)
        if not bbox or (bbox['width'] == 0 and bbox['height'] == 0):
            return path
        
        # 计算缩放比例
        scale = target_size / max(bbox['width'], bbox['height'])
        
        # 缩放所有点
        normalized_points = []
        for point in points:
            new_x = int((point[0] - bbox['min_x']) * scale)
            new_y = int((point[1] - bbox['min_y']) * scale)
            normalized_points.append([new_x, new_y])
        
        # 返回归一化的路径
        return {
            'points': normalized_points,
            'connections': path.get('connections', [])
        } 