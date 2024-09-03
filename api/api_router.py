import os
from fastapi import APIRouter
from config.config import config

# 加载配置
api_config = config.get_api_config()

# 优先使用环境变量，如果没有设置则使用配置文件中的值
api_version = os.getenv('API_VERSION', api_config['version'])

# 创建一个带有动态前缀的 APIRouter
api_router = APIRouter(prefix=f"/api/{api_version}")

@api_router.get("/test")
async def test_route():
    return {"message": "Test route", "version": api_version}

# 这里可以添加一些通用的路由设置，比如标签
# api_router.tags = ["api"]

# 在这里可以添加其他的路由器或路由
# 例如：
# from .users import router as users_router
# api_router.include_router(users_router)
