from .cache_manager import get_cache_manager
from config.config import config

cache_config = config.get_cache_config()
cache_manager = get_cache_manager(cache_config)
