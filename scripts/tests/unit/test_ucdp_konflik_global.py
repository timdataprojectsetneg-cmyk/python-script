"""Unit tests for UCDP Konflik Global Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.ucdp.konflik_global.models import (
    Record,
    UcdpKonflikGlobalRecord,
)
from ingestion.usecases.geopolitik.ucdp.konflik_global.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    parse_float_safe,
    normalize_single,
    TYPE_OF_VIOLENCE_MAP,
)
from ingestion.usecases.geopolitik.ucdp.konflik_global.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated UCDP record passes Pydantic validation."""
    data = {
        "id_konflik": "UCDP-2026-091",
        "negara": "Ukraina",
        "kawasan": "Eropa Timur",
        "aktor_terlibat": "Militer Rusia vs Angkatan Bersenjata Ukraina",
        "jenis_konflik": "State-based conflict (Pertempuran Terorganisir)",
        "tanggal_kejadian": "2026-10-06",
        "jumlah_korban_tewas": 42,
        "koordinat_lat": 48.4647,
        "koordinat_lon": 35.0462,
    }
    rec = Record(**data)
    assert rec.id_konflik == "UCDP-2026-091"
    assert rec.negara == "Ukraina"
    assert rec.kawasan == "Eropa Timur"
    assert rec.jumlah_korban_tewas == 42
    assert rec.koordinat_lat == 48.4647
    assert rec.koordinat_lon == 35.0462
    assert "Uppsala Conflict Data Program" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        id_konflik="UCDP-TEST-001",
        negara="Sudan",
        kawasan="Afrika Utara",
        aktor_terlibat="SAF vs RSF",
    )
    assert rec.id_konflik == "UCDP-TEST-001"
    assert rec.negara == "Sudan"
    assert rec.jumlah_korban_tewas == 0
    assert rec.jenis_konflik == "State-based conflict"
    assert rec.tanggal_kejadian is None
    assert rec.koordinat_lat is None


def test_parse_helpers():
    """Verify string, int, and float helper parsers."""
    assert parse_int_safe("42") == 42
    assert parse_int_safe("1,250") == 1250
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0

    assert parse_float_safe("48.4647") == 48.4647
    assert parse_float_safe("-") is None
    assert parse_float_safe(None) is None

    assert clean_str("  Ukraina  ") == "Ukraina"
    assert clean_str("-") is None
    assert clean_str("NaN") is None
    assert clean_str(None) is None

    assert 1 in TYPE_OF_VIOLENCE_MAP
    assert 2 in TYPE_OF_VIOLENCE_MAP
    assert 3 in TYPE_OF_VIOLENCE_MAP


def test_normalizer_flow():
    """Verify normalizer maps raw dictionary into validated payload."""
    raw = {
        "ID Konflik": "UCDP-2026-092",
        "Negara": "Sudan",
        "Kawasan": "Afrika Utara",
        "Aktor Bertikai": "SAF vs RSF",
        "Jenis Konflik": "Non-state conflict",
        "Tanggal": "2026-10-07",
        "Korban Jiwa": "18",
        "Lat": "15.5007",
        "Lon": "32.5599",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_konflik"] == "UCDP-2026-092"
    assert item["negara"] == "Sudan"
    assert item["kawasan"] == "Afrika Utara"
    assert item["aktor_terlibat"] == "SAF vs RSF"
    assert item["jumlah_korban_tewas"] == 18
    assert item["koordinat_lat"] == 15.5007


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when URL is unreachable."""
    ext = Extractor({
        "url": "http://invalid-ucdp-stream.local",
        "backup_url": "http://invalid-backup.local",
        "max_records": 3,
        "timeout": 1,
    })
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_konflik"] == "UCDP-2026-091"
    assert records[0]["negara"] == "Ukraina"
    assert records[0]["jumlah_korban_tewas"] == 42
