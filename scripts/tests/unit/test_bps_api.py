"""Structural tests for the BPS API sources (flat extractors)."""

from ingestion.core.extractors.api_extractor import ApiExtractor
from ingestion.usecases.ketenagakerjaan.bps.bps_consumer_price_index.extractor import (
    Extractor as CpiExtractor,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_consumer_price_index.models import (
    Record as CpiRecord,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_inflasi_mom.extractor import (
    Extractor as MomExtractor,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_inflasi_mom.models import Record as MomRecord


def test_extractors_are_flat_api_extractors():
    assert issubclass(CpiExtractor, ApiExtractor)
    assert issubclass(MomExtractor, ApiExtractor)
    assert CpiExtractor.__module__.endswith("bps_consumer_price_index.extractor")
    assert MomExtractor.__module__.endswith("bps_inflasi_mom.extractor")


def test_cpi_model_maps_months():
    record = CpiRecord(**{"Provinsi": "ACEH", "Januari": 105.5, "Tahun": "2026"})
    assert record.provinsi == "ACEH"
    assert record.januari == 105.5
    assert record.tahun == "2026"


def test_mom_model_maps_tahunan():
    record = MomRecord(**{"Kota_Inflasi": "KOTA MEDAN", "Januari": 0.4, "Tahun": 3.2})
    assert record.kota_inflasi == "KOTA MEDAN"
    assert record.januari == 0.4
    assert record.tahun == 3.2
