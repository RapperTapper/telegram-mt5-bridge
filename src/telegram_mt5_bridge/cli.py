import sys
from typing import Never


class NoAllowedChatsError(RuntimeError):
    """Raised when the Telegram collector has no configured chat allowlist."""


def abort_configuration_error(error: ValueError) -> Never:
    """Exit with safe configuration guidance and no secret values."""

    error_text = str(error)

    if "TELEGRAM_API_ID" in error_text:
        detail = "TELEGRAM_API_ID is not configured."
    elif "TELEGRAM_API_HASH" in error_text:
        detail = "TELEGRAM_API_HASH is not configured."
    else:
        detail = "The local configuration is invalid."

    print(
        "Configuration error:\n"
        f"{detail}\n\n"
        "Create .env from .env.example and configure your Telegram credentials.",
        file=sys.stderr,
    )
    raise SystemExit(1) from None


def abort_no_allowed_chats() -> Never:
    """Exit with guidance for configuring the Telegram chat allowlist."""

    print(
        "No Telegram chats configured.\n\n"
        "Run:\n"
        "uv run telegram-mt5-dialogs\n\n"
        "Then add the desired IDs to TELEGRAM_ALLOWED_CHAT_IDS in .env.",
        file=sys.stderr,
    )
    raise SystemExit(1) from None
