import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.config import config
except ImportError as e:
    print(f"Error importing config: {e}")
    print(f"Current sys.path: {sys.path}")
    raise

__all__ = ['get_logger']

"""
LogHelper 类：日志辅助工具

这个类提供了一个集中的日志管理解决方案，具有以下特点：
1. 单例模式：确保整个应用程序中只有一个日志实例，避免资源浪费和日志混乱。
2. 配置灵活：支持从配置文件加载设置，也可以通过参数自定义。
3. 双重输出：同时支持控制台和文件日志输出。
4. 文件日志管理：
   - 按日期自动组织日志文件（年/月/日）。
   - 支持日志文件大小限制和备份。
5. 日志级别控制：支持设置全局日志级别。
6. 简单API：提供常用的日志方法（debug, info, warning, error, critical）。

使用方法：
1. 获取日志实例：
   logger = get_logger()

2. 记录日志：
   logger.info("这是一条信息日志")
   logger.error("这是一条错误日志")

3. 自定义配置（可选）：
   custom_logger = LogHelper(project_name="MyProject", log_level="DEBUG")

注意：
- 首次使用时会自动初始化并加载配置。
- 日志文件默认保存在 '../log' 目录下，可通过配置文件或初始化参数修改。
- 默认的日志级别是 INFO，可以通过配置文件或初始化参数修改。
"""

class LogHelper:
    """
    日志辅助类，用于创建和管理日志实例。
    使用单例模式确保全局只有一个日志实例。
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, project_name=None, base_log_directory=None, log_level=None, max_bytes=10*1024*1024, backup_count=5):
        """
        初始化日志辅助类。
        
        :param project_name: 项目名称，用于日志文件夹命名
        :param base_log_directory: 基础日志目录
        :param log_level: 日志级别
        :param max_bytes: 单个日志文件的最大字节数
        :param backup_count: 保留的日志文件数量
        """
        if not hasattr(self, 'initialized'):
            self.load_config(project_name, base_log_directory, log_level)
            self.max_bytes = max_bytes
            self.backup_count = backup_count
            self.logger = logging.getLogger(self.project_name)
            self.logger.setLevel(self.log_level)
            self.setup_handlers()
            self.initialized = True

    def load_config(self, project_name=None, base_log_directory=None, log_level=None):
        """
        从配置文件加载日志配置。
        如果传入参数，则优先使用传入的参数。
        """
        log_config = config.get_log_config()
        self.project_name = project_name or log_config.get('project_name', 'default_project')
        self.base_log_directory = base_log_directory or log_config.get('base_log_directory', '../log')
        log_level_str = log_level or log_config.get('log_level', 'DEBUG').upper()
        self.log_level = getattr(logging, log_level_str, logging.DEBUG)

    def setup_handlers(self):
        """
        设置日志处理器，包括控制台输出和文件输出。
        """
        # 设置控制台处理器
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # 设置文件处理器
        try:
            self.create_log_file_handler()
        except Exception as e:
            print(f"Error creating log file handler: {e}")

    def create_log_file_handler(self):
        """
        创建文件日志处理器，支持按大小和时间轮转。
        """
        current_date = datetime.now()
        year, month, day = current_date.strftime('%Y'), current_date.strftime('%Y-%m'), current_date.strftime('%Y-%m-%d')
        
        month_dir = os.path.join(self.base_log_directory, self.project_name, year, month)
        os.makedirs(month_dir, exist_ok=True)
        
        log_file_path = os.path.join(month_dir, f'{day}.log')
        
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=self.max_bytes, backupCount=self.backup_count
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        self.logger.addHandler(file_handler)

    def debug(self, message): self.logger.debug(message)
    def info(self, message): self.logger.info(message)
    def warning(self, message): self.logger.warning(message)
    def error(self, message): self.logger.error(message)
    def critical(self, message): self.logger.critical(message)

def get_logger():
    """
    获取日志实例的全局方法。
    :return: LogHelper实例
    """
    return LogHelper()