from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=schemas.NotificationsResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_notification(request: Request, notification: schemas.NotificationsCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    notif_crud = crud.NotificationsCRUD(db)

    if current_user.role != "admin" and notification.triggered_by != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create notifications as yourself"
        )

    return notif_crud.create(**notification.model_dump())


@router.patch("/{notif_id}/read", response_model=schemas.NotificationsResponse)
@limiter.limit("30/minute")
def update_notification_read(request: Request, notif_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    notif_crud = crud.NotificationsCRUD(db)

    notification = notif_crud.get(notif_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if current_user.role != "admin" and notification.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this notification"
        )
    
    notification = notif_crud.mark_as_read(notif_id=notif_id)
    
    return notification

@router.get("/user/{user_id}", response_model=List[schemas.NotificationsResponse])
@limiter.limit("30/minute")
def get_user_notifications(
    request: Request,
    user_id: int,
    unread_only: bool = False,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view these notifications"
        )
    notif_crud = crud.NotificationsCRUD(db)

    notifications = notif_crud.get_user_notifications(user_id=user_id, unread_only=unread_only)

    return notifications