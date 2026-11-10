"""Rejestr konwerterów — oddziela logikę konwersji od GUI."""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from converter.logutil import log_error, log_info

Converter = Callable[[Path, Path], Path]

REGISTRY: dict[tuple[str, str], Converter] = {}


def converter(source: str, target: str):
    """Dekorator rejestrujący pojedynczy kierunek konwersji."""

    def register(func: Converter) -> Converter:
        REGISTRY[(source.lower(), target.lower())] = func
        return func

    return register


def supported_source_extensions() -> list[str]:
    """Rozszerzenia wejściowe obecne w rejestrze."""
    return sorted({src for src, _ in REGISTRY})


@dataclass(frozen=True)
class ConversionRequest:
    source: Path
    target_format: str
    output_dir: Path

    def validate(self) -> None:
        """Sprawdza plik, katalog, rozszerzenie, parę formatów i możliwość zapisu.

        Komunikaty zawierają przyczynę oraz sugerowany dalszy krok.
        """
        if not str(self.source).strip():
            raise ValueError(
                "Nie wybrano pliku wejściowego. Wybierz plik w oknie dialogowym."
            )
        if not str(self.output_dir).strip():
            raise ValueError(
                "Nie wybrano katalogu zapisu. Wskaż istniejący katalog docelowy."
            )

        target = self.target_format.strip().lower()
        if not target:
            raise ValueError(
                "Nie wybrano formatu docelowego. Wybierz format z listy Combobox."
            )
        if not target.startswith("."):
            target = f".{target}"

        if not self.source.exists():
            raise FileNotFoundError(
                f"Nie znaleziono pliku wejściowego: {self.source}. "
                "Sprawdź ścieżkę lub wybierz inny plik."
            )
        if not self.source.is_file():
            raise ValueError(
                f"Ścieżka wejściowa nie jest plikiem: {self.source}. "
                "Wybierz zwykły plik, nie katalog."
            )

        suffix = self.source.suffix.lower()
        if not suffix:
            raise ValueError(
                "Plik wejściowy nie ma rozszerzenia. "
                "Podaj plik z obsługiwanym rozszerzeniem "
                f"({', '.join(supported_source_extensions()) or 'brak zarejestrowanych'})."
            )

        known_sources = set(supported_source_extensions())
        if known_sources and suffix not in known_sources:
            raise ValueError(
                f"Rozszerzenie wejściowe {suffix} nie jest obsługiwane. "
                f"Obsługiwane wejścia: {', '.join(sorted(known_sources))}. "
                "Wybierz inny plik lub dodaj konwerter do rejestru."
            )

        if not self.output_dir.exists():
            raise NotADirectoryError(
                f"Nie znaleziono katalogu docelowego: {self.output_dir}. "
                "Utwórz katalog albo wybierz inny."
            )
        if not self.output_dir.is_dir():
            raise NotADirectoryError(
                f"Ścieżka zapisu nie jest katalogiem: {self.output_dir}. "
                "Wybierz folder, nie plik."
            )

        if not os.access(self.output_dir, os.W_OK):
            raise PermissionError(
                f"Brak uprawnień do zapisu w katalogu: {self.output_dir}. "
                "Wybierz inny katalog lub zmień uprawnienia."
            )

        key = (suffix, target)
        if key not in REGISTRY:
            available = available_targets(self.source)
            hint = (
                f"Dostępne dla tego pliku: {', '.join(available)}."
                if available
                else "Brak zarejestrowanych celów dla tego rozszerzenia."
            )
            raise ValueError(
                f"Nieobsługiwana konwersja: {suffix} -> {target}. {hint} "
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
    try:
        request.validate()
        target_fmt = request.target_format.strip().lower()
        if not target_fmt.startswith("."):
            target_fmt = f".{target_fmt}"
        key = (request.source.suffix.lower(), target_fmt)

        planned = planned_output(request.source, target_fmt, request.output_dir)
        log_info(
            f"Start konwersji: {request.source.name} -> {target_fmt} "
            f"(overwrite={overwrite})"
        )

        if planned.exists() and not overwrite:
            safe = unique_path(planned)
            temp_source = (
                request.output_dir / f"{safe.stem}{request.source.suffix.lower()}"
            )
            if temp_source.exists():
                temp_source = unique_path(temp_source)
            shutil.copy2(request.source, temp_source)
            try:
                result = REGISTRY[key](temp_source, request.output_dir)
            finally:
                temp_source.unlink(missing_ok=True)
        else:
            result = REGISTRY[key](request.source, request.output_dir)

        log_info(f"Sukces: zapisano {result}")
        return result
    except Exception as exc:
        log_error("Konwersja nieudana", exc)
        raise
