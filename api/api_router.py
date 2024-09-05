from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .auth.auth_service import authenticate_user, get_current_user, get_db, get_current_app
from .auth.token_service import create_tokens, refresh_access_token, revoke_tokens, generate_permanent_token
from api.models.token_response_model import TokenResponse
from api.models.auth_models import User
from config.config import config
from .auth.token_service import verify_token    
from log.logHelper import get_logger
from api.exception.custom_exceptions import APIException, IncorrectCredentialsException, InvalidCredentialsException, InvalidTokenException
from api.models.result_vo import ResultVO
from api.http_status import HTTPStatus

logger = get_logger()

api_config = config.get_api_config()
API_VERSION = api_config.get('api_version')
API_PREFIX = f"/api/{API_VERSION}"

api_router = APIRouter(prefix=API_PREFIX)

#######################
# 实际使用的生产接口 #
#######################

@api_router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    """
    用户登录并获取访问令牌
    
    此接口用于用户登录并获取访问令牌和刷新令牌。
    
    参数:
    - form_data (OAuth2PasswordRequestForm): 包含以下字段的表单数据:
        - username (str): 用户名
        - password (str): 密码
    - session (Session): 数据库会话对象
    
    返回:
    - 成功: ResultVO对象,包含以下数据:
        - code (int): 状态码
        - message (str): 成功消息
        - data (dict): 包含以下字段:
            - access_token (str): 访问令牌
            - token_type (str): 令牌类型,固定为"bearer"
            - refresh_token (str): 刷新令牌
    - 失败: ResultVO对象,包含以下数据:
        - code (int): 错误码
        - message (str): 错误信息
        - data (None): 失败时data为空
    
    异常:
    - InvalidCredentialsException: 用户名或密码不正确
    - 其他异常: 记录到日志并返回通用错误信息
    """
    try:
        user = authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise InvalidCredentialsException(detail="Incorrect username or password")
        access_token, refresh_token = create_tokens(form_data.username)
        return ResultVO.success(data=TokenResponse(access_token=access_token, token_type="bearer", refresh_token=refresh_token))
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return ResultVO.error(code=e.status_code, message=e.detail)

@api_router.post("/refresh")
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    """
    刷新访问令牌
    
    此接口用于使用刷新令牌获取新的访问令牌和刷新令牌。
    
    参数:
    - refresh_token (str): 用于刷新的令牌
    
    返回:
    - 成功: ResultVO对象,包含以下数据:
        - code (int): 状态码
        - message (str): 成功消息
        - data (dict): 包含以下字段:
            - access_token (str): 新的访问令牌
            - token_type (str): 令牌类型,固定为"bearer"
            - refresh_token (str): 新的刷新令牌
    - 失败: ResultVO对象,包含以下数据:
        - code (int): 错误码
        - message (str): 错误信息
        - data (None): 失败时data为空
    
    异常:
    - InvalidTokenException: 令牌类型无效
    - 其他异常: 记录到日志并返回通用错误信息
    """
    try:
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenException(detail="Invalid token type")
        new_access_token, new_refresh_token = refresh_access_token(refresh_token)
        return ResultVO.success(data=TokenResponse(access_token=new_access_token, token_type="bearer", refresh_token=new_refresh_token))
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Invalid or expired refresh token")

@api_router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    
    此接口用于用户登出,会撤销用户的所有令牌。
    
    认证:
    - 此接口需要认证。请在请求头中提供有效的Bearer Token。
    - 格式: Authorization: Bearer <access_token>
    - 系统会自动验证token并获取对应的用户信息,无需在请求体中额外提供用户信息。
    
    参数:
    - current_user (User): 当前登录的用户对象。此参数由系统根据提供的token自动注入,包含以下字段:
        - username (str): 用户名
        - user_id (int): 用户ID
        - email (str): 用户邮箱
        - ... (其他用户模型中定义的字段)
    
    返回:
    - 成功: ResultVO对象,包含以下数据:
        - code (int): 状态码
        - message (str): 成功消息
        - data (None): 登出成功时data为空
    - 失败: ResultVO对象,包含以下数据:
        - code (int): 错误码
        - message (str): 错误信息
        - data (None): 失败时data为空
    
    异常:
    - 401 Unauthorized: 如果提供的token无效或已过期
    - 404 Not Found: 如果token对应的用户不存在
    - 500 Internal Server Error: 服务器内部错误
    
    注意:
    - 调用此接口会使当前用户的所有有效token失效,包括其他设备上的登录状态。
    """
    try:
        revoke_tokens(current_user.username)
        return ResultVO.success(message="Successfully logged out")
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Failed to log out")

@api_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    """
    用户登录
    
    此接口用于用户登录并获取访问令牌和刷新令牌。
    
    参数:
    - form_data (OAuth2PasswordRequestForm): 包含以下字段的表单数据:
        - username (str): 用户名
        - password (str): 密码
    - session (Session): 数据库会话对象
    
    返回:
    - 成功: ResultVO对象,包含以下数据:
        - code (int): 状态码
        - message (str): 成功消息
        - data (dict): 包含以下字段:
            - access_token (str): 访问令牌
            - refresh_token (str): 刷新令牌
            - token_type (str): 令牌类型,固定为"bearer"
    - 失败: ResultVO对象,包含以下数据:
        - code (int): 错误码
        - message (str): 错误信息
        - data (None): 失败时data为空
    
    异常:
    - IncorrectCredentialsException: 用户名或密码不正确
    - 其他异常: 记录到日志并返回通用错误信息
    """
    try:
        user = authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise IncorrectCredentialsException(detail="Incorrect username or password")
        access_token, refresh_token = create_tokens(user.username)
        return ResultVO.success(data={"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Invalid credentials")

@api_router.post("/generate_permanent_token")
async def generate_token(user_id: int, provider: str, session: Session = Depends(get_db)):
    """
    生成永久令牌
    
    此接口用于生成长期有效的令牌,通常用于第三方应用或服务集成。
    
    参数:
    - user_id (int): 用户ID
    - provider (str): 提供者信息,用于标识令牌的来源或用途
    - session (Session): 数据库会话对象
    
    返回:
    - 成功: ResultVO对象,包含以下数据:
        - code (int): 状态码
        - message (str): 成功消息
        - data (dict): 包含以下字段:
            - permanent_token (str): 生成的永久令牌
    - 失败: ResultVO对象,包含以下数据:
        - code (int): 错误码
        - message (str): 错误信息
        - data (None): 失败时data为空
    """
    try:
        token = generate_permanent_token(session, user_id, provider)
        return ResultVO.success(data={"permanent_token": token})
    except Exception as e:
        logger.error(f"Error generating permanent token: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Failed to generate permanent token")

#######################
#     测试用接口     #
#######################

@api_router.get("/test")
async def test_route(current_user: User = Depends(get_current_user)):
    try:
        return ResultVO.success(data={"message": "Test route", "version": API_VERSION, "user": current_user.username})
    except Exception as e:
        logger.error(f"Error testing route: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Failed to test route")

@api_router.get("/third_party_test")
async def third_party_test(current_app: str = Depends(get_current_app)):
    try:
        return ResultVO.success(data={"app": current_app}, message="Third party access successful")
    except Exception as e:
        logger.error(f"Error testing third party access: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Failed to test third party access")

@api_router.get("/test_exception")
async def test_exception_route():
    raise APIException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.code, detail="测试异常")

