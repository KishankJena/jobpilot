"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class SignupRequest(BaseModel):
    """Request schema for user signup."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
            }
        }


class SignupResponse(BaseModel):
    """Response schema for user signup."""
    
    id: str
    email: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2024-02-06T10:30:00Z",
            }
        }


class LoginRequest(BaseModel):
    """Request schema for user login."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
            }
        }


class LoginResponse(BaseModel):
    """Response schema for user login."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(..., description="User information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "is_active": True,
                }
            }
        }


class LogoutRequest(BaseModel):
    """Request schema for user logout."""
    
    pass


class LogoutResponse(BaseModel):
    """Response schema for user logout."""
    
    message: str = Field(default="Logged out successfully")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Logged out successfully",
            }
        }


class TokenPayload(BaseModel):
    """JWT token payload schema."""
    
    user_id: str
    email: str
    exp: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "exp": 1707218400,
            }
        }


class UserResponse(BaseModel):
    """Response schema for user information."""
    
    id: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "is_active": True,
                "created_at": "2024-02-06T10:30:00Z",
                "updated_at": "2024-02-06T10:30:00Z",
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: str
    detail: Optional[dict] = None
    status_code: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "invalid_credentials",
                "detail": {"message": "Invalid email or password"},
                "status_code": 401,
            }
        }
