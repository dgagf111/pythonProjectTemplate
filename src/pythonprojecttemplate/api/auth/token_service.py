from datetime import datetime, timedelta, UTC, timezone
from typing import Tuple
from jose import jwt
from sqlalchemy import select

from pythonprojecttemplate.cache.cache_manager import get_cache_manager
from pythonprojecttemplate.config.settings import settings
from pythonprojecttemplate.log.logHelper import get_logger
from .utils import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    create_jwt_token,
)
from pythonprojecttemplate.cache.cache_keys_manager import CacheKeysManager
from ..models.auth_models import Token
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
from zoneinfo import ZoneInfo
from pythonprojecttemplate.api.exception.custom_exceptions import InvalidTokenException, TokenRevokedException

# 日志
logger = get_logger()
# 配置
TIME_ZONE = ZoneInfo(settings.common.time_zone)
REFRESH_TOKEN_EXPIRE_DAYS = settings.api.refresh_token_expire_days

# 使用缓存管理器实例
cache_manager = get_cache_manager()
cache_keys = CacheKeysManager()

def create_tokens(username: str) -> Tuple[str, str]:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_jwt_token({"sub": username}, access_token_expires)
    refresh_token = create_jwt_token({"sub": username, "type": "refresh"}, refresh_token_expires)
    
    token_map = cache_manager.get(cache_keys.get_auth_token_map_key()) or {}
    token_map[username] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "refresh_expires": (datetime.now(timezone.utc) + refresh_token_expires).isoformat()
    }
    cache_manager.set(cache_keys.get_auth_token_map_key(), token_map)
    
    return access_token, refresh_token

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise InvalidTokenException()
        
        token_map = cache_manager.get(cache_keys.get_auth_token_map_key()) or {}
        logger.debug(f"Retrieved token_map: {token_map}")
        
        if username not in token_map:
            logger.error(f"Username {username} not found in token_map")
            raise TokenRevokedException()
        
        user_tokens = token_map[username]
        if not isinstance(user_tokens, dict):
            logger.error(f"Invalid token data for user {username}: {user_tokens}")
            raise TokenRevokedException()
        
        if user_tokens.get("access_token") != token and user_tokens.get("refresh_token") != token:
            logger.error(f"Token mismatch for user {username}")
            raise TokenRevokedException()
        
        return payload
    except jwt.JWTError:
        raise InvalidTokenException()

def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if payload.get("type") != "refresh":
            raise InvalidTokenException(detail="Invalid token type")
        
        token_map = cache_manager.get(cache_keys.get_auth_token_map_key())
        logger.debug(f"Retrieved token_map for refresh: {token_map}")
        if not isinstance(token_map, dict):
            logger.error(f"Invalid token_map type: {type(token_map)}")
            token_map = {}
        if username not in token_map:
            logger.error(f"Username {username} not found in token_map during refresh")
            raise InvalidTokenException(detail="Token has been revoked")
        
        new_access_token = create_access_token(data={"sub": username}, username=username)
        new_refresh_token = create_refresh_token(data={"sub": username}, username=username)
        
        token_map[username] = {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "refresh_expires": (datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
        }
        cache_manager.set(cache_keys.get_auth_token_map_key(), token_map)
        logger.debug(f"Updated token_map after refresh: {token_map}")
        
        return new_access_token, new_refresh_token
    except jwt.JWTError:
        raise InvalidTokenException(detail="Invalid or expired refresh token")

def revoke_tokens(username: str):
    token_map = cache_manager.get(cache_keys.get_auth_token_map_key()) or {}
    if username in token_map:
        del token_map[username]
    cache_manager.set(cache_keys.get_auth_token_map_key(), token_map)

async def generate_permanent_token(session: AsyncSession, user_id: int, provider: str) -> str:
    """生成永久token并保存到数据库"""
    token = secrets.token_urlsafe(32)
    new_token = Token(
        user_id=user_id,
        token=token,
        token_type=1,  # 1 表示用户API调用的token
        expires_at=datetime.now(TIME_ZONE) + timedelta(days=365*1000),
        state=0  # 正常状态
    )
    session.add(new_token)
    await session.commit()
    return token

async def verify_permanent_token(session: AsyncSession, token: str) -> bool:
    """验证永久token"""
    try:
        result = await session.execute(
            select(Token).where(
                Token.token == token,
                Token.token_type == 1,
                Token.state == 0
            )
        )
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            logger.debug(f"Token not found: {token[:10]}...")
            return False

        # 安全地检查过期时间，不修改原始对象
        expires_at = stored_token.expires_at
        if expires_at.tzinfo is None:
            # 如果没有时区信息，添加默认时区
            expires_at = expires_at.replace(tzinfo=TIME_ZONE)

        is_valid = expires_at > datetime.now(TIME_ZONE)

        if not is_valid:
            logger.warning(f"Token expired: {token[:10]}..., expires_at: {expires_at}")

        return is_valid

    except Exception as e:
        logger.error(f"验证token时发生错误: {e}", exc_info=True)
        return False
