from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import verify_token
from app.services.driver_service import DriverService
from app.services.auth_service import AuthService
from app.schemas.driver import DriverStatus, DriverEarnings, RideRequestResponse, DriverStats
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/drivers", tags=["Drivers"])

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

def get_driver_user(current_user = Depends(get_current_user)):
    """Ensure current user is a driver."""
    if current_user.role != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only drivers can access this endpoint"
        )
    return current_user

@router.put("/status", response_model=DriverStatus)
async def toggle_driver_status(
    status_data: dict,
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Toggle driver online/offline status."""
    driver_service = DriverService(db)
    return driver_service.toggle_driver_status(current_user.id, status_data.get("status"))

@router.get("/status", response_model=DriverStatus)
async def get_driver_status(
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Get current driver status."""
    driver_service = DriverService(db)
    return driver_service.get_driver_status(current_user.id)

@router.get("/requests", response_model=List[RideRequestResponse])
async def get_ride_requests(
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Get available ride requests for driver."""
    driver_service = DriverService(db)
    return driver_service.get_ride_requests(current_user.id)

@router.post("/requests/{ride_id}/accept", response_model=SuccessResponse)
async def accept_ride_request(
    ride_id: str,
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Accept a ride request."""
    driver_service = DriverService(db)
    driver_service.accept_ride_request(ride_id, current_user.id)
    return SuccessResponse(message="Ride request accepted successfully")

@router.post("/requests/{ride_id}/reject", response_model=SuccessResponse)
async def reject_ride_request(
    ride_id: str,
    reject_data: dict,
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Reject a ride request."""
    driver_service = DriverService(db)
    driver_service.reject_ride_request(ride_id, current_user.id, reject_data.get("reason"))
    return SuccessResponse(message="Ride request rejected")

@router.get("/earnings", response_model=DriverEarnings)
async def get_driver_earnings(
    period: str = "today",  # today, week, month, year
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Get driver earnings for specified period."""
    driver_service = DriverService(db)
    return driver_service.get_driver_earnings(current_user.id, period)

@router.get("/stats", response_model=DriverStats)
async def get_driver_stats(
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Get driver statistics."""
    driver_service = DriverService(db)
    return driver_service.get_driver_stats(current_user.id)

@router.get("/active-rides", response_model=List[dict])
async def get_active_rides(
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Get driver's active rides."""
    driver_service = DriverService(db)
    return driver_service.get_active_rides(current_user.id)

@router.get("/ride-history", response_model=List[dict])
async def get_driver_ride_history(
    page: int = 1,
    limit: int = 20,
    current_user = Depends(get_driver_user),
    db: Session = Depends(get_db)
):
    """Get driver's ride history."""
    driver_service = DriverService(db)
    return driver_service.get_driver_ride_history(current_user.id, page, limit)
