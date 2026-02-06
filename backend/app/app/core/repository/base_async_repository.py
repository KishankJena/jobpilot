"""
Base repository class for common CRUD operations.
"""
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar('T')


class BaseAsyncRepository(Generic[T]):
    """Base repository with common async database operations.
    
    Generic repository that can be extended for specific model types.
    Implements standard CRUD operations for any SQLAlchemy model.
    """
    
    def __init__(self, model: type[T], session: AsyncSession):
        """Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session
    
    async def create(self, obj_in: dict) -> T:
        """Create and save a new object.
        
        Args:
            obj_in: Dictionary of object attributes
            
        Returns:
            Created model instance
        """
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj
    
    async def get_by_id(self, obj_id: any) -> Optional[T]:
        """Get object by ID.
        
        Args:
            obj_id: Object primary key
            
        Returns:
            Model instance if found, None otherwise
        """
        result = await self.session.execute(
            select(self.model).filter(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of model instances
        """
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update(self, obj_id: any, obj_in: dict) -> Optional[T]:
        """Update an object.
        
        Args:
            obj_id: Object primary key
            obj_in: Dictionary of attributes to update
            
        Returns:
            Updated model instance if found, None otherwise
        """
        db_obj = await self.get_by_id(obj_id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            await self.session.flush()
        return db_obj
    
    async def delete(self, obj_id: any) -> bool:
        """Delete an object.
        
        Args:
            obj_id: Object primary key
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = await self.get_by_id(obj_id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.flush()
            return True
        return False
    
    async def commit(self) -> None:
        """Commit current transaction."""
        await self.session.commit()
    
    async def rollback(self) -> None:
        """Rollback current transaction."""
        await self.session.rollback()
