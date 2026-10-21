"""Konwersje CSV ↔ JSON (UTF-8, zachowane nagłówki i kolejność kolumn).

Akceptowana struktura JSON:
- lista obiektów (tablica dictów), np. [{"imie": "Anna", "miasto": "Kraków"}, ...]
- wszystkie obiekty powinny mieć te same klucze (nagłówki CSV)
- kodowanie: UTF-8
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from converter.registry import converter

ENCODING = "utf-8"


@converter(".csv", ".json")
def csv_to_json(source: Path, output_dir: Path) -> Path:
    """CSV → JSON: lista obiektów z kluczami z nagłówka."""
    with source.open("r", encoding=ENCODING, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(
                "Plik CSV nie zawiera nagłówka. "
                "Dodaj wiersz z nazwami kolumn w pierwszym wierszu."
            )
        rows = list(reader)

    target = output_dir / f"{source.stem}.json"
    with target.open("w", encoding=ENCODING, newline="\n") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return target


@converter(".json", ".csv")
def json_to_csv(source: Path, output_dir: Path) -> Path:
    """JSON → CSV: lista obiektów → wiersze z nagłówkiem z kluczy pierwszego obiektu."""
    try:
        with source.open("r", encoding=ENCODING) as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Niepoprawny JSON ({exc.msg} w linii {exc.lineno}). "
            "Sprawdź składnię pliku wejściowego."
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            "Oczekiwana lista obiektów JSON (np. [{...}, {...}]). "
            f"Otrzymano typ: {type(data).__name__}."
        )
    if len(data) == 0:
        raise ValueError("Plik JSON jest pustą listą — brak wierszy do zapisu.")
    if not all(isinstance(row, dict) for row in data):
        raise ValueError(
            "Każdy element listy JSON musi być obiektem (słownikiem klucz→wartość)."
        )

    # Zachowaj kolejność kolumn z pierwszego obiektu; dołącz brakujące klucze z kolejnych
    fieldnames: list[str] = list(data[0].keys())
    for row in data[1:]:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    target = output_dir / f"{source.stem}.csv"
    with target.open("w", encoding=ENCODING, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in data:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return target
