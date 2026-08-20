from unittest.mock import Mock

from telegram_mt5_bridge.telegram.collector import (
    resolve_deleted_message_chat_id,
)


def test_delete_uses_event_chat_id_when_available() -> None:
    repository = Mock()

    result = resolve_deleted_message_chat_id(
        event_chat_id=-100123,
        message_id=42,
        allowed_chat_ids={-100123},
        repository=repository,
    )

    assert result == -100123
    repository.find_chat_ids_for_message.assert_not_called()


def test_delete_resolves_missing_chat_from_database() -> None:
    repository = Mock()
    repository.find_chat_ids_for_message.return_value = [-100123]

    result = resolve_deleted_message_chat_id(
        event_chat_id=None,
        message_id=42,
        allowed_chat_ids={-100123},
        repository=repository,
    )

    assert result == -100123


def test_delete_rejects_ambiguous_database_match() -> None:
    repository = Mock()
    repository.find_chat_ids_for_message.return_value = [
        -100123,
        -100456,
    ]

    result = resolve_deleted_message_chat_id(
        event_chat_id=None,
        message_id=42,
        allowed_chat_ids={
            -100123,
            -100456,
        },
        repository=repository,
    )

    assert result is None


def test_delete_rejects_disallowed_event_chat() -> None:
    repository = Mock()

    result = resolve_deleted_message_chat_id(
        event_chat_id=-100999,
        message_id=42,
        allowed_chat_ids={-100123},
        repository=repository,
    )

    assert result is None
    repository.find_chat_ids_for_message.assert_not_called()
