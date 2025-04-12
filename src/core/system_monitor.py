import os
import sys
import time
import psutil
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

try:
    from core.logger import get_logger
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
    from core.logger import get_logger

class SystemMonitor(QObject):
    """系统监测器，提供CPU、内存使用情况和程序运行时间等信息"""
    
    # 自定义信号
    dataUpdated = pyqtSignal(dict)  # 数据更新时触发的信号
    
    def __init__(self, update_interval=1000):
        """
        初始化系统监测器
        
        参数:
            update_interval (int): 更新间隔，单位毫秒
        """
        super().__init__()
        self.logger = get_logger("SystemMonitor")
        self.logger.debug("初始化系统监测器")
        
        self._update_interval = update_interval
        self._start_time = datetime.now()
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_data)
        self._running = False
        
        # 初始化数据
        self._data = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_used": 0,
            "memory_total": 0,
            "runtime": "00:00:00",
            "process_memory": 0.0,
            "process_cpu": 0.0
        }
        
        # 获取当前进程
        self._process = psutil.Process(os.getpid())
        
        self.logger.debug("系统监测器初始化完成")
    
    def start(self):
        """开始监测系统信息"""
        if not self._running:
            self.logger.info("开始系统监测")
            self._running = True
            self._timer.start(self._update_interval)
            return True
        return False
    
    def stop(self):
        """停止监测系统信息"""
        if self._running:
            self.logger.info("停止系统监测")
            self._running = False
            self._timer.stop()
            return True
        return False
    
    def is_running(self):
        """返回监测器是否正在运行"""
        return self._running
    
    def get_data(self):
        """获取当前监测数据"""
        return self._data.copy()
    
    def _update_data(self):
        """更新系统信息数据"""
        try:
            # 获取CPU和内存数据
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            # 获取当前进程资源使用情况
            process_memory = self._process.memory_percent()
            process_cpu = self._process.cpu_percent(interval=None) / psutil.cpu_count()
            
            # 计算运行时间
            runtime = datetime.now() - self._start_time
            runtime_str = str(runtime).split('.')[0]  # 去除微秒部分
            
            # 更新数据字典
            self._data.update({
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_total": memory.total,
                "runtime": runtime_str,
                "process_memory": process_memory,
                "process_cpu": process_cpu
            })
            
            # 发送数据更新信号
            self.dataUpdated.emit(self._data)
            
        except Exception as e:
            self.logger.error(f"更新系统信息时发生错误: {e}")
    
    def set_update_interval(self, interval):
        """设置更新间隔，单位毫秒"""
        self._update_interval = interval
        if self._running:
            self._timer.stop()
            self._timer.start(self._update_interval)
        self.logger.debug(f"更新间隔已设置为 {interval} 毫秒")
    
    def get_update_interval(self):
        """获取当前更新间隔"""
        return self._update_interval
    
    def reset_start_time(self):
        """重置运行时间计时器"""
        self._start_time = datetime.now()
        self.logger.debug("运行时间计时器已重置")


# 辅助函数，用于格式化显示内存大小
def format_bytes(bytes_value):
    """将字节数转换为可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB" 