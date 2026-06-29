import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.core.logging_config import logger
from app.core.exceptions import RateLimitExceededError
from app.core.config import settings
from app.services.redis_service import redis_service


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request details, response status codes, and latency.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request receipt
        logger.info(
            f"Incoming Request: {request.method} {request.url.path}",
            extra={"extra": {
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "query_params": str(request.query_params)
            }}
        )
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            logger.info(
                f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Latency: {duration:.4f}s",
                extra={"extra": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": duration,
                    "client_ip": client_ip
                }}
            )
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request processing failed: {request.method} {request.url.path} - Latency: {duration:.4f}s - Error: {str(e)}",
                exc_info=e,
                extra={"extra": {
                    "method": request.method,
                    "path": request.url.path,
                    "duration_seconds": duration,
                    "client_ip": client_ip
                }}
            )
            raise e


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces API rate limits using Redis.
    Bypasses health checks and OpenAPI docs to avoid disruption.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Bypass rate limiting for health check, API documentation, or static files
        path = request.url.path
        if path in ["/", "/health", "/docs", "/openapi.json", "/redoc"] or path.startswith("/public/"):
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"
        
        try:
            # Check rate limit status
            limit = settings.RATE_LIMIT_REQUESTS
            window = settings.RATE_LIMIT_WINDOW_SECONDS
            
            is_allowed = await redis_service.check_rate_limit(key, limit, window)
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded for client {client_ip} on path {path}",
                    extra={"extra": {"client_ip": client_ip, "path": path}}
                )
                
                # Return standard 429 JSON response
                # Note: Instead of raising exception which can be tricky inside BaseHTTPMiddleware,
                # we return a structured JSON response directly, or raise the exception.
                # Standard BaseHTTPMiddleware does not propagate exception handlers correctly for exceptions raised inside it,
                # so it is safer and cleaner to return the JSON response directly.
                return Response(
                    content='{"success":false,"error":{"code":"RATE_LIMIT_EXCEEDED","message":"Too many requests. Please try again later.","details":null}}',
                    status_code=429,
                    media_type="application/json"
                )
                
        except Exception as e:
            # Log Redis failure but do not crash the request in production (fail-open)
            # This is standard practice so that cache failures do not bring down the main API
            logger.error(f"Redis rate limiter exception: {str(e)}", exc_info=e)
            
        return await call_next(request)
