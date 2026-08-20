from telethon import TelegramClient

from telegram_mt5_bridge.config.paths import get_telegram_session_path
from telegram_mt5_bridge.config.settings import Settings, get_telegram_credentials


def create_telegram_client(settings: Settings) -> TelegramClient:
    """Create a configured Telethon client."""

    credentials = get_telegram_credentials(settings)
    session_path = get_telegram_session_path()

    return TelegramClient(
        str(session_path),
        credentials.api_id,
        credentials.api_hash.get_secret_value(),
    )
