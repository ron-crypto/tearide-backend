from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_verified = Column(Boolean, default=False)
    profile_picture = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    total_rides = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    rides_as_passenger = relationship("Ride", foreign_keys="Ride.passenger_id", back_populates="passenger")
    rides_as_driver = relationship("Ride", foreign_keys="Ride.driver_id", back_populates="driver")
    payment_methods = relationship("PaymentMethod", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

