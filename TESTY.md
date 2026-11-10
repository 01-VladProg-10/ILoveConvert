# Raport testów

## Uruchomienie

```bash
pip install -r requirements.txt
python -m unittest tests.test_registry -v
```

## Macierz z instrukcji

| Przypadek | Dowód |
|-----------|-------|
| Poprawny plik w każdej grupie | `data/` + CLI/GUI; testy CSV/JSON/TXT/DOCX |
| Błędny plik | `sample_bad.json` → `ValueError`; test `test_bad_json` |
| Nieobsługiwana para | Combobox / `test_bad_pair` |
| Brak LibreOffice | zła `LIBREOFFICE_PATH` → komunikat z instrukcją |
| Plik już istnieje | pytanie o nadpisanie w GUI; `test_no_overwrite_raises` |
| Polskie znaki | `test_csv_to_json`, `test_txt_docx_roundtrip` |

## Wynik

```
Ran 12 tests
OK
```
