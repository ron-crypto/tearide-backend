from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.services.notification_service import NotificationService
from app.services.auth_service import AuthService
from app.schemas.notification import NotificationResponse, NotificationHistory
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])

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

@router.get("/", response_model=NotificationHistory)
async def get_notifications(
    page: int = 1,
    limit: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notifications."""
    notification_service = NotificationService(db)
    notifications, total = notification_service.get_user_notifications(current_user.id, page, limit)
    
    return NotificationHistory(
        notifications=notifications,
        total=total,
        page=page,
        limit=limit
    )

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification_service = NotificationService(db)
    return notification_service.mark_notification_as_read(notification_id, current_user.id)

@router.put("/read-all", response_model=SuccessResponse)
async def mark_all_notifications_as_read(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read."""
    notification_service = NotificationService(db)
    notification_service.mark_all_notifications_as_read(current_user.id)
    return SuccessResponse(message="All notifications marked as read")

@router.get("/unread-count")
async def get_unread_count(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications."""
    notification_service = NotificationService(db)
    count = notification_service.get_unread_count(current_user.id)
    return {"unread_count": count}

