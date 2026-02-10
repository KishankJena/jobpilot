"""API routes for job application tracking."""
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.dependencies.dependency import get_current_user
from app.model.models import JobApplicationStatusEnum
from app.services.job_application.schemas import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationStatusUpdate,
    JobApplicationResponse,
    PaginatedJobApplicationsResponse,
    JobApplicationStatusHistoryItem,
    KanbanBoardResponse,
)
from app.services.job_application.service import JobApplicationService


router = APIRouter(
    prefix="/applications",
    tags=["Job Applications"],
)


def _get_service(
    session: AsyncSession = Depends(get_db_session),
) -> JobApplicationService:
    return JobApplicationService(session)


@router.get(
    "",
    response_model=PaginatedJobApplicationsResponse,
    summary="List job applications",
    description="List current user's job applications with pagination, filtering, and sorting.",
)
async def list_applications(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[JobApplicationStatusEnum] = None,
    company: Optional[str] = None,
    search: Optional[str] = None,
    order_by: str = "created_at",
    sort_dir: str = "desc",
    current_user=Depends(get_current_user),
    service: JobApplicationService = Depends(_get_service),
) -> PaginatedJobApplicationsResponse:
    return await service.list_applications(
        user_id=current_user["user_id"],
        page=page,
        page_size=page_size,
        status=status_filter,
        company=company,
        search=search,
        order_by=order_by,
        sort_dir=sort_dir,
    )


@router.post(
    "",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job application",
)
async def create_application(
    payload: JobApplicationCreate,
    current_user=Depends(get_current_user),
    service: JobApplicationService = Depends(_get_service),
) -> JobApplicationResponse:
    return await service.create_application(
        user_id=current_user["user_id"],
        payload=payload,
    )


@router.get(
    "/{application_id}",
    response_model=JobApplicationResponse,
    summary="Get job application",
)
async def get_application(
    application_id: str,
    current_user=Depends(get_current_user),
    service: JobApplicationService = Depends(_get_service),
) -> JobApplicationResponse:
    return await service.get_application(
        user_id=current_user["user_id"],
        application_id=application_id,
    )


@router.put(
    "/{application_id}",
    response_model=JobApplicationResponse,
    summary="Update job application",
)
async def update_application(
    application_id: str,
    payload: JobApplicationUpdate,
    current_user=Depends(get_current_user),
    service: JobApplicationService = Depends(_get_service),
) -> JobApplicationResponse:
    return await service.update_application(
        user_id=current_user["user_id"],
        application_id=application_id,
        payload=payload,
    )


@router.patch(
    "/{application_id}/status",
    response_model=JobApplicationResponse,
    summary="Change application status",
    description="Update high-level status and Kanban column; records a status history entry.",
)
async def change_status(
    application_id: str,
    payload: JobApplicationStatusUpdate,
    current_user=Depends(get_current_user),
    service: JobApplicationService = Depends(_get_service),
) -> JobApplicationResponse:
    return await service.update_status(
        user_id=current_user["user_id"],
        application_id=application_id,
        payload=payload,
    )


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete job application (soft delete)",
)
async def delete_application(
    application_id: str,
    current_user=Depends(get_current_user),
    service: JobApplicationService = Depends(_get_service),
) -> None:
    await service.delete_application(
        user_id=current_user["user_id"],
        application_id=application_id,
    )


@router.get(
    "/{application_id}/status-history",
    response_model=list[JobApplicationStatusHistoryItem],
    summary="Get status history",
)
async def get_status_history(
    application_id: str,
    current_user=Depends(get_current_user),
    service: JobApplicationService = Depends(_get_service),
) -> list[JobApplicationStatusHistoryItem]:
    return await service.list_status_history(
        user_id=current_user["user_id"],
        application_id=application_id,
    )


@router.get(
    "/kanban",
    response_model=KanbanBoardResponse,
    summary="Get Kanban board",
    description="Return job applications grouped into Kanban columns.",
)
async def get_kanban_board(
    current_user=Depends(get_current_user),
    service: JobApplicationService = Depends(_get_service),
) -> KanbanBoardResponse:
    return await service.get_kanban_board(user_id=current_user["user_id"])

