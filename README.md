# Uniwersalny konwerter plików

Aplikacja desktopowa (Python 3 + Tkinter/ttk), która pozwala wybrać plik wejściowy,
pokazuje wyłącznie dostępne dla niego formaty docelowe, wykonuje konwersję
i zapisuje wynik we wskazanym katalogu.

**Projekt 1 — Programowanie V (Lab 2–5).**

## Cel

Utrwalenie pracy z systemem plików, bibliotekami zewnętrznymi, narzędziami
systemowymi (LibreOffice) oraz obsługą błędów w aplikacji z GUI.
Logika konwersji jest oddzielona od interfejsu (rejestr + dekorator `@converter`).

## Macierz wspieranych konwersji

| Grupa | Kierunek | Narzędzie | Znane ograniczenia |
|-------|----------|-----------|-------------------|
| A | CSV → JSON | stdlib (`csv`, `json`) | JSON = lista obiektów; pierwszy wiersz CSV = nagłówki |
| A | JSON → CSV | stdlib (`csv`, `json`) | Tylko lista obiektów; zły JSON → kontrolowany błąd |
| B | TXT → DOCX | `python-docx` | Linie → akapity; bez stylów/tabel/obrazów |
| B | DOCX → TXT | `python-docx` | Tylko tekst akapitów; formatowanie tracone |
| C | DOCX → PDF | LibreOffice headless | Wymaga LO; układ stron nieidentyczny z oryginałem |
| C | ODT → PDF | LibreOffice headless | Wymaga LO; układ stron nieidentyczny z oryginałem |

Aplikacja **nie** oferuje „dowolnej konwersji” — tylko pary z tabeli powyżej.

### Semantyka CSV / JSON

- Kodowanie: **UTF-8**
- JSON: `[{kolumna: wartość}, ...]`
- CSV: pierwszy wiersz = nagłówki; kolejność kolumn zachowana
- Puste wartości są dozwolone

## Wymagania

- Python 3.10+
- zależności z `requirements.txt` (`python-docx`)
- **LibreOffice** (systemowo) — tylko do DOCX/ODT → PDF
- Tkinter (zwykle w standardowej instalacji Pythona)

### LibreOffice

1. Zainstaluj: https://www.libreoffice.org/
2. Albo ustaw `LIBREOFFICE_PATH` na `soffice.exe` / `soffice`, np.:
   - Windows: `C:\Program Files\LibreOffice\program\soffice.exe`
   - Linux: `/usr/bin/soffice`

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

Przepływ: plik → katalog zapisu → format z listy → **Konwertuj**.

- formaty zależą od rozszerzenia (`available_targets`)
- dłuższe operacje w wątku (okno nie zamarza)
- konflikt nazw: nadpisanie / bezpieczna nazwa / anulowanie
- walidacja: plik, katalog, rozszerzenie, para, uprawnienia zapisu
- log: `conversion.log` (lokalny, w `.gitignore`)

### CLI

```bash
python run_cli.py data/sample.csv .json output
python run_cli.py data/sample.json .csv output
python run_cli.py data/sample_bad.json .csv output
python run_cli.py data/sample.txt .docx output
python run_cli.py data/sample.docx .txt output
python run_cli.py data/sample.docx .pdf output
python run_cli.py data/sample.odt .pdf output
```

### Testy

```bash
python -m unittest tests.test_registry -v
```

Szczegóły: [`TESTY.md`](TESTY.md). Opis danych: [`data/README.md`](data/README.md).

## Struktura projektu

```
converter/           # logika (bez GUI)
  registry.py        # rejestr, walidacja, execute
  logutil.py         # conversion.log
  libreoffice.py     # wykrywanie soffice
  converters/        # csv_json, text_docx, office_pdf
gui/app.py           # Tkinter/ttk
data/                # dane testowe
tests/               # unittest
main.py              # GUI
run_cli.py           # CLI
TESTY.md             # raport / macierz testów
requirements.txt
```

## Źródła, biblioteki i narzędzia

- [tkinter.filedialog](https://docs.python.org/3/library/dialog.html)
- [python-docx](https://python-docx.readthedocs.io/)
- [LibreOffice — parametry startowe](https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html)
- [subprocess](https://docs.python.org/3/library/subprocess.html)
- Wzorzec rejestru konwerterów z instrukcji projektowej (Programowanie V)

### Narzędzia AI

Przy tworzeniu kodu i dokumentacji korzystano z asystenta AI w Cursor (Composer).
Kod został przejrzany i dostosowany do wymagań prowadzącej; student rozumie
przepływ konwersji, rejestr, walidację oraz wywołanie LibreOffice.

## Autor

Polishchuk Vladyslav — Programowanie V, Projekt 1.
