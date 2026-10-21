# Uniwersalny konwerter plików

## Instalacja i uruchomienie

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
```

GUI i CLI pojawią się w kolejnych etapach.

## Struktura projektu

```
converter/           # logika konwersji (bez GUI)
  registry.py        # rejestr, walidacja, execute
  converters/        # konkretne konwertery
data/                # przykładowe dane testowe
gui/                 # interfejs Tkinter (Lab 4)
tests/               # testy (Lab 5)
```

## Autor

Polishchuk Vladysalv — Projekt 1.
