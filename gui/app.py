"""Okno główne aplikacji — wybór pliku, katalogu i formatu docelowego."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import converter.converters  # noqa: F401 — rejestracja konwerterów
from converter.logutil import log_error, setup_logging
from converter.registry import (
    ConversionRequest,
    available_targets,
    execute,
    planned_output,
)


class ConverterApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=12)
        self.master = master
        self.source_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.target_format = tk.StringVar()
        self.status = tk.StringVar(value="Gotowy — wybierz plik wejściowy.")
        self._busy = False

        setup_logging()
        self._build()
        self.pack(fill=tk.BOTH, expand=True)

    def _build(self) -> None:
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Plik wejściowy:").grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Entry(self, textvariable=self.source_path, width=50).grid(
            row=0, column=1, sticky=tk.EW, padx=6, pady=4
        )
        ttk.Button(self, text="Wybierz…", command=self._choose_source).grid(
            row=0, column=2, pady=4
        )

        ttk.Label(self, text="Katalog zapisu:").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(self, textvariable=self.output_dir, width=50).grid(
            row=1, column=1, sticky=tk.EW, padx=6, pady=4
        )
        ttk.Button(self, text="Wybierz…", command=self._choose_output_dir).grid(
            row=1, column=2, pady=4
        )

        ttk.Label(self, text="Format docelowy:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.format_combo = ttk.Combobox(
            self,
            textvariable=self.target_format,
            state="readonly",
            width=20,
        )
        self.format_combo.grid(row=2, column=1, sticky=tk.W, padx=6, pady=4)

        self.convert_btn = ttk.Button(self, text="Konwertuj", command=self._convert)
        self.convert_btn.grid(row=3, column=1, sticky=tk.W, padx=6, pady=12)

        ttk.Label(self, text="Status:").grid(row=4, column=0, sticky=tk.NW, pady=4)
        ttk.Label(self, textvariable=self.status, wraplength=420).grid(
            row=4, column=1, columnspan=2, sticky=tk.W, padx=6, pady=4
        )

    def _choose_source(self) -> None:
        path = filedialog.askopenfilename(
            title="Wybierz plik wejściowy",
            filetypes=[
                ("Wspierane", "*.csv *.json *.txt *.docx *.odt"),
                ("Wszystkie", "*.*"),
            ],
        )
        if not path:
            return
        self.source_path.set(path)
        self._refresh_targets()

    def _choose_output_dir(self) -> None:
        path = filedialog.askdirectory(title="Wybierz katalog zapisu")
        if path:
            self.output_dir.set(path)

    def _refresh_targets(self) -> None:
        source = Path(self.source_path.get())
        targets = available_targets(source) if source.suffix else []
        self.format_combo["values"] = targets
        if targets:
            self.target_format.set(targets[0])
            self.status.set(f"Dostępne formaty: {', '.join(targets)}")
            if not self._busy:
                self.convert_btn.state(["!disabled"])
        else:
            self.target_format.set("")
            self.status.set(
                "Brak obsługiwanych formatów dla tego pliku. "
                "Wybierz plik CSV, JSON, TXT, DOCX lub ODT."
            )
            self.convert_btn.state(["disabled"])

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        if busy:
            self.convert_btn.state(["disabled"])
        elif self.target_format.get():
            self.convert_btn.state(["!disabled"])
        else:
            self.convert_btn.state(["disabled"])

    def _show_validation_error(self, message: str) -> None:
        log_error(f"Walidacja GUI: {message}")
        self.status.set(f"Błąd: {message}")
        messagebox.showwarning("Walidacja", message)

    def _convert(self) -> None:
        if self._busy:
            return

        source_raw = self.source_path.get().strip()
        output_raw = self.output_dir.get().strip()
        target = self.target_format.get().strip()

        if not source_raw:
            self._show_validation_error(
                "Nie wybrano pliku wejściowego. Kliknij „Wybierz…” przy pliku."
            )
            return
        if not output_raw:
            self._show_validation_error(
                "Nie wybrano katalogu zapisu. Kliknij „Wybierz…” przy katalogu."
            )
            return
        if not target:
            self._show_validation_error(
                "Nie wybrano formatu docelowego. Wybierz wartość z listy."
            )
            return

        source = Path(source_raw)
        output = Path(output_raw)
        request = ConversionRequest(
            source=source,
            target_format=target,
            output_dir=output,
        )

        try:
            request.validate()
        except (
            FileNotFoundError,
            NotADirectoryError,
            ValueError,
            PermissionError,
            OSError,
        ) as exc:
            self._show_validation_error(str(exc))
            return

        planned = planned_output(source, target, output)
        overwrite = True

        if planned.exists():
            choice = messagebox.askyesnocancel(
                "Plik już istnieje",
                f"Plik docelowy już istnieje:\n{planned}\n\n"
                "Tak — nadpisz\n"
                "Nie — zapisz pod bezpieczną nazwą (np. plik_1)\n"
                "Anuluj — przerwij",
            )
            if choice is None:
                self.status.set("Anulowano — plik nie został nadpisany.")
                return
            overwrite = bool(choice)

        self._set_busy(True)
        self.status.set("Trwa konwersja…")

        worker = threading.Thread(
            target=self._convert_worker,
            args=(request, overwrite),
            daemon=True,
        )
        worker.start()

    def _convert_worker(self, request: ConversionRequest, overwrite: bool) -> None:
        try:
            result = execute(request, overwrite=overwrite)
        except (
            FileNotFoundError,
            NotADirectoryError,
            ValueError,
            PermissionError,
            OSError,
            RuntimeError,
        ) as exc:
            self.after(0, self._on_error, str(exc))
            return
        self.after(0, self._on_success, result)

    def _on_success(self, result: Path) -> None:
        self._set_busy(False)
        self.status.set(f"Sukces — zapisano: {result}")
        messagebox.showinfo("Gotowe", f"Zapisano plik:\n{result}")

    def _on_error(self, message: str) -> None:
        self._set_busy(False)
        self.status.set(f"Błąd: {message}")
        messagebox.showerror("Konwersja nieudana", message)


def run_app() -> None:
    root = tk.Tk()
    root.title("Uniwersalny konwerter plików")
    root.minsize(560, 220)
    ConverterApp(root)
    root.mainloop()
