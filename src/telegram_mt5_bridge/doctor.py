from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from telegram_mt5_bridge.config.paths import (
    ensure_app_directories,
    get_app_data_dir,
    get_database_path,
    get_runtime_dir,
    get_telegram_session_path,
)
from telegram_mt5_bridge.config.settings import (
    Settings,
    get_allowed_chat_ids,
    load_settings,
)
from telegram_mt5_bridge.storage.stats import (
    DatabaseStatistics,
    read_database_statistics,
)


@dataclass(frozen=True)
class DoctorReport:
    """Results of local configuration and runtime checks."""

    api_id_configured: bool
    api_hash_configured: bool
    allowed_chat_count: int | None
    app_data_dir: Path
    runtime_accessible: bool
    session_found: bool
    database_path: Path
    database_found: bool
    database_writable: bool
    database_statistics: DatabaseStatistics | None

    @property
    def is_ok(self) -> bool:
        """Return whether the local setup is ready to run the collector."""

        return all(
            (
                self.api_id_configured,
                self.api_hash_configured,
                self.allowed_chat_count is not None and self.allowed_chat_count > 0,
                self.runtime_accessible,
                self.session_found,
                self.database_found,
                self.database_writable,
                self.database_statistics is not None,
            )
        )


def inspect_local_setup(
    settings: Settings,
    app_data_dir: Path | None = None,
) -> DoctorReport:
    """Inspect local configuration and storage without connecting to Telegram."""

    resolved_app_data_dir = app_data_dir or get_app_data_dir()
    runtime_dir = get_runtime_dir(resolved_app_data_dir)
    database_path = get_database_path(resolved_app_data_dir)
    session_path = get_telegram_session_path(resolved_app_data_dir).with_suffix(".session")

    try:
        allowed_chat_count = len(get_allowed_chat_ids(settings))
    except ValueError:
        allowed_chat_count = None

    runtime_accessible = False
    database_found = False
    database_writable = False
    database_statistics = None

    try:
        ensure_app_directories(resolved_app_data_dir)
        runtime_accessible = runtime_dir.is_dir()
        database_statistics = read_database_statistics(database_path)
        database_found = database_path.is_file()
        database_writable = True
    except (OSError, SQLAlchemyError):
        pass

    return DoctorReport(
        api_id_configured=settings.telegram_api_id is not None,
        api_hash_configured=settings.telegram_api_hash is not None,
        allowed_chat_count=allowed_chat_count,
        app_data_dir=resolved_app_data_dir,
        runtime_accessible=runtime_accessible,
        session_found=session_path.is_file(),
        database_path=database_path,
        database_found=database_found,
        database_writable=database_writable,
        database_statistics=database_statistics,
    )


def _status(value: bool, *, positive: str = "yes", negative: str = "no") -> str:
    return positive if value else negative


def render_doctor_report(report: DoctorReport) -> str:
    """Render a Doctor report without secrets or message contents."""

    allowed_chats = (
        str(report.allowed_chat_count) if report.allowed_chat_count is not None else "invalid"
    )
    statistics = report.database_statistics

    lines = [
        "Telegram MT5 Bridge",
        "",
        "Configuration",
        "-------------",
        f"{'Telegram API ID:':<24}{_status(report.api_id_configured, positive='configured', negative='missing')}",
        f"{'Telegram API hash:':<24}{_status(report.api_hash_configured, positive='configured', negative='missing')}",
        f"{'Allowed chats:':<24}{allowed_chats}",
        "",
        "Runtime",
        "-------",
        f"Application directory: {report.app_data_dir}",
        f"{'Runtime directory:':<24}{_status(report.runtime_accessible, positive='accessible')}",
        f"{'Telegram session:':<24}{_status(report.session_found, positive='found', negative='missing')}",
        f"{'Database:':<24}{_status(report.database_found, positive='found', negative='missing')}",
        f"{'Database writable:':<24}{_status(report.database_writable)}",
        "",
        "Database",
        "--------",
    ]

    if statistics is None:
        lines.append("Statistics:             unavailable")
    else:
        lines.extend(
            [
                f"{'Messages:':<24}{statistics.message_count}",
                f"{'Events:':<24}{statistics.event_count}",
                f"{'Replies:':<24}{statistics.reply_count}",
                f"{'Edits:':<24}{statistics.event_counts.get('edit', 0)}",
                f"{'Deletes:':<24}{statistics.event_counts.get('deleted', 0)}",
            ]
        )

    lines.extend(
        [
            "",
            f"Status: {'OK' if report.is_ok else 'SETUP REQUIRED'}",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    """Run local setup diagnostics without connecting to Telegram."""

    try:
        settings = load_settings()
    except (OSError, ValidationError):
        print(
            "Telegram MT5 Bridge\n\n"
            "Configuration error:\n"
            "The local configuration could not be loaded.\n\n"
            "Create .env from .env.example and configure your Telegram credentials."
        )
        raise SystemExit(1) from None

    report = inspect_local_setup(settings)
    print(render_doctor_report(report))

    if not report.is_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
