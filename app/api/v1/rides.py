from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_token
from app.services.ride_service import RideService
from app.services.auth_service import AuthService
from app.schemas.ride import RideRequest, RideResponse, RideHistory, RideEstimate
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/rides", tags=["Rides"])

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/request", response_model=RideResponse)
async def request_ride(
    ride_data: RideRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request a new ride."""
    ride_service = RideService(db)
    return ride_service.create_ride_request(ride_data, current_user.id)

@router.get("/active", response_model=Optional[RideResponse])
async def get_active_ride(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active ride for current user."""
    ride_service = RideService(db)
    return ride_service.get_active_ride(current_user.id)

@router.get("/history", response_model=RideHistory)
async def get_ride_history(
    page: int = 1,
    limit: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ride history for current user."""
    ride_service = RideService(db)
    rides, total = ride_service.get_ride_history(current_user.id, page, limit)
    
    return RideHistory(
        rides=rides,
        total=total,
        page=page,
        limit=limit
    )

@router.post("/estimate", response_model=RideEstimate)
async def get_ride_estimate(ride_data: dict, db: Session = Depends(get_db)):
    """Get ride fare estimate."""
    ride_service = RideService(db)
    return ride_service.get_ride_estimate(ride_data)

@router.get("/drivers/available")
async def get_available_drivers(
    latitude: float,
    longitude: float,
    radius: float = 5.0,
    db: Session = Depends(get_db)
):
    """Get available drivers near a location."""
    ride_service = RideService(db)
    return ride_service.get_available_drivers(latitude, longitude, radius)

@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride_details(
    ride_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ride details by ID."""
    ride_service = RideService(db)
    ride = ride_service.get_ride_by_id(ride_id)
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check if user is authorized to view this ride
    if ride.passenger_id != current_user.id and ride.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this ride"
        )
    
    return ride

@router.put("/{ride_id}/status", response_model=RideResponse)
async def update_ride_status(
    ride_id: str,
    status_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update ride status."""
    ride_service = RideService(db)
    ride = ride_service.get_ride_by_id(ride_id)
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check authorization
    if ride.driver_id != current_user.id and ride.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ride"
        )
    
    return ride_service.update_ride_status(ride_id, status_data["status"], current_user.id)

@router.post("/{ride_id}/cancel")
async def cancel_ride(
    ride_id: str,
    cancel_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a ride."""
    ride_service = RideService(db)
    ride = ride_service.get_ride_by_id(ride_id)
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check authorization
    if ride.passenger_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only passengers can cancel rides"
        )
    
    # Check if ride can be cancelled
    if ride.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride cannot be cancelled"
        )
    
    ride_service.cancel_ride(ride_id, cancel_data.get("reason"))
    return {"message": "Ride cancelled successfully"}

@router.post("/{ride_id}/complete", response_model=RideResponse)
async def complete_ride(
    ride_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a ride."""
    ride_service = RideService(db)
    ride = ride_service.get_ride_by_id(ride_id)
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check authorization
    if ride.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can complete rides"
        )
    
    # Check if ride can be completed
    if ride.status != "started":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride must be started to be completed"
        )
    
    return ride_service.complete_ride(ride_id)

@router.post("/{ride_id}/rate")
async def rate_ride(
    ride_id: str,
    rating_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a ride."""
    ride_service = RideService(db)
    ride = ride_service.get_ride_by_id(ride_id)
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check if user is authorized to rate this ride
    if ride.passenger_id != current_user.id and ride.driver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to rate this ride"
        )
    
    # Check if ride is completed
    if ride.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rate completed rides"
        )
    
    ride_service.rate_ride(ride_id, current_user.id, rating_data["rating"], rating_data.get("comment"))
    return {"message": "Ride rated successfully"}

