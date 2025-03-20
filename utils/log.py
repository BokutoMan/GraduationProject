from logging import Logger
import time
import os
import os
import inspect
from datetime import datetime

import psutil

class Logger:
    def __init__(self, module_name, process_id=None, date_fmt="%Y-%m-%dT%H:%M:%S.%f", set_process=False):
        """
        初始化日志记录器
        :param module_name: 模块名称
        :param process_id: 进程ID(默认自动获取)
        :param date_fmt: 时间格式(ISO8601 格式)
        """
        self.module_name = module_name
        self.process_id = process_id or os.getpid()
        self.date_fmt = date_fmt
        self.handlers = []
        self.last_print_time = time.time()
        self.process = None
        if set_process:
            self.set_process()
    
    def set_process(self):
        self.process = psutil.Process(os.getpid())
        
    def add_handler(self, handler):
        """添加日志处理函数"""
        self.handlers.append(handler)
        
    def _log(self, level, message, *args, **kwargs):
        """日志记录核心方法"""
        timestamp = datetime.now().strftime(self.date_fmt)
        stack = inspect.stack()
        caller_frame = stack[2]  # 获取调用者帧信息
        
        # 获取代码位置信息
        filename = os.path.basename(caller_frame.filename)
        lineno = caller_frame.lineno
        code_location = f"{filename}:{lineno}"

        # 格式化消息内容
        formatted_msg = message.format(*args, **kwargs) if args or kwargs else message
        
        # 构造完整日志条目
        log_entry = (
            f"pid {self.process_id} - {self.module_name} - {timestamp} - "
            f"{code_location} - {level.upper()} - {formatted_msg}"
        )
        
        # 调用所有处理函数
        for handler in self.handlers:
            handler(log_entry)
    
    def debug(self, message, *args, **kwargs):
        self._log("DEBUG", message, *args,  **kwargs)
    
    def info(self, message, *args, **kwargs):
        self._log("INFO", message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        self._log("WARNING", message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        self._log("ERROR", message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        self._log("CRITICAL", message, *args, **kwargs)

    # 预定义输出处理函数
    def console_handler(self, log_entry):
        """控制台输出处理器"""
        print(log_entry)

    def file_handler(self, file_path):
        """文件输出处理器工厂函数"""
        def handler(log_entry):
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        return handler

    def memory_log(self, msg=None, no_lock=False):
        current_time = time.time()
        if current_time - self.last_print_time >= 1 or no_lock:
            message = ""
            # 获取内存使用量
            memory_info = self.process.memory_info()
            message += f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB   "
            # 获取cpu使用率
            cpu_usage_percent = self.process.cpu_percent(interval=None)
            message += f"  CPU使用率: {cpu_usage_percent:.2f}%"
        
            # 加入msg
            message += ('' if msg == None else f"    Message: {msg}" )
            self._log("MEMORY", message)
            self.last_print_time = current_time


# 使用示例
if __name__ == "__main__":
    # 初始化日志记录器
    logger = Logger(
        module_name="UserAuth",
        date_fmt="%Y-%m-%dT%H:%M:%S.%f",
        set_process=True
    )
    
    # 添加处理器
    logger.add_handler(logger.console_handler)
    logger.add_handler(logger.file_handler("log/app.log"))
    
    # 记录不同级别日志
    logger.info("System initialization completed")
    logger.warning("Disk usage exceeds 80%")
    logger.error("Failed to connect to database: user_db", db_name="user_db")
    
    # 带参数的日志
    user = "john_doe"
    logger.debug("User login attempt: {username}", username=user)
    
    # 记录代码位置
    def login():
        logger.info("User {uid} logged in", uid="A123")
        logger.memory_log("Login success", no_lock=True)
    
    login()
    