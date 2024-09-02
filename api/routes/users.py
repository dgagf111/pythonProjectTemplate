from fastapi import APIRouter, HTTPException, Depends, Security
from pydantic import BaseModel
from api.fastapi_auth import get_current_active_user, get_api_key, User

router = APIRouter()

class User(BaseModel):
    id: int
    name: str
    email: str

@router.get("/{user_id}")
async def get_user(user_id: int):
    # 这里应该是从数据库获取用户的逻辑
    if user_id == 1:
        return User(id=1, name="John Doe", email="john@example.com")
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/")
async def create_user(user: User):
    # 这里应该是创建用户的逻辑
    return {"message": "User created successfully", "user_id": user.id}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"你好，{current_user.username}"}

@router.get("/api_protected")
async def api_protected_route(api_key: str = Security(get_api_key)):
    return {"message": "通过API密钥成功访问"}
