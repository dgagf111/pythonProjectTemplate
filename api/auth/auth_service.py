import os
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from typing import Optional
from api.auth.token_service import create_tokens, verify_token
from cache.cache_manager import get_cache_manager
from config.config import config
from db.mysql.mysql import MySQL_Database
from .auth_models import User, Token
from .utils import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, create_refresh_token
from sqlalchemy.orm import Session
from cache.cache_keys_manager import CacheKeysManager

# 获取API配置
api_config = config.get_api_config()

# 获取缓存键管理器
cache_keys = CacheKeysManager()

# 设置关键常量
SECRET_KEY = api_config.get("secret_key")  # 用于JWT加密的密钥
ALGORITHM = "HS256"  # JWT加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = eval(str(api_config.get("access_token_expire_minutes"))) # 访问令牌过期时间，单位：分钟，总时长：7天

# 创建密码上下文，用于密码哈希和验证
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建OAuth2密码承载流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 使用缓存管理器实例
cache_manager = get_cache_manager()

def get_db():
    """
    创建并yield一个数据库会话。
    在请求结束时自动关闭会话。
    """
    db = MySQL_Database()
    try:
        yield db.get_session()
    finally:
        db.close_session()

def generate_secret_key():
    """
    生成一个随机的密钥。
    用于为每个用户创建唯一的密钥。
    """
    return os.urandom(32).hex()

def save_secret_key(username: str, secret_key: str):
    """
    将用户的密钥保存到缓存中的secret_key大map结构。
    
    :param username: 用户名
    :param secret_key: 生成的密钥
    """
    secret_key_map = cache_manager.get(cache_keys.get_auth_secret_key_map_key()) or {}
    secret_key_map[username] = secret_key
    cache_manager.set(cache_keys.get_auth_secret_key_map_key(), secret_key_map, ttl=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

def get_secret_key(username: str):
    """
    从缓存中的secret_key大map结构获取用户的密钥。
    
    :param username: 用户名
    :return: 用户的密钥，如果不存在则返回None
    """
    secret_key_map = cache_manager.get(cache_keys.get_auth_secret_key_map_key()) or {}
    return secret_key_map.get(username)

def verify_password(plain_password, hashed_password):
    """
    验证明文密码是否与哈希密码匹配。
    
    :param plain_password: 明文密码
    :param hashed_password: 哈希后的密码
    :return: 如果密码匹配返回True，否则返回False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_user(session: Session, username: str):
    """
    根据用户名从数据库中获取用户。
    
    :param session: 数据库会话
    :param username: 用户名
    :return: 用户对，如果不存在则返回None
    """
    return session.query(User).filter(User.username == username, User.state >= 0).first()

def authenticate_user(session: Session, username: str, password: str):
    user = get_user(session, username)
    if not user or not verify_password(password, user.password_hash):
        return False
    access_token, refresh_token = create_tokens(user.username)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

def create_access_token(data: dict, username: str, expires_delta: Optional[timedelta] = None):
    """
    创建访问令牌并将其存储在token大map结构中。
    
    :param data: 要编码到令牌中的数据
    :param username: 用户名，用于获取用户特定的密钥
    :param expires_delta: 令牌的过期时间增量
    :return: 编码后的JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # 将token存储在token大map结构中
    token_map = cache_manager.get(cache_keys.get_auth_token_map_key()) or {}
    token_map[username] = encoded_jwt
    cache_manager.set(cache_keys.get_auth_token_map_key(), token_map, ttl=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)):
    """
    从JWT令牌中获取当前用户，并验证token是否存在于token大map结构中。
    
    :param token: JWT令牌
    :param session: 数据库会话
    :return: 当前用户对象
    :raises HTTPException: 如果凭据无效或用户不存在
    """
    payload = verify_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user(session, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# 新增函数：创建新用户
def create_user(session: Session, username: str, password: str, email: str):
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, password_hash=hashed_password, email=email)
    session.add(new_user)
    session.commit()
    return new_user

# 新增函数：保存token
def save_token(session: Session, user_id: int, token: str, token_type: int, expires_at: datetime):
    new_token = Token(user_id=user_id, token=token, token_type=token_type, expires_at=expires_at)
    session.add(new_token)
    session.commit()
    return new_token

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
