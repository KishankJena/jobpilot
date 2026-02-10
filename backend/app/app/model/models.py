"""
SQLAlchemy models for JobPath database with pgvector support.
"""
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional, Any
from enum import Enum

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Index,
    Uuid,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
    Text,
    Float,
    JSON,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class User(Base):
    """User model for authentication and profile management with embeddings support."""
    
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[str] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    
    # User Information
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Profile Embedding (for similarity search, recommendations, etc.)
    profile_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(dim=1536),  # OpenAI embeddings dimension
        nullable=True,
        comment="Vector embedding of user profile for semantic search and recommendations"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary (excludes embeddings for API responses)."""
        return {
            "id": str(self.id),
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class JobListing(Base):
    """Job listing model with semantic search capabilities via embeddings."""
    
    __tablename__ = "job_listings"
    
    # Primary Key
    id: Mapped[str] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    
    # Job Information
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(4000), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Location
    location: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Job Embedding (for semantic search and matching)
    description_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(dim=1536),
        nullable=True,
        comment="Vector embedding of job description for semantic search and matching"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_job_listings_title", "title"),
        Index("ix_job_listings_company", "company"),
        Index("ix_job_listings_location", "location"),
        Index("ix_job_listings_is_active", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<JobListing(id={self.id}, title={self.title}, company={self.company})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary (excludes embeddings)."""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "company": self.company,
            "location": self.location,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


#
# User profile & preferences
#


class UserProfile(Base):
    """Extended user profile and preferences for personalization."""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    years_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    current_role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_roles: Mapped[Optional[list[str]]] = mapped_column(
        JSON, nullable=True, comment="List of target role titles"
    )
    target_locations: Mapped[Optional[list[str]]] = mapped_column(
        JSON, nullable=True, comment="List of preferred locations (cities, remote, etc.)"
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Notification and product preferences
    timezone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    email_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    push_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    weekly_summary_email_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_user_profiles_user_id", "user_id"),
        Index("ix_user_profiles_created_at", "created_at"),
    )


#
# Job applications & status history
#


class JobApplicationStatusEnum(str, Enum):
    """Enum for high-level job application status (Kanban columns)."""

    PROSPECT = "prospect"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    WITHDRAWN = "withdrawn"


class JobApplicationSourceEnum(str, Enum):
    """Enum for where the job came from (for analytics)."""

    MANUAL = "manual"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    COMPANY_SITE = "company_site"
    REFERRAL = "referral"
    OTHER = "other"


class JobApplication(Base):
    """Tracked job applications for a user with Kanban-friendly status."""

    __tablename__ = "job_applications"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional link to normalized job listing (for reuse and analytics)
    job_listing_id: Mapped[Optional[str]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("job_listings.id"), nullable=True, index=True
    )

    # Denormalized core job info for resilience even if listing changes
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    job_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    source: Mapped[JobApplicationSourceEnum] = mapped_column(
        SQLEnum(JobApplicationSourceEnum, name="job_application_source_enum"),
        nullable=False,
        default=JobApplicationSourceEnum.MANUAL,
    )

    status: Mapped[JobApplicationStatusEnum] = mapped_column(
        SQLEnum(JobApplicationStatusEnum, name="job_application_status_enum"),
        nullable=False,
        default=JobApplicationStatusEnum.PROSPECT,
        index=True,
    )

    # Kanban explicit column allows future customization (e.g., "Phone screen")
    kanban_column: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default=JobApplicationStatusEnum.PROSPECT.value,
        index=True,
        comment="Current Kanban column label used in UI",
    )

    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    applied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_status_change_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Soft delete flag; records are retained for analytics.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_job_applications_user_id_status", "user_id", "status"),
        Index("ix_job_applications_company_name", "company_name"),
    )


class JobApplicationStatusHistory(Base):
    """Immutable log of application status transitions for analytics."""

    __tablename__ = "job_application_status_history"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    application_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    from_status: Mapped[Optional[JobApplicationStatusEnum]] = mapped_column(
        SQLEnum(JobApplicationStatusEnum, name="job_application_status_enum"),
        nullable=True,
    )
    to_status: Mapped[JobApplicationStatusEnum] = mapped_column(
        SQLEnum(JobApplicationStatusEnum, name="job_application_status_enum"),
        nullable=False,
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


#
# Resume management, analysis, and AI customization
#


class Resume(Base):
    """A logical resume entity; can have multiple versions."""

    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User-facing name, e.g. 'General SWE Resume'",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Soft delete; versions are retained for auditability.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ResumeVersion(Base):
    """Concrete resume content version; immutable once created."""

    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    resume_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version_label: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="v1",
        comment="Short label (e.g., 'v1', 'v2 - tailored for Backend role').",
    )
    base_version_id: Mapped[Optional[str]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resume_versions.id"),
        nullable=True,
        comment="If derived from another version (e.g. AI-tailored), reference base.",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Resume content in markdown or plain text.",
    )

    is_ai_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if content was generated or heavily modified by AI.",
    )
    ai_explanation: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Structured explanation of AI changes for transparency.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ResumeAnalysis(Base):
    """Structured analysis of a particular resume version."""

    __tablename__ = "resume_analyses"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    resume_version_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resume_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    structure_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    clarity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    impact_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    strengths: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="Key strengths identified in the resume."
    )
    weaknesses: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="Areas to improve, without fabricating experience."
    )
    suggestions: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Concrete, explainable suggestions that the user can accept/reject.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


