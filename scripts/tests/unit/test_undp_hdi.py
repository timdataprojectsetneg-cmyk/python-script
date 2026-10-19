"""Unit tests for UNDP Human Development Index (HDI) Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.undp.hdi.models import Record, UndpHdiRecord
from ingestion.usecases.geopolitik.undp.hdi.normalizer import (
    Normalizer,
    classify_hdi_tier,
    parse_float_safe,
    parse_int_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.undp.hdi.extractor import Extractor, OFFLINE_FALLBACK_DATA


def test_models_validation_valid():
    """Verify that a properly populated UNDP HDI record passes Pydantic validation."""
    data = {
        "tahun": 2023,
        "negara": "Indonesia",
        "iso3": "IDN",
        "skor_hdi": 0.7280,
        "peringkat_hdi_dunia": 113,
        "angka_harapan_hidup_tahun": 71.15,
        "harapan_lama_sekolah_tahun": 13.34,
        "rata_rata_lama_sekolah_tahun": 8.70,
        "gni_per_kapita_ppp_usd": 13700.13,
        "kategori_hdi": "High Human Development",
        "data_source": "United Nations Development Programme (UNDP) HDR Time Series",
    }
    rec = Record(**data)
    assert rec.tahun == 2023
    assert rec.negara == "Indonesia"
    assert rec.iso3 == "IDN"
    assert rec.skor_hdi == 0.7280
    assert rec.peringkat_hdi_dunia == 113
    assert rec.kategori_hdi == "High Human Development"


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        tahun=2023,
        negara="Malaysia",
        skor_hdi=0.8070
    )
    assert rec.tahun == 2023
    assert rec.negara == "Malaysia"
    assert rec.skor_hdi == 0.8070
    assert rec.kategori_hdi == "High Human Development"
    assert rec.data_source.startswith("United Nations")


def test_classify_hdi_tier():
    """Verify UNDP standard classifications."""
    assert classify_hdi_tier(0.949) == "Very High Human Development"
    assert classify_hdi_tier(0.800) == "Very High Human Development"
    assert classify_hdi_tier(0.728) == "High Human Development"
    assert classify_hdi_tier(0.700) == "High Human Development"
    assert classify_hdi_tier(0.650) == "Medium Human Development"
    assert classify_hdi_tier(0.550) == "Medium Human Development"
    assert classify_hdi_tier(0.490) == "Low Human Development"


def test_parse_safe_helpers():
    """Verify numeric parser helpers."""
    assert parse_float_safe("71.146") == 71.146
    assert parse_float_safe("13,700.13") == 13700.13
    assert parse_float_safe("..") is None
    assert parse_float_safe(None) is None

    assert parse_int_safe("113") == 113
    assert parse_int_safe("..") is None
    assert parse_int_safe(None) is None


def test_normalizer_flow():
    """Verify normalizer yields valid dict records."""
    raw_item = {
        "year": "2023",
        "country": "Singapore",
        "iso3": "SGP",
        "hdi": "0.949",
        "hdi_rank": "9",
        "le": "84.14",
        "eys": "16.92",
        "mys": "11.92",
        "gnipc": "88,761.40",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw_item])))
    assert len(results) == 1
    item = results[0]
    assert item["tahun"] == 2023
    assert item["negara"] == "Singapore"
    assert item["skor_hdi"] == 0.949
    assert item["peringkat_hdi_dunia"] == 9
    assert item["kategori_hdi"] == "Very High Human Development"


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when remote URL is unreachable."""
    ext = Extractor({"url": "http://invalid-undp-url.test", "max_records": 2})
    records = list(ext.extract())
    assert len(records) == 2
    assert records[0]["negara"] == "Indonesia"
    assert records[0]["skor_hdi"] == 0.7280
