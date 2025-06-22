import os
import sys
import time
from datetime import datetime, timedelta

import psutil
from qtpy.QtCore import QObject, QTimer, Signal

from core.logger import get_logger


class SystemMonitor(QObject):
    dataUpdated = Signal(dict)

    def __init__(self, update_interval=1000):
        super().__init__()
        self.logger = get_logger("SystemMonitor")

        self._update_interval = update_interval
        self._start_time = datetime.now()
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_data)
        self._running = False

        self._data = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_used": 0,
            "memory_total": 0,
            "runtime": "00:00:00",
            "process_memory": 0.0,
            "process_cpu": 0.0,
        }

        self._process = psutil.Process(os.getpid())

    def start(self):
        if not self._running:
            self._running = True
            self._timer.start(self._update_interval)
            return True
        return False

    def stop(self):
        if self._running:
            self._running = False
            self._timer.stop()
            return True
        return False

    def is_running(self):
        return self._running

    def get_data(self):
        return self._data.copy()

    def _update_data(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()

            process_memory = self._process.memory_percent()
            process_cpu = self._process.cpu_percent(interval=None) / psutil.cpu_count()

            runtime = datetime.now() - self._start_time
            runtime_str = str(runtime).split(".")[0]

            self._data.update({
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_total": memory.total,
                "runtime": runtime_str,
                "process_memory": process_memory,
                "process_cpu": process_cpu,
            })

            self.dataUpdated.emit(self._data)

        except Exception as e:
            self.logger.error(f"更新系统信息时发生错误: {e}")

    def set_update_interval(self, interval):
        self._update_interval = interval
        if self._running:
            self._timer.stop()
            self._timer.start(self._update_interval)

    def get_update_interval(self):
        return self._update_interval

    def reset_start_time(self):
        self._start_time = datetime.now()


def format_bytes(bytes_value):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"