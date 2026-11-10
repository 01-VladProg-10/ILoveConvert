"""GUI Tkinter — wybór pliku, katalogu i formatu docelowego."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import converter.converters  # noqa: F401
from converter.registry import (
    ConversionRequest,
    available_targets,
    execute,
    planned_output,
)


class ConverterApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=12)
        self.source_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.target_format = tk.StringVar()
        self.status = tk.StringVar(value="Gotowy — wybierz plik wejściowy.")
        self._busy = False
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
            self, textvariable=self.target_format, state="readonly", width=20
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
        if path:
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
            self.status.set("Brak obsługiwanych formatów dla tego pliku.")
            self.convert_btn.state(["disabled"])

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.convert_btn.state(["disabled"] if busy else ["!disabled"])

    def _convert(self) -> None:
        if self._busy:
            return

        source_raw = self.source_path.get().strip()
        output_raw = self.output_dir.get().strip()
        target = self.target_format.get().strip()
        if not source_raw or not output_raw or not target:
            messagebox.showwarning("Brak danych", "Uzupełnij plik, katalog i format.")
            return

        source = Path(source_raw)
        output = Path(output_raw)
        planned = planned_output(source, target, output)
        overwrite = False
        if planned.exists():
            if not messagebox.askyesno(
                "Plik już istnieje",
                f"Plik już istnieje:\n{planned}\n\nCzy nadpisać?",
            ):
                self.status.set("Anulowano — plik nie został nadpisany.")
                return
            overwrite = True

        request = ConversionRequest(source, target, output)
        self._set_busy(True)
        self.status.set("Trwa konwersja…")
        threading.Thread(
            target=self._worker, args=(request, overwrite), daemon=True
        ).start()

    def _worker(self, request: ConversionRequest, overwrite: bool) -> None:
        try:
            result = execute(request, overwrite=overwrite)
        except Exception as exc:
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
