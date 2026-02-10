"""Pydantic schemas for job search analytics and rejection insights."""
from datetime import datetime
from typing import Dict, Any, List

from pydantic import BaseModel, Field


class FunnelStageCounts(BaseModel):
    prospect: int = 0
    applied: int = 0
    interviewing: int = 0
    offer: int = 0
    rejected: int = 0
    on_hold: int = 0
    withdrawn: int = 0


class ApplicationsFunnelResponse(BaseModel):
    """High-level funnel metrics across application statuses."""

    total: int
    stages: FunnelStageCounts


class RejectionInsightCreate(BaseModel):
    """Request body for generating rejection insights."""

    focus_period_days: int = Field(
        60,
        ge=7,
        le=365,
        description="How far back to look when analyzing patterns.",
    )


class RejectionInsightResponse(BaseModel):
    id: str
    user_id: str
    job_application_id: str | None
    insight: str
    recommended_actions: List[str] | None
    tags: List[str] | None
    created_at: datetime


class RejectionInsightsListResponse(BaseModel):
    items: List[RejectionInsightResponse]

