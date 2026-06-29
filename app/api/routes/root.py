from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/", tags=["root"])
async def read_root():
    """
    Base endpoint returning high-level information about the API service.
    """
    return {
        "app_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs"
    }
