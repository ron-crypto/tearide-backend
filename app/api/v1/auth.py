from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.services.auth_service import AuthService
from app.schemas.user import UserLogin, UserRegister
from app.schemas.auth import AuthResponse
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)

@router.post("/login", response_model=AuthResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user."""
    auth_service = AuthService(db)
    return auth_service.login_user(login_data)

@router.post("/logout", response_model=SuccessResponse)
async def logout():
    """Logout user."""
    # In a real implementation, you might want to blacklist the token
    return SuccessResponse(message="Successfully logged out")

@router.get("/me", response_model=AuthResponse)
async def get_current_user_info(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Get current user information."""
    auth_service = AuthService(db)
    user = auth_service.get_user_by_email(token["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

