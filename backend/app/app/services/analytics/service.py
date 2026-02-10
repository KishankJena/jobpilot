"""Business logic for analytics and rejection insights."""
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.dependencies.ai_client import get_ai_client
from app.model.models import (
    JobApplication,
    JobApplicationStatusEnum,
    RejectionInsight,
)
from app.services.ai.base import ChatMessage
from app.services.analytics.schemas import (
    ApplicationsFunnelResponse,
    FunnelStageCounts,
    RejectionInsightCreate,
    RejectionInsightResponse,
)


class AnalyticsService:
    """Service for computing aggregate analytics metrics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def applications_funnel(self, *, user_id: str) -> ApplicationsFunnelResponse:
        """Return simple funnel counts by application status."""
        result = await self.session.execute(
            select(
                JobApplication.status,
                func.count().label("count"),
            ).where(
                JobApplication.user_id == user_id,
                JobApplication.is_deleted.is_(False),
            ).group_by(JobApplication.status)
        )
        rows = result.all()
        counts = {status: 0 for status in JobApplicationStatusEnum}
        total = 0
        for status, count in rows:
            counts[status] = count
            total += count

        return ApplicationsFunnelResponse(
            total=total,
            stages=FunnelStageCounts(
                prospect=counts[JobApplicationStatusEnum.PROSPECT],
                applied=counts[JobApplicationStatusEnum.APPLIED],
                interviewing=counts[JobApplicationStatusEnum.INTERVIEWING],
                offer=counts[JobApplicationStatusEnum.OFFER],
                rejected=counts[JobApplicationStatusEnum.REJECTED],
                on_hold=counts[JobApplicationStatusEnum.ON_HOLD],
                withdrawn=counts[JobApplicationStatusEnum.WITHDRAWN],
            ),
        )


class RejectionInsightsService:
    """Service for AI-assisted rejection pattern analysis."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate_insights(
        self,
        *,
        user_id: str,
        payload: RejectionInsightCreate,
    ) -> List[RejectionInsightResponse]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=payload.focus_period_days)
        result = await self.session.execute(
            select(JobApplication)
            .where(
                JobApplication.user_id == user_id,
                JobApplication.status == JobApplicationStatusEnum.REJECTED,
                JobApplication.created_at >= cutoff,
            )
            .order_by(JobApplication.created_at.desc())
        )
        rejections = result.scalars().all()

        # Short-circuit if there is nothing to analyze.
        if not rejections:
            return []

        ai_client = await get_ai_client()

        text_summary = "\n\n".join(
            [
                f"- {r.company_name} / {r.job_title} (applied {r.applied_at}, notes: {r.notes or 'n/a'})"
                for r in rejections
            ]
        )
        system_prompt = (
            "You are an empathetic career coach. Analyze these rejected applications "
            "for supportive, constructive patterns. Never blame the user; focus on "
            "specific, actionable recommendations (e.g., tailoring resumes, targeting "
            "roles better, improving interview prep). Return JSON with 'insights': a "
            "list of objects containing insight, recommended_actions (list of strings), "
            "and tags (list of strings)."
        )
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=text_summary),
        ]
        result_ai = await ai_client.chat_completion(
            model="rejection-insights",
            messages=messages,
            temperature=0.4,
            max_tokens=800,
            metadata={"tool": "rejection_insights"},
        )

        import json  # local import

        try:
            parsed = json.loads(result_ai.choices[0].message.content)
        except Exception:
            # If parsing fails, gracefully degrade by not persisting any insights.
            return []

        raw_insights = parsed.get("insights", [])
        if not isinstance(raw_insights, list):
            return []

        responses: list[RejectionInsightResponse] = []
        for item in raw_insights:
            insight = RejectionInsight(
                user_id=user_id,
                job_application_id=None,
                insight=item.get("insight", ""),
                recommended_actions=item.get("recommended_actions"),
                tags=item.get("tags"),
            )
            self.session.add(insight)
            await self.session.flush()
            responses.append(RejectionInsightResponse.model_validate(insight))

        await self.session.commit()
        return responses

    async def list_insights(self, *, user_id: str) -> List[RejectionInsightResponse]:
        result = await self.session.execute(
            select(RejectionInsight)
            .where(RejectionInsight.user_id == user_id)
            .order_by(RejectionInsight.created_at.desc())
        )
        items = result.scalars().all()
        return [RejectionInsightResponse.model_validate(i) for i in items]

