from pydantic import BaseModel
from app.schemas.user import UserResponse

class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    expires_in: int

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int

