"""Wykrywanie instalacji LibreOffice (soffice) na Windows / Linux / macOS."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

_INSTALL_HINT = (
    "Zainstaluj LibreOffice (https://www.libreoffice.org/) "
    "albo ustaw zmienną środowiskową LIBREOFFICE_PATH "
    "na pełną ścieżkę do soffice / soffice.exe."
)

_WINDOWS_CANDIDATES = (
    Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
    Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
)


def find_libreoffice() -> Path:
    """Zwraca ścieżkę do wykonywalnego soffice albo rzuca RuntimeError."""
    env = os.environ.get("LIBREOFFICE_PATH")
    if env:
        path = Path(env)
        if path.is_file():
            return path
        raise RuntimeError(
            f"LIBREOFFICE_PATH wskazuje nieistniejący plik: {path}. {_INSTALL_HINT}"
        )

    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return Path(found)

    for candidate in _WINDOWS_CANDIDATES:
        if candidate.is_file():
            return candidate

    raise RuntimeError(f"Nie znaleziono LibreOffice. {_INSTALL_HINT}")
