"""Rejestr konwerterów — oddziela logikę konwersji od GUI."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from converter.logutil import log

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
                f"Nie znaleziono pliku wejściowego: {self.source}. "
                "Wybierz istniejący plik."
            )
        if not self.output_dir.is_dir():
            raise NotADirectoryError(
                f"Nie znaleziono katalogu docelowego: {self.output_dir}. "
                "Wybierz istniejący katalog zapisu."
            )
        if not os.access(self.output_dir, os.W_OK):
            raise PermissionError(
                f"Brak uprawnień do zapisu w: {self.output_dir}. "
                "Wybierz inny katalog."
            )

        target = self.target_format.strip().lower()
        if not target:
            raise ValueError(
                "Nie wybrano formatu docelowego. Wybierz format z listy."
            )
        if not target.startswith("."):
            target = f".{target}"

        key = (self.source.suffix.lower(), target)
        if key not in REGISTRY:
            raise ValueError(
                f"Nieobsługiwana konwersja: {key}. "
                "Wybierz format z listy dostępnych celów."
            )


def available_targets(source: Path) -> list[str]:
    return sorted(
        target for (src, target) in REGISTRY if src == source.suffix.lower()
    )


def planned_output(source: Path, target_format: str, output_dir: Path) -> Path:
    suffix = target_format if target_format.startswith(".") else f".{target_format}"
    return output_dir / f"{source.stem}{suffix.lower()}"


def execute(request: ConversionRequest, *, overwrite: bool = False) -> Path:
    """Waliduje żądanie i uruchamia konwerter z rejestru."""
    try:
        request.validate()
        target = request.target_format.strip().lower()
        if not target.startswith("."):
            target = f".{target}"
        key = (request.source.suffix.lower(), target)

        planned = planned_output(request.source, target, request.output_dir)
        if planned.exists() and not overwrite:
            raise FileExistsError(
                f"Plik już istnieje: {planned}. "
                "Zatwierdź nadpisanie albo wybierz inny katalog."
            )

        log(f"START {request.source.name} -> {target}")
        result = REGISTRY[key](request.source, request.output_dir)
        log(f"OK {result}")
        return result
    except Exception as exc:
        log(f"BLAD {type(exc).__name__}: {exc}")
        raise
