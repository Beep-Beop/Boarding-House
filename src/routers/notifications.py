from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Data model
class Notification(BaseModel):
    user_name: str
    message: str
    is_read: bool = False

# In-memory storage
notifications_db = []

@router.get("/{user_name}")
async def get_notifications(user_name: str, unread_only: bool = False):
    """Get all notifications for a user, optionally only unread ones"""
    user_notifs = [n for n in notifications_db if n["user_name"] == user_name]
    
    if unread_only:
        user_notifs = [n for n in user_notifs if not n["is_read"]]
    
    return {"user_name": user_name, "notifications": user_notifs}

@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: int):
    """Mark a specific notification as read"""
    for notif in notifications_db:
        if notif["id"] == notification_id:
            notif["is_read"] = True
            return {"message": "Notification marked as read", "data": notif}
    
    raise HTTPException(status_code=404, detail="Notification not found")