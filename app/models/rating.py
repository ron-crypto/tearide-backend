from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

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

