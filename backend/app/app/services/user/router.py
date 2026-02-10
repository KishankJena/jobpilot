"""API routes for user profile and preferences."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.dependencies.dependency import get_current_user
from app.services.user.schemas import (
    UserProfileResponse,
    UserProfileUpdate,
    UserPreferencesResponse,
)
from app.services.user.service import UserProfileService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def _get_service(session: AsyncSession = Depends(get_db_session)) -> UserProfileService:
    return UserProfileService(session)


@router.get(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Get current user's profile",
    description="Retrieve the authenticated user's profile and preferences.",
)
async def get_my_profile(
    current_user=Depends(get_current_user),
    service: UserProfileService = Depends(_get_service),
) -> UserProfileResponse:
    return await service.get_profile(current_user["user_id"])


@router.put(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Upsert current user's profile",
    description="Create or update the authenticated user's profile.",
)
async def upsert_my_profile(
    payload: UserProfileUpdate,
    current_user=Depends(get_current_user),
    service: UserProfileService = Depends(_get_service),
) -> UserProfileResponse:
    return await service.upsert_profile(current_user["user_id"], payload)


@router.get(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    summary="Get current user's preferences",
)
async def get_my_preferences(
    current_user=Depends(get_current_user),
    service: UserProfileService = Depends(_get_service),
) -> UserPreferencesResponse:
    return await service.get_preferences(current_user["user_id"])


@router.put(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    summary="Update current user's preferences",
)
async def update_my_preferences(
    payload: UserProfileUpdate,
    current_user=Depends(get_current_user),
    service: UserProfileService = Depends(_get_service),
) -> UserPreferencesResponse:
    return await service.update_preferences(current_user["user_id"], payload)

