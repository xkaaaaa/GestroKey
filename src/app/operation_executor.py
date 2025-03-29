"""
操作执行模块
处理手势识别后的命令执行逻辑
使用多进程执行以避免阻塞主程序
"""

import os
import sys
import time
import base64
import pyautogui
import subprocess
import traceback
import multiprocessing
from multiprocessing import Process, Queue

try:
    from .log import log
except ImportError:
    from log import log

# 全局进程池，避免频繁创建和销毁进程
_process_pool = None
_max_pool_size = 3  # 最大进程池大小
_task_queue = None
_debug_mode = False  # 调试模式标志

def set_debug_mode(debug=False):
    """设置调试模式
    
    Args:
        debug: 是否开启调试模式
    """
    global _debug_mode
    _debug_mode = debug
    if debug:
        log.debug("操作执行器已设置为调试模式")

def _initialize_process_pool():
    """初始化进程池和任务队列"""
    global _process_pool, _task_queue
    if _process_pool is None:
        _process_pool = []
        _task_queue = Queue()
        # 启动工作进程
        for _ in range(_max_pool_size):
            p = Process(target=_worker_process, args=(_task_queue,))
            p.daemon = True
            p.start()
            _process_pool.append(p)
        log.info(f"初始化操作执行进程池完成，大小: {_max_pool_size}")
        if _debug_mode:
            log.debug(f"操作执行进程池详情: {_process_pool}")

def _worker_process(task_queue):
    """工作进程函数，从队列获取任务并执行"""
    while True:
        try:
            # 从队列获取任务
            action_string = task_queue.get()
            if action_string == "STOP":
                break
                
            # 设置安全执行环境
            pyautogui.FAILSAFE = False  # 防止鼠标移动到角落导致异常
            
            # 创建执行环境
            local_vars = {}
            global_vars = {
                'os': os,
                'sys': sys,
                'subprocess': subprocess,
                'pyautogui': pyautogui,
                'time': time,
            }
            
            # 执行代码
            exec(action_string, global_vars, local_vars)
        except Exception as e:
            error_msg = f"执行操作失败: {str(e)}\n详细错误: {traceback.format_exc()}"
            print(error_msg)
            # 将错误信息写入临时文件，以便主进程可以读取
            try:
                temp_dir = os.path.join(os.path.expanduser("~"), ".gestrokey", "temp")
                os.makedirs(temp_dir, exist_ok=True)
                with open(os.path.join(temp_dir, f"executor_error_{os.getpid()}.log"), "a") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}\n")
            except:
                pass

def _quick_parse_base64(action_code):
    """快速判断字符串是否为base64编码并解码
    
    Args:
        action_code: 可能的base64编码字符串
        
    Returns:
        解码后的字符串或原始字符串
    """
    # 快速检查是否可能是base64编码（长度是4的倍数且只包含合法字符）
    if len(action_code) % 4 == 0 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for c in action_code):
        try:
            return base64.b64decode(action_code).decode('utf-8')
        except:
            pass
    return action_code

def execute(action_code):
    """执行操作代码，支持已解码的代码和base64编码的代码
    使用进程池执行，避免频繁创建进程的开销
    
    Args:
        action_code: 操作代码，可以是已解码的字符串或base64编码的字符串
    
    Returns:
        是否成功提交执行任务
    """
    try:
        # 确保进程池已初始化
        if _process_pool is None:
            _initialize_process_pool()
        
        # 快速解析操作字符串
        if not isinstance(action_code, str):
            log.warning(f"操作代码类型异常: {type(action_code)}")
            return False
            
        # 快速解码base64（如果是的话）
        action_string = _quick_parse_base64(action_code)
        
        # 检查操作字符串的有效性
        if not action_string or len(action_string.strip()) == 0:
            return False
        
        # 记录调试信息
        if _debug_mode:
            log.debug(f"执行操作: {action_string[:100]}{'...' if len(action_string) > 100 else ''}")
        
        # 提交任务到队列
        _task_queue.put(action_string)
        
        return True
    except Exception as e:
        log.error(f"提交操作执行任务失败: {str(e)}")
        if _debug_mode:
            log.debug(f"详细错误: {traceback.format_exc()}")
        return False

def shutdown():
    """关闭进程池"""
    global _process_pool, _task_queue
    if _process_pool:
        # 记录关闭日志
        log.info("正在关闭操作执行进程池...")
        if _debug_mode:
            log.debug(f"关闭前进程池状态: {[(p.pid, p.is_alive()) for p in _process_pool]}")
        
        # 发送停止信号
        for _ in range(len(_process_pool)):
            _task_queue.put("STOP")
        
        # 等待进程结束
        for p in _process_pool:
            p.join(0.5)  # 等待最多0.5秒
            
        _process_pool = None
        _task_queue = None
        log.info("操作执行进程池已关闭")
    
if __name__ == "__main__":
    # 简单测试
    set_debug_mode(True)  # 开启调试模式
    
    def test():
        # 测试长时间操作
        print("开始测试长时间操作")
        execute("import time; print('开始睡眠10秒'); time.sleep(10); print('睡眠结束')")
        print("操作已提交，主程序继续运行")
        time.sleep(2)
        print("主程序仍然响应")
        
        # 测试多个操作
        for i in range(5):
            execute(f"import time; print('操作 {i} 开始'); time.sleep(1); print('操作 {i} 结束')")
            time.sleep(0.1)
        
        print("所有操作已提交")
        time.sleep(15)  # 等待所有操作完成
        
        # 关闭进程池
        shutdown()
    
    test() 