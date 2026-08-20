from pathlib import Path

from telegram_mt5_bridge.config.settings import Settings
from telegram_mt5_bridge.telegram.client import create_telegram_client


def test_create_telegram_client(monkeypatch, tmp_path: Path) -> None:
    settings = Settings(
        telegram_api_id=123456,
        telegram_api_hash="test-secret",
        _env_file=None,
    )

    monkeypatch.setattr(
        "telegram_mt5_bridge.telegram.client.get_telegram_session_path",
        lambda: tmp_path / "telegram",
    )

    client = create_telegram_client(settings)

    assert client.api_id == 123456
