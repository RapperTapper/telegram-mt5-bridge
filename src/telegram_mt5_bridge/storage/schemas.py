from datetime import datetime

from pydantic import BaseModel


class TelegramMessageSnapshot(BaseModel):
    """Raw snapshot of a Telegram message as observed by the collector."""

    chat_id: int
    message_id: int
    sender_id: int | None

    message_date: datetime
    received_at: datetime

    text: str

    reply_to_message_id: int | None = None

    has_media: bool = False
    media_type: str | None = None

    edit_date: datetime | None = None
