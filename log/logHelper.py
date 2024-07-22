import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime
import config.config as config

"""
日志记录器

# 使用示例
# if __name__ == "__main__":
#     log_helper = LogHelper()
#     log_helper.info('This is an info message')
#     log_helper.error('This is an error message')

日志路径示意如下
parent_directory
│
├── discordbot (工程目录)
│   │
│   ├── main.py (工程文件示例)
│   └── ...
│
├── log
│   ├── discordbot
│       ├── 2024
│       │   ├── 2024-01
│       │   │   └── 2024-01-01.log
│       │   └── 2024-02
│       │       └── 2024-02-01.log
│       └── 2025
│           └── 2025-01
│               └── 2025-01-01.log

如果其他工程想要修改这个模板，
    
"""
class LogHelper:
    def __init__(self, project_name, base_log_directory='../log', log_level=logging.DEBUG):
        """
        初始化日志工具类。

        :param project_name: 工程名称，用于生成日志路径
        :param base_log_directory: 日志文件的基础目录，默认值为'../log'
        :param log_level: 日志级别，默认值为logging.DEBUG
        """
        self.base_log_directory = os.path.join(base_log_directory, project_name)
        self.log_level = log_level
        self.logger = logging.getLogger(project_name)
        self.logger.setLevel(self.log_level)
        
        # 创建一个流处理器（可选），用于将日志输出到控制台
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        
        # 创建日志文件处理器
        self.create_log_file_handler()
    
    def create_log_file_handler(self):
        """
        创建日志文件处理器，并按日期创建目录结构。
        """
        # 获取当前日期
        current_date = datetime.now()
        year = current_date.strftime('%Y')
        month = current_date.strftime('%Y-%m')
        day = current_date.strftime('%Y-%m-%d')
        
        # 根据日期创建所需的目录结构
        year_dir = os.path.join(self.base_log_directory, year)
        month_dir = os.path.join(year_dir, month)
        os.makedirs(month_dir, exist_ok=True)
        
        # 日志文件路径
        log_file_path = os.path.join(month_dir, f'{day}.log')
        
        # 创建按日期分割的日志文件处理器
        file_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=30)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        file_handler.suffix = "%Y-%m-%d"
        
        # 将文件处理器添加到记录器
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """
        记录DEBUG级别的日志。

        :param message: 要记录的消息
        """
        self.logger.debug(message)
    
    def info(self, message):
        """
        记录INFO级别的日志。

        :param message: 要记录的消息
        """
        self.logger.info(message)
    
    def warning(self, message):
        """
        记录WARNING级别的日志。

        :param message: 要记录的消息
        """
        self.logger.warning(message)
    
    def error(self, message):
        """
        记录ERROR级别的日志。

        :param message: 要记录的消息
        """
        self.logger.error(message)
    
    def critical(self, message):
        """
        记录CRITICAL级别的日志。

        :param message: 要记录的消息
        """
        self.logger.critical(message)

def initialize_logger_from_config():
    """
    从配置文件初始化日志工具类。

    :return: LogHelper实例
    """
    log_config = config.get_log_config()

    project_name = log_config['project_name']
    base_log_directory = log_config['base_log_directory']
    log_level = log_config['log_level'].upper()

    log_level = getattr(logging, log_level, logging.DEBUG)

    return LogHelper(project_name, base_log_directory, log_level)

# # 使用示例
# if __name__ == "__main__":
#     log_helper = initialize_logger_from_config()
#     log_helper.info('This is an info message')
#     log_helper.error('This is an error message')