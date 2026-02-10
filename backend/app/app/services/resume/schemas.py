"""Pydantic schemas for resume management and analysis."""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class ResumeBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=4000)
    is_primary: Optional[bool] = False


class ResumeCreate(ResumeBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "General SWE Resume",
                "description": "Default resume for software engineering roles.",
                "is_primary": True,
            }
        }
    )


class ResumeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=4000)
    is_primary: Optional[bool] = None


class ResumeResponse(ResumeBase):
    id: str
    user_id: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeVersionCreate(BaseModel):
    version_label: Optional[str] = Field(
        None, max_length=64, description="Short label for this version."
    )
    base_version_id: Optional[str] = None
    content: str = Field(..., description="Resume content in markdown or plain text.")


class ResumeVersionResponse(BaseModel):
    id: str
    resume_id: str
    version_label: str
    base_version_id: Optional[str]
    content: str
    is_ai_generated: bool
    ai_explanation: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeAnalysisResponse(BaseModel):
    id: str
    resume_version_id: str
    overall_score: Optional[float]
    structure_score: Optional[float]
    clarity_score: Optional[float]
    impact_score: Optional[float]
    strengths: Optional[Dict[str, Any]]
    weaknesses: Optional[Dict[str, Any]]
    suggestions: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobDescriptionCreate(BaseModel):
    title: str = Field(..., max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=1024)
    raw_text: str = Field(..., description="Raw job description text.")


class JobDescriptionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: Optional[str]
    source_url: Optional[str]
    raw_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeJobMatchResponse(BaseModel):
    id: str
    resume_version_id: str
    job_description_id: str
    match_score: float
    missing_skills: Optional[List[str]]
    summary: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeEditSuggestionCreate(BaseModel):
    job_description_id: Optional[str] = None
    instructions: str = Field(
        ...,
        description=(
            "High-level guidance for tailoring the resume (e.g., 'focus on leadership "
            "and cross-functional collaboration')."
        ),
    )


class ResumeEditSuggestionResponse(BaseModel):
    id: str
    resume_version_id: str
    job_description_id: Optional[str]
    original_excerpt: str
    suggested_excerpt: str
    rationale: Optional[str]
    status: str
    created_at: datetime
    decided_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

