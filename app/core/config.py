import os
from typing import Any, Dict, List, Union
from pydantic import AnyHttpUrl, BeforeValidator, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "ai-backend"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = ""

    # Security Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Database Configuration
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str

    # Redis Configuration
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_URL: str

    # CORS configuration
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        return parse_cors(v)


settings = Settings()
