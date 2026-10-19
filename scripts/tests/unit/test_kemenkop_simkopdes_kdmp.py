"""Unit tests for Kemenkop SIMKOPDES KDMP Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.kemenkop.simkopdes_kdmp.models import (
    Record,
    KemenkopSimkopdesKdmpRecord,
)
from ingestion.usecases.kunjungan_presiden.kemenkop.simkopdes_kdmp.normalizer import (
    Normalizer,
    clean_text,
    parse_int_safe,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.kemenkop.simkopdes_kdmp.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated SIMKOPDES record passes Pydantic validation."""
    data = {
        "provinsi": "JAWA TIMUR",
        "provinsi_id": 15,
        "kabupaten_kota": "Kabupaten Banyuwangi",
        "total_koperasi": 8363,
        "koperasi_sehat": 698,
        "koperasi_cukup_sehat": 2095,
        "koperasi_tidak_sehat": 5570,
        "total_anggota": 1832243,
        "omzet_pendapatan": 68222662677.0,
        "latitude": -8.2192,
        "longitude": 114.3692,
    }
    rec = Record(**data)
    assert rec.provinsi == "JAWA TIMUR"
    assert rec.provinsi_id == 15
    assert rec.kabupaten_kota == "Kabupaten Banyuwangi"
    assert rec.total_koperasi == 8363
    assert rec.koperasi_sehat == 698
    assert rec.omzet_pendapatan == 68222662677.0
    assert "Kementerian Koperasi" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        provinsi="JAWA TENGAH",
        kabupaten_kota="Kabupaten Banyumas",
    )
    assert rec.provinsi == "JAWA TENGAH"
    assert rec.kabupaten_kota == "Kabupaten Banyumas"
    assert rec.total_koperasi == 0
    assert rec.koperasi_sehat == 0
    assert rec.omzet_pendapatan == 0.0
    assert rec.latitude is None


def test_parse_helpers():
    """Verify numeric and string helper functions."""
    assert parse_int_safe("1,500") == 1500
    assert parse_int_safe("8363") == 8363
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0

    assert parse_float_safe("68222662677.0") == 68222662677.0
    assert parse_float_safe("-8.2192") == -8.2192
    assert parse_float_safe("-") is None
    assert parse_float_safe(None) is None

    assert clean_text("  Kabupaten Banyuwangi  ") == "Kabupaten Banyuwangi"
    assert clean_text("-") is None
    assert clean_text("NA") is None
    assert clean_text(None) is None


def test_normalizer_flow():
    """Verify normalizer maps raw dictionary into validated payload."""
    raw = {
        "Provinsi": "JAWA TENGAH",
        "ID Prov": 13,
        "Kabupaten/Kota": "Kabupaten Banyumas",
        "Total Koperasi": "7210",
        "Sehat": "520",
        "Cukup Sehat": "1850",
        "Tidak Sehat": "4840",
        "Anggota": "1420100",
        "Omzet (Rp)": "22132406819.0",
        "Lat": "-7.5167",
        "Lon": "109.2994",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["provinsi"] == "JAWA TENGAH"
    assert item["provinsi_id"] == 13
    assert item["kabupaten_kota"] == "Kabupaten Banyumas"
    assert item["total_koperasi"] == 7210
    assert item["koperasi_sehat"] == 520
    assert item["total_anggota"] == 1420100
    assert item["omzet_pendapatan"] == 22132406819.0
    assert item["latitude"] == -7.5167


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when URL is unreachable."""
    ext = Extractor({
        "url": "http://invalid-simkopdes.local",
        "api_provinces_url": "http://invalid-api-simkopdes.local",
        "max_records": 3,
        "timeout": 1,
    })
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["provinsi"] == "JAWA TIMUR"
    assert records[0]["kabupaten_kota"] == "Kabupaten Banyuwangi"
    assert records[0]["total_koperasi"] == 8363
