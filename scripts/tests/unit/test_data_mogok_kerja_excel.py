"""Tests for the Data Mogok Kerja Excel parser (province rows, 2-row header)."""

import io

from openpyxl import Workbook

from ingestion.usecases.ketenagakerjaan.data_mogok_kerja.excel.extractor import Extractor
from ingestion.core.normalizers.generic_normalizer import GenericNormalizer
from ingestion.usecases.ketenagakerjaan.data_mogok_kerja.models import (
    DataMogokKerjaRecord,
    Record,
)


def _build_workbook() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "mogok"
    ws.append(["Jumlah Kasus Mogok Kerja dan Tenaga Kerja yang Terlibat Menurut Provinsi", None, None, None])
    ws.append(["Tahun 2026"])
    ws.append([None])
    ws.append(["No.", "Provinsi", "Januari s.d Maret", None])
    ws.append([None, None, "Kasus", "Tenaga Kerja yang Terlibat (orang)"])
    ws.append([1, "Aceh", None, None])
    ws.append([2, "Sumatera Barat", 1, 11])
    ws.append([3, "Riau", 3, 380])
    ws.append(["Jumlah", None, 28, 5090])
    ws.append(["Sumber : Kemnaker RI", None, None, None])
    metadata = wb.create_sheet("metadata")
    metadata.append(["Metadata Statistik Indikator"])
    metadata.append([None])
    metadata.append(["No.", "Nama Indikator"])
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def _extractor() -> Extractor:
    return Extractor(
        {"usecase": "ketenagakerjaan", "source": "data_mogok_kerja", "access": "excel", "url": "https://x"}
    )


def test_parse_rows_and_skip_totals():
    records = _extractor()._parse_excel(_build_workbook())
    assert len(records) == 3
    assert [record["Provinsi"] for record in records] == ["Aceh", "Sumatera Barat", "Riau"]
    assert all(record["Provinsi"] != "Jumlah" for record in records)


def test_parse_values_and_periode():
    records = _extractor()._parse_excel(_build_workbook())
    aceh, sumbar, riau = records
    assert aceh["Periode"] == "Januari s.d Maret 2026"
    assert aceh["Jumlah_Kasus"] == 0 and aceh["Jumlah_Pekerja"] == 0
    assert sumbar["Jumlah_Kasus"] == 1 and sumbar["Jumlah_Pekerja"] == 11
    assert riau["Jumlah_Kasus"] == 3 and riau["Jumlah_Pekerja"] == 380


def test_normalizer_maps_to_model():
    normalizer = GenericNormalizer({}, model=Record)
    normalized = list(normalizer.normalize(iter(_extractor()._parse_excel(_build_workbook()))))
    assert len(normalized) == 3
    assert normalized[1]["wilayah"] == "Sumatera Barat"
    assert normalized[1]["kasus"] == 1
    assert normalized[1]["tenaga_kerja_yang_terlibat"] == 11
    assert normalized[0]["tahun"] == "2026"


def test_model_maps_source_columns_and_derives_tahun():
    record = DataMogokKerjaRecord(
        **{
            "Provinsi": "Aceh",
            "Jumlah_Kasus": 2,
            "Jumlah_Pekerja": 30,
            "Periode": "Januari s.d Maret 2026",
        }
    )
    assert record.wilayah == "Aceh"
    assert record.kasus == 2
    assert record.tenaga_kerja_yang_terlibat == 30
    assert record.tahun == "2026"
    assert Record is DataMogokKerjaRecord


def test_model_accepts_canonical_names():
    record = DataMogokKerjaRecord(wilayah="Bali", kasus=0, tenaga_kerja_yang_terlibat=0, tahun="2026")
    assert record.wilayah == "Bali"
