"""
FastAPI应用工厂

用于创建和配置FastAPI应用实例。
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ..core import get_logger, constants
from .middleware.cors import setup_cors
from .exceptions.handlers import setup_exception_handlers
from .v1.routes import api_router_v1

logger = get_logger()

def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    
    Returns:
        FastAPI: 配置好的FastAPI应用实例
    """
    app = FastAPI(
        title="Python Project Template API",
        description="统一的Python应用程序框架API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 设置CORS
    setup_cors(app)
    
    # 设置异常处理器
    setup_exception_handlers(app)
    
    # 注册路由 - 使用constants中的API_PREFIX
    app.include_router(api_router_v1, prefix=constants.API_PREFIX)
    
    # 添加启动事件
    @app.on_event("startup")
    async def startup_event():
        logger.info("FastAPI应用已启动")
    
    # 添加关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("FastAPI应用已关闭")
    
    logger.info("FastAPI应用工厂已完成应用创建")
    return app