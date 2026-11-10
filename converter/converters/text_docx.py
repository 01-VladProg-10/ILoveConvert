"""TXT ↔ DOCX (linie/akapity, UTF-8). Bez zachowania stylów."""

from __future__ import annotations

from pathlib import Path

from docx import Document

from converter.registry import converter


@converter(".txt", ".docx")
def txt_to_docx(source: Path, output_dir: Path) -> Path:
    lines = source.read_text(encoding="utf-8").splitlines() or [""]
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    target = output_dir / f"{source.stem}.docx"
    document.save(target)
    return target


@converter(".docx", ".txt")
def docx_to_txt(source: Path, output_dir: Path) -> Path:
    try:
        document = Document(source)
    except Exception as exc:
        raise ValueError(
            f"Nie udało się odczytać DOCX: {exc}. Sprawdź, czy plik nie jest uszkodzony."
        ) from exc

    text = "\n".join(p.text for p in document.paragraphs) + "\n"
    target = output_dir / f"{source.stem}.txt"
    target.write_text(text, encoding="utf-8")
    return target
