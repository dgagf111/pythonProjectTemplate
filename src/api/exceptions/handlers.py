"""
异常处理器
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ...core.logging.logger import get_logger

logger = get_logger()

def setup_exception_handlers(app: FastAPI) -> None:
    """
    设置全局异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"捕获到全局异常: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Internal server error",
                "data": None
            }
        )