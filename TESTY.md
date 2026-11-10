# Raport testów — Uniwersalny konwerter plików

## Jak uruchomić

```bash
pip install -r requirements.txt
python -m unittest tests.test_registry -v
```

Testy **nie** wymagają LibreOffice (PDF sprawdzany ręcznie / CLI).

## Macierz minimalna (z instrukcji projektowej)

| Przypadek | Oczekiwany rezultat | Dowód |
|-----------|---------------------|-------|
| Poprawny plik w każdej grupie | Otwieralny wynik o właściwej treści | `data/` + CLI/GUI; automatycznie: CSV/JSON/TXT/DOCX w `tests/` |
| Błędny / uszkodzony plik | Brak awarii, czytelny komunikat | `sample_bad.json` → `ValueError`; test `test_bad_json_controlled_error` |
| Nieobsługiwana para | Opcja niewidoczna w GUI / błąd walidacji | Combobox z `available_targets`; test `test_validate_unsupported_pair` |
| Brak LibreOffice | Kontrolowany błąd z instrukcją | `LIBREOFFICE_PATH` na złą ścieżkę / odinstalowanie; komunikat z `find_libreoffice()` |
| Plik docelowy istnieje | Pytanie Tak/Nie/Anuluj lub `plik_1.ext` | GUI + test `test_unique_path_and_safe_name` |
| Polskie znaki i puste wartości | Struktura i znaki poprawne | `sample.csv` / testy roundtrip |

## Testy automatyczne (unittest)

| Test | Co sprawdza |
|------|-------------|
| `test_csv_targets` | `available_targets` dla CSV |
| `test_docx_targets` | `available_targets` dla DOCX |
| `test_unknown_extension_empty` | brak celów dla `.bin` |
| `test_validate_ok` | poprawne żądanie przechodzi |
| `test_validate_missing_file` | brak pliku → `FileNotFoundError` |
| `test_validate_unsupported_pair` | CSV→PDF → `ValueError` |
| `test_validate_missing_directory` | brak katalogu → `NotADirectoryError` |
| `test_csv_to_json_polish_and_headers` | konwerter CSV→JSON, UTF-8, nagłówki |
| `test_json_to_csv_roundtrip_headers` | konwerter JSON→CSV |
| `test_bad_json_controlled_error` | uszkodzony JSON |
| `test_txt_to_docx_and_back` | konwertery TXT↔DOCX |
| `test_unique_path_and_safe_name` | bezpieczna nazwa przy konflikcie |

## Wynik ostatniego uruchomienia

```
python -m unittest tests.test_registry -v
Ran 12 tests in 0.093s
OK
```

Data: 2026-11-10. Przed obroną uruchom ponownie na czystym środowisku według README.
