from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=schemas.NotificationsResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification: schemas.NotificationsCreate, db: Session = Depends(database.get_db)):
    notif_crud = crud.NotificationsCRUD(db)

    return notif_crud.create(**notification.model_dump())


@router.patch("/{notif_id}/read", response_model=schemas.NotificationsResponse)
def update_notification_read(notif_id: int, db: Session = Depends(database.get_db)):
    notif_crud = crud.NotificationsCRUD(db)

    notification = notif_crud.mark_as_read(notif_id=notif_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification

@router.get("/user/{user_id}", response_model=List[schemas.NotificationsResponse])
def get_user_notifications(user_id: int, db: Session = Depends(database.get_db)):
    notif_crud = crud.NotificationsCRUD(db)

    notifications = notif_crud.get_user_unread(user_id=user_id)

    return notifications