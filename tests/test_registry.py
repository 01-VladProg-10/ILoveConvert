"""Testy automatyczne: validate(), available_targets() i konwertery."""

from __future__ import annotations

import json
import logging
import tempfile
import unittest
from pathlib import Path

import converter.converters  # noqa: F401 — rejestracja

logging.disable(logging.CRITICAL)
from converter.registry import (
    ConversionRequest,
    available_targets,
    execute,
    planned_output,
    unique_path,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class TestAvailableTargets(unittest.TestCase):
    def test_csv_targets(self) -> None:
        targets = available_targets(DATA / "sample.csv")
        self.assertEqual(targets, [".json"])

    def test_docx_targets(self) -> None:
        targets = available_targets(DATA / "sample.docx")
        self.assertEqual(targets, [".pdf", ".txt"])

    def test_unknown_extension_empty(self) -> None:
        targets = available_targets(Path("plik.bin"))
        self.assertEqual(targets, [])


class TestValidate(unittest.TestCase):
    def test_validate_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ConversionRequest(
                source=DATA / "sample.csv",
                target_format=".json",
                output_dir=Path(tmp),
            ).validate()

    def test_validate_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                ConversionRequest(
                    source=DATA / "nie_ma_takiego.csv",
                    target_format=".json",
                    output_dir=Path(tmp),
                ).validate()

    def test_validate_unsupported_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                ConversionRequest(
                    source=DATA / "sample.csv",
                    target_format=".pdf",
                    output_dir=Path(tmp),
                ).validate()

    def test_validate_missing_directory(self) -> None:
        with self.assertRaises(NotADirectoryError):
            ConversionRequest(
                source=DATA / "sample.csv",
                target_format=".json",
                output_dir=ROOT / "katalog_ktorego_nie_ma",
            ).validate()


class TestConverters(unittest.TestCase):
    def test_csv_to_json_polish_and_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = execute(
                ConversionRequest(DATA / "sample.csv", ".json", out),
                overwrite=True,
            )
            self.assertTrue(result.is_file())
            data = json.loads(result.read_text(encoding="utf-8"))
            self.assertIsInstance(data, list)
            self.assertGreaterEqual(len(data), 1)
            self.assertIn("imie", data[0])
            self.assertIn("Żaneta", [row["imie"] for row in data])
            self.assertIn("Łódź", [row["miasto"] for row in data])

    def test_json_to_csv_roundtrip_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = execute(
                ConversionRequest(DATA / "sample.json", ".csv", out),
                overwrite=True,
            )
            text = result.read_text(encoding="utf-8")
            first_line = text.splitlines()[0]
            self.assertEqual(first_line, "imie,nazwisko,miasto,uwagi")
            self.assertIn("Kowalska", text)

    def test_bad_json_controlled_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError) as ctx:
                execute(
                    ConversionRequest(DATA / "sample_bad.json", ".csv", Path(tmp)),
                    overwrite=True,
                )
            self.assertIn("JSON", str(ctx.exception))

    def test_txt_to_docx_and_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            docx = execute(
                ConversionRequest(DATA / "sample.txt", ".docx", out),
                overwrite=True,
            )
            self.assertTrue(docx.is_file())
            self.assertEqual(docx.suffix.lower(), ".docx")

            txt = execute(
                ConversionRequest(docx, ".txt", out),
                overwrite=True,
            )
            content = txt.read_text(encoding="utf-8")
            self.assertIn("ąćęłńóśźż", content)
            self.assertIn("ĄĆĘŁŃÓŚŹŻ", content)


class TestOverwritePolicy(unittest.TestCase):
    def test_unique_path_and_safe_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            first = execute(
                ConversionRequest(DATA / "sample.csv", ".json", out),
                overwrite=True,
            )
            planned = planned_output(DATA / "sample.csv", ".json", out)
            self.assertEqual(first, planned)
            self.assertTrue(planned.exists())

            safe = unique_path(planned)
            self.assertEqual(safe.name, "sample_1.json")

            second = execute(
                ConversionRequest(DATA / "sample.csv", ".json", out),
                overwrite=False,
            )
            self.assertEqual(second.name, "sample_1.json")
            self.assertTrue(second.is_file())


if __name__ == "__main__":
    unittest.main()
