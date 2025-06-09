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
        
        # 预处理：对小路径进行等比缩放
        scaled_coords = self._scale_small_path(coords)
        
        # 简化路径，提取关键点
        key_points = self._extract_key_points(scaled_coords)
        
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
    
    def _scale_small_path(self, coords):
        """对过小的路径进行等比缩放，提高格式化准确性
        
        Args:
            coords: 坐标点列表 [(x, y), ...]
            
        Returns:
            list: 缩放后的坐标点列表
        """
        if len(coords) < 2:
            return coords
            
        # 计算路径边界框
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        path_width = max_x - min_x
        path_height = max_y - min_y
        current_size = max(path_width, path_height)
        
        # 如果路径太小（小于50像素），等比放大到目标大小
        min_size_threshold = 50  # 最小尺寸阈值
        target_size = 200  # 目标尺寸
        
        if current_size < min_size_threshold and current_size > 0:
            scale_factor = target_size / current_size
            
            # 计算路径中心点
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            # 缩放所有点
            scaled_coords = []
            for x, y in coords:
                # 以中心点为基准进行缩放
                new_x = center_x + (x - center_x) * scale_factor
                new_y = center_y + (y - center_y) * scale_factor
                scaled_coords.append((int(new_x), int(new_y)))
            
            self.logger.info(f"路径预处理缩放：从{current_size:.1f}px 缩放到 {current_size*scale_factor:.1f}px (缩放因子: {scale_factor:.2f})")
            return scaled_coords
        else:
            # 路径大小合适，不需要缩放
            return coords
    
    def _extract_key_points(self, coords):
        """智能提取关键点，保留重要的转折点"""
        if len(coords) <= 2:
            return coords
        
        # 使用道格拉斯-普克算法进行初步简化
        simplified = self._douglas_peucker(coords, tolerance=8.0)
        
        # 再次分析以检测方向变化和重要特征
        key_points = self._analyze_direction_changes(simplified)
        
        # 确保至少有起点和终点
        if not key_points:
            key_points = [coords[0], coords[-1]]
        elif key_points[0] != coords[0]:
            key_points.insert(0, coords[0])
        if key_points[-1] != coords[-1]:
            key_points.append(coords[-1])
        
        # 去除重复点
        unique_points = []
        for point in key_points:
            if not unique_points or (point[0] != unique_points[-1][0] or point[1] != unique_points[-1][1]):
                unique_points.append(point)
        
        return unique_points
    
    def _douglas_peucker(self, points, tolerance):
        """道格拉斯-普克算法简化路径"""
        if len(points) <= 2:
            return points
            
        # 找到距离起点和终点连线最远的点
        dmax = 0
        index = 0
        end = len(points) - 1
        
        for i in range(1, end):
            d = self._distance_to_line(points[0], points[end], points[i])
            if d > dmax:
                index = i
                dmax = d
        
        # 如果最大距离大于容差，递归简化
        if dmax > tolerance:
            # 递归简化两段
            rec_results1 = self._douglas_peucker(points[:index + 1], tolerance)
            rec_results2 = self._douglas_peucker(points[index:], tolerance)
            
            # 合并结果（去除重复的中间点）
            result = rec_results1[:-1] + rec_results2
        else:
            # 所有点都在容差范围内，只保留起点和终点
            result = [points[0], points[end]]
            
        return result
    
    def _analyze_direction_changes(self, points):
        """分析方向变化，识别重要的转折点"""
        if len(points) <= 2:
            return points
        
        key_points = [points[0]]  # 起点
        
        for i in range(1, len(points) - 1):
            # 计算当前点的角度变化
            angle_change = self._calculate_angle_change(points[i-1], points[i], points[i+1])
            
            # 如果角度变化显著（大于30度），认为是重要转折点
            if abs(angle_change) > 30:
                key_points.append(points[i])
            # 或者如果距离上一个关键点较远，也保留
            elif len(key_points) > 0:
                distance = math.sqrt((points[i][0] - key_points[-1][0])**2 + 
                                   (points[i][1] - key_points[-1][1])**2)
                # 根据路径总长度动态调整距离阈值
                path_length = self._calculate_path_length(points)
                min_distance = max(path_length * 0.1, 20)  # 至少20像素或路径长度的10%
                
                if distance > min_distance:
                    key_points.append(points[i])
        
        key_points.append(points[-1])  # 终点
        return key_points
    
    def _calculate_angle_change(self, p1, p2, p3):
        """计算三点之间的角度变化（度数）"""
        # 计算两个向量
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # 计算向量长度
        len1 = math.sqrt(v1[0]**2 + v1[1]**2)
        len2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if len1 == 0 or len2 == 0:
            return 0
        
        # 计算夹角
        dot_product = v1[0]*v2[0] + v1[1]*v2[1]
        cross_product = v1[0]*v2[1] - v1[1]*v2[0]
        
        # 使用atan2计算角度，范围[-180, 180]
        angle = math.degrees(math.atan2(cross_product, dot_product))
        return angle
    
    def _calculate_path_length(self, points):
        """计算路径总长度"""
        total_length = 0
        for i in range(len(points) - 1):
            dx = points[i+1][0] - points[i][0]
            dy = points[i+1][1] - points[i][1]
            total_length += math.sqrt(dx*dx + dy*dy)
        return total_length
    
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
        
        # 1. 段数相似度 (10%权重)
        seg_count_diff = abs(len(connections1) - len(connections2))
        max_segments = max(len(connections1), len(connections2))
        if max_segments > 0:
            seg_similarity = max(0, 1 - (seg_count_diff / max_segments) * 2)
            score += seg_similarity * 0.10
            total_weight += 0.10
        
        # 2. 路径类型序列相似度 (15%权重)
        type_similarity = self._compare_path_types(connections1, connections2)
        score += type_similarity * 0.15
        total_weight += 0.15
        
        # 3. 路径顺序性相似度 (50%权重) - 大幅提高权重
        sequence_similarity = self._compare_path_sequence(points1, points2)
        score += sequence_similarity * 0.50
        total_weight += 0.50
        
        # 4. 形状相似度 (15%权重)
        shape_similarity = self._compare_detailed_shape(points1, points2)
        score += shape_similarity * 0.15
        total_weight += 0.15
        
        # 5. 路径方向相似度 (10%权重)
        direction_similarity = self._compare_path_directions(points1, points2)
        score += direction_similarity * 0.10
        total_weight += 0.10
        
        final_score = score / total_weight if total_weight > 0 else 0.0
        
        # 应用非线性变换，让差异更明显
        final_score = final_score ** 2.2  # 更严格的惩罚，让低分更低
        
        return final_score
    
    def _compare_path_types(self, connections1, connections2):
        """比较路径类型序列的相似度"""
        types1 = [conn.get('type', 'line') for conn in connections1]
        types2 = [conn.get('type', 'line') for conn in connections2]
        
        # 使用编辑距离算法
        max_len = max(len(types1), len(types2), 1)
        edit_dist = self._edit_distance(types1, types2)
        return max(0, 1 - (edit_dist / max_len))
    
    def _compare_path_sequence(self, points1, points2):
        """比较路径的顺序性相似度，确保绘制顺序和方向一致性
        
        Args:
            points1: 第一个路径的点列表
            points2: 第二个路径的点列表
            
        Returns:
            float: 顺序性相似度 (0.0 到 1.0)
        """
        if len(points1) < 2 or len(points2) < 2:
            return 0.5
        
        # 1. 计算正向匹配相似度
        forward_similarity = self._calculate_sequence_match(points1, points2)
        
        # 2. 计算反向匹配相似度（考虑路径可能被反向绘制）
        # 但是大幅降低权重，因为顺序在手势触发时坚决不可颠倒
        reversed_points2 = list(reversed(points2))
        backward_similarity = self._calculate_sequence_match(points1, reversed_points2)
        
        # 返回较高的相似度，但对反向匹配给予严格的惩罚
        # 反向匹配权重从0.8降低到0.1，确保顺序错误时相似度很低
        final_similarity = max(forward_similarity, backward_similarity * 0.1)
        
        return final_similarity
    
    def _calculate_sequence_match(self, points1, points2):
        """计算两个点序列的匹配度
        
        Args:
            points1: 第一个点序列
            points2: 第二个点序列
            
        Returns:
            float: 序列匹配度 (0.0 到 1.0)
        """
        # 将路径分割成相等数量的段进行比较
        segment_count = min(8, max(len(points1), len(points2)) // 2)  # 最多8段，最少根据点数确定
        
        if segment_count < 2:
            return 0.5
        
        # 获取路径段的方向向量
        vectors1 = self._get_path_segments(points1, segment_count)
        vectors2 = self._get_path_segments(points2, segment_count)
        
        if not vectors1 or not vectors2:
            return 0.5
        
        # 计算每个段的方向相似度
        similarities = []
        for i in range(min(len(vectors1), len(vectors2))):
            v1 = vectors1[i]
            v2 = vectors2[i]
            
            # 计算方向向量的余弦相似度
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            magnitude1 = math.sqrt(v1[0]**2 + v1[1]**2)
            magnitude2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if magnitude1 > 0 and magnitude2 > 0:
                cosine_similarity = dot_product / (magnitude1 * magnitude2)
                # 对方向差异进行更严格的惩罚
                if cosine_similarity > 0.5:  # 同向或接近同向
                    segment_similarity = (cosine_similarity + 1) / 2
                else:  # 反向或垂直方向，严重惩罚
                    segment_similarity = max(0, cosine_similarity * 0.2)
            else:
                segment_similarity = 0.1  # 零向量给予很低分数
            
            similarities.append(segment_similarity)
        
        # 计算加权平均，早期段权重更高（路径起始方向更重要）
        # 使用更陡峭的递减权重
        if similarities:
            weights = [1.0 - 0.2 * i for i in range(len(similarities))]  # 更快递减权重
            weights = [max(0.1, w) for w in weights]  # 确保最小权重为0.1
            weighted_sum = sum(sim * weight for sim, weight in zip(similarities, weights))
            weight_sum = sum(weights)
            return weighted_sum / weight_sum if weight_sum > 0 else 0.1
        
        return 0.1
    
    def _get_path_segments(self, points, segment_count):
        """将路径分割成指定数量的段，返回每段的方向向量
        
        Args:
            points: 点列表
            segment_count: 段数
            
        Returns:
            list: 方向向量列表，每个元素为(dx, dy)
        """
        if len(points) < 2 or segment_count < 1:
            return []
        
        segments = []
        step = len(points) / segment_count
        
        for i in range(segment_count):
            start_idx = int(i * step)
            end_idx = int((i + 1) * step)
            
            # 确保索引在有效范围内
            start_idx = min(start_idx, len(points) - 1)
            end_idx = min(end_idx, len(points) - 1)
            
            if start_idx >= end_idx:
                end_idx = min(start_idx + 1, len(points) - 1)
            
            if start_idx < end_idx:
                start_point = points[start_idx]
                end_point = points[end_idx]
                
                # 计算方向向量
                dx = end_point[0] - start_point[0]
                dy = end_point[1] - start_point[1]
                segments.append((dx, dy))
        
        return segments
    
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