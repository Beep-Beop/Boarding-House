from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# In-memory storage
notifications_db = []

@router.get("/{user_name}")
async def get_notifications(user_name: str, unread_only: bool = False, db: Session = Depends()):
    """Get all notifications for a user, optionally only unread ones"""
    user_notifs = [n for n in notifications_db if n["user_name"] == user_name]
    
    if unread_only:
        user_notifs = [n for n in user_notifs if not n["is_read"]]
    
    return {"user_name": user_name, "notifications": user_notifs}

@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: int, db: Session = Depends()):
    """Mark a specific notification as read"""
    for notif in notifications_db:
        if notif["id"] == notification_id:
            notif["is_read"] = True
            return {"message": "Notification marked as read", "data": notif}
    
    raise HTTPException(status_code=404, detail="Notification not found")

@router.post("/")
async def create_notification(user_name: str, message: str, is_read: bool = False, db: Session = Depends()):
    """Create a new notification"""
    new_notif = {
        "id": len(notifications_db) + 1,
        "user_name": user_name,
        "message": message,
        "is_read": is_read
    }
    notifications_db.append(new_notif)
    return {"message": "Notification created", "data": new_notif}