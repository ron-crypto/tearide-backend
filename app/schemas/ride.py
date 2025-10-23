from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.ride import RideStatus, RideType

class RideRequest(BaseModel):
    pickup: str
    destination: str
    pickup_latitude: float
    pickup_longitude: float
    destination_latitude: float
    destination_longitude: float
    ride_type: RideType = RideType.STANDARD
    estimated_fare: Optional[float] = None
    notes: Optional[str] = None

class RideResponse(BaseModel):
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
    passenger_id: str
    driver_id: Optional[str] = None
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
    rides: List[RideResponse]
    total: int
    page: int
    limit: int

class RideEstimate(BaseModel):
    distance: float
    duration: int
    fare: float
    breakdown: Dict[str, Any]

