import os
import logging
import time
from datetime import datetime
import getpass
import sys

class Logger:
    """日志记录工具类，负责将日志存储到指定位置"""
    
    def __init__(self, module_name="GestroKey"):
        """
        初始化日志记录器
        
        Args:
            module_name: 模块名称，默认为"GestroKey"
        """
        self.module_name = module_name
        self.logger = None
        self.setup_logger()
        
    def setup_logger(self):
        """设置日志记录器"""
        try:
            # 获取用户名
            username = getpass.getuser()
            
            # 构建日志目录路径，考虑不同操作系统
            if sys.platform.startswith('win'):
                # Windows系统使用用户文档目录
                user_dir = os.path.expanduser("~")
                log_dir = os.path.join(user_dir, ".gestrokey", "log")
            else:
                # 其他系统默认使用home目录
                log_dir = os.path.join(os.path.expanduser("~"), ".gestrokey", "log")
            
            # 确保日志目录存在
            os.makedirs(log_dir, exist_ok=True)
            
            # 生成日志文件名，格式：YYYY-MM-DD.log
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(log_dir, f"{today}.log")
            
            # 检查文件权限
            file_writable = True
            if os.path.exists(log_file):
                file_writable = os.access(log_file, os.W_OK)
            else:
                dir_writable = os.access(log_dir, os.W_OK)
                file_writable = dir_writable
                
            # 创建logger
            self.logger = logging.getLogger(self.module_name)
            self.logger.setLevel(logging.DEBUG)
            
            # 检查是否已经有处理器，避免重复添加
            if not self.logger.handlers:
                handlers = []
                
                # 创建文件处理器（如果可写）
                if file_writable:
                    try:
                        file_handler = logging.FileHandler(log_file, encoding='utf-8')
                        file_handler.setLevel(logging.DEBUG)
                        handlers.append(file_handler)
                    except (PermissionError, IOError) as e:
                        print(f"无法写入日志文件: {e}")
                
                # 创建控制台处理器
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                handlers.append(console_handler)
                
                # 设置日志格式
                formatter = logging.Formatter(
                    '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                
                # 为所有处理器设置格式并添加到logger
                for handler in handlers:
                    handler.setFormatter(formatter)
                    self.logger.addHandler(handler)
                
                # 记录初始化信息
                if file_writable:
                    self.logger.info(f"日志记录器初始化完成，日志保存在: {log_file}")
                else:
                    self.logger.warning(f"无法写入日志文件，仅输出到控制台")
                    
        except Exception as e:
            # 创建一个基本的控制台logger作为备用
            self.logger = logging.getLogger(self.module_name)
            self.logger.setLevel(logging.DEBUG)
            
            # 如果没有处理器，添加一个控制台处理器
            if not self.logger.handlers:
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
            
            self.logger.error(f"日志记录器初始化失败: {e}")
    
    def debug(self, message):
        """记录调试级别日志"""
        self.logger.debug(message)
    
    def info(self, message):
        """记录信息级别日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告级别日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误级别日志"""
        self.logger.error(message)
    
    def critical(self, message):
        """记录严重错误级别日志"""
        self.logger.critical(message)
    
    def exception(self, message):
        """记录异常信息，包含堆栈跟踪"""
        self.logger.exception(message)


# 创建一个默认的logger实例
default_logger = Logger()

def get_logger(module_name="GestroKey"):
    """获取一个命名的日志记录器"""
    return Logger(module_name)

if __name__ == "__main__":
    # 测试代码
    logger = Logger("测试模块")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    try:
        1/0
    except Exception as e:
        logger.exception(f"发生异常: {e}") 