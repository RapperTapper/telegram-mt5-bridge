import os
import platform
from pathlib import Path

APP_NAME = "TelegramMT5Bridge"


def get_app_data_dir(
    *,
    system: str | None = None,
    home: Path | None = None,
    environ: dict[str, str] | None = None,
) -> Path:
    """Return the platform-specific application data directory."""

    current_system = system or platform.system()
    current_home = home or Path.home()
    current_environ = environ if environ is not None else os.environ

    if current_system == "Darwin":
        return current_home / "Library" / "Application Support" / APP_NAME

    if current_system == "Windows":
        local_app_data = current_environ.get("LOCALAPPDATA")

        if local_app_data:
            return Path(local_app_data) / APP_NAME

        return current_home / "AppData" / "Local" / APP_NAME

    return current_home / ".local" / "share" / APP_NAME


def get_telegram_session_path(app_data_dir: Path | None = None) -> Path:
    """Return the Telethon session base path.

    Telethon will add the .session suffix itself.
    """
    base_dir = app_data_dir or get_app_data_dir()
    return base_dir / "telegram"


def get_log_dir(app_data_dir: Path | None = None) -> Path:
    """Return the application's log directory."""
    base_dir = app_data_dir or get_app_data_dir()
    return base_dir / "logs"


def get_runtime_dir(app_data_dir: Path | None = None) -> Path:
    """Return the application's runtime-data directory."""
    base_dir = app_data_dir or get_app_data_dir()
    return base_dir / "runtime"


def get_database_path(app_data_dir: Path | None = None) -> Path:
    """Return the path of the local SQLite message database."""
    base_dir = app_data_dir or get_app_data_dir()
    return get_runtime_dir(base_dir) / "messages.sqlite3"


def ensure_app_directories(app_data_dir: Path | None = None) -> None:
    """Create the directories required by the application."""
    base_dir = app_data_dir or get_app_data_dir()

    base_dir.mkdir(parents=True, exist_ok=True)
    get_log_dir(base_dir).mkdir(parents=True, exist_ok=True)
    get_runtime_dir(base_dir).mkdir(parents=True, exist_ok=True)
