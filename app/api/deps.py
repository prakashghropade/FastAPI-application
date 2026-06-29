import uuid
from typing import AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.services.redis_service import RedisService, redis_service
from app.services.user_service import UserService

# OAuth2 scheme configures Swagger to expect Bearer JWT token in Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)


async def get_redis() -> RedisService:
    """
    Dependency yielding the Redis service singleton.
    """
    return redis_service


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    FastAPI dependency that decodes the JWT access token and returns the authenticated User.
    Raises an AuthenticationError (401) if validation fails.
    """
    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationError(message="Could not validate token or token has expired")
        
    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError(message="Token payload is missing subject ('sub') field")
        
    try:
        user_uuid = uuid.UUID(subject)
    except ValueError:
        raise AuthenticationError(message="Token subject must be a valid UUID")
        
    user = await UserService.get_by_id(db, user_uuid)
    if not user:
        raise AuthenticationError(message="User matching the token subject was not found")
        
    return user
