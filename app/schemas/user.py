import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """
    Shared attributes for user schemas.
    """
    email: EmailStr = Field(..., description="The unique email address of the user")
    name: str = Field(..., min_length=2, max_length=50, description="The name of the user")


class UserCreate(UserBase):
    """
    Schema for user registration.
    """
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")


class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    """
    email: EmailStr = Field(...)
    password: str = Field(...)


class UserResponse(UserBase):
    """
    Schema returned to the API client.
    """
    id: uuid.UUID
    created_at: datetime

    # Configure Pydantic to extract data from arbitrary class attributes (for SQLAlchemy integration)
    model_config = ConfigDict(from_attributes=True)
