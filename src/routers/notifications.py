from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/notification", tags=["Notifications"])

@router.get("/user/{user_id}", response_model=List[schemas.NotificationsResponse])
def get_notifications(user_id: int, unread_only: bool = False, db: Session = Depends(database.get_db)):
    notif_crud = crud.NotificationCRUD(db)

    return notif_crud.get_by_user(user_id, unread_only=unread_only)

@router.patch("/{notification_id}/read", response_model=schemas.NotificationsResponse)
def mark_as_read(notification_id: int, db: Session = Depends(database.get_db)):
    notif_crud = crud.NotificationCRUD(db)

    updated_notif = notif_crud.mark_as_read(notification_id)

    if not updated_notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return updated_notif

@router.post("/", response_model=schemas.NotificationsResponse)
def create_notification(notification: schemas.NotificationsCreate, db: Session = Depends(database.get_db)):
    notif_crud = crud.NotificationCRUD(db)

    return notif_crud.create(**notification.model_dump())