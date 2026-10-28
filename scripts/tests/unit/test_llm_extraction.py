"""Tests for the standalone LLM document extractor."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pymupdf
import pytest
from openpyxl import Workbook
from pydantic import BaseModel, Field

from ingestion.core.extractors.llm import (
    DocumentResult,
    LLMSettings,
    build_schema,
    extract_document,
    parse_json_response,
    read_document,
    resolve_output_path,
    validate_records,
    write_result,
)
from ingestion.core.extractors.llm.document_reader import DocumentReadError
from ingestion.core.extractors.llm.llm_client import Completion
from ingestion.core.extractors.llm_extractor import LLMExtractor, main
from ingestion.exceptions import IngestionError

METADATA = {
    "tahun": {"type": "integer", "required": True},
    "kategori": {"type": "string", "enum": ["Kapasitas Terpasang", "Produksi Listrik"]},
    "jenis_pembangkit": {"type": "string"},
    "nilai": {"type": ["number", "null"]},
    "satuan": {"type": ["string", "null"], "enum": ["GW", "TWh", None]},
}

RECORDS = [
    {
        "tahun": 2025,
        "kategori": "Kapasitas Terpasang",
        "jenis_pembangkit": "PLTGU",
        "nilai": 16.2,
        "satuan": "GW",
    }
]


def make_pdf(tmp_path: Path, text: str = "PLTGU 2025 Kapasitas Terpasang 16.2 GW") -> Path:
    path = tmp_path / "report.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()
    return path


def make_xlsx(tmp_path: Path) -> Path:
    path = tmp_path / "report.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ringkasan"
    sheet.append(["Tahun", "Kategori", "Jenis Pembangkit", "Nilai", "Satuan"])
    sheet.append([2025, "Kapasitas Terpasang", "PLTGU", 16.2, "GW"])
    workbook.save(path)
    return path


class Record(BaseModel):
    tahun: int
    kategori: str = Field(description="Jenis data")
    nilai: float | None = None


def test_schema_from_flat_dict():
    schema = build_schema(METADATA)
    assert schema is not None
    assert schema.names == ["tahun", "kategori", "jenis_pembangkit", "nilai", "satuan"]
    assert schema.field("tahun").required is True
    assert schema.field("nilai").nullable is True
    assert schema.field("satuan").enum == ("GW", "TWh", None)
    assert "required" in schema.json_schema()


def test_schema_from_pydantic_model():
    schema = build_schema(Record)
    assert schema is not None
    assert schema.names == ["tahun", "kategori", "nilai"]
    assert schema.field("nilai").nullable is True
    assert schema.field("kategori").description == "Jenis data"


def test_validator_drops_unknown_and_coerces_numbers():
    result = validate_records(
        [
            {
                "tahun": "2025",
                "kategori": "Kapasitas Terpasang",
                "jenis_pembangkit": "PLTGU",
                "nilai": "16.2",
                "satuan": "GW",
                "extra": "drop me",
            }
        ],
        build_schema(METADATA),
    )
    assert result.errors == []
    assert result.records == RECORDS
    assert any("unknown" in warning for warning in result.warnings)
    assert any("coerced" in warning for warning in result.warnings)


def test_validator_rejects_required_enum_and_type_errors():
    result = validate_records(
        [
            {"kategori": "Salah", "nilai": "bukan angka", "satuan": "MW"},
            {"tahun": 2025, "kategori": "Produksi Listrik", "nilai": 1, "satuan": None},
        ],
        build_schema(METADATA),
    )
    assert result.records == [
        {
            "tahun": 2025,
            "kategori": "Produksi Listrik",
            "jenis_pembangkit": None,
            "nilai": 1.0,
            "satuan": None,
        }
    ]
    assert any("required" in error for error in result.errors)
    assert any("not one of" in error for error in result.errors)
    assert any("expected number" in error for error in result.errors)


def test_document_reader_pdf_and_excel(tmp_path):
    pdf = read_document(make_pdf(tmp_path))
    assert pdf.kind == "pdf"
    assert pdf.page_count == 1
    assert "Kapasitas Terpasang" in pdf.segments[0].text

    xlsx = read_document(make_xlsx(tmp_path))
    assert xlsx.kind == "excel"
    assert xlsx.segments[0].label == "sheet Ringkasan"
    assert "PLTGU" in xlsx.segments[0].text


def test_document_reader_renders_image_for_scanned_page(tmp_path):
    path = tmp_path / "scan.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(path)
    doc.close()

    document = read_document(path, render_images=True)

    assert document.segments[0].image is not None
    assert document.images


def test_document_reader_rejects_unknown_file(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("hello")
    with pytest.raises(DocumentReadError):
        read_document(path)


def test_parse_json_response_variants():
    assert parse_json_response('```json\n{"records": [{"a": 1}]}\n```') == [{"a": 1}]
    assert parse_json_response('[{"a": 1}]') == [{"a": 1}]
    assert parse_json_response('{"a": 1}') == [{"a": 1}]


def test_extract_document_pdf_with_metadata(tmp_path):
    pdf = make_pdf(tmp_path)
    settings = LLMSettings(model="test-model", api_key_env="TEST_KEY")
    payload = json.dumps({"records": RECORDS})

    with patch(
        "ingestion.core.extractors.llm.extractor.LLMClient.complete",
        return_value=Completion(text=payload, usage={"total_tokens": 12}),
    ) as complete:
        result = extract_document(
            str(pdf),
            "Ekstrak kapasitas terpasang 2025",
            METADATA,
            settings=settings,
        )

    assert result.status == "success"
    assert result.records == RECORDS
    assert result.metadata["usage"] == {"total_tokens": 12}
    prompt = complete.call_args.args[1]
    assert "Ekstrak kapasitas" in prompt
    assert "Kapasitas Terpasang" in prompt


def test_extract_document_without_metadata_is_permissive(tmp_path):
    pdf = make_pdf(tmp_path)
    payload = json.dumps({"records": [{"apa_saja": "boleh", "nilai": 1}]})
    with patch(
        "ingestion.core.extractors.llm.extractor.LLMClient.complete",
        return_value=Completion(text=payload),
    ):
        result = extract_document(
            str(pdf),
            "Ambil apa saja",
            None,
            settings=LLMSettings(model="test-model", api_key_env="TEST_KEY"),
        )
    assert result.status == "success"
    assert result.records == [{"apa_saja": "boleh", "nilai": 1}]


def test_extract_document_invalid_json_fails(tmp_path):
    pdf = make_pdf(tmp_path)
    with patch(
        "ingestion.core.extractors.llm.extractor.LLMClient.complete",
        return_value=Completion(text="bukan json"),
    ):
        result = extract_document(
            str(pdf),
            "Ambil data",
            METADATA,
            settings=LLMSettings(model="test-model", api_key_env="TEST_KEY"),
        )
    assert result.status == "failed"
    assert any("invalid_json" in error for error in result.errors)


def test_output_writer_to_directory_and_json(tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    result = DocumentResult(status="success", records=RECORDS, metadata={"model": "test"})
    target = resolve_output_path("data/report.pdf", out_dir, "json")
    write_result(result, target, "json")

    assert target.parent == out_dir
    assert target.suffix == ".json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["status"] == "success"
    assert payload["records"] == RECORDS


def test_llm_extractor_adapter_and_save_output(tmp_path):
    pdf = make_pdf(tmp_path)
    out_dir = tmp_path / "out"
    payload = json.dumps({"records": RECORDS})

    with patch(
        "ingestion.core.extractors.llm.extractor.LLMClient.complete",
        return_value=Completion(text=payload),
    ):
        extractor = LLMExtractor(
            {},
            source_file=str(pdf),
            instruction="Ekstrak data",
            metadata=METADATA,
            settings=LLMSettings(model="test-model", api_key_env="TEST_KEY"),
            save_output=True,
            output_dir=out_dir,
        )
        records = list(extractor.extract())

    assert records == RECORDS
    files = list(out_dir.glob("*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8"))["records"] == RECORDS


def test_llm_extractor_raises_when_no_records(tmp_path):
    pdf = make_pdf(tmp_path)
    with patch(
        "ingestion.core.extractors.llm.extractor.LLMClient.complete",
        return_value=Completion(text='{"records": []}'),
    ):
        extractor = LLMExtractor(
            {},
            source_file=str(pdf),
            instruction="Ekstrak data",
            metadata=METADATA,
            settings=LLMSettings(model="test-model", api_key_env="TEST_KEY"),
        )
        with pytest.raises(IngestionError):
            list(extractor.extract())


def test_cli_save_output(tmp_path, monkeypatch):
    pdf = make_pdf(tmp_path)
    out_dir = tmp_path / "out-cli"
    payload = json.dumps({"records": RECORDS})

    with patch(
        "ingestion.core.extractors.llm.extractor.LLMClient.complete",
        return_value=Completion(text=payload),
    ):
        code = main(
            [
                str(pdf),
                "--instruction",
                "Ekstrak data",
                "--metadata",
                json.dumps(METADATA),
                "--model",
                "test-model",
                "--save-output",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert code == 0
    files = list(out_dir.glob("*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8"))["status"] == "success"


def make_multipage_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "multipage.pdf"
    doc = pymupdf.open()
    for number in range(1, 4):
        page = doc.new_page()
        page.insert_text((72, 72), f"Halaman {number} data unik {number}")
    doc.save(path)
    doc.close()
    return path


def test_document_reader_page_range(tmp_path):
    pdf = make_multipage_pdf(tmp_path)

    document = read_document(pdf, page="1-2")

    assert [segment.page for segment in document.segments] == [1, 2]
    assert "Halaman 1" in document.segments[0].text
    assert "Halaman 3" not in "\n".join(segment.text for segment in document.segments)


def test_extract_document_only_sends_requested_pages(tmp_path):
    pdf = make_multipage_pdf(tmp_path)
    with patch(
        "ingestion.core.extractors.llm.extractor.LLMClient.complete",
        return_value=Completion(text='{"records": [{"nilai": 1}]}'),
    ) as complete:
        result = extract_document(
            str(pdf),
            "Ambil data",
            None,
            page="1-2",
            settings=LLMSettings(model="test-model", api_key_env="TEST_KEY"),
        )

    assert result.status == "success"
    prompt = complete.call_args.args[1]
    assert "--- page 1 ---" in prompt
    assert "--- page 2 ---" in prompt
    assert "--- page 3 ---" not in prompt


def test_cli_page_alias(tmp_path):
    pdf = make_multipage_pdf(tmp_path)
    with patch(
        "ingestion.core.extractors.llm.extractor.LLMClient.complete",
        return_value=Completion(text='{"records": [{"nilai": 1}]}'),
    ) as complete:
        code = main(
            [
                str(pdf),
                "--instruction",
                "Ambil data",
                "--page",
                "1-2",
                "--model",
                "test-model",
            ]
        )

    assert code == 0
    prompt = complete.call_args.args[1]
    assert "--- page 1 ---" in prompt
    assert "--- page 3 ---" not in prompt


def test_document_reader_defaults_to_all_pages(tmp_path):
    pdf = make_multipage_pdf(tmp_path)
    document = read_document(pdf)
    assert [segment.page for segment in document.segments] == [1, 2, 3]
