"""Proste logowanie błędów i operacji do pliku conversion.log."""

from __future__ import annotations

import logging
from pathlib import Path

_LOG_PATH = Path("conversion.log")
_configured = False


def setup_logging() -> logging.Logger:
    """Konfiguruje logger aplikacji (plik + konsola). Wywołuj raz na start."""
    global _configured
    logger = logging.getLogger("converter")
    if _configured:
        return logger

    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(_LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    _configured = True
    return logger


def get_logger() -> logging.Logger:
    """Zwraca logger; przy pierwszym użyciu wywołuje setup_logging()."""
    if not _configured:
        return setup_logging()
    return logging.getLogger("converter")


def log_error(message: str, exc: BaseException | None = None) -> None:
    """Zapisuje błąd (z opcjonalnym wyjątkiem) do logu."""
    logger = get_logger()
    if exc is not None:
        logger.error("%s | %s: %s", message, type(exc).__name__, exc)
    else:
        logger.error("%s", message)


def log_info(message: str) -> None:
    get_logger().info(message)
