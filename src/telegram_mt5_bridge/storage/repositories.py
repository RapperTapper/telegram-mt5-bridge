from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from telegram_mt5_bridge.storage.models import (
    TelegramMessageEvent,
    TelegramMessageRecord,
    utc_now,
)
from telegram_mt5_bridge.storage.schemas import TelegramMessageSnapshot


class TelegramMessageRepository:
    """Persistence operations for raw Telegram messages."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _get_message(
        self,
        chat_id: int,
        message_id: int,
    ) -> TelegramMessageRecord | None:
        statement = select(TelegramMessageRecord).where(
            TelegramMessageRecord.chat_id == chat_id,
            TelegramMessageRecord.message_id == message_id,
        )

        return self.session.scalar(statement)

    def _event_exists(
        self,
        *,
        chat_id: int,
        message_id: int,
        event_type: str,
        event_date: datetime | None = None,
    ) -> bool:
        statement = select(TelegramMessageEvent.id).where(
            TelegramMessageEvent.chat_id == chat_id,
            TelegramMessageEvent.message_id == message_id,
            TelegramMessageEvent.event_type == event_type,
        )

        if event_date is not None:
            statement = statement.where(TelegramMessageEvent.event_date == event_date)

        return self.session.scalar(statement) is not None

    def _add_snapshot_event(
        self,
        *,
        snapshot: TelegramMessageSnapshot,
        event_type: str,
        event_date: datetime,
    ) -> None:
        if self._event_exists(
            chat_id=snapshot.chat_id,
            message_id=snapshot.message_id,
            event_type=event_type,
            event_date=event_date,
        ):
            return

        event = TelegramMessageEvent(
            chat_id=snapshot.chat_id,
            message_id=snapshot.message_id,
            event_type=event_type,
            sender_id=snapshot.sender_id,
            text=snapshot.text,
            reply_to_message_id=snapshot.reply_to_message_id,
            has_media=snapshot.has_media,
            media_type=snapshot.media_type,
            event_date=event_date,
        )

        self.session.add(event)

    def record_new(
        self,
        snapshot: TelegramMessageSnapshot,
    ) -> None:
        """Store a newly observed Telegram message."""

        record = self._get_message(
            snapshot.chat_id,
            snapshot.message_id,
        )

        now = utc_now()

        if record is None:
            record = TelegramMessageRecord(
                chat_id=snapshot.chat_id,
                message_id=snapshot.message_id,
                sender_id=snapshot.sender_id,
                message_date=snapshot.message_date,
                text=snapshot.text,
                reply_to_message_id=snapshot.reply_to_message_id,
                has_media=snapshot.has_media,
                media_type=snapshot.media_type,
                edit_date=snapshot.edit_date,
                first_seen_at=snapshot.received_at,
                last_seen_at=now,
            )

            self.session.add(record)

        else:
            record.sender_id = snapshot.sender_id
            record.text = snapshot.text
            record.reply_to_message_id = snapshot.reply_to_message_id
            record.has_media = snapshot.has_media
            record.media_type = snapshot.media_type
            record.last_seen_at = now

        self._add_snapshot_event(
            snapshot=snapshot,
            event_type="new",
            event_date=snapshot.message_date,
        )

    def record_edit(
        self,
        snapshot: TelegramMessageSnapshot,
    ) -> None:
        """Store an edited Telegram message."""

        record = self._get_message(
            snapshot.chat_id,
            snapshot.message_id,
        )

        now = utc_now()

        if record is None:
            record = TelegramMessageRecord(
                chat_id=snapshot.chat_id,
                message_id=snapshot.message_id,
                sender_id=snapshot.sender_id,
                message_date=snapshot.message_date,
                text=snapshot.text,
                reply_to_message_id=snapshot.reply_to_message_id,
                has_media=snapshot.has_media,
                media_type=snapshot.media_type,
                edit_date=snapshot.edit_date,
                first_seen_at=snapshot.received_at,
                last_seen_at=now,
            )

            self.session.add(record)

        else:
            record.sender_id = snapshot.sender_id
            record.text = snapshot.text
            record.reply_to_message_id = snapshot.reply_to_message_id
            record.has_media = snapshot.has_media
            record.media_type = snapshot.media_type
            record.edit_date = snapshot.edit_date
            record.last_seen_at = now

        event_date = snapshot.edit_date or snapshot.received_at

        self._add_snapshot_event(
            snapshot=snapshot,
            event_type="edit",
            event_date=event_date,
        )

    def record_deleted(
        self,
        *,
        chat_id: int,
        message_id: int,
        event_date: datetime,
    ) -> None:
        """Record that a Telegram message was deleted."""

        record = self._get_message(
            chat_id,
            message_id,
        )

        if record is not None:
            record.deleted_at = event_date
            record.last_seen_at = event_date

        if self._event_exists(
            chat_id=chat_id,
            message_id=message_id,
            event_type="deleted",
        ):
            return

        event = TelegramMessageEvent(
            chat_id=chat_id,
            message_id=message_id,
            event_type="deleted",
            event_date=event_date,
            text=None,
        )

        self.session.add(event)
