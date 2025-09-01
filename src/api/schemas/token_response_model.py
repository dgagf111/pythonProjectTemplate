"""
Token响应模型
"""

from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    
    class Config:
        json_encoders = {
            # 可以在这里添加自定义编码器
        }