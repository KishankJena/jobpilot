"""
Database connection and session management for JobPath.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from app.config.settings import settings


# Create async engine
engine_kwargs = {
    "echo": settings.DB_ECHO,
}

# SQLite-specific configuration
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Pool settings for other databases (PostgreSQL, etc.)
    engine_kwargs.update({
        "pool_pre_ping": settings.DB_POOL_PRE_PING,
    })
    if not settings.DEBUG:
        engine_kwargs.update({
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
        })
    else:
        engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
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
    """Dependency to get database session.
    
    Yields:
        AsyncSession: Database session for use in request handlers
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables).
    
    This should be called on application startup if using Alembic migrations,
    you may skip this and use Alembic instead.
    """
    from app.model.models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections.
    
    This should be called on application shutdown.
    """
    await engine.dispose()
