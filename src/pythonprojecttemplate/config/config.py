import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

# 使用示例
# from pythonprojecttemplate.config.config import config
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

    def _parse_value(self, value):
        if isinstance(value, str):
            # 使用正则表达式匹配 ${VAR_NAME:-default} 模式
            pattern = r'\$\{([^}^{]+)\}'
            matches = re.finditer(pattern, value)
            for match in matches:
                env_var = match.group(1)
                env_name, default = env_var.split(':-') if ':-' in env_var else (env_var, '')
                env_value = os.environ.get(env_name, default)
                value = value.replace(match.group(0), env_value)
        return value

    def _parse_config(self, config):
        if isinstance(config, dict):
            return {k: self._parse_config(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._parse_config(v) for v in config]
        else:
            return self._parse_value(config)

    def _load_yaml_file(self, file_path):
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        return self._parse_config(config)

    def _load_config(self):
        load_dotenv()  # 加载 .env 文件中的环境变量
        current_file_path = Path(__file__).resolve()
        package_root = current_file_path.parents[1]
        self._package_root = package_root

        # 允许通过环境变量覆盖配置文件位置
        env_file_override = os.getenv("PYTHONPROJECTTEMPLATE_ENV_FILE")
        config_dir_override = os.getenv("PYTHONPROJECTTEMPLATE_CONFIG_DIR")

        env_path = Path(env_file_override) if env_file_override else package_root / "env.yaml"
        config_dir = Path(config_dir_override) if config_dir_override else package_root / "config"

        # 加载环境配置文件（env.yaml）
        self._env_config = self._load_yaml_file(env_path)

        # 确定当前环境（dev, test, prod等）
        env = os.getenv('ENV', self._env_config.get('env', 'dev'))
        # 加载对应环境的配置文件（如dev.yaml）
        self._config = self._load_yaml_file(config_dir / f'{env}.yaml')

    def get_env_config(self) -> Dict[str, Any]:
        """获取环境配置"""
        return self._env_config

    def get_config(self) -> Dict[str, Any]:
        """获取主配置"""
        return self._config

    def get_mysql_config(self) -> Dict[str, Any]:
        """
        获取MySQL配置
        优先使用环境变量中的配置，如果没有才使用配置文件中的值
        """
        mysql_config = self._config.get('mysql', {})
        parsed_config = {}
        for k, v in mysql_config.items():
            if k == 'port':
                # 安全地解析端口
                try:
                    parsed_config[k] = int(v) if v and str(v).strip() else 3306
                except (ValueError, TypeError):
                    parsed_config[k] = 3306
            else:
                parsed_config[k] = v if v else ''
        return parsed_config

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

    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        cache_config = self._config.get('cache', {})
        if cache_config.get('type') == 'redis':
            redis_config = cache_config.get('redis', {})
            redis_config['host'] = self._parse_value(redis_config.get('host', 'localhost'))
            
            # 安全解析Redis端口
            port_value = self._parse_value(redis_config.get('port', '6379'))
            try:
                redis_config['port'] = int(port_value) if port_value else 6379
            except (ValueError, TypeError):
                redis_config['port'] = 6379
            
            redis_config['db'] = int(redis_config.get('db', 0))
            cache_config['redis'] = redis_config
        return cache_config

    def get_monitoring_config(self):
        """获取监控配置"""
        return self._config.get('monitoring', {})

    def get_api_config(self) -> Dict[str, Any]:
        """获取API服务器配置"""
        api_config = self._config.get('api', {})
        # 如果api_version不存在或为空，从公共配置获取
        if not api_config.get('api_version'):
            api_config['api_version'] = self.get_api_version()
        return api_config

    def get_time_zone(self):
        """获取时区配置，返回有效的时区字符串"""
        # 从 env.yaml 的 common 节点获取时区配置
        common_config = self._env_config.get('common', {})
        time_zone = common_config.get('time_zone')
        # 如果时区为空或无效，返回默认值
        if not time_zone or time_zone.strip() == '':
            return 'Asia/Shanghai'  # 默认使用中国时区
        return time_zone.strip()
    
    def get_common_config(self) -> Dict[str, Any]:
        """获取公共配置（非敏感参数）"""
        return self._env_config.get('common', {})
    
    def get_api_version(self) -> str:
        """获取API版本（从公共配置）"""
        common_config = self.get_common_config()
        return common_config.get('api_version', 'v1')

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

    # 测试API配置
    api_config = config.get_api_config()
    assert 'api_version' in api_config, "API配置缺少api_version"
    assert api_config['api_version'] != '${API_VERSION}', "API版本未被正确替换"

    print("所有测试通过！")

if __name__ == "__main__":
    run_tests()
