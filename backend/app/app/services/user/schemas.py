"""Pydantic schemas for user profile and preferences."""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class UserProfileBase(BaseModel):
    """Shared fields for user profile."""

    full_name: Optional[str] = Field(None, max_length=255)
    headline: Optional[str] = Field(
        None, max_length=255, description="Short professional headline."
    )
    location: Optional[str] = Field(None, max_length=255)
    years_experience: Optional[int] = Field(
        None, ge=0, le=80, description="Approximate years of professional experience."
    )
    current_role: Optional[str] = Field(None, max_length=255)
    target_roles: Optional[List[str]] = Field(
        default=None, description="List of target role titles."
    )
    target_locations: Optional[List[str]] = Field(
        default=None, description="Preferred locations (cities, remote, etc.)."
    )
    linkedin_url: Optional[str] = Field(None, max_length=512)
    website_url: Optional[str] = Field(None, max_length=512)

    timezone: Optional[str] = Field(None, max_length=64)
    email_notifications_enabled: Optional[bool] = True
    push_notifications_enabled: Optional[bool] = True
    weekly_summary_email_enabled: Optional[bool] = True


class UserProfileCreate(UserProfileBase):
    """Payload used when creating a profile (first-time setup)."""

    model_config = ConfigDict(json_schema_extra={"example": {"full_name": "Jane Doe"}})


class UserProfileUpdate(UserProfileBase):
    """Payload used when updating an existing profile."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "headline": "Senior Backend Engineer seeking remote roles",
                "target_roles": ["Senior Backend Engineer", "Staff Engineer"],
                "timezone": "Europe/Berlin",
            }
        }
    )


class UserProfileResponse(UserProfileBase):
    """Full profile representation returned to clients."""

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "full_name": "Jane Doe",
                "headline": "Senior Backend Engineer",
                "location": "Berlin, Germany",
                "years_experience": 8,
                "target_roles": ["Senior Backend Engineer"],
                "timezone": "Europe/Berlin",
                "email_notifications_enabled": True,
                "push_notifications_enabled": True,
                "weekly_summary_email_enabled": True,
                "created_at": "2024-02-06T10:30:00Z",
                "updated_at": "2024-02-06T10:30:00Z",
            }
        },
    )


class UserPreferencesResponse(BaseModel):
    """Thin wrapper exposing just preferences (for dedicated endpoints)."""

    timezone: Optional[str]
    email_notifications_enabled: bool
    push_notifications_enabled: bool
    weekly_summary_email_enabled: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timezone": "Europe/Berlin",
                "email_notifications_enabled": True,
                "push_notifications_enabled": True,
                "weekly_summary_email_enabled": True,
            }
        }
    )

