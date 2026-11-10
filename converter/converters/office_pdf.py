"""Konwersje DOCX/ODT → PDF przez LibreOffice (headless, bez shell=True)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from converter.registry import converter

_HINT = (
    "Zainstaluj LibreOffice (https://www.libreoffice.org/) "
    "albo ustaw LIBREOFFICE_PATH na ścieżkę do soffice.exe / soffice."
)


def find_libreoffice() -> Path:
    """Szuka soffice: LIBREOFFICE_PATH, PATH, typowe ścieżki Windows."""
    env = os.environ.get("LIBREOFFICE_PATH")
    if env:
        path = Path(env)
        if path.is_file():
            return path
        raise RuntimeError(f"LIBREOFFICE_PATH jest niepoprawne: {path}. {_HINT}")

    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return Path(found)

    for candidate in (
        Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
        Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
    ):
        if candidate.is_file():
            return candidate

    raise RuntimeError(f"Nie znaleziono LibreOffice. {_HINT}")


def _to_pdf(source: Path, output_dir: Path) -> Path:
    soffice = find_libreoffice()
    source = source.resolve()
    output_dir = output_dir.resolve()
    target = output_dir / f"{source.stem}.pdf"

    result = subprocess.run(
        [
            str(soffice),
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_dir),
            str(source),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(detail or "Konwersja do PDF nie powiodła się.")
    if not target.exists():
        raise RuntimeError("LibreOffice nie utworzyło oczekiwanego pliku PDF.")
    return target


@converter(".docx", ".pdf")
def docx_to_pdf(source: Path, output_dir: Path) -> Path:
    return _to_pdf(source, output_dir)


@converter(".odt", ".pdf")
def odt_to_pdf(source: Path, output_dir: Path) -> Path:
    return _to_pdf(source, output_dir)
