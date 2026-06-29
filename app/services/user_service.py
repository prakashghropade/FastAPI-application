import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import UserAlreadyExistsError, AuthenticationError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin


class UserService:
    """
    Service class encapsulating business logic for User operations.
    Implements Repository-like access methods on the database.
    """
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """
        Retrieves a user by their UUID primary key.
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Retrieves a user by their unique email.
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @classmethod
    async def create(cls, db: AsyncSession, user_in: UserCreate) -> User:
        """
        Registers a new user, checking if email already exists and hashing the password.
        """
        # Check if email is already registered
        existing_user = await cls.get_by_email(db, user_in.email)
        if existing_user:
            raise UserAlreadyExistsError(
                message=f"User with email '{user_in.email}' is already registered."
            )
            
        # Hash password and create database model
        hashed_password = hash_password(user_in.password)
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            password=hashed_password
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @classmethod
    async def authenticate(cls, db: AsyncSession, login_in: UserLogin) -> User:
        """
        Authenticates a user using email and plain password.
        Raises AuthenticationError if invalid credentials.
        """
        user = await cls.get_by_email(db, login_in.email)
        if not user:
            raise AuthenticationError(message="Incorrect email or password")
            
        if not verify_password(login_in.password, user.password):
            raise AuthenticationError(message="Incorrect email or password")
            
        return user
