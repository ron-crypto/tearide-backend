from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.schemas.auth import AuthResponse
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserCreate) -> AuthResponse:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.email == user_data.email) | (User.phone == user_data.phone)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or phone already exists"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            id=str(uuid.uuid4()),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            phone=user_data.phone,
            hashed_password=hashed_password,
            role=user_data.role,
            is_verified=True  # For development, auto-verify users
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        return AuthResponse(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def login_user(self, login_data: UserLogin) -> AuthResponse:
        """Authenticate and login user."""
        user = self.db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Update last active
        user.last_active_at = datetime.utcnow()
        self.db.commit()
        
        # Create tokens
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        return AuthResponse(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

