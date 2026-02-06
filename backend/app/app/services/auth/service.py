"""
Business logic for authentication operations.
"""
from datetime import timedelta
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth.repository import UserRepository
from app.services.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    add_token_to_blacklist,
    verify_token,
)
from app.exceptions.exceptions import (
    InvalidCredentialsException,
    DuplicateEmailException,
    UserNotFoundException,
    InvalidTokenException,
)
from app.config.settings import settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize auth service with database session.
        
        Args:
            session: AsyncSession for database operations
        """
        self.repository = UserRepository(session)
        self.session = session
    
    async def signup(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user.
        
        Args:
            email: User email address
            password: User password (plain text)
            
        Returns:
            Created user information
            
        Raises:
            DuplicateEmailException: If email already registered
        """
        # Check if user already exists
        if await self.repository.user_exists(email):
            raise DuplicateEmailException(f"Email {email} is already registered")
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user = await self.repository.create_user(
            email=email,
            password_hash=password_hash,
        )
        
        # Commit to database
        await self.repository.commit()
        
        return {
            "id": str(user.id),
            "email": user.email,
            "created_at": user.created_at,
        }
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and generate JWT token.
        
        Args:
            email: User email address
            password: User password (plain text)
            
        Returns:
            Access token and user information
            
        Raises:
            InvalidCredentialsException: Invalid email or password
        """
        # Find user by email
        user = await self.repository.get_user_by_email(email)
        
        if not user:
            raise InvalidCredentialsException()
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsException()
        
        # Check if user is active
        if not user.is_active:
            raise InvalidCredentialsException("User account is inactive")
        
        # Generate access token
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires,
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "is_active": user.is_active,
            },
        }
    
    async def logout(self, token: str) -> Dict[str, Any]:
        """Logout user by blacklisting token.
        
        Args:
            token: JWT token to invalidate
            
        Returns:
            Logout confirmation message
            
        Raises:
            InvalidTokenException: If token is invalid
        """
        # Verify token is valid before blacklisting
        payload = verify_token(token)
        
        # Add to blacklist
        add_token_to_blacklist(token)
        
        return {"message": "Logged out successfully"}
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from token.
        
        Args:
            token: JWT token
            
        Returns:
            User information from token payload
            
        Raises:
            InvalidTokenException: If token is invalid or expired
        """
        payload = verify_token(token)
        
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        if not user_id or not email:
            raise InvalidTokenException("Invalid token payload")
        
        # Verify user still exists
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        return {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
        }
