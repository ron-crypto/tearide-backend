from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role: UserRole

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None

class UserResponse(UserBase):
    id: str
    is_verified: bool
    profile_picture: Optional[str] = None
    rating: float
    total_rides: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_active_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(UserCreate):
    pass

