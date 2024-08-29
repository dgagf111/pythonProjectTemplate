import yaml
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 使用示例
# from config.config import config
# mysql_config = config.get_mysql_config()

class Config:
    # 单例模式实现
    _instance = None

    def __new__(cls):
        # 如果实例不存在，创建一个新实例
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # 如果已经初始化过，直接返回
        if self._initialized:
            return
        self._initialized = True
        self._env_config = None  # 存储环境配置
        self._config = None  # 存储主配置
        self._load_config()  # 加载配置

    def _load_config(self):
        # 获取当前工作目录和文件目录
        current_working_directory = os.getcwd()
        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)

        # 加载环境配置文件（env.yaml）
        with open(os.path.join(current_working_directory, 'env.yaml'), 'r') as file:
            self._env_config = yaml.safe_load(file)

        # 确定当前环境（dev, test, prod等）
        env = os.getenv('ENV', self._env_config.get('env', 'dev'))
        # 加载对应环境的配置文件（如dev.yaml）
        with open(os.path.join(current_directory, f'{env}.yaml'), 'r') as file:
            self._config = yaml.safe_load(file)

    def get_env_config(self) -> Dict[str, Any]:
        """获取环境配置"""
        return self._env_config

    def get_config(self) -> Dict[str, Any]:
        """获取主配置"""
        return self._config

    def get_mysql_config(self) -> Dict[str, Any]:
        """
        获取MySQL配置
        优先使用环境变量中的配置，如果没有则使用配置文件中的值
        """
        mysql_config = self._config.get('mysql', {})
        return {
            'username': os.getenv('MYSQL_USERNAME', mysql_config.get('username')),
            'password': os.getenv('MYSQL_PASSWORD', mysql_config.get('password')),
            'host': os.getenv('MYSQL_HOST', mysql_config.get('host')),
            'port': int(os.getenv('MYSQL_PORT', mysql_config.get('port', 3306))),
            'database': os.getenv('MYSQL_DATABASE', mysql_config.get('database'))
        }

    def get_log_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self._env_config.get('logging', {})

    def get_module_config(self) -> Dict[str, Any]:
        """获取模块配置"""
        return self._env_config.get('module_config', {})

    def get_load_modules(self) -> Dict[str, Any]:
        """
        加载并返回配置的模块
        """
        module_config = self.get_module_config()
        module_names = module_config.get('modules', [])
        base_path = module_config.get('base_path', 'modules')
        loaded_modules = {}
        for module_name in module_names:
            try:
                # 动态导入模块
                module_path = f"{base_path}.{module_name}"
                module = __import__(module_path, fromlist=[''])
                loaded_modules[module_name] = module
            except ImportError as e:
                print(f"Error loading module {module_name}: {e}")
        return loaded_modules

    def get_scheduler_config(self) -> Dict[str, Any]:
        """获取调度器配置"""
        return self._env_config.get('scheduler', {}) 

    def get_tasks_config(self) -> Dict[str, Any]:
        """获取任务配置"""
        return self._config.get('tasks', {})

# 全局配置实例
config = Config()

# 测试代码
def run_tests():
    print("运行配置测试...")
    
    # 测试单例模式
    config1, config2 = Config(), Config()
    assert config1 is config2, "单例模式测试失败"

    # 测试各种配置加载
    assert config.get_env_config() is not None, "环境配置加载失败"
    
    mysql_config = config.get_mysql_config()
    for key in ['username', 'password', 'host', 'port', 'database']:
        assert key in mysql_config, f"MySQL配置缺少{key}"
    
    assert config.get_log_config() is not None, "日志配置加载失败"
    assert config.get_module_config() is not None, "模块配置加载失败"

    print("所有测试通过！")

if __name__ == "__main__":
    run_tests()