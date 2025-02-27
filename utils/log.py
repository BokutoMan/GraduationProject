import logging
from logging import Logger
import logging.handlers
import time
from utils.config import Config
import os
import psutil

class SimpleLogger:
    # 获取当前进程ID
    pid = os.getpid()
    process = psutil.Process(pid)
    last_print_time = time.time()
    @classmethod
    def get_new_logger(cls, name="memory", level=logging.INFO, log_file=None):
        """
        初始化日志类。
        
        :param name: 日志记录器的名称。
        :param level: 日志级别（默认为INFO）。
        :param log_file: 日志文件路径（如果为None，则输出到控制台）。
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 如果提供了日志文件路径，则添加文件处理器
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10 * 1024 * 1024, backupCount=5)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            # 否则，添加控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    @classmethod
    def memory_log(cls, msg=None, interval=1, cup_and_io=False):
        current_time = time.time()
        if current_time - cls.last_print_time >= 1:
            message = ""
            # 获取内存使用量
            memory_info = cls.process.memory_info()
            message += f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB   "
            if cup_and_io:
                # 获取cpu使用率
                cpu_usage_percent = cls.process.cpu_percent(interval=None)
                message += f"  CPU使用率: {cpu_usage_percent:.2f}%"
                # 获取系统级别的IO信息
                disk_io = psutil.disk_io_counters()
                net_io = psutil.net_io_counters()
                message += f"  磁盘读取速度：{disk_io.read_bytes / interval / (1024 * 1024):.2f} MB/s"
                message += f"  磁盘写入速度：{disk_io.write_bytes / interval / (1024 * 1024):.2f} MB/s"
                message += f"  网络发送速度：{net_io.bytes_sent / interval / (1024 * 1024):.2f} MB/s"
                message += f"  网络接收速度：{net_io.bytes_recv / interval / (1024 * 1024):.2f} MB/s"
            
            # 加入msg
            message += ('' if msg == None else f"    Message: {msg}" )
            
            print( message)
            cls.last_print_time = current_time


# 使用示例
if __name__ == "__main__":
    
    # 创建一个日志对象，将日志输出到当前目录下的app.log文件
    logger = SimpleLogger.get_logger()

    # 记录不同级别的日志
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    logger.memory_log()
    logger.memory_log("llll")
