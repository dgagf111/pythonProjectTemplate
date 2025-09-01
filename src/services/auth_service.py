"""
认证服务

使用统一的工具和常量重构的认证服务。
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..core import get_logger
from ..core.constants import constants, cache_keys
from ..core.utils import jwt_utils, password_utils, cache_utils, database_utils
from ..core.exceptions import (
    InvalidTokenException, 
    UserNotFoundException, 
    InvalidCredentialsException,
    TokenRevokedException
)

logger = get_logger()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{constants.API_PREFIX}/token")

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.cache_manager = cache_utils.get_cache_manager()
    
    def authenticate_user(self, session: Session, username: str, password: str) -> dict:
        """
        验证用户凭据
        
        Args:
            session: 数据库会话
            username: 用户名
            password: 密码
            
        Returns:
            用户认证信息
            
        Raises:
            InvalidCredentialsException: 凭据无效
        """
        user = self.get_user_by_username(session, username)
        if not user or not password_utils.verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed for user: {username}")
            raise InvalidCredentialsException("Incorrect username or password")
        
        if user.state < constants.USER_STATE_NORMAL:
            logger.warning(f"Disabled user attempted login: {username}")
            raise InvalidCredentialsException("User account is disabled")
        
        logger.info(f"User authenticated successfully: {username}")
        return user
    
    def get_user_by_username(self, session: Session, username: str):
        """根据用户名获取用户"""
        # 这里需要导入User模型，为了避免循环导入，我们使用延迟导入
        try:
            # 尝试从新结构导入
            from ..api.schemas.auth_models import User
        except ImportError:
            # 兼容旧结构
            from ...api.models.auth_models import User
        
        return session.query(User).filter(
            User.username == username, 
            User.state >= constants.USER_STATE_NORMAL
        ).first()
    
    def create_tokens(self, username: str) -> Tuple[str, str]:
        """
        创建访问令牌和刷新令牌
        
        Args:
            username: 用户名
            
        Returns:
            (access_token, refresh_token) 元组
        """
        access_token = jwt_utils.create_access_token(username)
        refresh_token = jwt_utils.create_refresh_token(username)
        
        # 存储到缓存
        self._store_tokens_in_cache(username, access_token, refresh_token)
        
        logger.info(f"Tokens created for user: {username}")
        return access_token, refresh_token
    
    def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的 (access_token, refresh_token) 元组
            
        Raises:
            InvalidTokenException: 令牌无效
            TokenRevokedException: 令牌已被撤销
        """
        try:
            payload = jwt_utils.verify_token(refresh_token)
            username = payload.get("sub")
            
            if payload.get("type") != "refresh":
                raise InvalidTokenException("Invalid token type")
            
            # 检查令牌是否被撤销
            if not self._is_token_valid(username):
                raise TokenRevokedException("Token has been revoked")
            
            # 创建新的令牌
            new_access_token, new_refresh_token = self.create_tokens(username)
            
            logger.info(f"Tokens refreshed for user: {username}")
            return new_access_token, new_refresh_token
            
        except InvalidTokenException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise InvalidTokenException("Invalid or expired refresh token")
    
    def revoke_tokens(self, username: str) -> None:
        """
        撤销用户的所有令牌
        
        Args:
            username: 用户名
        """
        # 从缓存中删除用户的令牌
        token_map = self.cache_manager.get(cache_keys.AUTH_TOKEN_MAP) or {}
        if isinstance(token_map, dict) and username in token_map:
            del token_map[username]
            self.cache_manager.set(cache_keys.AUTH_TOKEN_MAP, token_map)
        
        logger.info(f"Tokens revoked for user: {username}")
    
    def verify_token(self, token: str) -> dict:
        """
        验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            令牌载荷
            
        Raises:
            HTTPException: 令牌无效或过期
        """
        try:
            payload = jwt_utils.verify_token(token)
            username = payload.get("sub")
            
            # 检查令牌是否被撤销
            if not self._is_token_valid(username):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            return payload
            
        except InvalidTokenException as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    
    def get_current_user(self, session: Session, token: str = Depends(oauth2_scheme)):
        """
        获取当前用户 (用于依赖注入)
        
        Args:
            session: 数据库会话
            token: JWT令牌
            
        Returns:
            当前用户
            
        Raises:
            HTTPException: 用户未找到或令牌无效
        """
        try:
            payload = self.verify_token(token)
            username = payload.get("sub")
            
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            
            user = self.get_user_by_username(session, username)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def _store_tokens_in_cache(self, username: str, access_token: str, refresh_token: str) -> None:
        """在缓存中存储令牌"""
        token_map = self.cache_manager.get(cache_keys.AUTH_TOKEN_MAP) or {}
        if not isinstance(token_map, dict):
            token_map = {}
        
        token_map[username] = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        
        self.cache_manager.set(
            cache_keys.AUTH_TOKEN_MAP, 
            token_map, 
            ttl=constants.AUTH_TOKEN_TTL
        )
    
    def _is_token_valid(self, username: str) -> bool:
        """检查令牌是否有效（未被撤销）"""
        token_map = self.cache_manager.get(cache_keys.AUTH_TOKEN_MAP)
        return isinstance(token_map, dict) and username in token_map

# 创建全局认证服务实例
auth_service = AuthService()

# 依赖函数（用于FastAPI依赖注入）
def get_db() -> Session:
    """获取数据库会话依赖"""
    return database_utils.get_db_session()

def get_current_user(
    session: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """获取当前用户依赖"""
    return auth_service.get_current_user(session, token)