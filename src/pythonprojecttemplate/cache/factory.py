"""
缓存工厂模块

负责根据配置创建合适的缓存管理器实例，支持内存缓存和Redis缓存的切换。
"""

from .memory_cache import MemoryCacheManager
from .redis_cache import RedisCacheManager
from pythonprojecttemplate.config.config import Config


class CacheFactory:
    """缓存工厂类"""
    
    @staticmethod
    def create_cache_manager(cache_type=None):
        """
        创建缓存管理器
        
        Args:
            cache_type (str): 缓存类型，'memory' 或 'redis'
            
        Returns:
            缓存管理器实例
        """
        if cache_type is None:
            # 从配置文件获取缓存类型
            config = Config()
            cache_config = config.get_cache_config()
            cache_type = cache_config.get('type', 'memory')
        
        if cache_type.lower() == 'redis':
            try:
                config = Config()
                cache_config = config.get_cache_config()
                return RedisCacheManager(
                    host=cache_config.get('host', 'localhost'),
                    port=cache_config.get('port', 6379),
                    db=cache_config.get('db', 0),
                    ttl=cache_config.get('ttl', 3600)
                )
            except Exception as e:
                print(f"Redis缓存初始化失败，降级到内存缓存: {e}")
                return MemoryCacheManager(ttl=3600, max_size=1000)
        else:
            return MemoryCacheManager(ttl=3600, max_size=1000)
    
    @staticmethod
    def create_memory_cache():
        """创建内存缓存管理器"""
        return MemoryCacheManager(ttl=3600, max_size=1000)
    
    @staticmethod
    def create_redis_cache():
        """创建Redis缓存管理器"""
        config = Config()
        cache_config = config.get_cache_config()
        return RedisCacheManager(
            host=cache_config.get('host', 'localhost'),
            port=cache_config.get('port', 6379),
            db=cache_config.get('db', 0),
            ttl=cache_config.get('ttl', 3600)
        )


# 提供便捷的工厂函数
def get_cache_manager(cache_type=None):
    """获取缓存管理器的便捷函数"""
    return CacheFactory.create_cache_manager(cache_type)


def get_memory_cache():
    """获取内存缓存管理器的便捷函数"""
    return CacheFactory.create_memory_cache()


def get_redis_cache():
    """获取Redis缓存管理器的便捷函数"""
    return CacheFactory.create_redis_cache()