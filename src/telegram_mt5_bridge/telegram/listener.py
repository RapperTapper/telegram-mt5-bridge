import asyncio
import logging

from telethon import events

from telegram_mt5_bridge.config.logging import configure_logging
from telegram_mt5_bridge.config.settings import (
    get_allowed_chat_ids,
    get_settings,
)
from telegram_mt5_bridge.telegram.client import create_telegram_client
from telegram_mt5_bridge.telegram.models import TelegramMessage

logger = logging.getLogger(__name__)


def is_allowed_chat(chat_id: int | None, allowed_chat_ids: set[int]) -> bool:
    """Return whether a Telegram chat is allowed."""
    return chat_id is not None and chat_id in allowed_chat_ids


async def run_listener() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    allowed_chat_ids = get_allowed_chat_ids(settings)

    if not allowed_chat_ids:
        raise RuntimeError("No Telegram chats are configured in TELEGRAM_ALLOWED_CHAT_IDS.")

    client = create_telegram_client(settings)

    @client.on(events.NewMessage)
    async def handle_new_message(event: events.NewMessage.Event) -> None:
        if not is_allowed_chat(event.chat_id, allowed_chat_ids):
            return

        message = TelegramMessage(
            chat_id=event.chat_id,
            message_id=event.id,
            sender_id=event.sender_id,
            received_at=event.date,
            text=event.raw_text or "",
        )

        logger.info(
            "Telegram message received chat=%s message=%s",
            message.chat_id,
            message.message_id,
        )

    await client.start()

    logger.info(
        "Telegram listener running for %d configured chat(s).",
        len(allowed_chat_ids),
    )

    await client.run_until_disconnected()


def main() -> None:
    asyncio.run(run_listener())


if __name__ == "__main__":
    main()
