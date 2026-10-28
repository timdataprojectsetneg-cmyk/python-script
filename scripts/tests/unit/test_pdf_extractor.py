"""Tests for the PDF extractor adapter (the extraction engine is mocked)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ingestion.core.extractors import pdf_extractor as module
from ingestion.core.extractors.pdf.models import ExtractionResult, SourceInfo, Status
from ingestion.core.extractors.pdf_extractor import PdfExtractor
from ingestion.exceptions import ConfigError, IngestionError, SourceUnavailable

DICTIONARY = {"fields": {"nilai": {"type": "integer"}}}


def _result(records=None, status=Status.SUCCESS, warnings=None, errors=None):
    return ExtractionResult(
        status=status,
        source=SourceInfo(file_name="doc.pdf"),
        records=records or [],
        warnings=warnings or [],
        errors=errors or [],
    )


def test_extract_yields_records_and_passes_options(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    captured = {}

    def fake_extract_pdf(**kwargs):
        captured.update(kwargs)
        return _result(records=[{"nilai": 7}])

    monkeypatch.setattr(module, "extract_pdf", fake_extract_pdf)

    extractor = PdfExtractor(
        dictionary=DICTIONARY,
        source_file=str(pdf),
        marker="Tabel Uji",
        pages="2",
        mode="table",
        page_numbering="printed",
    )
    records = list(extractor.extract())

    assert records == [{"nilai": 7}]
    assert extractor.result is not None
    assert captured["marker"] == "Tabel Uji"
    assert captured["pages"] == "2"
    assert captured["mode"] == "table"
    assert captured["page_numbering"] == "printed"
    assert Path(captured["pdf_path"]).name == "doc.pdf"


def test_marker_is_required(tmp_path):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    extractor = PdfExtractor(dictionary=DICTIONARY, source_file=str(pdf))

    with pytest.raises(ConfigError, match="marker"):
        list(extractor.extract())


def test_dictionary_is_required(tmp_path):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    extractor = PdfExtractor(marker="Tabel Uji", source_file=str(pdf))

    with pytest.raises(ConfigError, match="dictionary"):
        list(extractor.extract())


def test_non_pdf_content_is_rejected(tmp_path):
    source = tmp_path / "doc.pdf"
    source.write_bytes(b"<html>not a pdf</html>")

    extractor = PdfExtractor(
        source_file=str(source), dictionary=DICTIONARY, marker="Tabel Uji"
    )

    with pytest.raises(SourceUnavailable, match="Not a PDF"):
        list(extractor.extract())


def test_failed_extraction_without_records_raises(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr(
        module,
        "extract_pdf",
        lambda **_: _result(status=Status.MARKER_NOT_FOUND, warnings=["marker tidak ditemukan"]),
    )

    extractor = PdfExtractor(
        source_file=str(pdf), dictionary=DICTIONARY, marker="Tabel Uji"
    )

    with pytest.raises(IngestionError, match="marker_not_found"):
        list(extractor.extract())


def test_explicit_parameters_without_config(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    captured = {}

    def fake_extract_pdf(**kwargs):
        captured.update(kwargs)
        return _result(records=[{"nilai": 1}])

    monkeypatch.setattr(module, "extract_pdf", fake_extract_pdf)

    extractor = PdfExtractor(
        dictionary=DICTIONARY,
        marker="Tabel Uji",
        source_file=str(pdf),
        pages="3",
        mode="chart",
    )

    assert list(extractor.extract()) == [{"nilai": 1}]
    assert captured["pages"] == "3"
    assert captured["mode"] == "chart"


def test_cli_prints_records(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr(module, "extract_pdf", lambda **_: _result(records=[{"nilai": 7}]))

    code = module.main(
        [
            str(pdf),
            "--dictionary",
            json.dumps(DICTIONARY),
            "--marker",
            "Tabel Uji",
            "--format",
            "ndjson",
        ]
    )

    assert code == 0
    assert json.loads(capsys.readouterr().out.strip()) == {"nilai": 7}


def test_cli_writes_json_file(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    monkeypatch.setattr(module, "extract_pdf", lambda **_: _result(records=[{"nilai": 7}]))
    output = tmp_path / "out" / "result.json"

    code = module.main(
        [
            str(pdf),
            "--dictionary",
            json.dumps(DICTIONARY),
            "--marker",
            "Tabel Uji",
            "-o",
            str(output),
        ]
    )

    assert code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["records"] == [{"nilai": 7}]
