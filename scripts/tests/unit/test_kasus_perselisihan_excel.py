"""Structural tests for the Kasus Perselisihan source (flat extractor)."""

from ingestion.core.extractors.excel_extractor import ExcelExtractor
from ingestion.usecases.ketenagakerjaan.kemnaker.kasus_perselisihan.extractor import (
    Extractor,
)
from ingestion.usecases.ketenagakerjaan.kemnaker.kasus_perselisihan.models import Record


def test_extractor_is_flat_source_extractor():
    assert issubclass(Extractor, ExcelExtractor)
    assert Extractor.__module__.endswith("kasus_perselisihan.extractor")


def test_model_maps_aliased_columns():
    record = Record(
        **{
            "Jenis_Perselisihan": "PHK",
            "Jumlah_Pusat": 15,
            "Jumlah_Daerah": 31,
            "Sisa_Kasus": 16,
        }
    )
    assert record.jenis_perselisihan == "PHK"
    assert record.jumlah_pusat == 15
    assert record.jumlah_daerah == 31
    assert record.sisa_kasus == 16
