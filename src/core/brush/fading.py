import time
from qtpy.QtCore import QTimer, QObject, Signal


class FadingModule(QObject):
    """消失效果模块"""
    
    fade_update = Signal()
    fade_complete = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.fade_speed = 400
        self.fade_interval = 16
        
        self.is_fading = False
        self.fade_alpha = 255
        self.last_fade_time = 0
        
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self._update_fade)
        self.fade_timer.setInterval(self.fade_interval)
        
    def start_fade(self):
        if not self.is_fading:
            self.is_fading = True
            self.fade_alpha = 255
            self.last_fade_time = time.time()
            self.fade_timer.start()
            
    def stop_fade(self):
        if self.is_fading:
            self.is_fading = False
            self.fade_timer.stop()
            self.fade_alpha = 255
            
    def _update_fade(self):
        if not self.is_fading:
            return
            
        current_time = time.time()
        delta_time = current_time - self.last_fade_time
        self.last_fade_time = current_time
        
        fade_amount = self.fade_speed * delta_time
        self.fade_alpha = max(0, self.fade_alpha - fade_amount)
        
        self.fade_update.emit()
        
        if self.fade_alpha <= 0:
            self.is_fading = False
            self.fade_timer.stop()
            self.fade_complete.emit()
            
    def get_fade_alpha(self):
        return int(self.fade_alpha)