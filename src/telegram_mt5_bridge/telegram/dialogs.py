import asyncio

from telegram_mt5_bridge.cli import abort_configuration_error
from telegram_mt5_bridge.config.logging import configure_logging
from telegram_mt5_bridge.config.paths import ensure_app_directories, get_app_data_dir
from telegram_mt5_bridge.config.settings import get_settings
from telegram_mt5_bridge.telegram.client import create_telegram_client


async def list_dialogs() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    ensure_app_directories(get_app_data_dir())

    client = create_telegram_client(settings)

    async with client:
        async for dialog in client.iter_dialogs():
            print(f"id={dialog.id} | name={dialog.name!r}")


def main() -> None:
    try:
        asyncio.run(list_dialogs())
    except ValueError as error:
        abort_configuration_error(error)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
