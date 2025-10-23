from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import verify_token
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/users", tags=["Users"])

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

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_data: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    user_service = UserService(db)
    return user_service.update_user_profile(current_user.id, profile_data)

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user_service = UserService(db)
    return user_service.get_all_users(skip, limit)

@router.get("/drivers", response_model=List[UserResponse])
async def get_drivers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all drivers."""
    user_service = UserService(db)
    return user_service.get_users_by_role("driver", skip, limit)

