from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field
from api.http_status import HTTPStatus

T = TypeVar('T')

class ResultVO(BaseModel, Generic[T]):
    code: int = Field(default=200, description="code")
    message: str = Field(default="success", description="message")
    data: Optional[T] = Field(default=None, description="data")

    @classmethod
    def success(cls, data: Optional[T] = None, 
                message: str = HTTPStatus.SUCCESS.message) -> 'ResultVO[T]':
        return cls(code=HTTPStatus.SUCCESS.code, message=message, data=data)

    @classmethod
    def error(cls, code: int = HTTPStatus.INTERNAL_SERVER_ERROR.code,
               message: str = HTTPStatus.INTERNAL_SERVER_ERROR.message) -> 'ResultVO[None]':
        return cls(code=code, message=message, data=None)
