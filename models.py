from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    PASSENGER = "passenger"
    DRIVER = "driver"
    ADMIN = "admin"

class RideStatus(str, enum.Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    ARRIVED = "arrived"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RideType(str, enum.Enum):
    STANDARD = "standard"
    COMFORT = "comfort"
    PREMIUM = "premium"

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

class Ride(Base):
    __tablename__ = "rides"
    
    id = Column(String, primary_key=True, index=True)
    status = Column(Enum(RideStatus), default=RideStatus.REQUESTED)
    pickup_address = Column(String, nullable=False)
    destination_address = Column(String, nullable=False)
    pickup_latitude = Column(Float, nullable=False)
    pickup_longitude = Column(Float, nullable=False)
    destination_latitude = Column(Float, nullable=False)
    destination_longitude = Column(Float, nullable=False)
    ride_type = Column(Enum(RideType), default=RideType.STANDARD)
    fare = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    passenger_id = Column(String, ForeignKey("users.id"), nullable=False)
    driver_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    arrived_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String, nullable=True)
    
    # Relationships
    passenger = relationship("User", foreign_keys=[passenger_id], back_populates="rides_as_passenger")
    driver = relationship("User", foreign_keys=[driver_id], back_populates="rides_as_driver")
    payment = relationship("Payment", back_populates="ride", uselist=False)
    ratings = relationship("Rating", back_populates="ride")

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

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(String, primary_key=True, index=True)
    passenger_rating = Column(Integer, nullable=True)  # 1-5
    driver_rating = Column(Integer, nullable=True)  # 1-5
    passenger_comment = Column(Text, nullable=True)
    driver_comment = Column(Text, nullable=True)
    
    # Foreign keys
    ride_id = Column(String, ForeignKey("rides.id"), nullable=False)
    passenger_id = Column(String, ForeignKey("users.id"), nullable=False)
    driver_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ride = relationship("Ride", back_populates="ratings")
    passenger = relationship("User", foreign_keys=[passenger_id])
    driver = relationship("User", foreign_keys=[driver_id])

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    
    # Foreign key
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
