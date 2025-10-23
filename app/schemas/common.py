from pydantic import BaseModel
from typing import Any, Optional

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    field: Optional[str] = None

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None

