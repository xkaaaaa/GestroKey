"""
画笔模块

包含绘制、消失和其他画笔相关功能
"""

from .drawing import DrawingModule, PencilBrush, WaterBrush
from .fading import FadingModule
from .overlay import TransparentDrawingOverlay
from .manager import DrawingManager

__all__ = [
    'DrawingModule',
    'PencilBrush', 
    'WaterBrush',
    'FadingModule',
    'TransparentDrawingOverlay',
    'DrawingManager'
] 