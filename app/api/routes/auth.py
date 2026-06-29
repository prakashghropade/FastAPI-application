from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import create_access_token
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201, tags=["auth"])
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user in the system.
    """
    user = await UserService.create(db, user_in)
    return user


@router.post("/login", response_model=Token, tags=["auth"])
async def login_json(
    login_in: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user via JSON payload and returns a JWT access token.
    Suitable for API clients and web application frontends.
    """
    user = await UserService.authenticate(db, login_in)
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)


@router.post("/token", response_model=Token, tags=["auth"])
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user via form-data (x-www-form-urlencoded) and returns a JWT access token.
    Provides compatibility for OpenAPI/Swagger UI authentication.
    """
    login_in = UserLogin(email=form_data.username, password=form_data.password)
    user = await UserService.authenticate(db, login_in)
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token)
