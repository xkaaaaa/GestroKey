"""
应用程序初始化模块
用于预加载和初始化常用组件，提高后续响应速度
"""

import os
import sys
import time
import threading
import platform
import psutil

try:
    from .log import log, setup_logger
    from .operation_executor import _initialize_process_pool
except ImportError:
    from log import log, setup_logger
    from operation_executor import _initialize_process_pool

# 全局初始化标志
_APP_INITIALIZED = False
_DEBUG_MODE = False

def set_debug_mode(debug=False):
    """设置调试模式
    
    Args:
        debug: 是否启用调试模式
    """
    global _DEBUG_MODE
    _DEBUG_MODE = debug
    if debug:
        log.debug("应用初始化模块设置为调试模式")

def preload_modules():
    """预加载常用模块，减少首次使用时的延迟"""
    start_time = time.time()
    try:
        modules_to_load = [
            "numpy", 
            "pyautogui", 
            "base64", 
            "json",
            "PyQt5.QtWidgets",
            "PyQt5.QtCore",
            "PyQt5.QtGui"
        ]
        
        loaded_modules = []
        for module_name in modules_to_load:
            try:
                __import__(module_name)
                loaded_modules.append(module_name)
                if _DEBUG_MODE:
                    log.debug(f"已预加载模块: {module_name}")
            except ImportError as e:
                log.error(f"预加载模块 {module_name} 失败: {e}")
        
        elapsed = time.time() - start_time
        log.info(f"预加载常用模块完成，共加载 {len(loaded_modules)}/{len(modules_to_load)} 个模块，用时: {elapsed:.3f}秒")
        
        if _DEBUG_MODE:
            # 记录系统信息
            mem = psutil.virtual_memory()
            log.debug(f"系统信息: {platform.platform()}")
            log.debug(f"处理器: {platform.processor()}, {psutil.cpu_count()} 核心")
            log.debug(f"内存使用: {mem.percent}%, 可用内存: {mem.available / (1024*1024):.1f} MB")
            
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
        log.debug("应用程序已经初始化，跳过重复初始化")
        return True
    
    if async_init:
        # 异步初始化
        init_thread = threading.Thread(target=_do_initialize, daemon=True)
        init_thread.start()
        if _DEBUG_MODE:
            log.debug(f"启动异步初始化线程: {init_thread.name}")
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
        setup_logger(_DEBUG_MODE)
        log.info("开始初始化应用程序组件...")
        
        # 预加载模块
        preload_modules()
        
        # 初始化操作执行器进程池
        _initialize_process_pool()
        
        # 预加载配置文件
        try:
            from .gesture_parser import GestureParser
            # 预加载配置和手势库
            config_params = GestureParser.load_config_params()
            gesture_lib = GestureParser.load_gesture_lib()
            
            if _DEBUG_MODE:
                log.debug(f"预加载配置参数: {config_params}")
                log.debug(f"预加载手势库: {len(gesture_lib)} 个手势")
                
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
        if _DEBUG_MODE:
            import traceback
            log.debug(f"初始化失败详细信息: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("应用程序初始化模块")
    set_debug_mode(True)  # 启用调试模式进行测试
    initialize_app(async_init=False)
    print("初始化完成") 