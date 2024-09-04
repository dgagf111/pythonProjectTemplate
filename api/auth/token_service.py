from datetime import datetime, timedelta, UTC, timezone
from typing import Optional, Tuple
from jose import jwt, JWTError
from fastapi import HTTPException, status
from config.config import config
from cache.cache_manager import get_cache_manager
from log.logHelper import get_logger
from .utils import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, create_jwt_token, create_access_token, create_refresh_token
from cache.cache_keys_manager import CacheKeysManager
from .auth_models import ThirdPartyToken, Token
from sqlalchemy.orm import Session
import secrets
from zoneinfo import ZoneInfo

# 日志
logger = get_logger()
# 获取配置
api_config = config.get_api_config()
TIME_ZONE = ZoneInfo(config.get_time_zone())

# 设置关键常量
SECRET_KEY = api_config.get("secret_key")
ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = eval(str(api_config.get("access_token_expire_minutes")))
REFRESH_TOKEN_EXPIRE_DAYS = eval(str(api_config.get("refresh_token_expire_days")))

# 使用缓存管理器实例
cache_manager = get_cache_manager()
cache_keys = CacheKeysManager()

def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token_map = cache_manager.get(cache_keys.get_auth_token_map_key()) or {}
        logger.debug(f"Retrieved token_map: {token_map}")
        
        if username not in token_map:
            logger.error(f"Username {username} not found in token_map")
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        user_tokens = token_map[username]
        if not isinstance(user_tokens, dict):
            logger.error(f"Invalid token data for user {username}: {user_tokens}")
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        if user_tokens.get("access_token") != token and user_tokens.get("refresh_token") != token:
            logger.error(f"Token mismatch for user {username}")
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        token_map = cache_manager.get(cache_keys.get_auth_token_map_key())
        logger.debug(f"Retrieved token_map for refresh: {token_map}")
        if not isinstance(token_map, dict):
            logger.error(f"Invalid token_map type: {type(token_map)}")
            token_map = {}
        if username not in token_map:
            logger.error(f"Username {username} not found in token_map during refresh")
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
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
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

def revoke_tokens(username: str):
    token_map = cache_manager.get(cache_keys.get_auth_token_map_key()) or {}
    if username in token_map:
        del token_map[username]
    cache_manager.set(cache_keys.get_auth_token_map_key(), token_map)

def generate_permanent_token(session: Session, user_id: int, provider: str) -> str:
    token = secrets.token_urlsafe(32)
    new_token = Token(
        user_id=user_id,
        token=token,
        token_type=1,  # 1 表示用户API调用的token
        expires_at=datetime.now(TIME_ZONE) + timedelta(days=365*1000),
        state=0  # 正常状态
    )
    session.add(new_token)
    session.commit()
    return token

def verify_permanent_token(session: Session, token: str) -> bool:
    stored_token = session.query(Token).filter_by(token=token, token_type=1, state=0).first()
    if stored_token:
        # 确保 stored_token.expires_at 是带时区的
        if stored_token.expires_at.tzinfo is None:
            stored_token.expires_at = stored_token.expires_at.replace(tzinfo=TIME_ZONE)
        return stored_token.expires_at > datetime.now(TIME_ZONE)
    return False
