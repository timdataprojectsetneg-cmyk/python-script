"""Unit tests for WIPO Global Innovation Index Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.wipo.global_innovation_index.models import (
    Record,
    WipoGlobalInnovationIndexRecord,
)
from ingestion.usecases.geopolitik.wipo.global_innovation_index.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.wipo.global_innovation_index.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated GII record passes Pydantic validation."""
    data = {
        "tahun": 2026,
        "skor_gii_indonesia": 32.1,
        "peringkat_gii_indonesia": 51,
        "peringkat_asean": 4,
        "pilar_institusi": 54.1,
        "pilar_human_capital": 33.0,
        "pilar_infrastruktur": 46.2,
        "pilar_market_sophistication": 58.5,
        "pilar_business_sophistication": 34.2,
        "pilar_knowledge_technology": 25.1,
        "pilar_creative_outputs": 31.8,
    }
    rec = Record(**data)
    assert rec.tahun == 2026
    assert rec.skor_gii_indonesia == 32.1
    assert rec.peringkat_gii_indonesia == 51
    assert rec.peringkat_asean == 4
    assert rec.pilar_institusi == 54.1
    assert rec.pilar_market_sophistication == 58.5
    assert "World Intellectual Property Organization" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        tahun=2025,
        skor_gii_indonesia=30.8,
    )
    assert rec.tahun == 2025
    assert rec.skor_gii_indonesia == 30.8
    assert rec.peringkat_gii_indonesia == 0
    assert rec.pilar_institusi == 0.0


def test_parse_helpers():
    """Verify clean_str, parse_int_safe, and parse_float_safe helper functions."""
    assert clean_str("  WIPO  ") == "WIPO"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("51") == 51
    assert parse_int_safe("1,250") == 1250
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0

    assert parse_float_safe("32.1") == 32.1
    assert parse_float_safe("1,234.56") == 1234.56
    assert parse_float_safe("..") == 0.0
    assert parse_float_safe(None) == 0.0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Tahun": "2025",
        "Skor GII RI": "30.8",
        "Peringkat Dunia": "54",
        "Peringkat ASEAN": "5",
        "Pilar Institusi": "52.4",
        "Pilar SDM/Riset": "31.2",
        "Pilar Infrastruktur": "44.6",
        "Market Sophistication": "56.8",
        "Business Sophistication": "32.5",
        "Knowledge & Tech": "23.4",
        "Creative Outputs": "30.1",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["tahun"] == 2025
    assert item["skor_gii_indonesia"] == 30.8
    assert item["peringkat_gii_indonesia"] == 54
    assert item["peringkat_asean"] == 5
    assert item["pilar_institusi"] == 52.4
    assert item["pilar_human_capital"] == 31.2


def test_extractor_offline_fallback():
    """Verify extractor returns reference GII records."""
    ext = Extractor({"url": "http://invalid-wipo.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["tahun"] == 2026
    assert records[0]["skor_gii_indonesia"] == 32.1
    assert records[0]["peringkat_gii_indonesia"] == 51
