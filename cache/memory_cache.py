from cachetools import TTLCache
from .cache_manager import BaseCacheManager
import time

class MemoryCacheManager(BaseCacheManager):
    def __init__(self, ttl, max_size):
        self.default_ttl = ttl
        self.cache = TTLCache(maxsize=max_size, ttl=ttl)

    def get(self, key):
        item = self.cache.get(key)
        if item is None:
            return None
        if isinstance(item, tuple):
            value, expiration = item
            if time.time() > expiration:
                self.delete(key)
                return None
            return value
        return item

    def set(self, key, value, ttl=None):
        if ttl is not None:
            expiration = time.time() + ttl
            self.cache[key] = (value, expiration)
        else:
            self.cache[key] = value

    def delete(self, key):
        self.cache.pop(key, None)

    def clear(self):
        self.cache.clear()

    def set_list(self, key, value_list, ttl=None):
        self.set(key, value_list, ttl)

    def get_list(self, key):
        return self.get(key)

    def set_hash(self, key, value_dict, ttl=None):
        self.set(key, value_dict, ttl)

    def get_hash(self, key):
        return self.get(key)
