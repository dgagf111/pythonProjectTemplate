import yaml
import os

class CacheKeysManager:
    """
    缓存键管理器
    用于管理缓存键，方便在多个地方使用缓存键
    每一个缓存键都放在一个yaml文件中，方便管理
    在yaml文件中的所有键值对都要在这里声明读取的方法
    """
    # 初始化
    def __init__(self):
        self.cache_keys = self._load_cache_keys()

    # 加载缓存键
    def _load_cache_keys(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_file_path = os.path.join(current_dir, 'cache_keys.yaml')
        
        with open(yaml_file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data.get('cache_keys', {})

    # 获取 test_key
    def get_test_key(self):
        return self.cache_keys.get('test_key')

# 使用示例
cache_keys_manager = CacheKeysManager()

# 运行测试
if __name__ == "__main__":
    # 创建 CacheKeysManager 实例
    manager = CacheKeysManager()

    # 测试 _load_cache_keys 方法
    assert isinstance(manager.cache_keys, dict), "cache_keys 应该是一个字典"

    # 测试 get_test_key 方法
    test_key = manager.get_test_key()
    assert test_key is not None, "test_key 不应为 None"
    assert isinstance(test_key, str), "test_key 应该是一个字符串"

    # 测试 yaml 文件是否正确加载
    assert 'test_key' in manager.cache_keys, "cache_keys 中应包含 'test_key'"

    print("所有测试通过！")

