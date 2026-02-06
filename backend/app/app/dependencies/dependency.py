"""
Dependency injections for FastAPI route handlers.
"""
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_session
from app.services.auth.security import extract_token_from_header, verify_token
from app.exceptions.exceptions import InvalidTokenException


async def get_current_user(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Dependency to validate and extract current user from JWT token.
    
    Args:
        authorization: Authorization header with Bearer token
        session: Database session (for potential future user lookup)
        
    Returns:
        Current user information from token payload
        
    Raises:
        InvalidTokenException: If token is invalid or expired
    """
    try:
        token = extract_token_from_header(authorization)
        payload = verify_token(token)
        
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        if not user_id or not email:
            raise InvalidTokenException("Invalid token payload")
        
        return {
            "user_id": user_id,
            "email": email,
        }
    except InvalidTokenException:
        raise
    except Exception as e:
        raise InvalidTokenException(f"Token validation failed: {str(e)}")


async def get_current_user_optional(
    authorization: str = Header(None),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Dependency to optionally validate JWT token.
    
    Returns None if no token is provided, otherwise validates token.
    
    Args:
        authorization: Authorization header with Bearer token (optional)
        session: Database session
        
    Returns:
        User information if token is valid, None otherwise
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, session)
    except InvalidTokenException:
        return None
