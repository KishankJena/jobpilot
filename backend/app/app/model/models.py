"""
SQLAlchemy models for JobPath database with pgvector support.
"""
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, Index, Uuid, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from typing import Optional


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