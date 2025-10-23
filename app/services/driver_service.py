from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.models.user import User
from app.models.ride import Ride, RideStatus
from app.models.rating import Rating
from app.schemas.driver import DriverStatus, DriverEarnings, RideRequestResponse, DriverStats

class DriverService:
    def __init__(self, db: Session):
        self.db = db
    
    def toggle_driver_status(self, driver_id: str, status: Optional[str] = None) -> DriverStatus:
        """Toggle driver online/offline status."""
        driver = self.db.query(User).filter(User.id == driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # For now, we'll use a simple approach
        # In a real implementation, you might have a separate DriverStatus table
        current_status = getattr(driver, 'driver_status', 'offline')
        
        if status:
            new_status = status
        else:
            new_status = 'online' if current_status == 'offline' else 'offline'
        
        # Update driver status (you might want to add a driver_status field to User model)
        # For now, we'll simulate this
        driver.last_active_at = datetime.utcnow()
        self.db.commit()
        
        return DriverStatus(
            is_online=new_status == 'online',
            status=new_status,
            last_active=driver.last_active_at
        )
    
    def get_driver_status(self, driver_id: str) -> DriverStatus:
        """Get current driver status."""
        driver = self.db.query(User).filter(User.id == driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Simulate driver status
        is_online = driver.last_active_at and (datetime.utcnow() - driver.last_active_at).seconds < 300  # 5 minutes
        
        return DriverStatus(
            is_online=is_online,
            status='online' if is_online else 'offline',
            last_active=driver.last_active_at or datetime.utcnow()
        )
    
    def get_ride_requests(self, driver_id: str) -> List[RideRequestResponse]:
        """Get available ride requests for driver."""
        # Get rides that are requested and not assigned to any driver
        rides = self.db.query(Ride).filter(
            Ride.status == RideStatus.REQUESTED,
            Ride.driver_id.is_(None)
        ).all()
        
        requests = []
        for ride in rides:
            # Get passenger info
            passenger = self.db.query(User).filter(User.id == ride.passenger_id).first()
            
            requests.append(RideRequestResponse(
                id=ride.id,
                passenger_name=f"{passenger.first_name} {passenger.last_name}",
                passenger_phone=passenger.phone,
                pickup_address=ride.pickup_address,
                destination_address=ride.destination_address,
                pickup_latitude=ride.pickup_latitude,
                pickup_longitude=ride.pickup_longitude,
                destination_latitude=ride.destination_latitude,
                destination_longitude=ride.destination_longitude,
                ride_type=ride.ride_type,
                fare=ride.fare,
                distance=ride.distance,
                estimated_duration=ride.duration,
                requested_at=ride.requested_at,
                notes=ride.notes
            ))
        
        return requests
    
    def accept_ride_request(self, ride_id: str, driver_id: str) -> None:
        """Accept a ride request."""
        ride = self.db.query(Ride).filter(Ride.id == ride_id).first()
        if not ride:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ride not found"
            )
        
        if ride.status != RideStatus.REQUESTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ride is no longer available"
            )
        
        if ride.driver_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ride has already been accepted by another driver"
            )
        
        # Assign driver to ride
        ride.driver_id = driver_id
        ride.status = RideStatus.ACCEPTED
        ride.accepted_at = datetime.utcnow()
        
        self.db.commit()
    
    def reject_ride_request(self, ride_id: str, driver_id: str, reason: Optional[str] = None) -> None:
        """Reject a ride request."""
        # In a real implementation, you might want to track rejections
        # For now, we'll just log it or do nothing
        pass
    
    def get_driver_earnings(self, driver_id: str, period: str = "today") -> DriverEarnings:
        """Get driver earnings for specified period."""
        now = datetime.utcnow()
        
        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get completed rides in the period
        rides = self.db.query(Ride).filter(
            Ride.driver_id == driver_id,
            Ride.status == RideStatus.COMPLETED,
            Ride.completed_at >= start_date
        ).all()
        
        total_earnings = sum(ride.fare for ride in rides)
        total_rides = len(rides)
        average_earnings = total_earnings / total_rides if total_rides > 0 else 0
        
        return DriverEarnings(
            period=period,
            total_earnings=total_earnings,
            total_rides=total_rides,
            average_earnings_per_ride=average_earnings,
            breakdown={}  # You could implement detailed breakdown here
        )
    
    def get_driver_stats(self, driver_id: str) -> DriverStats:
        """Get driver statistics."""
        # Get all rides for this driver
        all_rides = self.db.query(Ride).filter(Ride.driver_id == driver_id).all()
        completed_rides = [r for r in all_rides if r.status == RideStatus.COMPLETED]
        cancelled_rides = [r for r in all_rides if r.status == RideStatus.CANCELLED]
        
        # Calculate earnings
        total_earnings = sum(ride.fare for ride in completed_rides)
        
        # Calculate average rating
        ratings = self.db.query(Rating).filter(Rating.driver_id == driver_id).all()
        average_rating = sum(r.driver_rating for r in ratings if r.driver_rating) / len(ratings) if ratings else 0
        
        # Today's stats
        today = datetime.utcnow().date()
        today_rides = [r for r in completed_rides if r.completed_at and r.completed_at.date() == today]
        today_earnings = sum(ride.fare for ride in today_rides)
        
        # This week's stats
        week_start = today - timedelta(days=today.weekday())
        this_week_rides = [r for r in completed_rides if r.completed_at and r.completed_at.date() >= week_start]
        this_week_earnings = sum(ride.fare for ride in this_week_rides)
        
        # This month's stats
        month_start = today.replace(day=1)
        this_month_rides = [r for r in completed_rides if r.completed_at and r.completed_at.date() >= month_start]
        this_month_earnings = sum(ride.fare for ride in this_month_rides)
        
        return DriverStats(
            total_rides=len(all_rides),
            completed_rides=len(completed_rides),
            cancelled_rides=len(cancelled_rides),
            total_earnings=total_earnings,
            average_rating=round(average_rating, 2),
            total_online_hours=0,  # You'd need to track this separately
            today_rides=len(today_rides),
            today_earnings=today_earnings,
            this_week_rides=len(this_week_rides),
            this_week_earnings=this_week_earnings,
            this_month_rides=len(this_month_rides),
            this_month_earnings=this_month_earnings
        )
    
    def get_active_rides(self, driver_id: str) -> List[dict]:
        """Get driver's active rides."""
        active_rides = self.db.query(Ride).filter(
            Ride.driver_id == driver_id,
            Ride.status.in_([RideStatus.ACCEPTED, RideStatus.ARRIVED, RideStatus.STARTED])
        ).all()
        
        return [{
            "id": ride.id,
            "status": ride.status,
            "pickup_address": ride.pickup_address,
            "destination_address": ride.destination_address,
            "fare": ride.fare,
            "passenger_id": ride.passenger_id,
            "accepted_at": ride.accepted_at,
            "arrived_at": ride.arrived_at,
            "started_at": ride.started_at
        } for ride in active_rides]
    
    def get_driver_ride_history(self, driver_id: str, page: int = 1, limit: int = 20) -> List[dict]:
        """Get driver's ride history."""
        rides = self.db.query(Ride).filter(
            Ride.driver_id == driver_id
        ).offset((page - 1) * limit).limit(limit).all()
        
        return [{
            "id": ride.id,
            "status": ride.status,
            "pickup_address": ride.pickup_address,
            "destination_address": ride.destination_address,
            "fare": ride.fare,
            "distance": ride.distance,
            "duration": ride.duration,
            "requested_at": ride.requested_at,
            "accepted_at": ride.accepted_at,
            "completed_at": ride.completed_at,
            "passenger_id": ride.passenger_id
        } for ride in rides]
