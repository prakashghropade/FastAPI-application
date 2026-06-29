from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_redis
from app.services.redis_service import RedisService

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: RedisService = Depends(get_redis)
):
    """
    Consolidated health status endpoint.
    Tests active connections to PostgreSQL and Redis.
    """
    db_status = "unhealthy"
    redis_status = "unhealthy"
    
    # 1. Test PostgreSQL health
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        # DB connection failed
        pass
        
    # 2. Test Redis health
    try:
        is_redis_alive = await redis.ping()
        if is_redis_alive:
            redis_status = "healthy"
    except Exception:
        pass
        
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy"
    
    # Return appropriate status code. Let's return 200, or 503 if unhealthy.
    # Standard health-check allows a 200 response with detailed JSON.
    return {
        "status": overall_status,
        "services": {
            "api": "healthy",
            "database": db_status,
            "redis": redis_status
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/version", tags=["health"])
async def get_version():
    """
    Endpoint returning app version information.
    """
    return {
        "name": "ai-backend",
        "version": "1.0.0",
        "api_spec": "v1"
    }
