from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import UserRole, RideStatus, RideType, PaymentMethodType as PaymentMethodEnum, PaymentStatus

# User Schemas
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None

class User(UserBase):
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

# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(UserCreate):
    pass

class AuthResponse(BaseModel):
    user: User
    access_token: str
    refresh_token: str
    expires_in: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Location Schemas
class Location(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

# Ride Schemas
class RideRequest(BaseModel):
    pickup: str
    destination: str
    ride_type: RideType
    estimated_fare: Optional[float] = None
    notes: Optional[str] = None

class RideEstimate(BaseModel):
    distance: float
    duration: int
    fare: float
    breakdown: dict

class Ride(BaseModel):
    id: str
    status: RideStatus
    pickup_address: str
    destination_address: str
    pickup_latitude: float
    pickup_longitude: float
    destination_latitude: float
    destination_longitude: float
    ride_type: RideType
    fare: float
    distance: float
    duration: int
    notes: Optional[str] = None
    requested_at: datetime
    accepted_at: Optional[datetime] = None
    arrived_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None

    class Config:
        from_attributes = True

class RideHistory(BaseModel):
    rides: List[Ride]
    total: int
    page: int
    limit: int

# Payment Schemas
class PaymentMethodCreate(BaseModel):
    type: PaymentMethodEnum
    name: str
    phone_number: Optional[str] = None

class PaymentMethodResponse(BaseModel):
    id: str
    type: PaymentMethodEnum
    name: str
    is_default: bool
    phone_number: Optional[str] = None
    last_four: Optional[str] = None
    brand: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    amount: float
    method: PaymentMethodEnum
    ride_id: Optional[str] = None
    phone_number: Optional[str] = None
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    amount: float
    method: PaymentMethodEnum
    status: PaymentStatus
    transaction_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentHistory(BaseModel):
    payments: List[PaymentResponse]
    total: int
    page: int
    limit: int

# Notification Schemas
class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationHistory(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    page: int
    limit: int

# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
