"""
PostgreSQL async database connection and session management with pgvector support.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, event
from typing import AsyncGenerator
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


# Determine engine arguments based on database type
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "pool_pre_ping": settings.DB_POOL_PRE_PING,
}

# Add pooling arguments ONLY for PostgreSQL
if settings.DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": 3600,
    })

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session for FastAPI.
    
    Yields:
        AsyncSession: Database session for use in request handlers
        
    Example:
        async def get_user(session: AsyncSession = Depends(get_db_session)):
            # Use session here
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_pgvector_extension(connection) -> None:
    """Initialize pgvector extension if not already exists (PostgreSQL only)."""
    if "postgresql" not in str(connection.engine.url):
        return
        
    try:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        logger.info("pgvector extension enabled successfully")
    except Exception as e:
        logger.warning(f"pgvector extension may already exist or failed to create: {str(e)}")


async def verify_database_connection() -> bool:
    """Verify database connection is working.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to verify database connection: {str(e)}")
        return False


async def init_db() -> None:
    """Initialize database on application startup.
    
    This function:
    1. Creates pgvector extension
    2. Creates all tables from models
    3. Verifies connection is working
    
    Must be called during application lifespan startup.
    """
    # Verify connection first
    if not await verify_database_connection():
        raise RuntimeError("Cannot connect to PostgreSQL database. Check DATABASE_URL in .env")
    
    # Initialize pgvector extension (PostgreSQL only)
    if settings.DATABASE_URL.startswith("postgresql"):
        async with engine.begin() as conn:
            await init_pgvector_extension(conn)
    
    # Create all tables
    from app.model.models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialization completed successfully")


async def close_db() -> None:
    """Close all database connections gracefully.
    
    Must be called during application lifespan shutdown.
    """
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.warning(f"Error closing database connections: {str(e)}")