from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar('T')

class ApiSuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None


class ApiErrorResponse(BaseModel):
    success: bool = False
    message: str
    details: Optional[Any] = None