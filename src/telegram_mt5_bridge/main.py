import logging

from telegram_mt5_bridge.config.logging import configure_logging
from telegram_mt5_bridge.config.paths import ensure_app_directories, get_app_data_dir
from telegram_mt5_bridge.config.settings import get_settings

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the Telegram MT5 Bridge application."""

    settings = get_settings()
    configure_logging(settings.log_level)

    app_data_dir = get_app_data_dir()
    ensure_app_directories(app_data_dir)

    logger.info("Telegram MT5 Bridge starting")
    logger.info("Application data directory: %s", app_data_dir)
    logger.info(
        "Local API configuration: %s:%s",
        settings.api_host,
        settings.api_port,
    )


if __name__ == "__main__":
    main()
