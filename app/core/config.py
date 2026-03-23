# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # 项目信息
    PROJECT_NAME: str = "Policy Management API"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"

    # 数据库
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/policy_db"
    )

    # JWT
    SECRET_KEY: str = Field(default="your-super-secret-key-change-me-please-1234567890")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 环境
    ENVIRONMENT: str = Field(default="development")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
