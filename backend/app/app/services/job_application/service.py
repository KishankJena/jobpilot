"""Business logic for job application tracking and Kanban support."""
from datetime import datetime, timezone
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import ValidationException, AuthorizationException
from app.model.models import JobApplicationStatusEnum
from app.services.job_application.repository import (
    JobApplicationRepository,
    JobApplicationStatusHistoryRepository,
)
from app.services.job_application.schemas import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationStatusUpdate,
    JobApplicationResponse,
    PaginatedJobApplicationsResponse,
    JobApplicationStatusHistoryItem,
    KanbanBoardResponse,
    KanbanColumn,
)


class JobApplicationService:
    """Service encapsulating job application lifecycle operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.app_repo = JobApplicationRepository(session)
        self.history_repo = JobApplicationStatusHistoryRepository(session)

    async def list_applications(
        self,
        *,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        status: JobApplicationStatusEnum | None = None,
        company: str | None = None,
        search: str | None = None,
        order_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PaginatedJobApplicationsResponse:
        if page <= 0:
            raise ValidationException("page must be >= 1")
        if page_size <= 0 or page_size > 100:
            raise ValidationException("page_size must be between 1 and 100")

        skip = (page - 1) * page_size
        items, total = await self.app_repo.get_for_user(
            user_id=user_id,
            status=status,
            company_like=company,
            search=search,
            order_by=order_by,
            sort_dir=sort_dir,
            skip=skip,
            limit=page_size,
        )
        return PaginatedJobApplicationsResponse(
            items=[JobApplicationResponse.model_validate(a) for a in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def create_application(
        self,
        *,
        user_id: str,
        payload: JobApplicationCreate,
    ) -> JobApplicationResponse:
        data = payload.model_dump(exclude_unset=True)
        # Default kanban column to status if not explicitly provided.
        status = data.get("status") or JobApplicationStatusEnum.PROSPECT
        data.setdefault("status", status)
        data.setdefault("kanban_column", status.value)
        data["user_id"] = user_id
        now = datetime.now(timezone.utc)
        data.setdefault("last_status_change_at", now)

        app = await self.app_repo.create(data)
        await self.app_repo.commit()

        # Seed initial status history entry
        await self.history_repo.create(
            {
                "application_id": app.id,
                "from_status": None,
                "to_status": status,
                "changed_at": now,
                "note": "Application created",
            }
        )
        await self.history_repo.commit()

        return JobApplicationResponse.model_validate(app)

    async def get_application(
        self,
        *,
        user_id: str,
        application_id: str,
    ) -> JobApplicationResponse:
        app = await self.app_repo.get_by_id_for_user(
            application_id=application_id, user_id=user_id
        )
        if app is None:
            raise AuthorizationException("Application not found or not accessible")
        return JobApplicationResponse.model_validate(app)

    async def update_application(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: JobApplicationUpdate,
    ) -> JobApplicationResponse:
        app = await self.app_repo.get_by_id_for_user(
            application_id=application_id, user_id=user_id
        )
        if app is None:
            raise AuthorizationException("Application not found or not accessible")

        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(app, field, value)
        await self.session.flush()
        await self.app_repo.commit()

        return JobApplicationResponse.model_validate(app)

    async def update_status(
        self,
        *,
        user_id: str,
        application_id: str,
        payload: JobApplicationStatusUpdate,
    ) -> JobApplicationResponse:
        app = await self.app_repo.get_by_id_for_user(
            application_id=application_id, user_id=user_id
        )
        if app is None:
            raise AuthorizationException("Application not found or not accessible")

        previous_status = app.status
        new_status = payload.status

        now = datetime.now(timezone.utc)
        app.status = new_status
        app.kanban_column = payload.kanban_column or new_status.value
        app.last_status_change_at = now

        await self.session.flush()
        await self.app_repo.commit()

        await self.history_repo.create(
            {
                "application_id": app.id,
                "from_status": previous_status,
                "to_status": new_status,
                "changed_at": now,
                "note": payload.note,
            }
        )
        await self.history_repo.commit()

        return JobApplicationResponse.model_validate(app)

    async def delete_application(
        self,
        *,
        user_id: str,
        application_id: str,
    ) -> None:
        deleted = await self.app_repo.soft_delete_for_user(
            application_id=application_id, user_id=user_id
        )
        if not deleted:
            raise AuthorizationException("Application not found or not accessible")

    async def list_status_history(
        self,
        *,
        user_id: str,
        application_id: str,
    ) -> List[JobApplicationStatusHistoryItem]:
        # Ensure user owns the application before returning history
        await self.get_application(user_id=user_id, application_id=application_id)
        history = await self.history_repo.list_for_application(application_id)
        return [JobApplicationStatusHistoryItem.model_validate(h) for h in history]

    async def get_kanban_board(
        self,
        *,
        user_id: str,
    ) -> KanbanBoardResponse:
        """Return applications grouped into Kanban columns."""
        # We intentionally keep this simple; front-end can derive swimlanes etc.
        apps, _ = await self.app_repo.get_for_user(
            user_id=user_id,
            skip=0,
            limit=1000,  # Kanban is typically visual; large boards can be paginated client-side.
        )
        by_status: dict[JobApplicationStatusEnum, list[JobApplicationResponse]] = {
            s: [] for s in JobApplicationStatusEnum
        }
        for app in apps:
            by_status[app.status].append(JobApplicationResponse.model_validate(app))

        columns: list[KanbanColumn] = []
        for status in JobApplicationStatusEnum:
            columns.append(
                KanbanColumn(
                    key=status.value,
                    label=status.name.replace("_", " ").title(),
                    status=status,
                    applications=by_status[status],
                )
            )

        return KanbanBoardResponse(columns=columns)

