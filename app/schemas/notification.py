from pydantic import BaseModel
from typing import List
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationHistory(BaseModel):
    notifications: List[NotificationResponse]
    total: int
    page: int
    limit: int

