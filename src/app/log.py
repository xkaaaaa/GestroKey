import os
import sys
import logging
import datetime
from logging.handlers import RotatingFileHandler

# 全局日志对象
log = logging.getLogger('GestroKey')

def setup_logger(debug_mode=False):
    """设置日志系统
    
    Args:
        debug_mode: 是否开启调试模式，默认为False
    """
    # 设置日志级别
    level = logging.DEBUG if debug_mode else logging.INFO
    log.setLevel(level)
    
    # 如果已经有处理器，则先移除所有处理器
    if log.handlers:
        for handler in log.handlers[:]:
            log.removeHandler(handler)
        
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    log.addHandler(console_handler)
    
    # 创建文件处理器
    try:
        # 创建日志目录
        log_dir = os.path.join(os.path.expanduser("~"), ".gestrokey", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件名，包含当前日期
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f"gestrokey_{today}.log")
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        log.addHandler(file_handler)
        
    except Exception as e:
        # 如果创建文件处理器失败，仅使用控制台日志
        log.warning(f"无法创建日志文件：{str(e)}")
        
    log.info("日志系统已初始化" + (" (调试模式)" if debug_mode else ""))
    
# 设置日志方法别名，方便直接使用
def info(message):
    """记录信息级别日志
    
    Args:
        message: 日志消息
    """
    log.info(message)
    
def warning(message):
    """记录警告级别日志
    
    Args:
        message: 日志消息
    """
    log.warning(message)
    
def error(message):
    """记录错误级别日志
    
    Args:
        message: 日志消息
    """
    log.error(message)
    
def debug(message):
    """记录调试级别日志
    
    Args:
        message: 日志消息
    """
    log.debug(message)
    
def critical(message):
    """记录严重错误级别日志
    
    Args:
        message: 日志消息
    """
    log.critical(message)
    
# 模块初始化时设置日志系统，默认非调试模式
setup_logger(False)

if __name__ == "__main__":
    # 测试日志功能
    setup_logger(True)  # 测试时使用调试模式
    info("这是一条信息日志")
    warning("这是一条警告日志")
    error("这是一条错误日志")
    debug("这是一条调试日志")
    critical("这是一条严重错误日志")
    
    print("日志文件位置:", os.path.join(os.path.expanduser("~"), ".gestrokey", "logs")) 