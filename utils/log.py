import logging
from logging import Logger

import os
import subprocess

class SimpleLogger:
    logger:Logger = None
    # 获取当前进程ID
    pid = os.getpid()

    @classmethod
    def get_new_logger(cls, name="memory", level=logging.INFO, log_file="log/memory.log"):
        """
        初始化日志类。
        
        :param name: 日志记录器的名称。
        :param level: 日志级别（默认为INFO）。
        :param log_file: 日志文件路径（如果为None，则输出到控制台）。
        """
        cls.logger = logging.getLogger(name)
        cls.logger.setLevel(level)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 如果提供了日志文件路径，则添加文件处理器
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            cls.logger.addHandler(file_handler)
        else:
            # 否则，添加控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            cls.logger.addHandler(console_handler)
        
        cls.logger.memory_log = cls.memory_log
        return cls.logger
    
    @classmethod
    def get_logger(cls):
        if cls.logger == None:
            return cls.get_new_logger()
        return cls.logger
    
    @classmethod
    def memory_log(cls, msg=None):
        # 使用tasklist命令获取内存使用情况
        tasklist_output = subprocess.check_output(['tasklist', '/FI', f'PID eq {cls.pid}', '/FO', 'LIST']).decode(encoding='gbk')

        # 解析输出以获取内存使用量
        for line in tasklist_output.split('\n'):
            if '内存使用' in line:
                memory_usage = line.split(':')[-1].strip()
                cls.logger.info(f'Memory usage: {memory_usage}' + ('' if msg == None else f"    Message: {msg}" ))



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
