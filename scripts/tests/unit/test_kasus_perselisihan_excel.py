"""Tests for the Kasus Perselisihan Excel parser (3-row header, month sheets)."""

import io

from openpyxl import Workbook

from ingestion.usecases.ketenagakerjaan.kasus_perselisihan.excel.extractor import (
    Extractor,
    _canonical_jenis,
)
from ingestion.usecases.ketenagakerjaan.kasus_perselisihan.normalizer import Normalizer


def _build_workbook() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Januari"
    ws.append(["Jumlah Kasus Perselisihan", None, None, None, None, None, None, None, None, None, None, None])
    ws.append(["Tahun 2026"])
    ws.append([None])
    ws.append(["Jenis Perselisihan", "Jumlah Perselisihan", None, None, "Penyelesaian Perselisihan", None, None, None, None, None, None, "Sisa Kasus"])
    ws.append([None, None, None, None, "Bipartit", "Mediasi", None, "Konsiliasi", "Arbitrasi", "Hakim HI", "Jumlah", None])
    ws.append([None, "Pusat", "Daerah", "Jumlah", None, "PB", "Anjuran", None, None, None, None, None])
    ws.append(["Perselisihan Hak", 3, 14, 17, 1, 4, 1, 0, 0, 0, 6, 11])
    ws.append(["Perselisihan Kepentingan", 5, 2, 7, 1, 0, 1, 0, 0, 0, 2, 5])
    ws.append(["Perselisihan PHK", 15, 31, 46, 12, 11, 6, 0, 0, 1, 30, 16])
    ws.append(["Perselisihan Serikat Pekerja", 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1])
    ws.append(["Total", 23, 48, 71, 14, 15, 8, 0, 0, 1, 38, 33])
    ws.append(["Sumber: Kemnaker RI"])
    metadata = wb.create_sheet("metadata")
    metadata.append(["Metadata Statistik"])
    metadata.append([None])
    metadata.append(["No.", "Nama Indikator"])
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _extractor() -> Extractor:
    return Extractor(
        {"usecase": "ketenagakerjaan", "source": "kasus_perselisihan", "access": "excel", "url": "https://x"}
    )


def test_parse_skips_totals_and_metadata():
    records = _extractor()._parse_excel(_build_workbook())
    assert len(records) == 4
    assert all(record["Jenis_Perselisihan"] != "Total" for record in records)


def test_parse_maps_columns_and_periode():
    records = _extractor()._parse_excel(_build_workbook())
    phk = records[2]
    assert phk["Jenis_Perselisihan"] == "PHK"
    assert phk["Periode"] == "2026-01"
    assert phk["Jumlah_Pusat"] == 15
    assert phk["Jumlah_Daerah"] == 31
    assert phk["Bipartit"] == 12
    assert phk["Mediasi_PB"] == 11
    assert phk["Mediasi_Anjuran"] == 6
    assert phk["Konsiliasi"] == 0
    assert phk["Arbitrasi"] == 0
    assert phk["Hakim_HI"] == 1
    assert phk["Sisa_Kasus"] == 16


def test_normalizer_produces_canonical_records():
    normalized = list(Normalizer({}).normalize(iter(_extractor()._parse_excel(_build_workbook()))))
    assert len(normalized) == 4
    assert normalized[0]["periode"] == "2026-01"
    assert normalized[2]["jenis_perselisihan"] == "PHK"


def test_canonical_jenis_variants():
    assert _canonical_jenis("Perselisihan Hak") == "Perselisihan Hak"
    assert _canonical_jenis("Perselisihan PHK") == "PHK"
    assert _canonical_jenis("Perselisihan Serikat Pekerja / Serikat Buruh") == "Serikat Pekerja"
