from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/info", tags=["public"])
async def get_info():
    """
    Returns general public information about the API.
    No authentication required.
    """
    return {
        "app_name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "description": "Production-ready FastAPI AI Backend",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/ping", tags=["public"])
async def ping():
    """
    Simple liveness check endpoint.
    Returns pong to confirm the API is reachable.
    No authentication required.
    """
    return {
        "message": "pong",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
