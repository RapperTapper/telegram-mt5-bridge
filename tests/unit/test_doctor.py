from pathlib import Path

from telegram_mt5_bridge.doctor import DoctorReport, render_doctor_report
from telegram_mt5_bridge.storage.stats import DatabaseStatistics


def test_render_doctor_report() -> None:
    statistics = DatabaseStatistics(
        message_count=428,
        event_count=437,
        event_counts={
            "new": 428,
            "edit": 7,
            "deleted": 2,
        },
        reply_count=12,
        media_count=21,
        edited_count=7,
        deleted_count=2,
        chat_counts=((-5269379494, 428),),
    )
    report = DoctorReport(
        api_id_configured=True,
        api_hash_configured=True,
        allowed_chat_count=3,
        app_data_dir=Path("/tmp/TelegramMT5Bridge"),
        runtime_accessible=True,
        session_found=True,
        database_path=Path("/tmp/TelegramMT5Bridge/runtime/messages.sqlite3"),
        database_found=True,
        database_writable=True,
        database_statistics=statistics,
    )

    output = render_doctor_report(report)

    assert "Telegram API ID:        configured" in output
    assert "Telegram API hash:      configured" in output
    assert "Allowed chats:          3" in output
    assert "Messages:               428" in output
    assert "Replies:                12" in output
    assert "Status: OK" in output


def test_doctor_report_requires_complete_setup() -> None:
    report = DoctorReport(
        api_id_configured=False,
        api_hash_configured=False,
        allowed_chat_count=0,
        app_data_dir=Path("/tmp/TelegramMT5Bridge"),
        runtime_accessible=True,
        session_found=False,
        database_path=Path("/tmp/TelegramMT5Bridge/runtime/messages.sqlite3"),
        database_found=True,
        database_writable=True,
        database_statistics=None,
    )

    assert report.is_ok is False
    assert "Status: SETUP REQUIRED" in render_doctor_report(report)
