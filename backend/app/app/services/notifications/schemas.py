"""Pydantic schemas for reminders and notifications."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class ReminderCreate(BaseModel):
    job_application_id: Optional[str] = None
    type: str = Field(..., description="Reminder type identifier.")
    channel: str = Field("in_app", description="Delivery channel, e.g., in_app or email.")
    due_at: datetime
    title: str = Field(..., max_length=255)
    body: Optional[str] = Field(None, max_length=4000)


class ReminderResponse(BaseModel):
    id: str
    user_id: str
    job_application_id: Optional[str]
    type: str
    status: str
    channel: str
    due_at: datetime
    sent_at: Optional[datetime]
    title: str
    body: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(BaseModel):
    type: str = Field(..., description="Notification type identifier.")
    title: str = Field(..., max_length=255)
    body: str = Field(..., max_length=4000)


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    body: str
    read_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReminderListResponse(BaseModel):
    items: List[ReminderResponse]


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]

