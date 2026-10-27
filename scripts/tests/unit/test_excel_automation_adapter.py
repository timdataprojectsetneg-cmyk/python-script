"""Tests for the Excel automation ingestion adapter."""

from __future__ import annotations

from openpyxl import Workbook

from ingestion.core.extractors.excel_automation_extractor import ExcelAutomationExtractor


def _make_workbook(tmp_path):
    path = tmp_path / "data.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Data"
    sheet.append(["Kategori", "Nilai"])
    sheet.append(["A", 1])
    sheet.append(["B", 2])
    workbook.save(path)
    return path


def test_adapter_yields_selected_data_table(tmp_path):
    path = _make_workbook(tmp_path)
    extractor = ExcelAutomationExtractor(
        {"source_file": str(path)},
        output="data",
        prefix="demo",
    )

    rows = list(extractor.extract())

    assert len(rows) == 2
    assert rows[0]["kategori"] == "A"
    assert rows[0]["nilai"] == 1
    assert extractor.result is not None


def test_adapter_accepts_exact_table_name(tmp_path):
    path = _make_workbook(tmp_path)
    extractor = ExcelAutomationExtractor(
        {"source_file": str(path)},
        output="data",
        table="demo_data",
        prefix="demo",
    )

    rows = list(extractor.extract())

    assert len(rows) == 2
    assert rows[1]["kategori"] == "B"
