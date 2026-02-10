"""API routes for resume management, analysis, and AI customization."""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.dependencies.dependency import get_current_user
from app.services.resume.schemas import (
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeVersionCreate,
    ResumeVersionResponse,
    ResumeAnalysisResponse,
    JobDescriptionCreate,
    JobDescriptionResponse,
    ResumeJobMatchResponse,
    ResumeEditSuggestionCreate,
    ResumeEditSuggestionResponse,
)
from app.services.resume.service import ResumeService


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


def _get_service(session: AsyncSession = Depends(get_db_session)) -> ResumeService:
    return ResumeService(session)


@router.get(
    "",
    response_model=List[ResumeResponse],
    summary="List resumes",
)
async def list_resumes(
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> List[ResumeResponse]:
    return await service.list_resumes(current_user["user_id"])


@router.post(
    "",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create resume",
)
async def create_resume(
    payload: ResumeCreate,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> ResumeResponse:
    return await service.create_resume(user_id=current_user["user_id"], payload=payload)


@router.put(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Update resume",
)
async def update_resume(
    resume_id: str,
    payload: ResumeUpdate,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> ResumeResponse:
    return await service.update_resume(
        user_id=current_user["user_id"],
        resume_id=resume_id,
        payload=payload,
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resume (soft delete)",
)
async def delete_resume(
    resume_id: str,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> None:
    await service.delete_resume(user_id=current_user["user_id"], resume_id=resume_id)


@router.get(
    "/{resume_id}/versions",
    response_model=List[ResumeVersionResponse],
    summary="List resume versions",
)
async def list_versions(
    resume_id: str,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> List[ResumeVersionResponse]:
    return await service.list_versions(
        user_id=current_user["user_id"],
        resume_id=resume_id,
    )


@router.post(
    "/{resume_id}/versions",
    response_model=ResumeVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create resume version",
)
async def create_version(
    resume_id: str,
    payload: ResumeVersionCreate,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> ResumeVersionResponse:
    return await service.create_version(
        user_id=current_user["user_id"],
        resume_id=resume_id,
        payload=payload,
    )


@router.post(
    "/{resume_id}/versions/{version_id}/analyze",
    response_model=ResumeAnalysisResponse,
    summary="Analyze resume version",
)
async def analyze_version(
    resume_id: str,
    version_id: str,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> ResumeAnalysisResponse:
    return await service.analyze_version(
        user_id=current_user["user_id"],
        resume_id=resume_id,
        version_id=version_id,
    )


@router.post(
    "/job-descriptions",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create job description",
)
async def create_job_description(
    payload: JobDescriptionCreate,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> JobDescriptionResponse:
    return await service.create_job_description(
        user_id=current_user["user_id"],
        payload=payload,
    )


@router.post(
    "/matches",
    response_model=ResumeJobMatchResponse,
    summary="Create resume vs job description match",
)
async def create_match(
    version_id: str,
    job_description_id: str,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> ResumeJobMatchResponse:
    return await service.create_match(
        user_id=current_user["user_id"],
        version_id=version_id,
        job_description_id=job_description_id,
    )


@router.post(
    "/versions/{version_id}/ai-suggestions",
    response_model=List[ResumeEditSuggestionResponse],
    summary="Generate AI resume edit suggestions",
)
async def generate_ai_suggestions(
    version_id: str,
    payload: ResumeEditSuggestionCreate,
    current_user=Depends(get_current_user),
    service: ResumeService = Depends(_get_service),
) -> List[ResumeEditSuggestionResponse]:
    return await service.generate_edit_suggestions(
        user_id=current_user["user_id"],
        version_id=version_id,
        payload=payload,
    )

