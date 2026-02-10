"""API routes for wellbeing and burnout monitoring."""
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.dependencies.dependency import get_current_user
from app.services.wellbeing.schemas import (
    WellbeingCheckInCreate,
    WellbeingCheckInResponse,
    WellbeingCheckInListResponse,
)
from app.services.wellbeing.service import WellbeingService


router = APIRouter(
    prefix="/wellbeing",
    tags=["Wellbeing"],
)


def _get_service(session: AsyncSession = Depends(get_db_session)) -> WellbeingService:
    return WellbeingService(session)


@router.post(
    "/checkins",
    response_model=WellbeingCheckInResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create wellbeing check-in",
)
async def create_checkin(
    payload: WellbeingCheckInCreate,
    current_user=Depends(get_current_user),
    service: WellbeingService = Depends(_get_service),
) -> WellbeingCheckInResponse:
    return await service.create_checkin(
        user_id=current_user["user_id"],
        payload=payload,
    )


@router.get(
    "/checkins",
    response_model=WellbeingCheckInListResponse,
    summary="List wellbeing check-ins",
)
async def list_checkins(
    current_user=Depends(get_current_user),
    service: WellbeingService = Depends(_get_service),
) -> WellbeingCheckInListResponse:
    items: List[WellbeingCheckInResponse] = await service.list_checkins(
        user_id=current_user["user_id"]
    )
    return WellbeingCheckInListResponse(items=items)

