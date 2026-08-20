from sqlalchemy import func, select

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


def main() -> None:
    """Print basic statistics about the local message database."""

    database_path = get_database_path()

    engine = create_sqlite_engine(database_path)
    init_database(engine)

    session_factory = create_session_factory(engine)

    with session_factory() as session:
        message_count = session.scalar(select(func.count()).select_from(TelegramMessageRecord))

        event_count = session.scalar(select(func.count()).select_from(TelegramMessageEvent))

        chats = session.execute(
            select(
                TelegramMessageRecord.chat_id,
                func.count(TelegramMessageRecord.id),
            )
            .group_by(TelegramMessageRecord.chat_id)
            .order_by(TelegramMessageRecord.chat_id)
        ).all()

    print(f"Database: {database_path}")
    print(f"Messages: {message_count or 0}")
    print(f"Events: {event_count or 0}")

    for chat_id, count in chats:
        print(f"Chat {chat_id}: {count} message(s)")

    engine.dispose()


if __name__ == "__main__":
    main()
