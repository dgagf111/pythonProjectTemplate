import redis
from config.config import config

class MessageConfig:
    def __init__(self):
        cache_config = config.get_cache_config()
        redis_config = cache_config.get('redis', {})
        if not redis_config:
            raise ValueError("Redis configuration not found in cache config")

        self.redis_client = redis.Redis(
            host=redis_config['host'],
            port=int(redis_config['port']),
            db=int(redis_config['db'])
        )
        self.queue_key = 'redis_msg_queue_key'  # 直接在类中定义，不从配置文件读取

    def _get_config_value(self, config_dict, key):
        value = config_dict.get(key)
        if value is None:
            raise ValueError(f"Configuration key '{key}' not found in Redis config")
        return value
