import pytest
from pydantic import ValidationError

from telegram_mt5_bridge.config.settings import (
    Settings,
    get_allowed_chat_ids,
    get_telegram_credentials,
)


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


def test_get_telegram_credentials() -> None:
    settings = Settings(
        telegram_api_id=123456,
        telegram_api_hash="test-secret",
        _env_file=None,
    )

    credentials = get_telegram_credentials(settings)

    assert credentials.api_id == 123456
    assert credentials.api_hash.get_secret_value() == "test-secret"


def test_get_telegram_credentials_requires_api_id() -> None:
    settings = Settings(
        telegram_api_hash="test-secret",
        _env_file=None,
    )

    with pytest.raises(ValueError, match="TELEGRAM_API_ID"):
        get_telegram_credentials(settings)


def test_get_telegram_credentials_requires_api_hash() -> None:
    settings = Settings(
        telegram_api_id=123456,
        _env_file=None,
    )

    with pytest.raises(ValueError, match="TELEGRAM_API_HASH"):
        get_telegram_credentials(settings)


def test_get_allowed_chat_ids_empty() -> None:
    settings = Settings(_env_file=None)

    assert get_allowed_chat_ids(settings) == set()


def test_get_allowed_chat_ids() -> None:
    settings = Settings(
        telegram_allowed_chat_ids="-100123,-100456",
        _env_file=None,
    )

    assert get_allowed_chat_ids(settings) == {
        -100123,
        -100456,
    }
