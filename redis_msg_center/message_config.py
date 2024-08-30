import redis
from config.config import config

class MessageConfig:
    def __init__(self):
        redis_config = config.get_config().get('cache', {}).get('redis', {})
        if not redis_config:
            raise ValueError("Redis configuration not found in config files")

        self.redis_client = redis.Redis(
            host=self._get_config_value(redis_config, 'host'),
            port=self._get_config_value(redis_config, 'port'),
            db=self._get_config_value(redis_config, 'db')
        )
        self.queue_key = 'redis_msg_queue_key'  # 直接在类中定义，不从配置文件读取

    def _get_config_value(self, config_dict, key):
        value = config_dict.get(key)
        if value is None:
            raise ValueError(f"Configuration key '{key}' not found in Redis config")
        return value
