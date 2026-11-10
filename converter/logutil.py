"""Logowanie do conversion.log."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

_LOG = Path("conversion.log")


def log(message: str) -> None:
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}\n"
    with _LOG.open("a", encoding="utf-8") as f:
        f.write(line)
