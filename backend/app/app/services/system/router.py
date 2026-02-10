"""System endpoints for JobPath."""
from fastapi import APIRouter

from app.config.settings import settings


router = APIRouter(
    prefix="/system",
    tags=["System"],
)


@router.get("/version", summary="Get API version")
async def get_version() -> dict:
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
    }


@router.get("/info", summary="Get basic system information")
async def get_info() -> dict:
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }

