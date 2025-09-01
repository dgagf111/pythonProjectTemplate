"""
API v1路由集成

整合所有v1版本的API路由。
"""

from fastapi import APIRouter
from .auth_routes import router as auth_router
from ...core import constants

# 创建API v1路由器 - 不需要prefix，由factory中的注册处理
api_router_v1 = APIRouter()

# 添加认证相关路由
api_router_v1.include_router(auth_router, tags=["authentication"])

# 添加其他路由组...
# api_router_v1.include_router(user_router, prefix="/users", tags=["users"])
# api_router_v1.include_router(admin_router, prefix="/admin", tags=["admin"])