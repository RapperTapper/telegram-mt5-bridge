from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    telegram_api_id: int | None = None
    telegram_api_hash: SecretStr | None = None
    telegram_allowed_chat_ids: str = ""

    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8765, ge=1, le=65535)

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        env_ignore_empty=True,  # temp
        extra="ignore",
    )


def load_settings(env_file: Path | str = ".env") -> Settings:
    """Load application settings from the environment and an optional .env file."""
    return Settings(_env_file=env_file, _env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    """Return one cached Settings instance for normal application runtime."""
    return load_settings()
