import pytest

from telegram_mt5_bridge.cli import (
    abort_configuration_error,
    abort_no_allowed_chats,
)


def test_configuration_error_does_not_expose_input(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        abort_configuration_error(ValueError("invalid value super-secret"))

    output = capsys.readouterr().err

    assert "The local configuration is invalid." in output
    assert "super-secret" not in output


def test_no_allowed_chats_error_has_setup_guidance(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        abort_no_allowed_chats()

    output = capsys.readouterr().err

    assert "No Telegram chats configured." in output
    assert "uv run telegram-mt5-dialogs" in output
    assert "TELEGRAM_ALLOWED_CHAT_IDS" in output
