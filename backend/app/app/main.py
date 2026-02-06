"""
Main FastAPI application factory and entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.config.log_config import setup_logging, get_logger
from app.db.database import init_db, close_db
from app.exceptions.exceptions import JobPathException
from app.services.auth.router import router as auth_router

# Setup logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_format=settings.LOG_FORMAT,
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup event
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize database: {str(e)}")
        if not settings.DEBUG:
            raise
        logger.info("Continuing startup in DEBUG mode without database")
    
    yield
    
    # Shutdown event
    logger.info("Shutting down application")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.warning(f"Error closing database: {str(e)}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade FastAPI backend for JobPath SaaS platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # Include routers
    app.include_router(auth_router)
    
    # Exception handler
    @app.exception_handler(JobPathException)
    async def jobpath_exception_handler(request, exc: JobPathException):
        """Handle JobPathException globally.
        
        Args:
            request: Request object
            exc: Exception instance
            
        Returns:
            JSON response with error details
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail.get("error", "error"),
                "message": exc.message,
                "detail": exc.detail,
            },
        )
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint.
        
        Returns:
            Status of the application
        """
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information.
        
        Returns:
            API information
        """
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
        }
    
    logger.info(f"FastAPI application '{settings.APP_NAME}' created successfully")
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
