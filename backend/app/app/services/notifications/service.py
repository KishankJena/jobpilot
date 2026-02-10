"""Business logic for reminders and notifications."""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.model.models import Reminder, Notification
from app.services.notifications.schemas import (
    ReminderCreate,
    ReminderResponse,
    NotificationCreate,
    NotificationResponse,
)


class ReminderService:
    """Service for creating and listing reminders."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_reminder(
        self,
        *,
        user_id: str,
        payload: ReminderCreate,
    ) -> ReminderResponse:
        data = payload.model_dump(exclude_unset=True)
        reminder = Reminder(user_id=user_id, **data)
        self.session.add(reminder)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(reminder)
        return ReminderResponse.model_validate(reminder)

    async def list_reminders(self, *, user_id: str) -> List[ReminderResponse]:
        result = await self.session.execute(
            select(Reminder)
            .where(Reminder.user_id == user_id)
            .order_by(Reminder.due_at.asc())
        )
        items = result.scalars().all()
        return [ReminderResponse.model_validate(r) for r in items]


class NotificationService:
    """Service for in-app notifications."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_notification(
        self,
        *,
        user_id: str,
        payload: NotificationCreate,
    ) -> NotificationResponse:
        data = payload.model_dump(exclude_unset=True)
        notification = Notification(user_id=user_id, **data)
        self.session.add(notification)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(notification)
        return NotificationResponse.model_validate(notification)

    async def list_notifications(self, *, user_id: str) -> List[NotificationResponse]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        items = result.scalars().all()
        return [NotificationResponse.model_validate(n) for n in items]

    async def mark_as_read(
        self,
        *,
        user_id: str,
        notification_id: str,
    ) -> NotificationResponse:
        result = await self.session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()
        if notification is None:
            # we avoid importing additional exceptions here to keep module small
            from app.exceptions.exceptions import AuthorizationException

            raise AuthorizationException("Notification not found or not accessible")

        from datetime import datetime, timezone

        notification.read_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(notification)
        return NotificationResponse.model_validate(notification)

