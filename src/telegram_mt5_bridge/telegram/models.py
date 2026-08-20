from datetime import datetime

from pydantic import BaseModel


class TelegramMessage(BaseModel):
    chat_id: int
    message_id: int
    sender_id: int | None
    received_at: datetime
    text: str
