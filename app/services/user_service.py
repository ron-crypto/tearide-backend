from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_profile(self, user_id: str) -> Optional[User]:
        """Get user profile by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user_profile(self, user_id: str, update_data: UserUpdate) -> User:
        """Update user profile."""
        user = self.get_user_profile(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role with pagination."""
        return self.db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        user = self.get_user_profile(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # In a real implementation, you might want to add an is_active field
        # For now, we'll just update the last_active_at timestamp
        user.last_active_at = datetime.utcnow()
        self.db.commit()
        
        return True

