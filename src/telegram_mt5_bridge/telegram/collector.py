import asyncio
import logging
from datetime import UTC, datetime

from telethon import events

from telegram_mt5_bridge.config.logging import configure_logging
from telegram_mt5_bridge.config.paths import (
    ensure_app_directories,
    get_app_data_dir,
    get_database_path,
)
from telegram_mt5_bridge.config.settings import (
    get_allowed_chat_ids,
    get_settings,
)
from telegram_mt5_bridge.storage.database import (
    checkpoint_database,
    create_session_factory,
    create_sqlite_engine,
    init_database,
)
from telegram_mt5_bridge.storage.repositories import TelegramMessageRepository
from telegram_mt5_bridge.storage.schemas import TelegramMessageSnapshot
from telegram_mt5_bridge.telegram.client import create_telegram_client
from telegram_mt5_bridge.telegram.listener import is_allowed_chat

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(UTC)


def message_snapshot_from_event(
    event: events.NewMessage.Event | events.MessageEdited.Event,
) -> TelegramMessageSnapshot:
    """Convert a Telethon message event into a raw storage snapshot."""

    received_at = utc_now()

    telegram_message = event.message
    media = getattr(telegram_message, "media", None)

    return TelegramMessageSnapshot(
        chat_id=event.chat_id,
        message_id=event.id,
        sender_id=event.sender_id,
        message_date=event.date or received_at,
        received_at=received_at,
        text=event.raw_text or "",
        reply_to_message_id=getattr(
            telegram_message,
            "reply_to_msg_id",
            None,
        ),
        has_media=media is not None,
        media_type=(type(media).__name__ if media is not None else None),
        edit_date=getattr(
            telegram_message,
            "edit_date",
            None,
        ),
    )


async def run_collector() -> None:
    """Run the raw Telegram message collector."""

    settings = get_settings()
    configure_logging(settings.log_level)

    allowed_chat_ids = get_allowed_chat_ids(settings)

    if not allowed_chat_ids:
        raise RuntimeError("No Telegram chats are configured in TELEGRAM_ALLOWED_CHAT_IDS.")

    app_data_dir = get_app_data_dir()
    ensure_app_directories(app_data_dir)

    database_path = get_database_path(app_data_dir)

    engine = create_sqlite_engine(database_path)
    init_database(engine)

    session_factory = create_session_factory(engine)

    client = create_telegram_client(settings)

    @client.on(events.NewMessage)
    async def handle_new_message(
        event: events.NewMessage.Event,
    ) -> None:
        if not is_allowed_chat(
            event.chat_id,
            allowed_chat_ids,
        ):
            return

        snapshot = message_snapshot_from_event(event)

        with session_factory.begin() as session:
            repository = TelegramMessageRepository(session)
            repository.record_new(snapshot)

        logger.info(
            "Stored Telegram message chat=%s message=%s",
            snapshot.chat_id,
            snapshot.message_id,
        )

    @client.on(events.MessageEdited)
    async def handle_edited_message(
        event: events.MessageEdited.Event,
    ) -> None:
        if not is_allowed_chat(
            event.chat_id,
            allowed_chat_ids,
        ):
            return

        snapshot = message_snapshot_from_event(event)

        with session_factory.begin() as session:
            repository = TelegramMessageRepository(session)
            repository.record_edit(snapshot)

        logger.info(
            "Stored Telegram edit chat=%s message=%s",
            snapshot.chat_id,
            snapshot.message_id,
        )

    @client.on(events.MessageDeleted)
    async def handle_deleted_message(
        event: events.MessageDeleted.Event,
    ) -> None:
        if not is_allowed_chat(
            event.chat_id,
            allowed_chat_ids,
        ):
            return

        if event.chat_id is None:
            return

        event_date = utc_now()

        with session_factory.begin() as session:
            repository = TelegramMessageRepository(session)

            for message_id in event.deleted_ids:
                repository.record_deleted(
                    chat_id=event.chat_id,
                    message_id=message_id,
                    event_date=event_date,
                )

        logger.info(
            "Stored Telegram deletion chat=%s count=%s",
            event.chat_id,
            len(event.deleted_ids),
        )

    await client.start()

    logger.info(
        "Telegram collector running for %d configured chat(s).",
        len(allowed_chat_ids),
    )

    logger.info(
        "SQLite database: %s",
        database_path,
    )

    try:
        await client.run_until_disconnected()
    finally:
        await client.disconnect()

        checkpoint_database(engine)
        engine.dispose()

        logger.info("Telegram collector stopped.")


def main() -> None:
    asyncio.run(run_collector())


if __name__ == "__main__":
    main()
