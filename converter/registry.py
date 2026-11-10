"""Rejestr konwerterów — oddziela logikę konwersji od GUI."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

Converter = Callable[[Path, Path], Path]

REGISTRY: dict[tuple[str, str], Converter] = {}


def converter(source: str, target: str):
    """Dekorator rejestrujący pojedynczy kierunek konwersji."""

    def register(func: Converter) -> Converter:
        REGISTRY[(source.lower(), target.lower())] = func
        return func

    return register


@dataclass(frozen=True)
class ConversionRequest:
    source: Path
    target_format: str
    output_dir: Path

    def validate(self) -> None:
        if not self.source.is_file():
            raise FileNotFoundError(
                "Nie znaleziono pliku wejściowego. Wybierz istniejący plik."
            )
        if not self.output_dir.is_dir():
            raise NotADirectoryError(
                "Nie znaleziono katalogu docelowego. Wybierz istniejący katalog zapisu."
            )
        key = (self.source.suffix.lower(), self.target_format.lower())
        if key not in REGISTRY:
            raise ValueError(
                f"Nieobsługiwana konwersja: {key}. "
                "Wybierz format z listy dostępnych celów."
            )


def available_targets(source: Path) -> list[str]:
    """Zwraca listę obsługiwanych formatów docelowych dla danego pliku."""
    return sorted(
        target for (src, target) in REGISTRY if src == source.suffix.lower()
    )


def planned_output(source: Path, target_format: str, output_dir: Path) -> Path:
    """Domyślna ścieżka pliku wynikowego (ten sam stem co wejście)."""
    suffix = target_format if target_format.startswith(".") else f".{target_format}"
    return output_dir / f"{source.stem}{suffix.lower()}"


def unique_path(path: Path) -> Path:
    """Zwraca wolną nazwę: plik.ext → plik_1.ext, plik_2.ext, …"""
    if not path.exists():
        return path
    index = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def execute(request: ConversionRequest, *, overwrite: bool = False) -> Path:
    """Waliduje żądanie i uruchamia konwerter.

    Gdy plik docelowy istnieje:
    - overwrite=True  → nadpisuje
    - overwrite=False → zapisuje pod bezpieczną nazwą (stem_1, stem_2, …)
    """
    request.validate()
    key = (request.source.suffix.lower(), request.target_format.lower())
    planned = planned_output(request.source, request.target_format, request.output_dir)

    if planned.exists() and not overwrite:
        safe = unique_path(planned)
        # Konwertery zapisują jako {stem źródła}.{format} — kopiujemy wejście
        # pod unikalnym stemem, żeby wynik dostał bezpieczną nazwę.
        temp_source = request.output_dir / f"{safe.stem}{request.source.suffix.lower()}"
        if temp_source.exists():
            temp_source = unique_path(temp_source)
        shutil.copy2(request.source, temp_source)
        try:
            return REGISTRY[key](temp_source, request.output_dir)
        finally:
            temp_source.unlink(missing_ok=True)

    return REGISTRY[key](request.source, request.output_dir)
