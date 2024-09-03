import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from config.config import config
from .auth.auth_service import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_db
from datetime import timedelta
from .auth.auth_models import User
from sqlalchemy.orm import Session

# 加载配置
api_config = config.get_api_config()

# 获取API版本
api_version = api_config.get('api_version')

# 创建一个带有动态前缀的 APIRouter
api_router = APIRouter(prefix=f"/api/{api_version}")

@api_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, username=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

@api_router.get("/test")
async def test_route(current_user: User = Depends(get_current_user)):
    return {"message": "Test route", "version": api_version, "user": current_user.username}

# 这里可以添加其他的路由器或路由
# api_router.tags = ["api"]

# 在这里可以添加其他的路由器或路由
# 例如：
# from .users import router as users_router
# api_router.include_router(users_router)
