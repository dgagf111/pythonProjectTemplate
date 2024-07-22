import yaml
import os

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

# 获取autoMate_token
def get_autoMate_token():
    return config['autoMate_token']

# 获取MySQL配置字典
def get_MySQL_config():
    return config['mysql']

# 获取日志配置字典
def get_log_config():
    return env_config['logging']

# 打印读取的配置
# print(get_log_config())