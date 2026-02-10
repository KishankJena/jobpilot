"""Repository for job application and status history operations."""
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.repository.base_async_repository import BaseAsyncRepository
from app.model.models import (
    JobApplication,
    JobApplicationStatusHistory,
    JobApplicationStatusEnum,
)
from app.exceptions.exceptions import DatabaseException


class JobApplicationRepository(BaseAsyncRepository[JobApplication]):
    """Repository for `JobApplication` with user-scoped queries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(JobApplication, session)

    async def get_for_user(
        self,
        *,
        user_id: str,
        status: Optional[JobApplicationStatusEnum] = None,
        company_like: Optional[str] = None,
        search: Optional[str] = None,
        order_by: str = "created_at",
        sort_dir: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[JobApplication], int]:
        """Return paginated list of applications for a user with filters."""
        try:
            query = select(JobApplication).where(
                JobApplication.user_id == user_id,
                JobApplication.is_deleted.is_(False),
            )

            if status:
                query = query.where(JobApplication.status == status)

            if company_like:
                pattern = f"%{company_like.lower()}%"
                query = query.where(
                    func.lower(JobApplication.company_name).like(pattern)
                )

            if search:
                pattern = f"%{search.lower()}%"
                query = query.where(
                    or_(
                        func.lower(JobApplication.job_title).like(pattern),
                        func.lower(JobApplication.company_name).like(pattern),
                    )
                )

            # Sorting
            field_map = {
                "created_at": JobApplication.created_at,
                "applied_at": JobApplication.applied_at,
                "last_status_change_at": JobApplication.last_status_change_at,
            }
            sort_field = field_map.get(order_by, JobApplication.created_at)
            if sort_dir.lower() == "asc":
                query = query.order_by(sort_field.asc())
            else:
                query = query.order_by(sort_field.desc())

            count_query = select(func.count()).select_from(query.subquery())

            total_result = await self.session.execute(count_query)
            total = total_result.scalar_one()

            result = await self.session.execute(query.offset(skip).limit(limit))
            items = result.scalars().all()

            return items, total
        except Exception as exc:  # pragma: no cover - defensive
            raise DatabaseException(f"Failed to list applications: {exc}")

    async def get_by_id_for_user(
        self,
        *,
        application_id: str,
        user_id: str,
    ) -> Optional[JobApplication]:
        """Get application by id for a given user."""
        try:
            result = await self.session.execute(
                select(JobApplication).where(
                    JobApplication.id == application_id,
                    JobApplication.user_id == user_id,
                    JobApplication.is_deleted.is_(False),
                )
            )
            return result.scalar_one_or_none()
        except Exception as exc:
            raise DatabaseException(f"Failed to get application: {exc}")

    async def soft_delete_for_user(
        self,
        *,
        application_id: str,
        user_id: str,
    ) -> bool:
        """Soft delete an application."""
        app = await self.get_by_id_for_user(application_id=application_id, user_id=user_id)
        if app is None:
            return False
        app.is_deleted = True
        await self.session.flush()
        await self.commit()
        return True


class JobApplicationStatusHistoryRepository(BaseAsyncRepository[JobApplicationStatusHistory]):
    """Repository for immutable status history entries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(JobApplicationStatusHistory, session)

    async def list_for_application(
        self,
        application_id: str,
    ) -> List[JobApplicationStatusHistory]:
        try:
            result = await self.session.execute(
                select(JobApplicationStatusHistory)
                .where(JobApplicationStatusHistory.application_id == application_id)
                .order_by(JobApplicationStatusHistory.changed_at.asc())
            )
            return result.scalars().all()
        except Exception as exc:
            raise DatabaseException(f"Failed to list status history: {exc}")

