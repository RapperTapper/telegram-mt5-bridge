import asyncio
import logging

from telegram_mt5_bridge.cli import abort_configuration_error
from telegram_mt5_bridge.config.logging import configure_logging
from telegram_mt5_bridge.config.paths import ensure_app_directories, get_app_data_dir
from telegram_mt5_bridge.config.settings import get_settings
from telegram_mt5_bridge.telegram.client import create_telegram_client

logger = logging.getLogger(__name__)


async def check_telegram_connection() -> None:
    """Connect to Telegram and verify the authenticated user."""

    settings = get_settings()
    configure_logging(settings.log_level)

    ensure_app_directories(get_app_data_dir())

    client = create_telegram_client(settings)

    async with client:
        me = await client.get_me()

        if me is None:
            raise RuntimeError("Telegram authentication failed.")

        logger.info("Telegram authentication successful.")


def main() -> None:
    try:
        asyncio.run(check_telegram_connection())
    except ValueError as error:
        abort_configuration_error(error)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
