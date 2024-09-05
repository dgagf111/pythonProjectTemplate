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
from api.exception.custom_exceptions import IncorrectCredentialsException, InvalidCredentialsException, InvalidTokenException
from api.models.result_vo import ResultVO
from api.http_status import HTTPStatus

logger = get_logger()

api_config = config.get_api_config()
API_VERSION = api_config.get('api_version')
API_PREFIX = f"/api/{API_VERSION}"

api_router = APIRouter(prefix=API_PREFIX)

@api_router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
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
    try:
        revoke_tokens(current_user.username)
        return ResultVO.success(message="Successfully logged out")
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Failed to log out")

@api_router.get("/test")
async def test_route(current_user: User = Depends(get_current_user)):
    try:
        return ResultVO.success(data={"message": "Test route", "version": API_VERSION, "user": current_user.username})
    except Exception as e:
        logger.error(f"Error testing route: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Failed to test route")

@api_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
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
    try:
        token = generate_permanent_token(session, user_id, provider)
        return ResultVO.success(data={"permanent_token": token})
    except Exception as e:
        logger.error(f"Error generating permanent token: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Failed to generate permanent token")

@api_router.get("/third_party_test")
async def third_party_test(current_app: str = Depends(get_current_app)):
    try:
        return ResultVO.success(data={"app": current_app}, message="Third party access successful")
    except Exception as e:
        logger.error(f"Error testing third party access: {str(e)}")
        return ResultVO.error(code=HTTPStatus.INTERNAL_SERVER_ERROR.code, message="Failed to test third party access")
