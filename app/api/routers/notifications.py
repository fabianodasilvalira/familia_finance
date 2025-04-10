from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.notification import Notification, NotificationCreate, NotificationUpdate
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("/notifications/", response_model=List[Notification])
def read_notifications(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve notifications.
    """
    notification_service = NotificationService(db)
    return notification_service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )

@router.post("/notifications/", response_model=Notification)
def create_notification(
    *,
    db: Session = Depends(get_db),
    notification_in: NotificationCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new manual notification.
    """
    # Check if user is family head or sending to themselves
    if notification_in.user_id != current_user.id:
        if not current_user.is_family_head:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Check if target user is a family member
        user = db.query(User).filter(User.id == notification_in.user_id).first()
        if not user or user.family_head_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    notification_service = NotificationService(db)
    return notification_service.create_manual_notification(
        user_id=notification_in.user_id,
        title=notification_in.title,
        message=notification_in.message
    )

@router.put("/notifications/{notification_id}", response_model=Notification)
def update_notification(
    *,
    db: Session = Depends(get_db),
    notification_id: int,
    notification_in: NotificationUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Mark notification as read.
    """
    notification_service = NotificationService(db)
    notification = notification_service.get(id=notification_id)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return notification_service.update(db_obj=notification, obj_in=notification_in)

@router.delete("/notifications/{notification_id}", response_model=Notification)
def delete_notification(
    *,
    db: Session = Depends(get_db),
    notification_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete notification.
    """
    notification_service = NotificationService(db)
    notification = notification_service.get(id=notification_id)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return notification_service.remove(id=notification_id)
