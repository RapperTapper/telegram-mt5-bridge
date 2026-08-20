from pathlib import Path

from telegram_mt5_bridge.storage.stats import (
    DatabaseStatistics,
    render_database_statistics,
)


def test_render_database_statistics() -> None:
    statistics = DatabaseStatistics(
        message_count=428,
        event_count=437,
        event_counts={
            "new": 428,
            "edit": 7,
            "deleted": 2,
        },
        reply_count=14,
        media_count=21,
        edited_count=7,
        deleted_count=2,
        chat_counts=(
            (-5584034450, 147),
            (-5269379494, 281),
        ),
    )

    output = render_database_statistics(
        Path("/tmp/telegram-mt5-test/messages.sqlite3"),
        statistics,
    )

    assert "Messages: 428" in output
    assert "Events:   437" in output
    assert "new:      428" in output
    assert "replies:  14" in output
    assert "-5269379494: 281" in output
