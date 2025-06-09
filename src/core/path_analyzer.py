import math
import sys
import os
from typing import List, Tuple, Dict  # 确保所有需要的类型都被导入

import numpy as np
from numpy.linalg import svd, norm

try:
    from core.logger import get_logger
except ImportError:
    # 兼容性：如果直接运行此文件或在不同结构中，确保能找到logger
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.logger import get_logger


class PathAnalyzer:
    """
    路径分析器，用于格式化原始鼠标/触摸板绘制路径，并计算路径间的相似度。
    相似度计算主要关注两大核心要素：
      1. 形状轮廓 (Shape): 路径在视觉上的几何形态。
      2. 笔画顺序 (Stroke Order): 路径的绘制方向和顺序。
    """
    
    def __init__(self):
        self.logger = get_logger("PathAnalyzer")
    
    # ===================== 路径格式化与关键点提取 ===================== #

    def format_raw_path(self, raw_points: List[Tuple]) -> Dict:
        """
        将原始绘制点列表转换为格式化的路径字典。
        流程: 缩放 -> 简化 -> 提取关键点 -> 生成连接。
        """
        if len(raw_points) < 2:
            return {'points': [], 'connections': []}
        
        coords = [(int(p[0]), int(p[1])) for p in raw_points]
        scaled_coords = self._scale_small_path(coords)
        key_points = self._extract_key_points(scaled_coords)
        
        connections = [
            {'from': i, 'to': i + 1, 'type': 'line'}
            for i in range(len(key_points) - 1)
        ]

        return {'points': key_points, 'connections': connections}

    def _scale_small_path(self, coords: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """对尺寸过小的路径进行等比放大，以提高后续处理的精度。"""
        if len(coords) < 2:
            return coords
            
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        path_width = max_x - min_x
        path_height = max_y - min_y
        current_size = max(path_width, path_height)
        
        min_size_threshold = 50
        target_size = 200
        
        if 0 < current_size < min_size_threshold:
            scale_factor = target_size / current_size
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            scaled_coords = [
                (
                    int(center_x + (x - center_x) * scale_factor),
                    int(center_y + (y - center_y) * scale_factor)
                )
                for x, y in coords
            ]
            self.logger.info(f"路径预处理缩放：从 {current_size:.1f}px 放大至 {target_size:.1f}px。")
            return scaled_coords
        
            return coords
    
    def _extract_key_points(self, coords: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """从坐标点中智能提取关键点，保留路径的核心特征。"""
        if len(coords) <= 2:
            return coords
        
        # 1. 初步简化
        simplified = self._douglas_peucker(coords, tolerance=8.0)
        # 2. 细化分析，保留重要转角和特征点
        key_points = self._analyze_direction_changes(simplified)
        
        # 3. 确保起点和终点始终存在
        if not key_points or key_points[0] != coords[0]:
            key_points.insert(0, coords[0])
        if key_points[-1] != coords[-1]:
            key_points.append(coords[-1])
        
        # 4. 去除连续的重复点
        unique_points = [key_points[0]]
        for point in key_points[1:]:
            if point != unique_points[-1]:
                unique_points.append(point)
        
        return unique_points
    
    def _douglas_peucker(self, points: List[Tuple[int, int]], tolerance: float) -> List[Tuple[int, int]]:
        """使用道格拉斯-普克算法简化路径。"""
        if len(points) <= 2:
            return points
            
        dmax, index = 0, 0
        end = len(points) - 1
        for i in range(1, end):
            d = self._distance_to_line(points[0], points[end], points[i])
            if d > dmax:
                index, dmax = i, d
        
        if dmax > tolerance:
            rec1 = self._douglas_peucker(points[:index + 1], tolerance)
            rec2 = self._douglas_peucker(points[index:], tolerance)
            return rec1[:-1] + rec2
        else:
            return [points[0], points[end]]

    def _analyze_direction_changes(self, points: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """通过分析角度和距离变化，识别重要的转折点。"""
        if len(points) <= 2:
            return points
        
        key_points = [points[0]]
        path_length = self._calculate_path_length(points)
        min_distance_threshold = max(path_length * 0.1, 20)
        
        for i in range(1, len(points) - 1):
            angle_change = self._calculate_angle_change(points[i - 1], points[i], points[i + 1])
            distance_from_last_key = math.dist(points[i], key_points[-1])
            
            # 保留点位的条件：显著的角度变化 或 与上一个关键点距离足够远
            if abs(angle_change) > 30 or distance_from_last_key > min_distance_threshold:
                    key_points.append(points[i])
        
        key_points.append(points[-1])
        return key_points
    
    # ====================== 相似度核心实现 ====================== #

    def calculate_similarity(self, path1: Dict, path2: Dict) -> float:
        """
        计算两条格式化路径的相似度，结果范围 [0, 1]，值越大越相似。
        """
        # 1. 安全检查
        if not all([path1, path2, path1.get("points", []), path2.get("points", [])]) or \
           len(path1["points"]) < 2 or len(path2["points"]) < 2:
            return 0.0
        
        # 2. 预处理：归一化与重采样
        try:
            pts1 = self._preprocess_for_comparison(path1)
            pts2 = self._preprocess_for_comparison(path2)
        except (ValueError, IndexError) as e:
            self.logger.error(f"路径预处理失败: {e}")
            return 0.0

        if pts1 is None or pts2 is None:
            return 0.0
        
        # 3. 正向比较
        shape_fwd, dir_fwd = self._compute_scores(pts1, pts2)
        # 权重调整：更平衡形状和方向，以体现笔顺的重要性
        sim_forward = 0.55 * shape_fwd + 0.45 * dir_fwd

        # 4. 反向比较 (处理反向绘制但形状相同的情况)
        pts2_rev = np.flipud(pts2)
        shape_rev, dir_rev = self._compute_scores(pts1, pts2_rev)
        sim_reverse_raw = 0.55 * shape_rev + 0.45 * dir_rev
        # 惩罚加重：对反向绘制给予更严厉的惩罚，因为笔顺是手势的关键
        REVERSE_PENALTY = 0.25
        sim_reverse = sim_reverse_raw * REVERSE_PENALTY

        # 5. 最终得分
        final_sim = max(sim_forward, sim_reverse)
        final_sim = np.clip(final_sim, 0.0, 1.0)

        # 6. 调试日志 (只记录有意义的匹配)
        if final_sim > 0.1:
            match_type = "Forward" if abs(final_sim - sim_forward) < 1e-6 else "Reverse (Penalized)"
            shape, direction = (shape_fwd, dir_fwd) if match_type == "Forward" else (shape_rev, dir_rev)
            self.logger.debug(
                f"[Similarity] Match: {match_type}. Score: {final_sim:.3f} "
                f"(Shape: {shape:.3f}, Dir: {direction:.3f})"
            )
            
        return float(final_sim)

    # ====================== 相似度计算的内部辅助函数 ====================== #

    def _preprocess_for_comparison(self, path: Dict, target_size: int = 200, resample_n: int = 64) -> np.ndarray | None:
        """为相似度计算准备路径：归一化 + 重采样。"""
        # 归一化
        norm_path = self.normalize_path_scale(path, target_size)
        points = np.array(norm_path["points"], dtype=float)
        if points.shape[0] < 2:
            return None
        # 重采样
        return self._resample_points(points, resample_n)

    def _resample_points(self, pts: np.ndarray, target_n: int) -> np.ndarray:
        """沿曲线总长度等距采样 target_n 个点。"""
        distances = np.cumsum(np.sqrt(np.sum(np.diff(pts, axis=0)**2, axis=1)))
        distances = np.insert(distances, 0, 0)
        
        if distances[-1] == 0:  # 路径所有点重合
            return np.repeat(pts[:1], target_n, axis=0)

        # 使用np.interp进行高效插值
        regular_distances = np.linspace(0, distances[-1], target_n)
        resampled_x = np.interp(regular_distances, distances, pts[:, 0])
        resampled_y = np.interp(regular_distances, distances, pts[:, 1])
        
        return np.vstack((resampled_x, resampled_y)).T

    def _compute_scores(self, pts1: np.ndarray, pts2: np.ndarray) -> Tuple[float, float]:
        """计算两条点集的形状得分和方向得分。"""
        # 形状得分 (Shape Score)
        aligned_pts1 = self._procrustes_align(pts1, pts2)
        shape_dist = np.mean(norm(aligned_pts1 - pts2, axis=1))
        # 放宽标准：增大边界值，使得对微小形状偏差更宽容，尤其对复杂路径有益
        shape_scale_boundary = 175.0
        shape_score = max(0.0, 1.0 - shape_dist / shape_scale_boundary)

        # 方向得分 (Direction Score)
        vec1 = np.diff(aligned_pts1, axis=0)
        vec2 = np.diff(pts2, axis=0)
        
        norm_vec1 = vec1 / (norm(vec1, axis=1, keepdims=True) + 1e-9)
        norm_vec2 = vec2 / (norm(vec2, axis=1, keepdims=True) + 1e-9)
        
        cosines = np.sum(norm_vec1 * norm_vec2, axis=1)
        direction_score = np.mean(np.clip((cosines + 1) / 2, 0, 1))

        return shape_score, direction_score

    def _procrustes_align(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """通过旋转和平移将点集A对齐到点集B (Orthogonal Procrustes problem)。"""
        A_centered = A - A.mean(axis=0)
        B_centered = B - B.mean(axis=0)

        # 计算协方差矩阵
        C = A_centered.T @ B_centered
        # SVD分解
        U, _, Vt = svd(C)
        # 计算最佳旋转矩阵R
        R = Vt.T @ U.T

        # 保证R是旋转矩阵而非反射矩阵 (det(R) = 1)
        if np.linalg.det(R) < 0:
            Vt[-1, :] *= -1
            R = Vt.T @ U.T

        # 应用旋转并移回B的中心
        return A_centered @ R + B.mean(axis=0)

    # ====================== 通用工具函数 ====================== #

    def normalize_path_scale(self, path: Dict, target_size: int = 100) -> Dict:
        """将路径归一化到指定的边界框尺寸。"""
        points = path.get('points', [])
        if len(points) < 2:
            return path
        
        bbox = self._get_path_bbox(points)
        max_dim = max(bbox['width'], bbox['height'])
        if max_dim == 0:
            return path
        
        scale = target_size / max_dim
        
        normalized_points = [
            [
                (p[0] - bbox['min_x']) * scale,
                (p[1] - bbox['min_y']) * scale
            ] for p in points
        ]
        
        return {'points': normalized_points, 'connections': path.get('connections', [])}

    def _get_path_bbox(self, points: List[Tuple]) -> Dict:
        """计算路径的边界框。"""
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return {
            'min_x': min_x, 'max_x': max_x,
            'min_y': min_y, 'max_y': max_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }
    
    def _calculate_path_length(self, points: List[Tuple[int, int]]) -> float:
        """计算路径的总长度。"""
        return sum(math.dist(points[i], points[i+1]) for i in range(len(points) - 1))

    def _calculate_angle_change(self, p1: Tuple, p2: Tuple, p3: Tuple) -> float:
        """计算三点构成的夹角变化。"""
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        
        return math.degrees(math.atan2(cross_product, dot_product))
    
    def _distance_to_line(self, p1: Tuple, p2: Tuple, point: Tuple) -> float:
        """计算一个点到由另外两点确定的线段的距离。"""
        x1, y1 = p1
        x2, y2 = p2
        x0, y0 = point
        
        line_len_sq = (x2 - x1)**2 + (y2 - y1)**2
        if line_len_sq == 0:
            return math.dist(p1, point)
        
        t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_len_sq))
        projection_x = x1 + t * (x2 - x1)
        projection_y = y1 + t * (y2 - y1)
        
        return math.dist(point, (projection_x, projection_y))