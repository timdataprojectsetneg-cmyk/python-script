"""Unit tests for AirNav NOTAM & Kesiapan Evakuasi WNI Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.airnav.notam.models import (
    Record,
    AirNavNotamRecord,
)
from ingestion.usecases.geopolitik.airnav.notam.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.airnav.notam.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated NOTAM record passes Pydantic validation."""
    data = {
        "id_wilayah": "EVAC-2026-ME-01",
        "negara": "Lebanon",
        "kawasan": "Timur Tengah",
        "status_siaga_evakuasi": "Siaga I",
        "estimasi_wni_terdampak": 185,
        "jalur_evakuasi_utama": "Jalur darat menuju Damaskus / Beirut port via laut ke Siprus",
        "titik_kumpul_safe_haven": "KBRI Beirut & Wisma Duta",
        "status_ruang_udara_notam": "Restricted (NOTAM B0122/26)",
        "kesiapan_bandara_pelabuhan": "Bandara Rafic Hariri Beroperasi Terbatas",
        "koordinasi_satgas_tni_kemlu": "Koordinasi Satgas Unifil TNI dan KBRI Beirut",
    }
    rec = Record(**data)
    assert rec.id_wilayah == "EVAC-2026-ME-01"
    assert rec.negara == "Lebanon"
    assert rec.kawasan == "Timur Tengah"
    assert rec.estimasi_wni_terdampak == 185
    assert rec.status_siaga_evakuasi == "Siaga I"
    assert "Restricted" in rec.status_ruang_udara_notam
    assert "AirNav Indonesia" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        id_wilayah="EVAC-TEST-01",
        negara="Iran",
        kawasan="Timur Tengah",
    )
    assert rec.id_wilayah == "EVAC-TEST-01"
    assert rec.negara == "Iran"
    assert rec.status_siaga_evakuasi == "Siaga I"
    assert rec.estimasi_wni_terdampak == 0
    assert rec.status_ruang_udara_notam == "Restricted"
    assert rec.jalur_evakuasi_utama is None


def test_parse_helpers():
    """Verify clean_str and parse_int_safe helper functions."""
    assert clean_str("  Lebanon  ") == "Lebanon"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("185") == 185
    assert parse_int_safe("1,250") == 1250
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Wilayah": "EVAC-2026-AF-02",
        "Negara": "Sudan",
        "Kawasan": "Afrika Utara",
        "Status Siaga": "Siaga II",
        "WNI Terdampak": "95",
        "Jalur Evakuasi": "Jalur evakuasi darat ke Port Sudan dilanjutkan KRI ke Jeddah",
        "Titik Kumpul Safe Haven": "Safe Haven Wisma KBRI Port Sudan",
        "Status Udara (NOTAM)": "Closed (NOTAM A0441/26)",
        "Kesiapan Bandara": "Bandara Khartum Ditutup; Port Sudan Operasional",
        "Koordinasi Satgas TNI/Kemlu": "Satgas Evakuasi Gabungan TNI & Kemlu",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_wilayah"] == "EVAC-2026-AF-02"
    assert item["negara"] == "Sudan"
    assert item["estimasi_wni_terdampak"] == 95
    assert item["status_siaga_evakuasi"] == "Siaga II"
    assert "Closed" in item["status_ruang_udara_notam"]


def test_extractor_offline_fallback():
    """Verify extractor returns reference contingency records."""
    ext = Extractor({"url": "http://invalid-airnav.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_wilayah"] == "EVAC-2026-ME-01"
    assert records[0]["negara"] == "Lebanon"
    assert records[0]["estimasi_wni_terdampak"] == 185
