from pathlib import Path

from telegram_mt5_bridge.config.paths import (
    APP_NAME,
    ensure_app_directories,
    get_app_data_dir,
    get_log_dir,
    get_runtime_dir,
    get_telegram_session_path,
)


def test_macos_app_data_path() -> None:
    home = Path("/Users/raphael")

    path = get_app_data_dir(
        system="Darwin",
        home=home,
        environ={},
    )

    assert path == (home / "Library" / "Application Support" / APP_NAME)


def test_windows_app_data_path_uses_localappdata() -> None:
    path = get_app_data_dir(
        system="Windows",
        home=Path("C:/Users/Raphael"),
        environ={
            "LOCALAPPDATA": "C:/Users/Raphael/AppData/Local",
        },
    )

    assert path == Path("C:/Users/Raphael/AppData/Local") / APP_NAME


def test_windows_app_data_path_has_fallback() -> None:
    home = Path("C:/Users/Raphael")

    path = get_app_data_dir(
        system="Windows",
        home=home,
        environ={},
    )

    assert path == home / "AppData" / "Local" / APP_NAME


def test_linux_app_data_path() -> None:
    home = Path("/home/raphael")

    path = get_app_data_dir(
        system="Linux",
        home=home,
        environ={},
    )

    assert path == home / ".local" / "share" / APP_NAME


def test_telegram_session_path() -> None:
    base_dir = Path("/tmp/telegram-mt5-test")

    assert get_telegram_session_path(base_dir) == base_dir / "telegram"


def test_runtime_paths() -> None:
    base_dir = Path("/tmp/telegram-mt5-test")

    assert get_log_dir(base_dir) == base_dir / "logs"
    assert get_runtime_dir(base_dir) == base_dir / "runtime"


def test_ensure_app_directories(tmp_path: Path) -> None:
    app_data_dir = tmp_path / APP_NAME

    ensure_app_directories(app_data_dir)

    assert app_data_dir.is_dir()
    assert get_log_dir(app_data_dir).is_dir()
    assert get_runtime_dir(app_data_dir).is_dir()
