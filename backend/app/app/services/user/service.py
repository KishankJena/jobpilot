"""Business logic for user profile and preferences."""
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user.repository import UserProfileRepository
from app.services.user.schemas import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    UserPreferencesResponse,
)
from app.exceptions.exceptions import UserNotFoundException
from app.model.models import User
from sqlalchemy import select


class UserProfileService:
    """Service for managing user profile and preferences."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.profile_repo = UserProfileRepository(session)

    async def _ensure_user_exists(self, user_id: str) -> None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundException()

    async def get_profile(self, user_id: str) -> UserProfileResponse:
        """Return the user's profile, creating an empty one if necessary."""
        await self._ensure_user_exists(user_id)
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            # Lazy-create a minimal profile so clients always see a consistent shape.
            profile = await self.profile_repo.upsert_for_user(user_id, {})
        return UserProfileResponse.model_validate(profile)

    async def upsert_profile(
        self,
        user_id: str,
        payload: UserProfileCreate | UserProfileUpdate,
    ) -> UserProfileResponse:
        await self._ensure_user_exists(user_id)
        data: Dict[str, Any] = payload.model_dump(exclude_unset=True)
        profile = await self.profile_repo.upsert_for_user(user_id, data)
        return UserProfileResponse.model_validate(profile)

    async def get_preferences(self, user_id: str) -> UserPreferencesResponse:
        profile = await self.get_profile(user_id)
        return UserPreferencesResponse(
            timezone=profile.timezone,
            email_notifications_enabled=profile.email_notifications_enabled or False,
            push_notifications_enabled=profile.push_notifications_enabled or False,
            weekly_summary_email_enabled=profile.weekly_summary_email_enabled or False,
        )

    async def update_preferences(
        self,
        user_id: str,
        payload: UserProfileUpdate,
    ) -> UserPreferencesResponse:
        # Reuse profile semantics; any preference fields present will be updated.
        profile = await self.upsert_profile(user_id, payload)
        return UserPreferencesResponse(
            timezone=profile.timezone,
            email_notifications_enabled=profile.email_notifications_enabled or False,
            push_notifications_enabled=profile.push_notifications_enabled or False,
            weekly_summary_email_enabled=profile.weekly_summary_email_enabled or False,
        )