#
# Job description normalization and resume–JD matching
#


class JobDescription(Base):
    """Normalized job description for matching and analytics."""

    __tablename__ = "job_descriptions"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    description_embedding: Mapped[Optional[Vector]] = mapped_column(
        Vector(dim=1536),
        nullable=True,
        comment="Vector embedding used to power semantic matching.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class ResumeJobMatch(Base):
    """Matching results between a resume version and a job description."""

    __tablename__ = "resume_job_matches"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    resume_version_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resume_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_description_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    match_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="0–1 score representing overall match strength.",
    )
    missing_skills: Mapped[Optional[list[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="List of skills that appear important in JD but not in resume.",
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable explanation of strengths and gaps.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class ResumeEditSuggestionStatusEnum(str, Enum):
    """User decision status for AI edit suggestions."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ResumeEditSuggestion(Base):
    """Fine-grained AI suggestions that must be explicitly accepted by the user."""

    __tablename__ = "resume_edit_suggestions"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    resume_version_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resume_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_description_id: Mapped[Optional[str]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    original_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Explainable rationale describing why the change may help.",
    )

    status: Mapped[ResumeEditSuggestionStatusEnum] = mapped_column(
        SQLEnum(
            ResumeEditSuggestionStatusEnum,
            name="resume_edit_suggestion_status_enum",
        ),
        nullable=False,
        default=ResumeEditSuggestionStatusEnum.PENDING,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the user accepted or rejected the suggestion.",
    )


#
# Interview preparation, analytics, rejection insights
#


class InterviewSession(Base):
    """A focused interview prep session for a role/company."""

    __tablename__ = "interview_sessions"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_application_id: Mapped[Optional[str]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    role: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    focus_areas: Mapped[Optional[list[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Areas to emphasize (e.g., system design, leadership).",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class InterviewQuestionDifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewQuestionCategoryEnum(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SYSTEM_DESIGN = "system_design"
    COMPANY = "company"
    OTHER = "other"


class InterviewQuestion(Base):
    """Questions generated or curated for an interview session."""

    __tablename__ = "interview_questions"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    session_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer_hint: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional coach-style hints, never fabricated experience.",
    )

    difficulty: Mapped[InterviewQuestionDifficultyEnum] = mapped_column(
        SQLEnum(
            InterviewQuestionDifficultyEnum,
            name="interview_question_difficulty_enum",
        ),
        nullable=False,
        default=InterviewQuestionDifficultyEnum.MEDIUM,
        index=True,
    )
    category: Mapped[InterviewQuestionCategoryEnum] = mapped_column(
        SQLEnum(
            InterviewQuestionCategoryEnum,
            name="interview_question_category_enum",
        ),
        nullable=False,
        default=InterviewQuestionCategoryEnum.OTHER,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class RejectionInsight(Base):
    """AI-assisted insights about rejection patterns; fully explainable."""

    __tablename__ = "rejection_insights"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_application_id: Mapped[Optional[str]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    insight: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Actionable, empathetic explanation of observed patterns.",
    )
    recommended_actions: Mapped[Optional[list[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Concrete actions the user can take (never deceptive).",
    )
    tags: Mapped[Optional[list[str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Short labels useful for analytics (e.g., 'resume_clarity').",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


#
# Wellbeing, reminders, and notifications
#


class WellbeingCheckIn(Base):
    """User-submitted wellbeing check-ins; intentionally low-friction and non-invasive."""

    __tablename__ = "wellbeing_checkins"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    mood_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="1–5 mood rating where 1 is very low and 5 is very positive.",
    )
    energy_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Optional free-form journal entry; never analyzed for ads.",
    )
    burnout_risk_level: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        comment="High-level categorization (e.g., 'low', 'medium', 'high').",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )


class ReminderTypeEnum(str, Enum):
    FOLLOW_UP = "follow_up"
    INTERVIEW_PREP = "interview_prep"
    APPLICATION_CHECKIN = "application_checkin"
    WELLBEING_CHECKIN = "wellbeing_checkin"
    OTHER = "other"


class ReminderStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DISMISSED = "dismissed"


class ReminderChannelEnum(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"


class Reminder(Base):
    """Smart reminders and follow-ups for applications and wellbeing."""

    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_application_id: Mapped[Optional[str]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    type: Mapped[ReminderTypeEnum] = mapped_column(
        SQLEnum(ReminderTypeEnum, name="reminder_type_enum"),
        nullable=False,
        index=True,
    )
    status: Mapped[ReminderStatusEnum] = mapped_column(
        SQLEnum(ReminderStatusEnum, name="reminder_status_enum"),
        nullable=False,
        default=ReminderStatusEnum.PENDING,
        index=True,
    )
    channel: Mapped[ReminderChannelEnum] = mapped_column(
        SQLEnum(ReminderChannelEnum, name="reminder_channel_enum"),
        nullable=False,
        default=ReminderChannelEnum.IN_APP,
    )

    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class NotificationTypeEnum(str, Enum):
    APPLICATION_EVENT = "application_event"
    REMINDER = "reminder"
    SYSTEM = "system"
    WELLBEING = "wellbeing"
    OTHER = "other"


class Notification(Base):
    """In-app notifications for key events and insights."""

    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[NotificationTypeEnum] = mapped_column(
        SQLEnum(NotificationTypeEnum, name="notification_type_enum"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
