"""Konwersje DOCX/ODT → PDF przez LibreOffice w trybie headless.

Wymaga zainstalowanego LibreOffice. Wywołanie bez shell=True;
sprawdzany jest kod zakończenia oraz istnienie pliku wynikowego.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from converter.libreoffice import find_libreoffice
from converter.registry import converter


def _convert_with_libreoffice(source: Path, output_dir: Path) -> Path:
    soffice = find_libreoffice()
    source = source.resolve()
    output_dir = output_dir.resolve()
    target = output_dir / f"{source.stem}.pdf"

    command = [
        str(soffice),
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(source),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "LibreOffice nie zakończyło konwersji w limicie czasu (120 s)."
        ) from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(
            detail or f"Konwersja nie powiodła się (kod {result.returncode})."
        )

    if not target.exists():
        raise RuntimeError(
            f"LibreOffice nie utworzyło oczekiwanego pliku: {target}"
        )
    return target


@converter(".docx", ".pdf")
def docx_to_pdf(source: Path, output_dir: Path) -> Path:
    """DOCX → PDF (LibreOffice headless)."""
    return _convert_with_libreoffice(source, output_dir)


@converter(".odt", ".pdf")
def odt_to_pdf(source: Path, output_dir: Path) -> Path:
    """ODT → PDF (LibreOffice headless)."""
    return _convert_with_libreoffice(source, output_dir)
