"""Tests for the Data Mogok Kerja source (flat extractor, 2-row header)."""

from io import BytesIO

from openpyxl import Workbook

from ingestion.core.extractors.excel_extractor import ExcelExtractor
from ingestion.usecases.ketenagakerjaan.kemnaker.data_mogok_kerja.extractor import (
    Extractor,
)
from ingestion.usecases.ketenagakerjaan.kemnaker.data_mogok_kerja.models import Record
from ingestion.usecases.ketenagakerjaan.kemnaker.data_mogok_kerja.normalizer import (
    Normalizer,
)


def _build_workbook() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "mogok"
    worksheet.append(["Jumlah Kasus Mogok Kerja dan Tenaga Kerja yang Terlibat di Indonesia Menurut Provinsi", None, None, None])
    worksheet.append(["Tahun 2026", None, None, None])
    worksheet.append([None, None, None, None])
    worksheet.append(["No.", "Provinsi", "Januari s.d Maret", None])
    worksheet.append([None, None, "Kasus", "Tenaga Kerja yang Terlibat (orang)"])
    worksheet.append([1, "Aceh", None, None])
    worksheet.append([2, "Riau", 3, 380])
    worksheet.append(["Jumlah", None, 3, 380])
    worksheet.append(["Sumber : Kemnaker RI", None, None, None])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_extractor_is_flat_source_extractor():
    assert issubclass(Extractor, ExcelExtractor)
    assert Extractor.__module__.endswith("data_mogok_kerja.extractor")


def test_parse_skips_aggregate_and_footer():
    records = Extractor({})._parse_excel(_build_workbook())
    assert [r["provinsi"] for r in records] == ["Aceh", "Riau"]
    assert records[1] == {
        "provinsi": "Riau",
        "kasus": 3,
        "tenaga_kerja_yang_terlibat": 380,
        "tahun": 2026,
    }


def test_normalizer_produces_canonical_records():
    raw = Extractor({})._parse_excel(_build_workbook())
    normalized = list(Normalizer({}).normalize(iter(raw)))
    assert [r["provinsi"] for r in normalized] == ["Aceh", "Riau"]
    assert normalized[1]["tenaga_kerja_yang_terlibat"] == 380


def test_model_maps_aliased_columns():
    record = Record(
        **{
            "Provinsi": "Aceh",
            "Kasus": 2,
            "Tenaga Kerja yang Terlibat (orang)": 30,
            "Tahun": 2026,
        }
    )
    assert record.provinsi == "Aceh"
    assert record.kasus == 2
    assert record.tenaga_kerja_yang_terlibat == 30
    assert record.tahun == 2026
