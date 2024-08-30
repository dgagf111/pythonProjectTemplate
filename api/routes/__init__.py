from fastapi import APIRouter
from .health import router as health_router
from .users import router as users_router

main_router = APIRouter()

main_router.include_router(health_router, prefix="/health", tags=["health"])
main_router.include_router(users_router, prefix="/users", tags=["users"])
