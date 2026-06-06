"""Application settings (Pydantic Settings v2).

All values overridable via environment variables / .env.
Defaults target local dev; production must override SECRET_KEY and DATABASE_URL.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    PROJECT_NAME: str = "Neurostep API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- Security / JWT ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_dev_only_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # --- Database ---
    # Defaults to local SQLite so the skeleton boots with zero infra.
    # Production: set DATABASE_URL to the PostgreSQL DSN (see .env.example).
    DATABASE_URL: str = "sqlite:///./neurostep.db"

    # --- Redis (cache + sessions) ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Object storage (S3 / MinIO) ---
    S3_ENDPOINT_URL: str | None = None
    S3_BUCKET: str = "neurostep-media"
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None

    # --- CORS ---
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])

    # --- First admin (created by seed) ---
    FIRST_ADMIN_EMAIL: str = "admin@neurostep.app"
    FIRST_ADMIN_PASSWORD: str = "admin"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
