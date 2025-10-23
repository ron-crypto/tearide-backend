from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

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

