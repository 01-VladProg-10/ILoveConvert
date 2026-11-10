# Dane testowe — oczekiwane wyniki

| Plik | Przeznaczenie | Oczekiwany wynik konwersji |
|------|---------------|----------------------------|
| `sample.csv` | Grupa A, poprawne dane + polskie znaki + pusta wartość w `uwagi` | CSV→JSON: lista 4 obiektów, klucze `imie,nazwisko,miasto,uwagi`, UTF-8, puste `uwagi` dla Anny |
| `sample.json` | Grupa A, ta sama treść co CSV | JSON→CSV: nagłówek zachowany, 4 wiersze, polskie znaki bez uszkodzenia |
| `sample_bad.json` | Błędna składnia JSON | JSON→CSV: **brak pliku wynikowego**, kontrolowany `ValueError` (komunikat o JSON) |
| `sample.txt` | Grupa B, akapity + polskie znaki | TXT→DOCX: dokument z akapitami odpowiadającymi liniom |
| `sample.docx` | Grupa B/C | DOCX→TXT: tekst z akapitów; DOCX→PDF: otwieralny PDF (wymaga LibreOffice) |
| `sample.odt` | Grupa C | ODT→PDF: otwieralny PDF (wymaga LibreOffice) |

Minimalny zestaw do demonstracji: `sample.csv`, `sample.txt`, `sample.docx` (trzy grupy).
