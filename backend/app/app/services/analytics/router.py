"""API routes for analytics and rejection insights."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.dependencies.dependency import get_current_user
from app.services.analytics.schemas import (
    ApplicationsFunnelResponse,
    RejectionInsightCreate,
    RejectionInsightResponse,
    RejectionInsightsListResponse,
)
from app.services.analytics.service import AnalyticsService, RejectionInsightsService


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


def _get_analytics_service(
    session: AsyncSession = Depends(get_db_session),
) -> AnalyticsService:
    return AnalyticsService(session)


def _get_rejection_insights_service(
    session: AsyncSession = Depends(get_db_session),
) -> RejectionInsightsService:
    return RejectionInsightsService(session)


@router.get(
    "/applications/funnel",
    response_model=ApplicationsFunnelResponse,
    summary="Get application funnel metrics",
)
async def get_applications_funnel(
    current_user=Depends(get_current_user),
    service: AnalyticsService = Depends(_get_analytics_service),
) -> ApplicationsFunnelResponse:
    return await service.applications_funnel(user_id=current_user["user_id"])


@router.post(
    "/rejection-insights",
    response_model=List[RejectionInsightResponse],
    summary="Generate rejection insights",
)
async def generate_rejection_insights(
    payload: RejectionInsightCreate,
    current_user=Depends(get_current_user),
    service: RejectionInsightsService = Depends(_get_rejection_insights_service),
) -> List[RejectionInsightResponse]:
    return await service.generate_insights(
        user_id=current_user["user_id"],
        payload=payload,
    )


@router.get(
    "/rejection-insights",
    response_model=RejectionInsightsListResponse,
    summary="List rejection insights",
)
async def list_rejection_insights(
    current_user=Depends(get_current_user),
    service: RejectionInsightsService = Depends(_get_rejection_insights_service),
) -> RejectionInsightsListResponse:
    items: List[RejectionInsightResponse] = await service.list_insights(
        user_id=current_user["user_id"]
    )
    return RejectionInsightsListResponse(items=items)

