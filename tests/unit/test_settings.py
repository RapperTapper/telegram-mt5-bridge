import pytest
from pydantic import ValidationError

from telegram_mt5_bridge.config.settings import Settings


def test_settings_use_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 8765
    assert settings.log_level == "INFO"
    assert settings.telegram_api_id is None
    assert settings.telegram_api_hash is None
    assert settings.telegram_allowed_chat_ids == ""


def test_settings_accept_valid_port() -> None:
    settings = Settings(api_port=9000, _env_file=None)

    assert settings.api_port == 9000


@pytest.mark.parametrize(
    "port",
    [
        0,
        -1,
        65536,
    ],
)
def test_settings_reject_invalid_port(port: int) -> None:
    with pytest.raises(ValidationError):
        Settings(api_port=port, _env_file=None)


def test_telegram_api_hash_is_not_exposed_in_repr() -> None:
    settings = Settings(
        telegram_api_hash="super-secret-value",
        _env_file=None,
    )

    assert "super-secret-value" not in repr(settings)
