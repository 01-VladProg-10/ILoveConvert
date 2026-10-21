"""Proste CLI do demonstracji konwersji bez GUI (Lab 2).

Przykłady:
  python run_cli.py data/sample.csv .json output
  python run_cli.py data/sample.json .csv output
"""

from __future__ import annotations

import sys
from pathlib import Path

# Import konwerterów rejestruje je w REGISTRY
import converter.converters  # noqa: F401
from converter.registry import ConversionRequest, available_targets, execute


def main() -> int:
    if len(sys.argv) != 4:
        print("Użycie: python run_cli.py <plik_wejściowy> <format_docelowy> <katalog_wyjściowy>")
        print("Przykład: python run_cli.py data/sample.csv .json output")
        return 1

    source = Path(sys.argv[1])
    target_format = sys.argv[2]
    if not target_format.startswith("."):
        target_format = f".{target_format}"
    output_dir = Path(sys.argv[3])
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Dostępne formaty dla {source.name}: {available_targets(source)}")

    try:
        result = execute(
            ConversionRequest(
                source=source,
                target_format=target_format,
                output_dir=output_dir,
            )
        )
    except (FileNotFoundError, NotADirectoryError, ValueError, OSError) as exc:
        print(f"Błąd: {exc}")
        return 1

    print(f"Zapisano: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
