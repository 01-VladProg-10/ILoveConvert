# Uniwersalny konwerter plików

Aplikacja desktopowa (Python 3 + Tkinter), która pozwala wybrać plik wejściowy,
pokazuje dostępne formaty docelowe, wykonuje konwersję i zapisuje wynik
we wskazanym katalogu.

## Macierz wspieranych konwersji

| Grupa | Kierunek | Status | Narzędzie |
|-------|----------|--------|-----------|
| A | CSV → JSON | działa (CLI) | stdlib (`csv`, `json`) |
| A | JSON → CSV | działa (CLI) | stdlib (`csv`, `json`) |
| B | TXT → DOCX | działa (CLI) | `python-docx` |
| B | DOCX → TXT | działa (CLI) | `python-docx` |
| C | DOCX → PDF | planowane (Lab 3) | LibreOffice headless |
| C | ODT → PDF | planowane (Lab 3) | LibreOffice headless |

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

## Wymagania

- Python 3.10+
- `python-docx` (patrz `requirements.txt`)
- (później) LibreOffice — do konwersji DOCX/ODT → PDF

## Instalacja i uruchomienie

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
```

### CLI (bez GUI)

```bash
# Grupa A
python run_cli.py data/sample.csv .json output
python run_cli.py data/sample.json .csv output
python run_cli.py data/sample_bad.json .csv output

# Grupa B
python run_cli.py data/sample.txt .docx output
python run_cli.py output/sample.docx .txt output
```

## Struktura projektu

```
converter/           # logika konwersji (bez GUI)
  registry.py        # rejestr, walidacja, execute
  converters/        # konkretne konwertery
data/                # przykładowe dane testowe
gui/                 # interfejs Tkinter (Lab 4)
tests/               # testy (Lab 5)
run_cli.py           # demonstracja bez GUI
```

## Autor

Polishchuk Vladyslav — Projekt 1.
