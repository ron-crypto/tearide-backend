from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.payment import PaymentMethodType, PaymentStatus

class PaymentRequest(BaseModel):
    amount: float
    method: PaymentMethodType
    description: Optional[str] = None
    ride_id: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    amount: float
    method: PaymentMethodType
    status: PaymentStatus
    transaction_id: Optional[str] = None
    description: Optional[str] = None
    failure_reason: Optional[str] = None
    user_id: str
    ride_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PaymentHistory(BaseModel):
    payments: List[PaymentResponse]
    total: int
    page: int
    limit: int

class PaymentMethodCreate(BaseModel):
    type: PaymentMethodType
    name: str
    phone_number: Optional[str] = None
    is_default: bool = False

class PaymentMethodResponse(BaseModel):
    id: str
    type: PaymentMethodType
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

