"""Pydantic schemas for job application tracking."""
from datetime import datetime
from typing import Optional, List, Literal

from pydantic import BaseModel, Field, ConfigDict

from app.model.models import JobApplicationStatusEnum, JobApplicationSourceEnum


class JobApplicationBase(BaseModel):
    """Shared fields for job applications."""

    job_title: str = Field(..., max_length=255)
    company_name: str = Field(..., max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    job_url: Optional[str] = Field(
        None, max_length=1024, description="Link to the job description."
    )
    source: Optional[JobApplicationSourceEnum] = Field(
        default=JobApplicationSourceEnum.MANUAL
    )
    salary_min: Optional[float] = Field(default=None, ge=0)
    salary_max: Optional[float] = Field(default=None, ge=0)
    salary_currency: Optional[str] = Field(default=None, max_length=8)
    notes: Optional[str] = Field(default=None, max_length=4000)
    applied_at: Optional[datetime] = None


class JobApplicationCreate(JobApplicationBase):
    """Payload for creating a job application."""

    status: Optional[JobApplicationStatusEnum] = Field(
        default=JobApplicationStatusEnum.PROSPECT
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_title": "Senior Backend Engineer",
                "company_name": "Acme Corp",
                "location": "Remote",
                "job_url": "https://jobs.example.com/backend",
                "source": "linkedin",
                "status": "applied",
                "notes": "Referred by former colleague.",
            }
        }
    )


class JobApplicationUpdate(BaseModel):
    """Payload for updating general application fields."""

    job_title: Optional[str] = Field(None, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    job_url: Optional[str] = Field(None, max_length=1024)
    source: Optional[JobApplicationSourceEnum] = None
    salary_min: Optional[float] = Field(default=None, ge=0)
    salary_max: Optional[float] = Field(default=None, ge=0)
    salary_currency: Optional[str] = Field(default=None, max_length=8)
    notes: Optional[str] = Field(default=None, max_length=4000)
    applied_at: Optional[datetime] = None


class JobApplicationStatusUpdate(BaseModel):
    """Payload dedicated to status transitions (driving Kanban)."""

    status: JobApplicationStatusEnum = Field(..., description="New high-level status.")
    kanban_column: Optional[str] = Field(
        None,
        max_length=64,
        description="Optional custom column label; defaults to status value.",
    )
    note: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional note recorded in status history.",
    )


class JobApplicationResponse(JobApplicationBase):
    """Full application representation returned to clients."""

    id: str
    status: JobApplicationStatusEnum
    kanban_column: str
    last_status_change_at: Optional[datetime]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "job_title": "Senior Backend Engineer",
                "company_name": "Acme Corp",
                "status": "interviewing",
                "kanban_column": "interviewing",
                "created_at": "2024-02-06T10:30:00Z",
                "updated_at": "2024-02-06T11:00:00Z",
            }
        },
    )


class JobApplicationStatusHistoryItem(BaseModel):
    """Single status history entry."""

    id: str
    application_id: str
    from_status: Optional[JobApplicationStatusEnum] = None
    to_status: JobApplicationStatusEnum
    changed_at: datetime
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedJobApplicationsResponse(BaseModel):
    """Standard paginated list response."""

    items: List[JobApplicationResponse]
    total: int
    page: int
    page_size: int


class KanbanColumn(BaseModel):
    """Kanban column with associated applications."""

    key: str
    label: str
    status: JobApplicationStatusEnum
    applications: List[JobApplicationResponse]


class KanbanBoardResponse(BaseModel):
    """Structure used for Kanban views."""

    columns: List[KanbanColumn]

