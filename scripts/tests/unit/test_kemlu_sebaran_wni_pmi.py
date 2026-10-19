"""Unit tests for Kemlu Sebaran WNI & PMI Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.kemlu.sebaran_wni_pmi.models import (
    Record,
    KemluSebaranWniPmiRecord,
)
from ingestion.usecases.geopolitik.kemlu.sebaran_wni_pmi.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.kemlu.sebaran_wni_pmi.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated WNI/PMI record passes Pydantic validation."""
    data = {
        "negara": "Malaysia",
        "kawasan": "Asia Tenggara",
        "jumlah_wni_lapor_diri": 1250000,
        "pekerja_migran_pmi": 950000,
        "pelajar_mahasiswa": 15000,
        "staf_profesional_ekspat": 45000,
        "perwakilan_ri_pengampu": "KBRI Kuala Lumpur, KJRI Penang, KJRI Johor Bahru",
    }
    rec = Record(**data)
    assert rec.negara == "Malaysia"
    assert rec.kawasan == "Asia Tenggara"
    assert rec.jumlah_wni_lapor_diri == 1250000
    assert rec.pekerja_migran_pmi == 950000
    assert rec.pelajar_mahasiswa == 15000
    assert rec.staf_profesional_ekspat == 45000
    assert "KBRI Kuala Lumpur" in rec.perwakilan_ri_pengampu
    assert "Kementerian Luar Negeri" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        negara="Jepang",
        kawasan="Asia Timur",
        perwakilan_ri_pengampu="KBRI Tokyo",
    )
    assert rec.negara == "Jepang"
    assert rec.kawasan == "Asia Timur"
    assert rec.jumlah_wni_lapor_diri == 0
    assert rec.pekerja_migran_pmi == 0
    assert rec.perwakilan_ri_pengampu == "KBRI Tokyo"


def test_parse_helpers():
    """Verify clean_str and parse_int_safe helper functions."""
    assert clean_str("  Malaysia  ") == "Malaysia"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("1,250,000") == 1250000
    assert parse_int_safe("850.000") == 850000
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Negara": "Arab Saudi",
        "Kawasan": "Timur Tengah",
        "Total WNI Lapor Diri": "850,000",
        "PMI": "720,000",
        "Pelajar/Mahasiswa": "8,500",
        "Profesional": "25,000",
        "Perwakilan Pengampu": "KBRI Riyadh, KJRI Jeddah",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["negara"] == "Arab Saudi"
    assert item["kawasan"] == "Timur Tengah"
    assert item["jumlah_wni_lapor_diri"] == 850000
    assert item["pekerja_migran_pmi"] == 720000
    assert "KJRI Jeddah" in item["perwakilan_ri_pengampu"]


def test_extractor_offline_fallback():
    """Verify extractor returns reference records when URL is unreachable."""
    ext = Extractor({"url": "http://invalid-satudata.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["negara"] == "Malaysia"
    assert records[0]["kawasan"] == "Asia Tenggara"
    assert records[0]["jumlah_wni_lapor_diri"] == 1250000
