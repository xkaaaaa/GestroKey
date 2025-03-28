import os
import sys
import logging
import datetime
import threading
import queue
import time
from logging.handlers import RotatingFileHandler

# 全局日志对象
log = logging.getLogger('GestroKey')

# 日志消息队列
log_queue = queue.Queue(maxsize=2000)  # 增加队列大小

# 日志处理线程是否运行中
_log_thread_running = False
_log_thread = None
_log_handlers = []  # 保存所有处理器的引用
_logger_initialized = False  # 标记日志系统是否已初始化

# 日志批处理大小和时间间隔
BATCH_SIZE = 200  # 增加每批处理的日志条数
FLUSH_INTERVAL = 0.3  # 减少强制刷新间隔（秒）

class AsyncHandler(logging.Handler):
    """异步日志处理器，将日志消息放入队列，由后台线程处理"""
    
    def __init__(self, handler):
        """初始化异步处理器
        
        Args:
            handler: 实际的日志处理器或处理器列表
        """
        super().__init__()
        # 处理单个处理器或处理器列表
        if isinstance(handler, list):
            self.handler = handler[0]  # 主处理器
            self.handlers = handler    # 所有处理器
        else:
            self.handler = handler
            self.handlers = [handler]
            
        # 设置级别为所有处理器中最低的级别
        min_level = min(h.level for h in self.handlers)
        self.setLevel(min_level)
        
        # 使用主处理器的格式化器
        self.setFormatter(self.handler.formatter)
        
    def emit(self, record):
        """将日志记录放入队列
        
        Args:
            record: 日志记录
        """
        try:
            # 创建记录的副本以避免并发问题
            record_copy = self.prepare(record)
            # 使用非阻塞方式，丢弃低优先级的日志而不是阻塞程序
            try:
                if log_queue.qsize() >= log_queue.maxsize - 10:
                    # 队列接近满，只处理ERROR及以上级别的日志
                    if record_copy.levelno >= logging.ERROR:
                        log_queue.put_nowait(record_copy)
                else:
                    log_queue.put_nowait(record_copy)
            except queue.Full:
                # 队列已满，记录到标准错误，避免死锁
                if record.levelno >= logging.ERROR:
                    sys.stderr.write(f"Log queue full, dropping message: {record.getMessage()}\n")
                    sys.stderr.flush()
        except Exception as e:
            # 捕获任何异常，确保日志问题不会导致应用崩溃
            sys.stderr.write(f"日志记录失败: {str(e)}\n")
            
    def prepare(self, record):
        """准备记录的副本，预先格式化消息
        
        Args:
            record: 原始日志记录
            
        Returns:
            格式化后的日志记录副本
        """
        # 创建记录的副本
        record_copy = logging.makeLogRecord(record.__dict__)
        # 预先计算格式化的消息
        if record_copy.exc_info:
            # 记录异常信息
            record_copy.exc_text = self.formatter.formatException(record_copy.exc_info)
            record_copy.exc_info = None  # 避免在其他线程中尝试访问异常对象
        
        return record_copy

class QueueListener(threading.Thread):
    """队列监听器，从队列中取出日志消息并处理"""
    
    def __init__(self, handlers):
        """初始化队列监听器
        
        Args:
            handlers: 日志处理器列表
        """
        super().__init__(daemon=True, name="LoggerThread")
        self.handlers = handlers
        self.running = True
        
    def run(self):
        """监听线程主函数"""
        records = []
        last_flush_time = time.time()
        
        while self.running:
            try:
                # 尝试从队列获取日志记录，设置超时确保周期性刷新
                try:
                    record = log_queue.get(timeout=0.1)
                    records.append(record)
                    log_queue.task_done()  # 标记任务完成
                except queue.Empty:
                    # 队列为空，检查是否需要刷新
                    pass
                
                # 如果达到批处理大小或刷新间隔，处理所有记录
                current_time = time.time()
                if (len(records) >= BATCH_SIZE or 
                    (records and current_time - last_flush_time >= FLUSH_INTERVAL)):
                    self._process_records(records)
                    records = []
                    last_flush_time = current_time
                    
            except Exception:
                # 捕获所有异常，确保日志线程不会崩溃
                try:
                    import traceback
                    sys.stderr.write(f"日志处理线程异常: {traceback.format_exc()}\n")
                    sys.stderr.flush()
                except:
                    pass  # 如果连这个都失败了，就放弃
        
        # 线程结束前处理剩余记录
        try:
            if records:
                self._process_records(records)
                
            # 确保所有处理器都被刷新
            for handler in self.handlers:
                try:
                    handler.flush()
                except:
                    pass
        except:
            pass
    
    def _process_records(self, records):
        """处理一批日志记录
        
        Args:
            records: 日志记录列表
        """
        for record in records:
            self._process_record(record)
                    
        # 刷新处理器
        for handler in self.handlers:
            try:
                if not (hasattr(handler, 'closed') and handler.closed):
                    handler.flush()
            except Exception:
                pass
                
    def _process_record(self, record):
        """处理单条日志记录
        
        确保每条日志只被一个合适的处理器处理一次
        
        Args:
            record: 日志记录
        """
        # 标记是否已经处理
        processed = False
        
        # 尝试找到一个合适的处理器
        for handler in self.handlers:
            # 跳过已关闭的处理器
            if hasattr(handler, 'closed') and handler.closed:
                continue
            
            # 检查日志级别是否合适
            if record.levelno >= handler.level:
                try:
                    # 只使用一个处理器处理日志
                    handler.emit(record)
                    processed = True
                    # 处理后立即返回，确保一条日志只通过一个处理器
                    return
                except Exception as e:
                    sys.stderr.write(f"处理日志失败: {str(e)}\n")
                    
        # 如果没有合适的处理器，使用第一个可用的处理器
        if not processed and self.handlers:
            for handler in self.handlers:
                if not (hasattr(handler, 'closed') and handler.closed):
                    try:
                        handler.emit(record)
                        return
                    except Exception:
                        pass
                
    def stop(self):
        """停止监听线程"""
        self.running = False
        

