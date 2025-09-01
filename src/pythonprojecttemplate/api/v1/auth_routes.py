"""
重构后的API路由

使用统一的服务和工具类。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core import get_logger, constants, response_utils, error_codes, messages
from ...services.auth_service import auth_service, get_db, get_current_user
from ..schemas.token_response_model import TokenResponse

logger = get_logger()

# 创建路由器
router = APIRouter()

@router.post("/token", response_model=dict, summary="用户登录")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_db)
):
    """
    用户登录并获取访问令牌
    
    参数:
    - form_data: 包含username和password的表单数据
    - session: 数据库会话对象
    
    返回:
    - 成功: 包含访问令牌和刷新令牌的响应
    - 失败: 错误信息
    """
    try:
        # 验证用户
        user = auth_service.authenticate_user(session, form_data.username, form_data.password)
        
        # 创建令牌
        access_token, refresh_token = auth_service.create_tokens(user.username)
        
        # 构造响应数据
        token_data = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token
        )
        
        return response_utils.success_response(
            data=token_data.dict(),
            message=messages.LOGIN_SUCCESS
        )
        
    except Exception as e:
        logger.error(f"Login error for user {form_data.username}: {str(e)}")
        
        # 根据异常类型返回相应的错误响应
        if hasattr(e, 'code'):
            return response_utils.error_response(e.code, str(e))
        else:
            return response_utils.error_response(
                error_codes.UNAUTHORIZED,
                "Invalid credentials"
            )

@router.post("/refresh", summary="刷新访问令牌")
async def refresh_token(refresh_token: str):
    """
    使用刷新令牌获取新的访问令牌
    
    参数:
    - refresh_token: 刷新令牌
    
    返回:
    - 成功: 新的访问令牌和刷新令牌
    - 失败: 错误信息
    """
    try:
        new_access_token, new_refresh_token = auth_service.refresh_access_token(refresh_token)
        
        token_data = {
            "access_token": new_access_token,
            "token_type": "bearer", 
            "refresh_token": new_refresh_token
        }
        
        return response_utils.success_response(
            data=token_data,
            message="Token refreshed successfully"
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        
        if hasattr(e, 'code'):
            return response_utils.error_response(e.code, str(e))
        else:
            return response_utils.error_response(
                error_codes.TOKEN_INVALID,
                "Invalid refresh token"
            )

@router.post("/logout", summary="用户登出")
async def logout(current_user = Depends(get_current_user)):
    """
    用户登出，撤销令牌
    
    参数:
    - current_user: 当前用户（通过令牌验证）
    
    返回:
    - 成功: 登出成功消息
    """
    try:
        auth_service.revoke_tokens(current_user.username)
        
        return response_utils.success_response(
            message=messages.LOGOUT_SUCCESS
        )
        
    except Exception as e:
        logger.error(f"Logout error for user {current_user.username}: {str(e)}")
        return response_utils.error_response(
            error_codes.SYSTEM_ERROR,
            "Logout failed"
        )

@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    
    参数:
    - current_user: 当前用户（通过令牌验证）
    
    返回:
    - 用户信息（不包含敏感数据）
    """
    try:
        user_info = {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "email": current_user.email,
            "last_login_at": current_user.last_login_at,
            "state": current_user.state,
            "created_at": current_user.created_at
        }
        
        return response_utils.success_response(
            data=user_info,
            message="User info retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        return response_utils.error_response(
            error_codes.SYSTEM_ERROR,
            "Failed to get user info"
        )

@router.get("/test", summary="测试端点")
async def test_endpoint(current_user = Depends(get_current_user)):
    """
    测试端点，用于验证认证是否工作正常
    
    参数:
    - current_user: 当前用户（通过令牌验证）
    
    返回:
    - 测试信息
    """
    return response_utils.success_response(
        data={
            "message": "Test route",
            "version": constants.API_VERSION,
            "user": current_user.username,
            "api_prefix": constants.API_PREFIX
        },
        message="Test successful"
    )

@router.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查端点
    
    返回:
    - 服务健康状态
    """
    return response_utils.success_response(
        data={
            "status": "healthy",
            "version": constants.API_VERSION,
            "service": "pythonprojecttemplate"
        },
        message="Service is healthy"
    )