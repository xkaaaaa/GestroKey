import logging
import os
import sys
from datetime import datetime
from version import APP_NAME, AUTHOR


class Logger:
    def __init__(self, module_name=None):
        self.module_name = module_name if module_name else APP_NAME
        self.logger = None
        self.setup_logger()

    def setup_logger(self):
        if sys.platform.startswith("win"):
            log_dir = os.path.join(os.path.expanduser("~"), f".{AUTHOR}", APP_NAME.lower(), "log")
        elif sys.platform.startswith("darwin"):
            user_dir = os.path.expanduser("~")
            log_dir = os.path.join(user_dir, "Library", "Application Support", f"{AUTHOR}", APP_NAME, "log")
        else:
            xdg_config_home = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
            log_dir = os.path.join(xdg_config_home, f"{AUTHOR}", APP_NAME, "log")

        os.makedirs(log_dir, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{today}.log")

        self.logger = logging.getLogger(self.module_name)
        self.logger.setLevel(logging.DEBUG)

        if self.logger.handlers:
            return

        handlers = []
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        file_writable = os.access(log_dir, os.W_OK)
        if os.path.exists(log_file):
            file_writable = os.access(log_file, os.W_OK)

        if file_writable:
            try:
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                handlers.append(file_handler)
            except Exception as e:
                print(f"无法写入日志文件: {e}")

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

        for handler in handlers:
            self.logger.addHandler(handler)

        if file_writable:
            self.logger.info(f"日志记录器初始化完成，日志保存在: {log_file}")
        else:
            self.logger.warning(f"无法写入日志文件，仅输出到控制台")

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def exception(self, message):
        self.logger.exception(message)


def get_logger(module_name=None):
    return Logger(module_name)