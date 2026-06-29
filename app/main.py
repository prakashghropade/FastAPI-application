from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes.api import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import logger, setup_logging
from app.core.middleware import LoggingMiddleware, RateLimitMiddleware
from app.services.redis_service import redis_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for FastAPI.
    Initializes services on startup and teardowns connections on shutdown.
    """
    # 1. Initialize logging
    setup_logging()
    logger.info("Application starting up...")
    
    # 2. Establish Redis connections
    await redis_service.connect()
    
    logger.info("Application startup sequence completed.")
    
    yield
    
    logger.info("Application shutting down...")
    
    # 3. Close Redis connections
    await redis_service.disconnect()
    
    logger.info("Application shutdown sequence completed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Production-ready FastAPI AI Backend",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. CORS Middleware
# Configure CORS based on environments loaded in settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Trusted Host Middleware
# Restricts incoming HTTP requests to specified hosts (helps prevent Host header injection attacks)
# Default is wildcard for easy development, but should be restricted in production config.
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# 3. Custom Request/Response Logging Middleware
app.add_middleware(LoggingMiddleware)

# 4. Custom Redis-based Rate Limiter Middleware
app.add_middleware(RateLimitMiddleware)

# 5. Register Custom Exception Handlers
register_exception_handlers(app)

# 6. Mount Master Router
app.mount(settings.API_V1_STR, api_router)
