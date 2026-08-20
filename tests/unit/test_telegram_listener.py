from telegram_mt5_bridge.telegram.listener import is_allowed_chat


def test_allowed_chat_returns_true() -> None:
    allowed_chat_ids = {-100123456789}

    assert is_allowed_chat(-100123456789, allowed_chat_ids) is True


def test_unknown_chat_returns_false() -> None:
    allowed_chat_ids = {-100123456789}

    assert is_allowed_chat(-100987654321, allowed_chat_ids) is False


def test_none_chat_id_returns_false() -> None:
    allowed_chat_ids = {-100123456789}

    assert is_allowed_chat(None, allowed_chat_ids) is False
