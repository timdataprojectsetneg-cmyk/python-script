"""Tests for the Kasus Perselisihan source (flat extractor, monthly sheets)."""

from io import BytesIO

from openpyxl import Workbook

from ingestion.core.extractors.excel_extractor import ExcelExtractor
from ingestion.usecases.ketenagakerjaan.kemnaker.kasus_perselisihan.extractor import (
    Extractor,
    _canonical_jenis,
)
from ingestion.usecases.ketenagakerjaan.kemnaker.kasus_perselisihan.models import Record
from ingestion.usecases.ketenagakerjaan.kemnaker.kasus_perselisihan.normalizer import (
    Normalizer,
)


def _build_workbook() -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Januari"
    worksheet.append(["Jumlah Kasus Perselisihan Hubungan Industrial dan Jenis Penyelesaiannya", None, None, None, None, None, None, None, None, None, None, None])
    worksheet.append(["Tahun 2026", None, None, None, None, None, None, None, None, None, None, None])
    worksheet.append([None, None, None, None, None, None, None, None, None, None, None, None])
    worksheet.append(["Jenis Perselisihan", "Jumlah Perselisihan", None, None, "Penyelesaian Perselisihan", None, None, None, None, None, None, "Sisa Kasus"])
    worksheet.append([None, None, None, None, "Bipartit", "Mediasi", None, "Konsiliasi", "Arbitrasi", "Hakim HI", "Jumlah", None])
    worksheet.append([None, "Pusat", "Daerah", "Jumlah", None, "PB", "Anjuran", None, None, None, None, None])
    worksheet.append(["Perselisihan Hak", 3, 14, 17, 1, 4, 1, 0, 0, 0, 6, 11])
    worksheet.append(["Perselisihan PHK", 15, 31, 46, 12, 11, 6, 0, 0, 1, 30, 16])
    worksheet.append(["Total", 18, 45, 63, 13, 15, 7, 0, 0, 1, 36, 27])
    worksheet.append(["Sumber: Kemnaker RI", None, None, None, None, None, None, None, None, None, None, None])
    workbook.create_sheet("metadata").append(["Metadata Statistik"])
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_extractor_is_flat_source_extractor():
    assert issubclass(Extractor, ExcelExtractor)
    assert Extractor.__module__.endswith("kasus_perselisihan.extractor")


def test_parse_skips_totals_and_metadata():
    records = Extractor({})._parse_excel(_build_workbook())
    assert len(records) == 2
    assert all(r["jenis_perselisihan"] != "Total" for r in records)


def test_parse_maps_columns_and_periode():
    phk = Extractor({})._parse_excel(_build_workbook())[1]
    assert phk["jenis_perselisihan"] == "PHK"
    assert phk["periode"] == "2026-01"
    assert phk["tahun"] == 2026
    assert phk["jumlah_pusat"] == 15
    assert phk["jumlah_daerah"] == 31
    assert phk["jumlah"] == 46
    assert phk["bipartit"] == 12
    assert phk["mediasi_pb"] == 11
    assert phk["mediasi_anjuran"] == 6
    assert phk["konsiliasi"] == 0
    assert phk["hakim_hi"] == 1
    assert phk["jumlah_penyelesaian"] == 30
    assert phk["sisa_kasus"] == 16


def test_normalizer_produces_canonical_records():
    raw = Extractor({})._parse_excel(_build_workbook())
    normalized = list(Normalizer({}).normalize(iter(raw)))
    assert len(normalized) == 2
    assert normalized[0]["periode"] == "2026-01"
    assert normalized[1]["jenis_perselisihan"] == "PHK"


def test_canonical_jenis_variants():
    assert _canonical_jenis("Perselisihan Hak") == "Perselisihan Hak"
    assert _canonical_jenis("Perselisihan PHK") == "PHK"
    assert _canonical_jenis("Perselisihan Serikat Pekerja / Serikat Buruh") == "Serikat Pekerja"


def test_model_maps_aliased_columns():
    record = Record(**{"Jenis_Perselisihan": "PHK", "Jumlah_Pusat": 15, "Sisa_Kasus": 16})
    assert record.jenis_perselisihan == "PHK"
    assert record.jumlah_pusat == 15
    assert record.sisa_kasus == 16
