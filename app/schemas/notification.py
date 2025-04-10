from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationType

# Shared properties
class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType

# Properties to receive via API on creation
class NotificationCreate(NotificationBase):
    user_id: int

# Properties to receive via API on update
class NotificationUpdate(BaseModel):
    is_read: bool = True

# Properties shared by models stored in DB
class NotificationInDBBase(NotificationBase):
    id: int
    is_read: bool
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Properties to return via API
class Notification(NotificationInDBBase):
    pass

# Properties stored in DB
class NotificationInDB(NotificationInDBBase):
    pass
