from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr
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


class TelegramCredentials(BaseModel):
    api_id: int
    api_hash: SecretStr


def load_settings(env_file: Path | str = ".env") -> Settings:
    """Load application settings from the environment and an optional .env file."""
    return Settings(
        _env_file=env_file,
        _env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    """Return one cached Settings instance for normal application runtime."""
    return load_settings()


def get_telegram_credentials(settings: Settings) -> TelegramCredentials:
    """Return validated Telegram credentials."""

    if settings.telegram_api_id is None:
        raise ValueError("TELEGRAM_API_ID is not configured.")

    if settings.telegram_api_hash is None:
        raise ValueError("TELEGRAM_API_HASH is not configured.")

    return TelegramCredentials(
        api_id=settings.telegram_api_id,
        api_hash=settings.telegram_api_hash,
    )


def get_allowed_chat_ids(settings: Settings) -> set[int]:
    """Return configured Telegram chat IDs."""

    raw_ids = settings.telegram_allowed_chat_ids.strip()

    if not raw_ids:
        return set()

    return {int(value.strip()) for value in raw_ids.split(",") if value.strip()}
