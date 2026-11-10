# Uniwersalny konwerter plików

Aplikacja desktopowa (Python 3 + Tkinter/ttk): wybór pliku, lista dostępnych
formatów docelowych, konwersja i zapis do wskazanego katalogu.

**Projekt 1 — Programowanie V (Lab 2–5).**

## Macierz konwersji

| Grupa | Kierunek | Narzędzie | Ograniczenia |
|-------|----------|-----------|--------------|
| A | CSV → JSON | stdlib | JSON = lista obiektów; UTF-8; nagłówki z 1. wiersza CSV |
| A | JSON → CSV | stdlib | Tylko lista obiektów; zły JSON → czytelny błąd |
| B | TXT → DOCX | python-docx | Linie → akapity; bez stylów |
| B | DOCX → TXT | python-docx | Tylko tekst akapitów |
| C | DOCX → PDF | LibreOffice | Wymaga LO; układ stron nieidentyczny |
| C | ODT → PDF | LibreOffice | Wymaga LO; układ stron nieidentyczny |

## Wymagania

- Python 3.10+
- `pip install -r requirements.txt` (`python-docx`)
- LibreOffice (do PDF) albo `LIBREOFFICE_PATH`
- Tkinter (zwykle w instalacji Pythona)

## Instalacja i uruchomienie

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

CLI:

```bash
python run_cli.py data/sample.csv .json output
python run_cli.py data/sample_bad.json .csv output
python run_cli.py data/sample.docx .pdf output
```

Testy:

```bash
python -m unittest tests.test_registry -v
```

Szczegóły: [`TESTY.md`](TESTY.md), dane: [`data/README.md`](data/README.md).

## Zachowanie GUI

- formaty z `available_targets` (niedozwolona para niewybieralna)
- konwersja w wątku (okno nie zamarza)
- gdy plik istnieje → pytanie o nadpisanie
- błędy w statusie / messagebox oraz w `conversion.log`

## Struktura

```
converter/     # logika (registry, logutil, converters)
gui/app.py     # Tkinter
data/          # dane testowe
tests/         # unittest
main.py        # start GUI
run_cli.py     # CLI
```

## Źródła

- dokumentacja tkinter, python-docx, LibreOffice CLI, subprocess
- wzorzec rejestru z instrukcji projektowej
- asystent AI w Cursor — kod przejrzany i dostosowany do wymagań

## Autor

Polishchuk Vladyslav — Programowanie V, Projekt 1.
