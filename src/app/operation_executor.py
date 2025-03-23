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
except ImportError:
    from log import log

def execute(action_code):
    """执行操作代码，支持已解码的代码和base64编码的代码
    
    Args:
        action_code: 操作代码，可以是已解码的字符串或base64编码的字符串
    
    Returns:
        是否执行成功
    """
    try:
        # 记录操作开始
        log.info(f"接收到操作请求")
        
        # 确定输入类型并获取操作字符串
        action_string = None
        if isinstance(action_code, str):
            # 尝试检测是否为base64编码字符串
            is_base64_encoded = True
            try:
                # 标准base64字符集为A-Za-z0-9+/=，可能末尾有=或==
                base64_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
                if not all(c in base64_chars for c in action_code) or len(action_code) % 4 != 0:
                    is_base64_encoded = False
                
                # 尝试解码
                if is_base64_encoded:
                    decoded = base64.b64decode(action_code).decode('utf-8')
                    log.info(f"解码操作成功: {decoded}")
                    action_string = decoded
                else:
                    log.info(f"接收到非Base64格式的操作代码，直接使用: {action_code[:30]}..." if len(action_code) > 30 else action_code)
                    action_string = action_code
            except Exception as e:
                # 解码失败，认为是已解码的字符串
                log.info(f"Base64解码失败，使用原始字符串: {str(e)}")
                action_string = action_code
        else:
            log.warning(f"操作代码类型异常: {type(action_code)}")
            return False
        
        # 检查操作字符串的有效性
        if not action_string or len(action_string.strip()) == 0:
            log.warning("操作字符串为空，跳过执行")
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
        }
        
        # 执行代码
        log.info("执行操作代码")
        exec(action_string, global_vars, local_vars)
        log.info("操作执行完成")
        return True
    except Exception as e:
        log.error(f"执行操作失败: {str(e)}")
        error_details = traceback.format_exc()
        log.error(f"详细错误: {error_details}")
        return False
    
if __name__ == "__main__":
    print("操作执行模块，不建议直接运行。") 