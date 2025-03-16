"""
操作执行模块
处理手势识别后的命令执行逻辑
"""

import os
import sys
import time
import base64
import pyautogui
import subprocess
import traceback

try:
    from .log import log
    from . import passapp
except ImportError:
    from log import log
    import passapp

def execute(action_base64):
    """解码并执行base64编码的Python代码"""
    try:
        # 记录操作开始
        log("operation_executor", f"接收到操作请求")
        
        # 解码base64指令
        action_string = base64.b64decode(action_base64).decode('utf-8')
        log("operation_executor", f"解码操作: {action_string}")
        
        # 检查操作字符串的有效性
        if not action_string or len(action_string.strip()) == 0:
            log("operation_executor", "操作字符串为空，跳过执行", level="warning")
            return False
            
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
            'passapp': passapp  # 添加passapp模块到全局变量
        }
        
        # 执行代码
        log("operation_executor", "执行操作代码")
        exec(action_string, global_vars, local_vars)
        log("operation_executor", "操作执行完成")
        return True
    except Exception as e:
        log("operation_executor", f"执行操作失败: {str(e)}", level="error")
        error_details = traceback.format_exc()
        log("operation_executor", f"详细错误: {error_details}", level="error")
        return False
    
if __name__ == "__main__":
    print("操作执行模块，不建议直接运行。") 