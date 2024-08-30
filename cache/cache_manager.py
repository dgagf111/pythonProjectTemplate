from abc import ABC, abstractmethod

# 使用示例
"""
from cache.cache_manager import get_cache_manager

# 获取缓存管理器实例
cache_manager = get_cache_manager()

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

# 数据类型支持：
# 1. 内存缓存（MemoryCacheManager）：
#    - 支持所有可序列化的 Python 数据类型，包括：
#      字符串、数字、列表、字典、元组等
#
# 2. Redis 缓存（RedisCacheManager）：
#    - 字符串
#    - 列表
#    - 哈希（字典）
#    - 不支持直接存储复杂的嵌套结构（如列表中包含字典）
#    - 不支持直接存储元组，元组会被自动转换为列表
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

from config.config import config as cfg

def get_cache_manager():
    """
    根据配置文件创建并返回适当的缓存管理器实例。

    此函数不接受任何参数，所有配置都从配置文件中读取。
    支持的缓存类型包括 'memory' 和 'redis'。

    返回:
        BaseCacheManager: 缓存管理器实例，可能是 MemoryCacheManager 或 RedisCacheManager。

    异常:
        ValueError: 如果配置文件中指定了不支持的缓存类型或缺少必要的配置。

    用法:
        cache_manager = get_cache_manager()
    """
    cache_config = cfg.get_config().get('cache')
    if not cache_config:
        raise ValueError("缓存配置不存在")

    cache_type = cache_config.get('type')
    if not cache_type:
        raise ValueError("缓存类型未指定")

    if cache_type == 'memory':
        from .memory_cache import MemoryCacheManager
        ttl = cache_config.get('ttl')
        max_size = cache_config.get('max_size')
        if ttl is None or max_size is None:
            raise ValueError("内存缓存配置不完整")
        return MemoryCacheManager(ttl=ttl, max_size=max_size)
    elif cache_type == 'redis':
        from .redis_cache import RedisCacheManager
        redis_config = cache_config.get('redis')
        if not redis_config:
            raise ValueError("Redis配置不存在")
        host = redis_config.get('host')
        port = redis_config.get('port')
        db = redis_config.get('db')
        ttl = cache_config.get('ttl')
        if None in (host, port, db, ttl):
            raise ValueError("Redis缓存配置不完整")
        return RedisCacheManager(host=host, port=port, db=db, ttl=ttl)
    else:
        raise ValueError(f"不支持的缓存类型: {cache_type}")

class MemoryCacheManager(BaseCacheManager):
    def set_list(self, key, value_list, ttl=None):
        self.set(key, value_list, ttl)

    def get_list(self, key):
        return self.get(key)

    def set_hash(self, key, value_dict, ttl=None):
        self.set(key, value_dict, ttl)

    def get_hash(self, key):
        return self.get(key)
