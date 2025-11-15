"""
API主模块

用于创建和配置FastAPI应用实例
"""

from fastapi import FastAPI
from .api_router import api_router
from pythonprojecttemplate.config.config import Config

# 创建FastAPI应用实例
app = FastAPI(
    title="Python Project Template API",
    description="一个功能完整的Python项目模板API服务",
    version="3.1.0"
)

# 获取配置
config = Config()
api_config = config.get_api_config()

# 添加路由
app.include_router(api_router)

# 添加健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Python Project Template",
        "version": "3.1.0"
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to Python Project Template API",
        "version": "3.1.0",
        "docs": "/docs",
        "health": "/health"
    }


def create_app():
    """工厂函数，用于创建FastAPI应用"""
    return app


# 导出应用实例，供测试和部署使用
__all__ = ['app', 'create_app']