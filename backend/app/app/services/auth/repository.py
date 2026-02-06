"""
Repository for user data access operations.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.model.models import User
from app.exceptions.exceptions import DatabaseException


class UserRepository:
    """Repository for User model database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session
    
    async def create_user(self, email: str, password_hash: str) -> User:
        """Create a new user in the database.
        
        Args:
            email: User email address
            password_hash: Hashed password
            
        Returns:
            Created User object
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            user = User(
                email=email,
                password_hash=password_hash,
                is_active=True,
            )
            self.session.add(user)
            await self.session.flush()
            return user
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to create user: {str(e)}")
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User object if found, None otherwise
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            result = await self.session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get user by email: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User object if found, None otherwise
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            result = await self.session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"Failed to get user by id: {str(e)}")
    
    async def user_exists(self, email: str) -> bool:
        """Check if a user with given email exists.
        
        Args:
            email: Email address to check
            
        Returns:
            True if user exists, False otherwise
            
        Raises:
            DatabaseException: If database operation fails
        """
        try:
            result = await self.session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            raise DatabaseException(f"Failed to check user existence: {str(e)}")
    
    async def commit(self) -> None:
        """Commit the current transaction.
        
        Raises:
            DatabaseException: If commit fails
        """
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise DatabaseException(f"Failed to commit transaction: {str(e)}")
