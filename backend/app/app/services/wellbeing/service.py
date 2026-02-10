"""Business logic for wellbeing check-ins and burnout monitoring."""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.model.models import WellbeingCheckIn
from app.services.wellbeing.schemas import (
    WellbeingCheckInCreate,
    WellbeingCheckInResponse,
)


class WellbeingService:
    """Service for recording and retrieving wellbeing check-ins."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_checkin(
        self,
        *,
        user_id: str,
        payload: WellbeingCheckInCreate,
    ) -> WellbeingCheckInResponse:
        data = payload.model_dump(exclude_unset=True)
        # Simple heuristic for burnout_risk_level – could be replaced by AI later.
        mood = data.get("mood_score", 3)
        stress = data.get("stress_level", 3)
        if mood <= 2 and stress >= 4:
            risk = "high"
        elif mood <= 3 and stress >= 3:
            risk = "medium"
        else:
            risk = "low"

        checkin = WellbeingCheckIn(
            user_id=user_id,
            burnout_risk_level=risk,
            **data,
        )
        self.session.add(checkin)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(checkin)
        return WellbeingCheckInResponse.model_validate(checkin)

    async def list_checkins(self, *, user_id: str) -> List[WellbeingCheckInResponse]:
        result = await self.session.execute(
            select(WellbeingCheckIn)
            .where(WellbeingCheckIn.user_id == user_id)
            .order_by(WellbeingCheckIn.created_at.desc())
        )
        items = result.scalars().all()
        return [WellbeingCheckInResponse.model_validate(c) for c in items]

