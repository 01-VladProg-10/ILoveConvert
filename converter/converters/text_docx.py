"""Konwersje TXT ↔ DOCX (akapity, UTF-8, polskie znaki).

TXT → DOCX: każda linia (rozdzielona \\n) staje się akapitem.
DOCX → TXT: każdy akapit trafia do osobnej linii.
Złożone formatowanie (style, tabele, obrazy) nie jest zachowywane.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document

from converter.registry import converter

ENCODING = "utf-8"


@converter(".txt", ".docx")
def txt_to_docx(source: Path, output_dir: Path) -> Path:
    """TXT → DOCX: linie tekstu → akapity dokumentu."""
    text = source.read_text(encoding=ENCODING)
    # splitlines zachowuje puste linie jako puste akapity
    lines = text.splitlines()

    document = Document()
    if not lines:
        document.add_paragraph("")
    else:
        for line in lines:
            document.add_paragraph(line)

    target = output_dir / f"{source.stem}.docx"
    document.save(target)
    return target


@converter(".docx", ".txt")
def docx_to_txt(source: Path, output_dir: Path) -> Path:
    """DOCX → TXT: akapity → linie tekstu."""
    try:
        document = Document(source)
    except Exception as exc:
        raise ValueError(
            f"Nie udało się odczytać pliku DOCX: {exc}. "
            "Sprawdź, czy plik nie jest uszkodzony."
        ) from exc

    lines = [paragraph.text for paragraph in document.paragraphs]
    target = output_dir / f"{source.stem}.txt"
    target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding=ENCODING)
    return target
