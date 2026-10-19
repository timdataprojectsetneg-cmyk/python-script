"""Unit tests for CSIS AMTI Insiden Maritim Indo-Pasifik Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.csis.amti_insiden_maritim.models import (
    Record,
    CsisAmtiInsidenMaritimRecord,
)
from ingestion.usecases.geopolitik.csis.amti_insiden_maritim.normalizer import (
    Normalizer,
    clean_str,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.csis.amti_insiden_maritim.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated maritime incident record passes Pydantic validation."""
    data = {
        "id_insiden": "INS-AMTI-2026-08",
        "tanggal_kejadian": "2026-10-02",
        "wilayah_perairan": "Laut China Selatan (Whitsun Reef)",
        "jenis_kejadian": "Manuver Kapal Milisi Maritim",
        "pihak_terlibat": "Tiongkok vs Filipina",
        "koordinat_lat": 9.9015,
        "koordinat_lon": 114.6542,
        "tingkat_eskalasi": "Tinggi",
        "catatan_analisis": "Peningkatan kehadiran 35 armada kapal penjaga pantai dan milisi maritim di zona ekonomi eksklusif Filipina.",
    }
    rec = Record(**data)
    assert rec.id_insiden == "INS-AMTI-2026-08"
    assert rec.tanggal_kejadian == "2026-10-02"
    assert rec.wilayah_perairan == "Laut China Selatan (Whitsun Reef)"
    assert rec.jenis_kejadian == "Manuver Kapal Milisi Maritim"
    assert rec.pihak_terlibat == "Tiongkok vs Filipina"
    assert rec.koordinat_lat == 9.9015
    assert rec.koordinat_lon == 114.6542
    assert rec.tingkat_eskalasi == "Tinggi"
    assert "CSIS Asia Maritime Transparency Initiative" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_insiden="INS-AMTI-TEST-01",
        wilayah_perairan="Laut Natuna Utara",
        jenis_kejadian="Patroli Maritim",
        pihak_terlibat="Bakamla RI",
    )
    assert rec.id_insiden == "INS-AMTI-TEST-01"
    assert rec.wilayah_perairan == "Laut Natuna Utara"
    assert rec.tingkat_eskalasi == "Sedang"
    assert rec.koordinat_lat == 0.0
    assert rec.koordinat_lon == 0.0
    assert rec.tanggal_kejadian is None
    assert rec.catatan_analisis is None


def test_parse_helpers():
    """Verify clean_str and parse_float_safe helper functions."""
    assert clean_str("  Laut Natuna Utara  ") == "Laut Natuna Utara"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_float_safe("9.9015") == 9.9015
    assert parse_float_safe("114.6542") == 114.6542
    assert parse_float_safe("1,234.56") == 1234.56
    assert parse_float_safe("..") == 0.0
    assert parse_float_safe(None) == 0.0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Insiden": "INS-AMTI-2026-10",
        "Tanggal": "2026-10-08",
        "Wilayah Perairan": "Laut Natuna Utara (Blok Tuna)",
        "Jenis Kejadian": "Bayang-bayang Kapal Penjaga Pantai Asing",
        "Pihak Terlibat": "China Coast Guard (CCG 5402) vs KN Tanjung Datu (Bakamla RI)",
        "Lat": "4.5218",
        "Lon": "109.1245",
        "Eskalasi": "Sedang",
        "Catatan Analisis": "Bakamla RI mengusir kapal CCG 5402 yang mengganggu aktivitas survei seismik migas nasional di ZEE Indonesia.",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_insiden"] == "INS-AMTI-2026-10"
    assert item["wilayah_perairan"] == "Laut Natuna Utara (Blok Tuna)"
    assert item["koordinat_lat"] == 4.5218
    assert item["koordinat_lon"] == 109.1245
    assert item["tingkat_eskalasi"] == "Sedang"
    assert "Bakamla RI" in item["catatan_analisis"]


def test_extractor_offline_fallback():
    """Verify extractor returns reference maritime incident records."""
    ext = Extractor({"url": "http://invalid-csis-domain.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_insiden"] == "INS-AMTI-2026-08"
    assert records[0]["wilayah_perairan"] == "Laut China Selatan (Whitsun Reef)"
    assert records[0]["tingkat_eskalasi"] == "Tinggi"
