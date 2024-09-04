from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .auth.auth_service import authenticate_user, get_current_user, get_db
from .auth.token_service import create_tokens, refresh_access_token, revoke_tokens
from .auth.auth_models import User, Token, TokenResponse
from config.config import config
from .auth.token_service import verify_token    
from log.logHelper import get_logger

logger = get_logger()

api_config = config.get_api_config()
API_VERSION = api_config.get('api_version')
API_PREFIX = f"/api/{API_VERSION}"

api_router = APIRouter(prefix=API_PREFIX)

@api_router.post("/token", response_model=TokenResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token, refresh_token = create_tokens(form_data.username)
    return TokenResponse(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@api_router.post("/refresh")
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    try:
        payload = verify_token(refresh_token)
        username = payload.get("sub")
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        new_access_token, new_refresh_token = refresh_access_token(refresh_token)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

@api_router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    revoke_tokens(current_user.username)
    return {"message": "Successfully logged out"}

@api_router.get("/test")
async def test_route(current_user: User = Depends(get_current_user)):
    print("API_VERSION:", API_VERSION)
    return {"message": "Test route", "version": API_VERSION, "user": current_user.username}

@api_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token, refresh_token = create_tokens(user.username)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
