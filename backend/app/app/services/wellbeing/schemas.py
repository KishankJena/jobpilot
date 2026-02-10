"""Pydantic schemas for wellbeing check-ins."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class WellbeingCheckInCreate(BaseModel):
    mood_score: int = Field(..., ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(
        None,
        max_length=4000,
        description="Optional, private journal-style note about how you're feeling.",
    )


class WellbeingCheckInResponse(BaseModel):
    id: str
    user_id: str
    mood_score: int
    energy_level: Optional[int]
    stress_level: Optional[int]
    notes: Optional[str]
    burnout_risk_level: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WellbeingCheckInListResponse(BaseModel):
    items: List[WellbeingCheckInResponse]

