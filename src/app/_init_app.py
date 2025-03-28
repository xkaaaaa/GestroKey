"""
应用程序初始化模块
用于预加载和初始化常用组件，提高后续响应速度
"""

import os
import sys
import time
import threading

try:
    from .log import log, setup_logger
    from .operation_executor import _initialize_process_pool
except ImportError:
    from log import log, setup_logger
    from operation_executor import _initialize_process_pool

# 全局初始化标志
_APP_INITIALIZED = False

def preload_modules():
    """预加载常用模块，减少首次使用时的延迟"""
    try:
        # 预加载库，避免首次导入延迟
        import numpy
        import pyautogui
        import base64
        import json
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QTimer
        
        log.info("预加载常用模块完成")
        return True
    except Exception as e:
        log.error(f"预加载模块失败: {e}")
        return False

def initialize_app(async_init=True):
    """初始化应用程序
    
    Args:
        async_init: 是否异步初始化
    """
    global _APP_INITIALIZED
    
    if _APP_INITIALIZED:
        return True
    
    if async_init:
        # 异步初始化
        threading.Thread(target=_do_initialize, daemon=True).start()
        return True
    else:
        # 同步初始化
        return _do_initialize()

def _do_initialize():
    """执行实际的初始化过程"""
    global _APP_INITIALIZED
    
    try:
        start_time = time.time()
        
        # 设置日志
        setup_logger()
        log.info("开始初始化应用程序组件...")
        
        # 预加载模块
        preload_modules()
        
        # 初始化操作执行器进程池
        _initialize_process_pool()
        
        # 预加载配置文件
        try:
            from .gesture_parser import GestureParser
            # 预加载配置和手势库
            GestureParser.load_config_params()
            GestureParser.load_gesture_lib()
            log.info("预加载配置和手势库完成")
        except Exception as e:
            log.error(f"预加载配置文件失败: {e}")
        
        # 标记为已初始化
        _APP_INITIALIZED = True
        
        elapsed = time.time() - start_time
        log.info(f"应用程序组件初始化完成，用时: {elapsed:.2f}秒")
        return True
    except Exception as e:
        log.error(f"初始化应用程序组件失败: {e}")
        return False

if __name__ == "__main__":
    print("应用程序初始化模块")
    initialize_app(async_init=False)
    print("初始化完成") 