"""CLI bez GUI — demonstracja konwersji.

Przykład: python run_cli.py data/sample.csv .json output
"""

from __future__ import annotations

import sys
from pathlib import Path

import converter.converters  # noqa: F401
from converter.registry import ConversionRequest, available_targets, execute


def main() -> int:
    if len(sys.argv) != 4:
        print("Użycie: python run_cli.py <plik> <format> <katalog>")
        print("Przykład: python run_cli.py data/sample.csv .json output")
        return 1

    source = Path(sys.argv[1])
    target = sys.argv[2] if sys.argv[2].startswith(".") else f".{sys.argv[2]}"
    output_dir = Path(sys.argv[3])
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Dostępne formaty: {available_targets(source)}")
    try:
        result = execute(
            ConversionRequest(source, target, output_dir),
            overwrite=True,
        )
    except Exception as exc:
        print(f"Błąd: {exc}")
        return 1

    print(f"Zapisano: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
