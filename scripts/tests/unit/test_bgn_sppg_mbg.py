"""Unit tests for BGN SPPG MBG Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.bgn.sppg_mbg.models import (
    Record,
    BgnSppgMbgRecord,
)
from ingestion.usecases.kunjungan_presiden.bgn.sppg_mbg.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.bgn.sppg_mbg.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated BGN SPPG record passes Pydantic validation."""
    data = {
        "id_sppg": "SPPG-3302-001",
        "nama_sppg": "SPPG Purwokerto Utara",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Banyumas",
        "kecamatan": "Purwokerto Utara",
        "kapasitas_porsi_harian": 3000,
        "jumlah_penerima_manfaat": 2850,
        "status_operasional": "Aktif",
        "latitude": -7.4121,
        "longitude": 109.2435,
    }
    rec = Record(**data)
    assert rec.id_sppg == "SPPG-3302-001"
    assert rec.nama_sppg == "SPPG Purwokerto Utara"
    assert rec.provinsi == "Jawa Tengah"
    assert rec.kapasitas_porsi_harian == 3000
    assert rec.latitude == -7.4121
    assert "Badan Gizi Nasional" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_sppg="SPPG-GEN-001",
        nama_sppg="SPPG Soreang",
        provinsi="Jawa Barat",
        kabupaten_kota="Bandung",
        kecamatan="Soreang",
    )
    assert rec.id_sppg == "SPPG-GEN-001"
    assert rec.kapasitas_porsi_harian == 0
    assert rec.status_operasional == "Aktif"
    assert rec.latitude is None


def test_helpers():
    """Verify parsing helper functions."""
    assert clean_str("  SPPG Soreang  ") == "SPPG Soreang"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("3,500") == 3500
    assert parse_int_safe(2850) == 2850
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0

    assert parse_float_safe("-7.4121") == -7.4121
    assert parse_float_safe(109.2435) == 109.2435
    assert parse_float_safe("-") is None
    assert parse_float_safe(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID SPPG": "SPPG-3302-001",
        "Nama SPPG": "SPPG Purwokerto Utara",
        "Provinsi": "Jawa Tengah",
        "Kabupaten/Kota": "Banyumas",
        "Kecamatan": "Purwokerto Utara",
        "Kapasitas (Porsi)": 3000,
        "Penerima": 2850,
        "Status": "Aktif",
        "Lat": -7.4121,
        "Lon": 109.2435,
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_sppg"] == "SPPG-3302-001"
    assert item["nama_sppg"] == "SPPG Purwokerto Utara"
    assert item["provinsi"] == "Jawa Tengah"
    assert item["kapasitas_porsi_harian"] == 3000
    assert item["latitude"] == -7.4121
    assert item["longitude"] == 109.2435


def test_extractor_offline_fallback():
    """Verify extractor returns reference SPPG kitchen records."""
    ext = Extractor({"url": "http://invalid-bgn-api.local", "max_records": 4, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 4
    assert records[0]["id_sppg"] == "SPPG-3302-001"
    assert records[0]["nama_sppg"] == "SPPG Purwokerto Utara"
    assert records[1]["id_sppg"] == "SPPG-3204-002"
