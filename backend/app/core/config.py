"""Application settings loaded from the environment."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Tathyashala API"
    api_prefix: str = "/api/v1"
    allowed_origins: str = "http://localhost:5173"
    max_upload_mb: int = 20
    max_rows: int = 100_000
    max_columns: int = 100
    session_ttl_minutes: int = 60
    cleanup_interval_seconds: int = 300
    temporary_directory: str = ".data"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="UPATTO_", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