def setup_logger(debug_mode=False):
    """设置日志系统
    
    Args:
        debug_mode: 是否开启调试模式，默认为False
    """
    global _log_thread, _log_thread_running, _log_handlers, _logger_initialized
    
    # 如果日志系统已经初始化，只更新日志级别
    if _logger_initialized:
        level = logging.DEBUG if debug_mode else logging.INFO
        log.setLevel(level)
        
        # 更新所有处理器的级别
        for handler in _log_handlers:
            if hasattr(handler, 'level'):
                handler.setLevel(level)
            
        return
        
    # 设置日志级别
    level = logging.DEBUG if debug_mode else logging.INFO
    log.setLevel(level)
    
    # 如果已经有处理器，则先移除所有处理器
    if log.handlers:
        for handler in log.handlers[:]:
            log.removeHandler(handler)
        
    # 创建格式化器 - 简化格式以提高性能
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'  # 明确指定日期格式，提高性能
    )
    
    # 创建实际的处理器
    handlers = []
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    handlers.append(console_handler)
    
    # 创建文件处理器
    file_handler = None
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
            backupCount=10,  # 增加备份文件数量
            encoding='utf-8',
            delay=True  # 延迟创建文件直到第一条日志
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        handlers.append(file_handler)
        
    except Exception as e:
        # 如果创建文件处理器失败，仅使用控制台日志
        sys.stderr.write(f"警告：无法创建日志文件：{str(e)}\n")
        sys.stderr.flush()
    
    # 保存处理器引用
    _log_handlers = handlers
    
    # 创建异步处理器，并添加到日志器
    # 创建一个AsyncHandler来处理所有实际处理器
    async_handler = AsyncHandler(handlers)  # 传递所有处理器列表
    log.addHandler(async_handler)
    
    # 停止现有线程（如果有）
    if _log_thread_running and _log_thread:
        _log_thread.stop()
        # 不等待，允许新线程立即启动
        _log_thread_running = False
    
    # 启动日志处理线程，只传递一个处理器列表
    _log_thread = QueueListener(handlers)
    _log_thread.start()
    _log_thread_running = True
    
    # 标记日志系统已初始化
    _logger_initialized = True
    
    # 添加一个直接消息，避免被队列过滤
    sys.stderr.write("日志系统已初始化" + (" (调试模式)\n" if debug_mode else "\n"))
    sys.stderr.flush()
    
    # 正常记录初始化消息
    log.info("日志系统已初始化" + (" (调试模式)" if debug_mode else ""))


def shutdown_logger():
    """关闭日志系统，确保所有日志都被处理"""
    global _log_thread, _log_thread_running, _log_handlers
    
    if _log_thread_running and _log_thread:
        # 记录关闭日志
        log.info("正在关闭日志系统...")
        
        # 等待队列处理完成（最多等待2秒）
        try:
            log_queue.join()
        except:
            pass
            
        # 停止线程
        _log_thread.stop()
        _log_thread.join(timeout=2.0)  # 等待日志线程结束，最多2秒
        _log_thread_running = False
        
        # 关闭所有处理器
        for handler in _log_handlers:
            try:
                handler.close()
            except:
                pass
                
        _log_handlers = []
        _log_thread = None
    
    # 清空队列
    try:
        while not log_queue.empty():
            try:
                log_queue.get_nowait()
                log_queue.task_done()
            except queue.Empty:
                break
    except:
        pass


# 在模块退出时自动清理资源
import atexit
atexit.register(shutdown_logger)
    
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

# 测试功能只在直接运行此模块时执行
if __name__ == "__main__":
    # 清理现有日志系统
    shutdown_logger()
    _logger_initialized = False
    
    # 测试日志功能
    print("\n=== 日志系统测试 ===")
    setup_logger(True)  # 测试时使用调试模式
    
    # 记录不同级别的日志
    info("这是一条信息日志")
    warning("这是一条警告日志")
    error("这是一条错误日志")
    debug("这是一条调试日志")
    critical("这是一条严重错误日志")
    
    # 等待日志处理完成
    time.sleep(1)
    
    # 关闭日志系统
    shutdown_logger()
    
    print("\n日志系统测试完成")
    print("日志文件位置:", os.path.join(os.path.expanduser("~"), ".gestrokey", "logs")) 