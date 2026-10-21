"""Rejestr konwerterów — oddziela logikę konwersji od GUI."""

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
            raise FileNotFoundError("Nie znaleziono pliku wejściowego")
        if not self.output_dir.is_dir():
            raise NotADirectoryError("Nie znaleziono katalogu docelowego")
        key = (self.source.suffix.lower(), self.target_format.lower())
        if key not in REGISTRY:
            raise ValueError(f"Nieobsługiwana konwersja: {key}")


def available_targets(source: Path) -> list[str]:
    """Zwraca listę obsługiwanych formatów docelowych dla danego pliku."""
    return sorted(
        target for (src, target) in REGISTRY if src == source.suffix.lower()
    )


def execute(request: ConversionRequest) -> Path:
    """Waliduje żądanie i uruchamia odpowiedni konwerter z rejestru."""
    request.validate()
    key = (request.source.suffix.lower(), request.target_format.lower())
    # TODO (Lab 4/5): polityka nadpisywania i rejestrowanie czasu operacji
    return REGISTRY[key](request.source, request.output_dir)
