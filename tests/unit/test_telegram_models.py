from datetime import UTC, datetime

from telegram_mt5_bridge.telegram.models import TelegramMessage


def test_telegram_message_model() -> None:
    message = TelegramMessage(
        chat_id=-100123456789,
        message_id=42,
        sender_id=123456,
        received_at=datetime.now(UTC),
        text="Example message",
    )

    assert message.chat_id == -100123456789
    assert message.message_id == 42
    assert message.text == "Example message"
