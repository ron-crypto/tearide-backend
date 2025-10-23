from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.ride import RideStatus, RideType

class DriverStatus(BaseModel):
    is_online: bool
    status: str  # online, offline, busy
    last_active: datetime
    current_location: Optional[dict] = None

class DriverEarnings(BaseModel):
    period: str
    total_earnings: float
    total_rides: int
    average_earnings_per_ride: float
    breakdown: dict  # earnings by day/week/month
    currency: str = "KES"

class RideRequestResponse(BaseModel):
    id: str
    passenger_name: str
    passenger_phone: str
    pickup_address: str
    destination_address: str
    pickup_latitude: float
    pickup_longitude: float
    destination_latitude: float
    destination_longitude: float
    ride_type: RideType
    fare: float
    distance: float
    estimated_duration: int
    requested_at: datetime
    notes: Optional[str] = None

class DriverStats(BaseModel):
    total_rides: int
    completed_rides: int
    cancelled_rides: int
    total_earnings: float
    average_rating: float
    total_online_hours: float
    today_rides: int
    today_earnings: float
    this_week_rides: int
    this_week_earnings: float
    this_month_rides: int
    this_month_earnings: float
