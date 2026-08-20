import asyncio

from telegram_mt5_bridge.config.logging import configure_logging
from telegram_mt5_bridge.config.settings import get_settings
from telegram_mt5_bridge.telegram.client import create_telegram_client


async def list_dialogs() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    client = create_telegram_client(settings)

    async with client:
        async for dialog in client.iter_dialogs():
            print(f"id={dialog.id} | name={dialog.name!r}")


def main() -> None:
    asyncio.run(list_dialogs())


if __name__ == "__main__":
    main()
