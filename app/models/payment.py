from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PaymentMethodType(str, enum.Enum):
    MPESA = "mpesa"
    CASH = "cash"
    CARD = "card"
    WALLET = "wallet"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    method = Column(Enum(PaymentMethodType), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String, nullable=True)
    description = Column(String, nullable=True)
    failure_reason = Column(String, nullable=True)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    ride_id = Column(String, ForeignKey("rides.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    ride = relationship("Ride", back_populates="payment")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    
    id = Column(String, primary_key=True, index=True)
    type = Column(Enum(PaymentMethodType), nullable=False)
    name = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    phone_number = Column(String, nullable=True)  # For M-Pesa
    last_four = Column(String, nullable=True)  # For cards
    brand = Column(String, nullable=True)  # For cards
    expiry_month = Column(Integer, nullable=True)  # For cards
    expiry_year = Column(Integer, nullable=True)  # For cards
    
    # Foreign key
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payment_methods")

