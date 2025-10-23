from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.ride import Ride, RideStatus, RideType
from app.models.user import User
from app.schemas.ride import RideRequest, RideEstimate

class RideService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_ride_request(self, ride_data: RideRequest, passenger_id: str) -> Ride:
        """Create a new ride request."""
        ride = Ride(
            id=str(uuid.uuid4()),
            status=RideStatus.REQUESTED,
            pickup_address=ride_data.pickup,
            destination_address=ride_data.destination,
            pickup_latitude=ride_data.pickup_latitude,
            pickup_longitude=ride_data.pickup_longitude,
            destination_latitude=ride_data.destination_latitude,
            destination_longitude=ride_data.destination_longitude,
            ride_type=ride_data.ride_type,
            fare=ride_data.estimated_fare or 100.0,  # Default fare
            distance=5.0,  # Default distance - would be calculated in real implementation
            duration=15,  # Default duration - would be calculated in real implementation
            notes=ride_data.notes,
            passenger_id=passenger_id
        )
        
        self.db.add(ride)
        self.db.commit()
        self.db.refresh(ride)
        
        return ride
    
    def get_active_ride(self, user_id: str) -> Optional[Ride]:
        """Get active ride for a user."""
        return self.db.query(Ride).filter(
            Ride.passenger_id == user_id,
            Ride.status.in_([RideStatus.REQUESTED, RideStatus.ACCEPTED, RideStatus.ARRIVED, RideStatus.STARTED])
        ).first()
    
    def get_ride_history(self, user_id: str, page: int = 1, limit: int = 20) -> tuple[List[Ride], int]:
        """Get ride history for a user."""
        rides = self.db.query(Ride).filter(
            Ride.passenger_id == user_id
        ).offset((page - 1) * limit).limit(limit).all()
        
        total = self.db.query(Ride).filter(Ride.passenger_id == user_id).count()
        
        return rides, total
    
    def get_ride_estimate(self, ride_data: dict) -> RideEstimate:
        """Get ride fare estimate."""
        # Mock estimate - in real implementation, use Google Maps API
        return RideEstimate(
            distance=5.2,
            duration=15,
            fare=120.0,
            breakdown={
                "baseFare": 50.0,
                "distanceFare": 60.0,
                "timeFare": 10.0,
                "surgeMultiplier": 1.0
            }
        )
    
    def update_ride_status(self, ride_id: str, status: RideStatus, driver_id: Optional[str] = None) -> Ride:
        """Update ride status."""
        ride = self.db.query(Ride).filter(Ride.id == ride_id).first()
        if not ride:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ride not found"
            )
        
        ride.status = status
        if driver_id:
            ride.driver_id = driver_id
        
        # Update timestamps based on status
        now = datetime.utcnow()
        if status == RideStatus.ACCEPTED:
            ride.accepted_at = now
        elif status == RideStatus.ARRIVED:
            ride.arrived_at = now
        elif status == RideStatus.STARTED:
            ride.started_at = now
        elif status == RideStatus.COMPLETED:
            ride.completed_at = now
        elif status == RideStatus.CANCELLED:
            ride.cancelled_at = now
        
        self.db.commit()
        self.db.refresh(ride)
        
        return ride
    
    def get_available_drivers(self, latitude: float, longitude: float, radius: float = 5.0) -> List[User]:
        """Get available drivers near a location."""
        # Mock implementation - in real implementation, use geospatial queries
        return self.db.query(User).filter(
            User.role == "driver",
            User.is_verified == True
        ).limit(10).all()

