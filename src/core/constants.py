"""
系统常量定义

统一管理项目中的所有常量，避免重复定义和魔法数字。
"""

from typing import Dict, Any
from .config.config import config

class Constants:
    """系统常量类 - 单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_constants()
    
    def _load_constants(self):
        """加载所有常量"""
        # API配置常量
        try:
            api_config = config.get_api_config()
        except:
            # 如果配置加载失败，使用默认值
            api_config = {}
        
        # JWT相关常量
        self.JWT_SECRET_KEY = api_config.get("secret_key") or "default_secret_key_for_development"
        self.JWT_ALGORITHM = "HS256"
        
        # 处理访问令牌过期时间
        access_token_config = api_config.get("access_token_expire_minutes", "180")
        try:
            if isinstance(access_token_config, str) and access_token_config.strip():
                # 尝试解析表达式
                if '*' in access_token_config or '+' in access_token_config:
                    self.ACCESS_TOKEN_EXPIRE_MINUTES = int(eval(access_token_config))
                else:
                    self.ACCESS_TOKEN_EXPIRE_MINUTES = int(access_token_config)
            else:
                self.ACCESS_TOKEN_EXPIRE_MINUTES = 180  # 默认3小时
        except (ValueError, SyntaxError, TypeError):
            self.ACCESS_TOKEN_EXPIRE_MINUTES = 180  # 默认3小时
        
        # 处理刷新令牌过期时间
        refresh_token_config = api_config.get("refresh_token_expire_days", "7")
        try:
            if isinstance(refresh_token_config, str) and refresh_token_config.strip():
                # 尝试解析表达式
                if '*' in refresh_token_config or '+' in refresh_token_config:
                    self.REFRESH_TOKEN_EXPIRE_DAYS = int(eval(refresh_token_config))
                else:
                    self.REFRESH_TOKEN_EXPIRE_DAYS = int(refresh_token_config)
            else:
                self.REFRESH_TOKEN_EXPIRE_DAYS = 7  # 默认7天
        except (ValueError, SyntaxError, TypeError):
            self.REFRESH_TOKEN_EXPIRE_DAYS = 7  # 默认7天
        
        # 数据库常量
        self.DB_POOL_SIZE = 10
        self.DB_MAX_OVERFLOW = 20
        self.DB_POOL_TIMEOUT = 30
        
        # 缓存常量
        try:
            cache_config = config.get_cache_config()
        except:
            cache_config = {}
            
        self.DEFAULT_CACHE_TTL = 3600  # 1小时
        self.AUTH_TOKEN_TTL = self.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        # Redis配置
        if cache_config.get('type') == 'redis':
            redis_config = cache_config.get('redis', {})
            self.REDIS_HOST = redis_config.get('host', 'localhost')
            self.REDIS_PORT = redis_config.get('port', 6379)
            self.REDIS_DB = redis_config.get('db', 0)
        else:
            self.REDIS_HOST = 'localhost'
            self.REDIS_PORT = 6379
            self.REDIS_DB = 0
        
        # API常量
        api_version = api_config.get("api_version", "v1")
        # 如果api_version为空或None，使用默认值
        self.API_VERSION = api_version if api_version else "v1"
        # 确保API_PREFIX不以斜杠结尾
        self.API_PREFIX = f"/api/{self.API_VERSION}"
        
        # HTTP状态码常量
        self.HTTP_OK = 200
        self.HTTP_CREATED = 201
        self.HTTP_BAD_REQUEST = 400
        self.HTTP_UNAUTHORIZED = 401
        self.HTTP_FORBIDDEN = 403
        self.HTTP_NOT_FOUND = 404
        self.HTTP_INTERNAL_ERROR = 500
        
        # 用户状态常量
        self.USER_STATE_DELETED = -1
        self.USER_STATE_DISABLED = -2
        self.USER_STATE_NORMAL = 0
        self.USER_STATE_HIGH_RISK = 1
        
        # 分页常量
        self.DEFAULT_PAGE_SIZE = 20
        self.MAX_PAGE_SIZE = 100
        
        # 文件上传常量
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        self.ALLOWED_FILE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xlsx'}
        
        # 监控常量
        try:
            monitoring_config = config.get_monitoring_config()
        except:
            monitoring_config = {}
            
        self.PROMETHEUS_PORT = monitoring_config.get('prometheus_port', 9966)
        self.CPU_THRESHOLD = monitoring_config.get('cpu_threshold', 80)
        self.MEMORY_THRESHOLD = monitoring_config.get('memory_threshold', 80)
        
        # 时区常量
        try:
            self.DEFAULT_TIMEZONE = config.get_time_zone() or 'UTC'
        except:
            self.DEFAULT_TIMEZONE = 'UTC'

class CacheKeys:
    """缓存键常量类"""
    
    # 认证相关缓存键
    AUTH_TOKEN_MAP = "auth_token_map"
    AUTH_SECRET_KEY_MAP = "auth_secret_key_map"
    USER_SESSION_PREFIX = "user_session:"
    
    # 业务缓存键
    USER_INFO_PREFIX = "user_info:"
    MENU_CACHE_PREFIX = "menu_cache:"
    CONFIG_CACHE_PREFIX = "config_cache:"
    
    @classmethod
    def get_user_session_key(cls, user_id: str) -> str:
        """获取用户会话缓存键"""
        return f"{cls.USER_SESSION_PREFIX}{user_id}"
    
    @classmethod
    def get_user_info_key(cls, user_id: str) -> str:
        """获取用户信息缓存键"""
        return f"{cls.USER_INFO_PREFIX}{user_id}"
    
    @classmethod
    def get_menu_cache_key(cls, role_id: str) -> str:
        """获取菜单缓存键"""
        return f"{cls.MENU_CACHE_PREFIX}{role_id}"

class ErrorCodes:
    """错误代码常量类"""
    
    # 通用错误码
    SUCCESS = 200
    SYSTEM_ERROR = 500
    PARAMETER_ERROR = 400
    
    # 认证相关错误码
    UNAUTHORIZED = 401
    TOKEN_EXPIRED = 4001
    TOKEN_INVALID = 4002
    PERMISSION_DENIED = 403
    
    # 用户相关错误码
    USER_NOT_FOUND = 5001
    USER_ALREADY_EXISTS = 5002
    PASSWORD_ERROR = 5003
    USER_DISABLED = 5004
    
    # 业务相关错误码
    RESOURCE_NOT_FOUND = 6001
    RESOURCE_ALREADY_EXISTS = 6002
    OPERATION_NOT_ALLOWED = 6003

class Messages:
    """消息常量类"""
    
    # 通用消息
    SUCCESS_MSG = "操作成功"
    SYSTEM_ERROR_MSG = "系统错误"
    PARAMETER_ERROR_MSG = "参数错误"
    
    # 认证消息
    LOGIN_SUCCESS = "登录成功"
    LOGOUT_SUCCESS = "登出成功"
    TOKEN_EXPIRED_MSG = "令牌已过期"
    TOKEN_INVALID_MSG = "无效的令牌"
    PERMISSION_DENIED_MSG = "权限不足"
    
    # 用户消息
    USER_NOT_FOUND_MSG = "用户不存在"
    USER_CREATED_MSG = "用户创建成功"
    PASSWORD_ERROR_MSG = "密码错误"
    
# 创建全局常量实例
constants = Constants()
cache_keys = CacheKeys()
error_codes = ErrorCodes()
messages = Messages()

# 为了向后兼容，导出常用常量
SECRET_KEY = constants.JWT_SECRET_KEY
ALGORITHM = constants.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = constants.ACCESS_TOKEN_EXPIRE_MINUTES
API_VERSION = constants.API_VERSION
API_PREFIX = constants.API_PREFIX