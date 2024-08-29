import pytest
import yaml
from config.config import Config, config

@pytest.fixture(scope="module")
def env_config():
    with open('env.yaml', 'r') as file:
        return yaml.safe_load(file)

def test_env_file_attributes(env_config):
    print("\n测试 env.yaml 文件属性")
    config_methods = [method for method in dir(Config) if method.startswith('get_') and callable(getattr(Config, method))]
    read_attributes = set()

    for method_name in config_methods:
        method = getattr(config, method_name)
        result = method()
        if isinstance(result, dict):
            read_attributes.update(result.keys())

    all_attributes = set(env_config.keys())
    unread_attributes = all_attributes - read_attributes

    for attr in unread_attributes:
        print(f"警告: '{attr}' 未被读取")

    print("env.yaml 检查完成")

def test_config_singleton():
    config1, config2 = Config(), Config()
    assert config1 is config2, "单例模式测试失败"

def test_dynamic_config_methods():
    print("\n测试 Config 动态方法")
    get_methods = [method for method in dir(Config) if method.startswith('get_') and callable(getattr(Config, method))]
    
    for method_name in get_methods:
        method = getattr(config, method_name)
        try:
            result = method()
            assert result is not None, f"{method_name} 返回 None"
            if isinstance(result, dict):
                assert len(result) > 0, f"{method_name} 返回空字典"
        except Exception as e:
            print(f"错误: {method_name} - {str(e)}")

    print("Config 方法测试完成")

if __name__ == "__main__":
    pytest.main([__file__, '-v'])