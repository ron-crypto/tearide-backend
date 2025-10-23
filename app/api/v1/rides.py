from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_token
from app.services.ride_service import RideService
from app.services.auth_service import AuthService
from app.schemas.ride import RideRequest, RideResponse, RideHistory, RideEstimate
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/rides", tags=["Rides"])

def get_current_user(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get current authenticated user."""
    auth_service = AuthService(db)
    user = auth_service.get_user_by_email(token["sub"])
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
async def get_ride_estimate(ride_data: dict):
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

