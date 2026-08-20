from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import func, select

from telegram_mt5_bridge.storage.database import (
    create_session_factory,
    create_sqlite_engine,
    init_database,
)
from telegram_mt5_bridge.storage.models import (
    TelegramMessageEvent,
    TelegramMessageRecord,
)
from telegram_mt5_bridge.storage.repositories import (
    TelegramMessageRepository,
)
from telegram_mt5_bridge.storage.schemas import (
    TelegramMessageSnapshot,
)
from telegram_mt5_bridge.storage.stats import collect_database_statistics


def make_snapshot(
    *,
    text: str = "BUY GOLD",
    edit_date: datetime | None = None,
) -> TelegramMessageSnapshot:
    now = datetime.now(UTC)

    return TelegramMessageSnapshot(
        chat_id=-100123456789,
        message_id=42,
        sender_id=123456,
        message_date=now,
        received_at=now,
        text=text,
        reply_to_message_id=None,
        has_media=False,
        media_type=None,
        edit_date=edit_date,
    )


def create_test_database(tmp_path: Path):
    database_path = tmp_path / "test.sqlite3"

    engine = create_sqlite_engine(database_path)
    init_database(engine)

    return engine, create_session_factory(engine)


def test_store_new_message(tmp_path: Path) -> None:
    engine, session_factory = create_test_database(tmp_path)

    snapshot = make_snapshot()

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_new(snapshot)

    with session_factory() as session:
        message_count = session.scalar(select(func.count()).select_from(TelegramMessageRecord))

        event_count = session.scalar(select(func.count()).select_from(TelegramMessageEvent))

    assert message_count == 1
    assert event_count == 1

    engine.dispose()


def test_duplicate_new_message_is_not_duplicated(
    tmp_path: Path,
) -> None:
    engine, session_factory = create_test_database(tmp_path)

    snapshot = make_snapshot()

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_new(snapshot)
        repository.record_new(snapshot)

    with session_factory() as session:
        message_count = session.scalar(select(func.count()).select_from(TelegramMessageRecord))

        event_count = session.scalar(select(func.count()).select_from(TelegramMessageEvent))

    assert message_count == 1
    assert event_count == 1

    engine.dispose()


def test_edit_updates_current_message(
    tmp_path: Path,
) -> None:
    engine, session_factory = create_test_database(tmp_path)

    original = make_snapshot(text="BUY GOLD 3300")

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_new(original)

    edit_time = datetime.now(UTC)

    edited = original.model_copy(
        update={
            "text": "BUY GOLD 3310",
            "edit_date": edit_time,
            "received_at": edit_time,
        }
    )

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_edit(edited)

    with session_factory() as session:
        record = session.scalar(select(TelegramMessageRecord))

        event_count = session.scalar(select(func.count()).select_from(TelegramMessageEvent))

    assert record is not None
    assert record.text == "BUY GOLD 3310"
    assert event_count == 2

    engine.dispose()


def test_delete_marks_message_deleted(
    tmp_path: Path,
) -> None:
    engine, session_factory = create_test_database(tmp_path)

    snapshot = make_snapshot()

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_new(snapshot)

    deleted_at = datetime.now(UTC)

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)

        repository.record_deleted(
            chat_id=snapshot.chat_id,
            message_id=snapshot.message_id,
            event_date=deleted_at,
        )

    with session_factory() as session:
        record = session.scalar(select(TelegramMessageRecord))

        event_count = session.scalar(select(func.count()).select_from(TelegramMessageEvent))

    assert record is not None
    assert record.deleted_at is not None
    assert event_count == 2

    engine.dispose()


def test_find_chat_id_for_message(
    tmp_path: Path,
) -> None:
    engine, session_factory = create_test_database(tmp_path)

    snapshot = make_snapshot()

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_new(snapshot)

    with session_factory() as session:
        repository = TelegramMessageRepository(session)

        chat_ids = repository.find_chat_ids_for_message(
            snapshot.message_id,
            {snapshot.chat_id},
        )

    assert chat_ids == [snapshot.chat_id]

    engine.dispose()


def test_find_chat_id_for_message_respects_allowlist(
    tmp_path: Path,
) -> None:
    engine, session_factory = create_test_database(tmp_path)

    snapshot = make_snapshot()

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_new(snapshot)

    with session_factory() as session:
        repository = TelegramMessageRepository(session)

        chat_ids = repository.find_chat_ids_for_message(
            snapshot.message_id,
            {-999999},
        )

    assert chat_ids == []

    engine.dispose()


def test_collect_database_statistics(tmp_path: Path) -> None:
    engine, session_factory = create_test_database(tmp_path)

    original = make_snapshot().model_copy(
        update={
            "reply_to_message_id": 41,
            "has_media": True,
            "media_type": "MessageMediaPhoto",
        }
    )

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_new(original)

    edit_time = datetime.now(UTC)
    edited = original.model_copy(
        update={
            "text": "SELL GOLD",
            "edit_date": edit_time,
            "received_at": edit_time,
        }
    )

    with session_factory.begin() as session:
        repository = TelegramMessageRepository(session)
        repository.record_edit(edited)
        repository.record_deleted(
            chat_id=edited.chat_id,
            message_id=edited.message_id,
            event_date=datetime.now(UTC),
        )

    with session_factory() as session:
        statistics = collect_database_statistics(session)

    assert statistics.message_count == 1
    assert statistics.event_count == 3
    assert statistics.event_counts == {
        "deleted": 1,
        "edit": 1,
        "new": 1,
    }
    assert statistics.reply_count == 1
    assert statistics.media_count == 1
    assert statistics.edited_count == 1
    assert statistics.deleted_count == 1
    assert statistics.chat_counts == ((original.chat_id, 1),)

    engine.dispose()
