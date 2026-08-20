from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from telegram_mt5_bridge.config.paths import get_database_path
from telegram_mt5_bridge.storage.database import (
    create_session_factory,
    create_sqlite_engine,
    init_database,
)
from telegram_mt5_bridge.storage.models import (
    TelegramMessageEvent,
    TelegramMessageRecord,
)

KNOWN_EVENT_TYPES = ("new", "edit", "deleted")


@dataclass(frozen=True)
class DatabaseStatistics:
    """Aggregate statistics for the local Telegram message database."""

    message_count: int
    event_count: int
    event_counts: dict[str, int]
    reply_count: int
    media_count: int
    edited_count: int
    deleted_count: int
    chat_counts: tuple[tuple[int, int], ...]


def collect_database_statistics(session: Session) -> DatabaseStatistics:
    """Collect aggregate statistics without exposing message contents."""

    message_count = session.scalar(select(func.count()).select_from(TelegramMessageRecord)) or 0
    event_count = session.scalar(select(func.count()).select_from(TelegramMessageEvent)) or 0

    event_rows = session.execute(
        select(
            TelegramMessageEvent.event_type,
            func.count(TelegramMessageEvent.id),
        )
        .group_by(TelegramMessageEvent.event_type)
        .order_by(TelegramMessageEvent.event_type)
    ).all()

    reply_count = (
        session.scalar(
            select(func.count())
            .select_from(TelegramMessageRecord)
            .where(TelegramMessageRecord.reply_to_message_id.is_not(None))
        )
        or 0
    )
    media_count = (
        session.scalar(
            select(func.count())
            .select_from(TelegramMessageRecord)
            .where(TelegramMessageRecord.has_media.is_(True))
        )
        or 0
    )
    edited_count = (
        session.scalar(
            select(func.count())
            .select_from(TelegramMessageRecord)
            .where(TelegramMessageRecord.edit_date.is_not(None))
        )
        or 0
    )
    deleted_count = (
        session.scalar(
            select(func.count())
            .select_from(TelegramMessageRecord)
            .where(TelegramMessageRecord.deleted_at.is_not(None))
        )
        or 0
    )

    chat_rows = session.execute(
        select(
            TelegramMessageRecord.chat_id,
            func.count(TelegramMessageRecord.id),
        )
        .group_by(TelegramMessageRecord.chat_id)
        .order_by(TelegramMessageRecord.chat_id)
    ).all()

    return DatabaseStatistics(
        message_count=message_count,
        event_count=event_count,
        event_counts={event_type: count for event_type, count in event_rows},
        reply_count=reply_count,
        media_count=media_count,
        edited_count=edited_count,
        deleted_count=deleted_count,
        chat_counts=tuple((chat_id, count) for chat_id, count in chat_rows),
    )


def read_database_statistics(database_path: Path) -> DatabaseStatistics:
    """Open the local database and return its aggregate statistics."""

    engine = create_sqlite_engine(database_path)

    try:
        init_database(engine)
        session_factory = create_session_factory(engine)

        with session_factory() as session:
            return collect_database_statistics(session)
    finally:
        engine.dispose()


def render_database_statistics(
    database_path: Path,
    statistics: DatabaseStatistics,
) -> str:
    """Render database statistics for terminal output."""

    event_types = [
        *KNOWN_EVENT_TYPES,
        *(
            event_type
            for event_type in statistics.event_counts
            if event_type not in KNOWN_EVENT_TYPES
        ),
    ]

    lines = [
        f"Database: {database_path}",
        "",
        f"{'Messages:':<10}{statistics.message_count}",
        f"{'Events:':<10}{statistics.event_count}",
        "",
        "Events",
        "------",
    ]

    lines.extend(
        f"{event_type + ':':<10}{statistics.event_counts.get(event_type, 0)}"
        for event_type in event_types
    )

    lines.extend(
        [
            "",
            "Features",
            "--------",
            f"{'replies:':<10}{statistics.reply_count}",
            f"{'media:':<10}{statistics.media_count}",
            f"{'edited:':<10}{statistics.edited_count}",
            f"{'deleted:':<10}{statistics.deleted_count}",
            "",
            "Chats",
            "-----",
        ]
    )

    if statistics.chat_counts:
        lines.extend(f"{chat_id}: {count}" for chat_id, count in statistics.chat_counts)
    else:
        lines.append("(none)")

    return "\n".join(lines)


def main() -> None:
    """Print statistics about the local message database."""

    database_path = get_database_path()
    statistics = read_database_statistics(database_path)

    print(render_database_statistics(database_path, statistics))


if __name__ == "__main__":
    main()
