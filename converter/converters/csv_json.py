"""CSV ↔ JSON (UTF-8). JSON = lista obiektów [{kolumna: wartość}, ...]."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from converter.registry import converter


@converter(".csv", ".json")
def csv_to_json(source: Path, output_dir: Path) -> Path:
    with source.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(
                "Plik CSV nie ma nagłówka. Dodaj nazwy kolumn w pierwszym wierszu."
            )
        rows = list(reader)

    target = output_dir / f"{source.stem}.json"
    with target.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return target


@converter(".json", ".csv")
def json_to_csv(source: Path, output_dir: Path) -> Path:
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Niepoprawny JSON ({exc.msg}, linia {exc.lineno}). "
            "Sprawdź składnię pliku."
        ) from exc

    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ValueError(
            "Oczekiwana niepusta lista obiektów JSON, np. [{...}, {...}]."
        )

    fieldnames = list(data[0].keys())
    target = output_dir / f"{source.stem}.csv"
    with target.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    return target
