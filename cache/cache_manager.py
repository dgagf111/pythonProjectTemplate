from abc import ABC, abstractmethod

# 使用示例
"""
from cache import cache_manager

# 配置缓存（这通常在应用程序启动时完成）
config = {
    'type': 'memory',  # 或 'redis'
    'ttl': 3600,  # 默认过期时间（秒）
    'max_size': 1000,  # 仅用于内存缓存
    'redis': {  # 仅用于 Redis 缓存
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }
}
cache = get_cache_manager(config)

# 使用缓存
cache.set('my_key', 'my_value')  # 设置缓存
value = cache.get('my_key')  # 获取缓存
cache.delete('my_key')  # 删除缓存
cache.clear()  # 清除所有缓存

# 使用列表和哈希缓存
cache.set_list('my_list', ['item1', 'item2', 'item3'])
my_list = cache.get_list('my_list')

cache.set_hash('my_hash', {'field1': 'value1', 'field2': 'value2'})
my_hash = cache.get_hash('my_hash')
"""

class BaseCacheManager(ABC):
    """
    缓存管理器的基类，定义了缓存操作的通用接口。
    所有具体的缓存实现（如内存缓存、Redis缓存等）都应该继承这个基类。
    """

    @abstractmethod
    def get(self, key):
        """
        获取缓存中的值。

        :param key: 缓存键
        :return: 缓存的值，如果键不存在则返回 None
        """
        pass

    @abstractmethod
    def set(self, key, value, ttl=None):
        """
        设置缓存。

        :param key: 缓存键
        :param value: 要缓存的值
        :param ttl: 过期时间（秒），如果为 None 则使用默认过期时间
        """
        pass

    @abstractmethod
    def delete(self, key):
        """
        删除缓存。

        :param key: 要删除的缓存键
        """
        pass

    @abstractmethod
    def clear(self):
        """
        清空所有缓存。
        """
        pass

    @abstractmethod
    def set_list(self, key, value_list, ttl=None):
        """
        设置列表类型的缓存。

        :param key: 缓存键
        :param value_list: 要缓存的列表
        :param ttl: 过期时间（秒），如果为 None 则使用默认过期时间
        """
        pass

    @abstractmethod
    def get_list(self, key):
        """
        获取列表类型的缓存。

        :param key: 缓存键
        :return: 缓存的列表，如果键不存在则返回 None
        """
        pass

    @abstractmethod
    def set_hash(self, key, value_dict, ttl=None):
        """
        设置哈希类型的缓存。

        :param key: 缓存键
        :param value_dict: 要缓存的字典
        :param ttl: 过期时间（秒），如果为 None 则使用默认过期时间
        """
        pass

    @abstractmethod
    def get_hash(self, key):
        """
        获取哈希类型的缓存。

        :param key: 缓存键
        :return: 缓存的字典，如果键不存在则返回 None
        """
        pass

def get_cache_manager(config):
    """
    根据配置创建并返回适当的缓存管理器实例。

    :param config: 包含缓存配置的字典
    :return: 缓存管理器实例
    :raises ValueError: 如果指定了不支持的缓存类型
    """
    cache_type = config['type']
    if cache_type == 'memory':
        from .memory_cache import MemoryCacheManager
        return MemoryCacheManager(ttl=config['ttl'], max_size=config['max_size'])
    elif cache_type == 'redis':
        from .redis_cache import RedisCacheManager
        return RedisCacheManager(host=config['redis']['host'],
                                 port=config['redis']['port'],
                                 db=config['redis']['db'],
                                 ttl=config['ttl'])
    else:
        raise ValueError(f"Unsupported cache type: {cache_type}")

class MemoryCacheManager(BaseCacheManager):
    def set_list(self, key, value_list, ttl=None):
        self.set(key, value_list, ttl)

    def get_list(self, key):
        return self.get(key)

    def set_hash(self, key, value_dict, ttl=None):
        self.set(key, value_dict, ttl)

    def get_hash(self, key):
        return self.get(key)
