"""Business logic for resume CRUD, analysis, matching, and AI customization."""
from datetime import datetime, timezone
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies.ai_client import get_ai_client
from app.exceptions.exceptions import AuthorizationException, ValidationException
from app.model.models import (
    Resume,
    ResumeVersion,
    ResumeAnalysis,
    JobDescription,
    ResumeJobMatch,
    ResumeEditSuggestion,
)
from app.services.ai.base import ChatMessage
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


class ResumeService:
    """Service implementing core resume workflows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_resumes(self, user_id: str) -> List[ResumeResponse]:
        result = await self.session.execute(
            select(Resume).where(
                Resume.user_id == user_id,
                Resume.is_deleted.is_(False),
            )
        )
        items = result.scalars().all()
        return [ResumeResponse.model_validate(r) for r in items]

    async def create_resume(
        self,
        *,
        user_id: str,
        payload: ResumeCreate,
    ) -> ResumeResponse:
        data = payload.model_dump(exclude_unset=True)
        resume = Resume(user_id=user_id, **data)
        self.session.add(resume)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(resume)
        return ResumeResponse.model_validate(resume)

    async def update_resume(
        self,
        *,
        user_id: str,
        resume_id: str,
        payload: ResumeUpdate,
    ) -> ResumeResponse:
        resume = await self._get_resume_owned_by_user(resume_id, user_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(resume, field, value)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(resume)
        return ResumeResponse.model_validate(resume)

    async def delete_resume(self, *, user_id: str, resume_id: str) -> None:
        resume = await self._get_resume_owned_by_user(resume_id, user_id)
        resume.is_deleted = True
        await self.session.flush()
        await self.session.commit()

    async def list_versions(
        self,
        *,
        user_id: str,
        resume_id: str,
    ) -> List[ResumeVersionResponse]:
        await self._get_resume_owned_by_user(resume_id, user_id)
        result = await self.session.execute(
            select(ResumeVersion)
            .where(ResumeVersion.resume_id == resume_id)
            .order_by(ResumeVersion.created_at.desc())
        )
        items = result.scalars().all()
        return [ResumeVersionResponse.model_validate(v) for v in items]

    async def create_version(
        self,
        *,
        user_id: str,
        resume_id: str,
        payload: ResumeVersionCreate,
    ) -> ResumeVersionResponse:
        resume = await self._get_resume_owned_by_user(resume_id, user_id)
        data = payload.model_dump(exclude_unset=True)
        if not data.get("version_label"):
            # Generate a simple label based on count
            count_result = await self.session.execute(
                select(ResumeVersion)
                .where(ResumeVersion.resume_id == resume_id)
            )
            count = len(count_result.scalars().all())
            data["version_label"] = f"v{count + 1}"

        version = ResumeVersion(
            resume_id=resume.id,
            **data,
        )
        self.session.add(version)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(version)
        return ResumeVersionResponse.model_validate(version)

    async def analyze_version(
        self,
        *,
        user_id: str,
        resume_id: str,
        version_id: str,
    ) -> ResumeAnalysisResponse:
        await self._get_resume_owned_by_user(resume_id, user_id)
        version = await self._get_version_owned_by_user(version_id, user_id)

        ai_client = await get_ai_client()

        system_prompt = (
            "You are an expert, ethical career coach. "
            "Analyze the following resume. Do not invent experience or skills. "
            "Focus on structure, clarity, and impact. Respond with a concise JSON object "
            "containing overall_score (0-1), structure_score, clarity_score, impact_score, "
            "strengths (list), weaknesses (list), and suggestions (list of concrete edits)."
        )
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=version.content),
        ]

        result = await ai_client.chat_completion(
            model="resume-analysis",
            messages=messages,
            temperature=0.2,
            max_tokens=800,
            metadata={"tool": "resume_analysis"},
        )
        content = result.choices[0].message.content

        # In a production system this would be robust JSON parsing with validation.
        # Here we keep it simple and defensive.
        import json  # local import to avoid polluting module namespace

        try:
            parsed = json.loads(content)
        except Exception as exc:
            raise ValidationException(
                "AI provider returned an unexpected format",
                detail={"error": "invalid_ai_response", "raw": str(exc)},
            )

        analysis = ResumeAnalysis(
            resume_version_id=version.id,
            overall_score=parsed.get("overall_score"),
            structure_score=parsed.get("structure_score"),
            clarity_score=parsed.get("clarity_score"),
            impact_score=parsed.get("impact_score"),
            strengths={"items": parsed.get("strengths", [])},
            weaknesses={"items": parsed.get("weaknesses", [])},
            suggestions={"items": parsed.get("suggestions", [])},
        )
        self.session.add(analysis)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(analysis)
        return ResumeAnalysisResponse.model_validate(analysis)

    async def create_job_description(
        self,
        *,
        user_id: str,
        payload: JobDescriptionCreate,
    ) -> JobDescriptionResponse:
        jd = JobDescription(user_id=user_id, **payload.model_dump(exclude_unset=True))
        self.session.add(jd)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(jd)
        return JobDescriptionResponse.model_validate(jd)

    async def create_match(
        self,
        *,
        user_id: str,
        version_id: str,
        job_description_id: str,
    ) -> ResumeJobMatchResponse:
        version = await self._get_version_owned_by_user(version_id, user_id)
        jd = await self._get_job_description_owned_by_user(job_description_id, user_id)

        ai_client = await get_ai_client()
        system_prompt = (
            "Compare the resume and job description. "
            "Return concise JSON with match_score (0-1), missing_skills (list of strings), "
            "and summary (short text). Do not invent skills not present in the resume."
        )
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(
                role="user",
                content=f"RESUME:\n{version.content}\n\nJOB DESCRIPTION:\n{jd.raw_text}",
            ),
        ]
        result = await ai_client.chat_completion(
            model="resume-jd-match",
            messages=messages,
            temperature=0.2,
            max_tokens=600,
            metadata={"tool": "resume_job_match"},
        )

        import json  # local import

        try:
            parsed = json.loads(result.choices[0].message.content)
        except Exception as exc:
            raise ValidationException(
                "AI provider returned an unexpected format",
                detail={"error": "invalid_ai_response", "raw": str(exc)},
            )

        match = ResumeJobMatch(
            resume_version_id=version.id,
            job_description_id=jd.id,
            match_score=float(parsed.get("match_score", 0.0)),
            missing_skills=parsed.get("missing_skills", []),
            summary=parsed.get("summary"),
        )
        self.session.add(match)
        await self.session.flush()
        await self.session.commit()
        await self.session.refresh(match)
        return ResumeJobMatchResponse.model_validate(match)

    async def generate_edit_suggestions(
        self,
        *,
        user_id: str,
        version_id: str,
        payload: ResumeEditSuggestionCreate,
    ) -> List[ResumeEditSuggestionResponse]:
        version = await self._get_version_owned_by_user(version_id, user_id)
        jd = None
        if payload.job_description_id:
            jd = await self._get_job_description_owned_by_user(
                payload.job_description_id, user_id
            )

        ai_client = await get_ai_client()
        context_intro = (
            "You are an ethical career coach. Suggest concrete text edits to improve the "
            "resume for the stated goals. Do NOT fabricate skills, employers, dates, or titles. "
            "Return JSON with 'suggestions': a list of objects with "
            "original_excerpt, suggested_excerpt, and rationale."
        )
        user_content = f"INSTRUCTIONS:\n{payload.instructions}\n\nRESUME:\n{version.content}"
        if jd:
            user_content += f"\n\nJOB DESCRIPTION:\n{jd.raw_text}"

        messages = [
            ChatMessage(role="system", content=context_intro),
            ChatMessage(role="user", content=user_content),
        ]
        result = await ai_client.chat_completion(
            model="resume-edit-suggestions",
            messages=messages,
            temperature=0.4,
            max_tokens=900,
            metadata={"tool": "resume_edit_suggestions"},
        )

        import json  # local import

        try:
            parsed = json.loads(result.choices[0].message.content)
        except Exception as exc:
            raise ValidationException(
                "AI provider returned an unexpected format",
                detail={"error": "invalid_ai_response", "raw": str(exc)},
            )

        raw_suggestions = parsed.get("suggestions", [])
        if not isinstance(raw_suggestions, list):
            raise ValidationException(
                "AI provider returned an unexpected format",
                detail={"error": "invalid_ai_response", "raw": "suggestions not a list"},
            )

        responses: list[ResumeEditSuggestionResponse] = []
        now = datetime.now(timezone.utc)
        for item in raw_suggestions:
            suggestion = ResumeEditSuggestion(
                resume_version_id=version.id,
                job_description_id=jd.id if jd else None,
                original_excerpt=item.get("original_excerpt", ""),
                suggested_excerpt=item.get("suggested_excerpt", ""),
                rationale=item.get("rationale"),
                created_at=now,
            )
            self.session.add(suggestion)
            await self.session.flush()
            responses.append(
                ResumeEditSuggestionResponse.model_validate(suggestion)
            )

        await self.session.commit()
        return responses

    # ------- helper lookups -------

    async def _get_resume_owned_by_user(self, resume_id: str, user_id: str) -> Resume:
        result = await self.session.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
                Resume.is_deleted.is_(False),
            )
        )
        resume = result.scalar_one_or_none()
        if resume is None:
            raise AuthorizationException("Resume not found or not accessible")
        return resume

    async def _get_version_owned_by_user(
        self,
        version_id: str,
        user_id: str,
    ) -> ResumeVersion:
        result = await self.session.execute(
            select(ResumeVersion, Resume)
            .join(Resume, ResumeVersion.resume_id == Resume.id)
            .where(
                ResumeVersion.id == version_id,
                Resume.user_id == user_id,
                Resume.is_deleted.is_(False),
            )
        )
        row = result.first()
        if not row:
            raise AuthorizationException("Resume version not found or not accessible")
        version: ResumeVersion = row[0]
        return version

    async def _get_job_description_owned_by_user(
        self,
        job_description_id: str,
        user_id: str,
    ) -> JobDescription:
        result = await self.session.execute(
            select(JobDescription).where(
                JobDescription.id == job_description_id,
                JobDescription.user_id == user_id,
            )
        )
        jd = result.scalar_one_or_none()
        if jd is None:
            raise AuthorizationException("Job description not found or not accessible")
        return jd

