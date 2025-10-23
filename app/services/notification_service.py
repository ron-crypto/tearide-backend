from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.notification import Notification

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(self, user_id: str, title: str, message: str, notification_type: str) -> Notification:
        """Create a new notification."""
        notification = Notification(
            id=str(uuid.uuid4()),
            title=title,
            message=message,
            type=notification_type,
            user_id=user_id,
            is_read=False
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def get_user_notifications(self, user_id: str, page: int = 1, limit: int = 20) -> tuple[List[Notification], int]:
        """Get user's notifications."""
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).offset((page - 1) * limit).limit(limit).all()
        
        total = self.db.query(Notification).filter(Notification.user_id == user_id).count()
        
        return notifications, total
    
    def mark_notification_as_read(self, notification_id: str, user_id: str) -> Notification:
        """Mark a notification as read."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def mark_all_notifications_as_read(self, user_id: str) -> bool:
        """Mark all user notifications as read."""
        self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        self.db.commit()
        return True
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications."""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

