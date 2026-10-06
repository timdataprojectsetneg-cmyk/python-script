"""Structural tests for the Data Mogok Kerja source (flat extractor)."""

from ingestion.core.extractors.excel_extractor import ExcelExtractor
from ingestion.usecases.ketenagakerjaan.kemnaker.data_mogok_kerja.extractor import Extractor
from ingestion.usecases.ketenagakerjaan.kemnaker.data_mogok_kerja.models import Record


def test_extractor_is_flat_source_extractor():
    assert issubclass(Extractor, ExcelExtractor)
    assert Extractor.__module__.endswith("data_mogok_kerja.extractor")


def test_model_maps_aliased_columns():
    record = Record(
        **{
            "Wilayah": "Aceh",
            "Kasus": 2,
            "Tenaga Kerja yang Terlibat": 30,
            "Tahun": 2026,
        }
    )
    assert record.wilayah == "Aceh"
    assert record.kasus == 2
    assert record.tenaga_kerja_yang_terlibat == 30
    assert record.tahun == 2026
