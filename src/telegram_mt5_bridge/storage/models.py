from datetime import UTC, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    """Return the current UTC time."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class TelegramMessageRecord(Base):
    """Current known state of one Telegram message."""

    __tablename__ = "telegram_messages"

    __table_args__ = (
        UniqueConstraint(
            "chat_id",
            "message_id",
            name="uq_telegram_message",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    message_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    sender_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    message_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    reply_to_message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    has_media: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    media_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    edit_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


class TelegramMessageEvent(Base):
    """Observed lifecycle event for a Telegram message."""

    __tablename__ = "telegram_message_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    chat_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
    )

    message_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    sender_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reply_to_message_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    has_media: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    media_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
