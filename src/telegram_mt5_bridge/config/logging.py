import logging

VALID_LOG_LEVELS = {
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
}


def configure_logging(log_level: str = "INFO") -> None:
    """Configure application logging."""

    normalized_level = log_level.upper()

    if normalized_level not in VALID_LOG_LEVELS:
        normalized_level = "INFO"

    logging.basicConfig(
        level=normalized_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
