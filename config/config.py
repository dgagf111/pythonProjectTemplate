import yaml
import os
import importlib

# 获取当前工作目录
current_working_directory = os.getcwd()
# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件夹路径
current_directory = os.path.dirname(current_file_path)
# 打开环境配置文件
with open(current_working_directory + '/' + 'env' + '.yaml', 'r') as file:
    env_config = yaml.safe_load(file)

# 打开并读取YAML文件
with open(current_directory + '/' + env_config['env'] + '.yaml', 'r') as file:
    config = yaml.safe_load(file)

# 获取全局环境配置json
def get_env_config():
    return env_config

# 获取读取的配置json
def get_config():
    return config

# 获取MySQL配置字典
def get_MySQL_config():
    return config['mysql']

# 获取日志配置字典
def get_log_config():
    return env_config['logging']

# 获取模块列表
def get_module_config():
    return env_config['module_config']

# 加载模块
def load_modules(module_names='', base_path='modules'):
    module_names = get_module_config()['modules']
    base_path = get_module_config()['base_path']
    loaded_modules = {}
    for module_name in module_names:
        try:
            # 构造模块的完整路径
            module_path = f"{base_path}.{module_name}"
            module = importlib.import_module(module_path)
            loaded_modules[module_name] = module
        except ImportError as e:
            print(f"Error loading module {module_name}: {e}")
    return loaded_modules

# 打印读取的配置
# print(load_modules())