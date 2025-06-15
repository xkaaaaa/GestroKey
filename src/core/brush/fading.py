"""
消失模块

处理画笔轨迹的淡出和消失效果
"""

import time
from qtpy.QtCore import QTimer, QObject, Signal
from qtpy.QtGui import QColor


class FadingModule(QObject):
    """消失效果模块"""
    
    # 信号
    fade_update = Signal()  # 淡出更新信号
    fade_complete = Signal()  # 淡出完成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 淡出参数
        self.fade_duration = 0.6  # 淡出持续时间（秒）
        self.fade_speed = 400  # 每秒淡出的透明度值
        self.fade_interval = 16  # 淡出更新间隔（毫秒，约60FPS）
        
        # 状态
        self.is_fading = False
        self.fade_alpha = 255  # 当前透明度
        self.last_fade_time = 0
        
        # 定时器
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self._update_fade)
        self.fade_timer.setInterval(self.fade_interval)
        
    def start_fade(self):
        """开始淡出效果"""
        if not self.is_fading:
            self.is_fading = True
            self.fade_alpha = 255
            self.last_fade_time = time.time()
            self.fade_timer.start()
            
    def stop_fade(self):
        """停止淡出效果"""
        if self.is_fading:
            self.is_fading = False
            self.fade_timer.stop()
            self.fade_alpha = 255
            
    def reset_fade(self):
        """重置淡出状态"""
        self.stop_fade()
        self.fade_alpha = 255
        
    def _update_fade(self):
        """更新淡出效果"""
        if not self.is_fading:
            return
            
        current_time = time.time()
        delta_time = current_time - self.last_fade_time
        self.last_fade_time = current_time
        
        # 计算透明度减少量
        fade_amount = self.fade_speed * delta_time
        self.fade_alpha = max(0, self.fade_alpha - fade_amount)
        
        # 发出更新信号
        self.fade_update.emit()
        
        # 检查是否完成淡出
        if self.fade_alpha <= 0:
            self.is_fading = False
            self.fade_timer.stop()
            self.fade_complete.emit()
            
    def get_fade_alpha(self):
        """获取当前淡出透明度"""
        return int(self.fade_alpha)
        
    def apply_fade_to_color(self, color):
        """将淡出效果应用到颜色"""
        if isinstance(color, QColor):
            faded_color = QColor(color)
            faded_color.setAlpha(int(self.fade_alpha))
            return faded_color
        return color
        
    def set_fade_duration(self, duration):
        """设置淡出持续时间"""
        if duration > 0:
            self.fade_duration = duration
            self.fade_speed = 255 / duration  # 重新计算淡出速度
            
    def set_fade_speed(self, speed):
        """设置淡出速度（每秒透明度变化量）"""
        if speed > 0:
            self.fade_speed = speed
            self.fade_duration = 255 / speed  # 重新计算持续时间 