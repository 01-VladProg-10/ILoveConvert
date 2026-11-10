"""Testy: validate(), available_targets() i konwertery."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import converter.converters  # noqa: F401
from converter.registry import (
    ConversionRequest,
    available_targets,
    execute,
    planned_output,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class TestAvailableTargets(unittest.TestCase):
    def test_csv_targets(self) -> None:
        self.assertEqual(available_targets(DATA / "sample.csv"), [".json"])

    def test_docx_targets(self) -> None:
        self.assertEqual(available_targets(DATA / "sample.docx"), [".pdf", ".txt"])

    def test_unknown_extension(self) -> None:
        self.assertEqual(available_targets(Path("plik.bin")), [])


class TestValidate(unittest.TestCase):
    def test_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ConversionRequest(DATA / "sample.csv", ".json", Path(tmp)).validate()

    def test_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                ConversionRequest(
                    DATA / "brak.csv", ".json", Path(tmp)
                ).validate()

    def test_bad_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                ConversionRequest(
                    DATA / "sample.csv", ".pdf", Path(tmp)
                ).validate()

    def test_missing_dir(self) -> None:
        with self.assertRaises(NotADirectoryError):
            ConversionRequest(
                DATA / "sample.csv", ".json", ROOT / "brak_katalogu"
            ).validate()


class TestConverters(unittest.TestCase):
    def test_csv_to_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = execute(
                ConversionRequest(DATA / "sample.csv", ".json", Path(tmp)),
                overwrite=True,
            )
            data = json.loads(result.read_text(encoding="utf-8"))
            self.assertIn("Żaneta", [row["imie"] for row in data])
            self.assertIn("Łódź", [row["miasto"] for row in data])

    def test_json_to_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = execute(
                ConversionRequest(DATA / "sample.json", ".csv", Path(tmp)),
                overwrite=True,
            )
            lines = result.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], "imie,nazwisko,miasto,uwagi")
            self.assertIn("Kowalska", result.read_text(encoding="utf-8"))

    def test_bad_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                execute(
                    ConversionRequest(DATA / "sample_bad.json", ".csv", Path(tmp)),
                    overwrite=True,
                )

    def test_txt_docx_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            docx = execute(
                ConversionRequest(DATA / "sample.txt", ".docx", out),
                overwrite=True,
            )
            txt = execute(ConversionRequest(docx, ".txt", out), overwrite=True)
            content = txt.read_text(encoding="utf-8")
            self.assertIn("ąćęłńóśźż", content)

    def test_no_overwrite_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            execute(
                ConversionRequest(DATA / "sample.csv", ".json", out),
                overwrite=True,
            )
            self.assertTrue(planned_output(DATA / "sample.csv", ".json", out).exists())
            with self.assertRaises(FileExistsError):
                execute(
                    ConversionRequest(DATA / "sample.csv", ".json", out),
                    overwrite=False,
                )


if __name__ == "__main__":
    unittest.main()
