"""Repository for user profile data access operations."""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.repository.base_async_repository import BaseAsyncRepository
from app.model.models import UserProfile
from app.exceptions.exceptions import DatabaseException


class UserProfileRepository(BaseAsyncRepository[UserProfile]):
    """Repository for `UserProfile` model database operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(UserProfile, session)

    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve profile for a given user."""
        try:
            result = await self.session.execute(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as exc:  # pragma: no cover - defensive
            raise DatabaseException(f"Failed to get profile by user_id: {exc}")

    async def upsert_for_user(
        self,
        user_id: str,
        data: dict,
    ) -> UserProfile:
        """
        Create or update a profile for the user.

        This keeps a single profile row per user for simplicity.
        """
        try:
            profile = await self.get_by_user_id(user_id)
            if profile is None:
                payload = {"user_id": user_id, **data}
                profile = await self.create(payload)
            else:
                for field, value in data.items():
                    setattr(profile, field, value)
                await self.session.flush()

            await self.commit()
            await self.session.refresh(profile)
            return profile
        except Exception as exc:
            await self.rollback()
            raise DatabaseException(f"Failed to upsert profile for user: {exc}")

