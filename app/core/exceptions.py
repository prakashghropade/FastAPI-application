from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging_config import logger


class AppException(Exception):
    """
    Base class for all application exceptions.
    """
    def __init__(self, message: str, code: str = "INTERNAL_SERVER_ERROR", status_code: int = 500, details: any = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class AuthenticationError(AppException):
    def __init__(self, message: str = "Could not validate credentials", details: any = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = "User with this email already exists", details: any = None):
        super().__init__(
            message=message,
            code="USER_ALREADY_EXISTS",
            status_code=400,
            details=details
        )


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", details: any = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details
        )


class ValidationError(AppException):
    def __init__(self, message: str = "Validation error", details: any = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class RateLimitExceededError(AppException):
    def __init__(self, message: str = "Too many requests. Please try again later.", details: any = None):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details
        )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers custom exception handlers on the FastAPI application.
    """
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(
            f"AppException: {exc.code} - {exc.message}",
            extra={"extra": {"path": request.url.path, "code": exc.code, "details": exc.details}}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = exc.errors()
        # Simplify errors for the response
        simplified_details = []
        for error in details:
            simplified_details.append({
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "type": error.get("type")
            })
            
        logger.warning(
            f"Validation failed for request to {request.url.path}",
            extra={"extra": {"path": request.url.path, "validation_errors": simplified_details}}
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed.",
                    "details": simplified_details
                }
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled exception occurred on request {request.method} {request.url.path}: {str(exc)}",
            exc_info=exc,
            extra={"extra": {"path": request.url.path}}
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": None
                }
            }
        )
