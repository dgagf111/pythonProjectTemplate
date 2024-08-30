from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
