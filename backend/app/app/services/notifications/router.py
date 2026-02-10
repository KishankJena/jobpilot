"""API routes for reminders and notifications."""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.dependencies.dependency import get_current_user
from app.services.notifications.schemas import (
    ReminderCreate,
    ReminderResponse,
    ReminderListResponse,
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
)
from app.services.notifications.service import ReminderService, NotificationService


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def _get_reminder_service(
    session: AsyncSession = Depends(get_db_session),
) -> ReminderService:
    return ReminderService(session)


def _get_notification_service(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationService:
    return NotificationService(session)


@router.post(
    "/reminders",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create reminder",
)
async def create_reminder(
    payload: ReminderCreate,
    current_user=Depends(get_current_user),
    service: ReminderService = Depends(_get_reminder_service),
) -> ReminderResponse:
    return await service.create_reminder(
        user_id=current_user["user_id"],
        payload=payload,
    )


@router.get(
    "/reminders",
    response_model=ReminderListResponse,
    summary="List reminders",
)
async def list_reminders(
    current_user=Depends(get_current_user),
    service: ReminderService = Depends(_get_reminder_service),
) -> ReminderListResponse:
    items: List[ReminderResponse] = await service.list_reminders(
        user_id=current_user["user_id"]
    )
    return ReminderListResponse(items=items)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create notification",
)
async def create_notification(
    payload: NotificationCreate,
    current_user=Depends(get_current_user),
    service: NotificationService = Depends(_get_notification_service),
) -> NotificationResponse:
    return await service.create_notification(
        user_id=current_user["user_id"],
        payload=payload,
    )


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List notifications",
)
async def list_notifications(
    current_user=Depends(get_current_user),
    service: NotificationService = Depends(_get_notification_service),
) -> NotificationListResponse:
    items: List[NotificationResponse] = await service.list_notifications(
        user_id=current_user["user_id"]
    )
    return NotificationListResponse(items=items)


@router.post(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: str,
    current_user=Depends(get_current_user),
    service: NotificationService = Depends(_get_notification_service),
) -> NotificationResponse:
    return await service.mark_as_read(
        user_id=current_user["user_id"],
        notification_id=notification_id,
    )

