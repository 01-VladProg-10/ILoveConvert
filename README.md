# Uniwersalny konwerter plików

Aplikacja desktopowa (Python 3 + Tkinter), która pozwala wybrać plik wejściowy,
pokazuje dostępne formaty docelowe, wykonuje konwersję i zapisuje wynik
we wskazanym katalogu.

## Macierz wspieranych konwersji

| Grupa | Kierunek | Status | Narzędzie |
|-------|----------|--------|-----------|
| A | CSV → JSON | działa | stdlib (`csv`, `json`) |
| A | JSON → CSV | działa | stdlib (`csv`, `json`) |
| B | TXT → DOCX | działa | `python-docx` |
| B | DOCX → TXT | działa | `python-docx` |
| C | DOCX → PDF | działa | LibreOffice headless |
| C | ODT → PDF | działa | LibreOffice headless |

### Semantyka CSV / JSON

- Kodowanie: **UTF-8**
- JSON: lista obiektów `[{kolumna: wartość}, ...]`
- CSV: pierwszy wiersz = nagłówki; kolejność kolumn zachowana
- Puste wartości są dozwolone

### Semantyka TXT / DOCX

- Kodowanie TXT: **UTF-8**
- TXT → DOCX: każda linia staje się akapitem
- DOCX → TXT: każdy akapit trafia do osobnej linii
- Złożone formatowanie (style, tabele, obrazy) **nie** jest zachowywane

### Semantyka DOCX/ODT → PDF

- Konwersja przez LibreOffice (`--headless`), **bez** `shell=True`
- Sprawdzany jest kod zakończenia procesu oraz istnienie pliku PDF
- Identyczny układ stron / złożone formatowanie nie jest gwarantowane

## Wymagania

- Python 3.10+
- `python-docx` (patrz `requirements.txt`)
- **LibreOffice** zainstalowane systemowo (do PDF)
- Tkinter (zwykle w standardowej instalacji Pythona)

### LibreOffice

1. Zainstaluj LibreOffice: https://www.libreoffice.org/
2. Albo ustaw `LIBREOFFICE_PATH` na pełną ścieżkę do `soffice.exe` / `soffice`, np.:
   - Windows: `C:\Program Files\LibreOffice\program\soffice.exe`
   - Linux: `/usr/bin/soffice` lub `/usr/bin/libreoffice`

## Instalacja i uruchomienie

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
```

### GUI

```bash
python main.py
```

Wybierz plik → katalog zapisu → format z listy (tylko dozwolone pary) → **Konwertuj**.

### CLI (bez GUI)

```bash
# Grupa A
python run_cli.py data/sample.csv .json output
python run_cli.py data/sample.json .csv output
python run_cli.py data/sample_bad.json .csv output

# Grupa B
python run_cli.py data/sample.txt .docx output
python run_cli.py data/sample.docx .txt output

# Grupa C (wymaga LibreOffice)
python run_cli.py data/sample.docx .pdf output
python run_cli.py data/sample.odt .pdf output
```

## Struktura projektu

```
converter/           # logika konwersji (bez GUI)
  registry.py        # rejestr, walidacja, execute
  libreoffice.py     # wykrywanie soffice
  converters/        # konkretne konwertery
gui/                 # interfejs Tkinter
  app.py
data/                # przykładowe dane testowe
tests/               # testy (Lab 5)
main.py              # uruchomienie GUI
run_cli.py           # demonstracja bez GUI
```

## Autor

Polishchuk Vladyslav — Projekt 1.
