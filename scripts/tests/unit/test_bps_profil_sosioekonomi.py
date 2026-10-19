"""Unit tests for BPS Profil Sosioekonomi Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.bps.profil_sosioekonomi.models import (
    Record,
    BpsProfilSosioekonomiRecord,
)
from ingestion.usecases.kunjungan_presiden.bps.profil_sosioekonomi.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.bps.profil_sosioekonomi.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated BPS record passes Pydantic validation."""
    data = {
        "kode_wilayah_kemendagri": "33.02",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Banyumas",
        "jumlah_penduduk_jiwa": 1828500,
        "kepadatan_penduduk_km2": 1378.5,
        "persentase_penduduk_miskin": 12.45,
        "tingkat_pengangguran_terbuka_tpt": 5.12,
        "indeks_pembangunan_manusia_ipm": 73.85,
        "pertumbuhan_ekonomi_pdrb_pct": 5.24,
        "pdrb_harga_berlaku_juta_rp": 62450800.0,
    }
    rec = Record(**data)
    assert rec.kode_wilayah_kemendagri == "33.02"
    assert rec.provinsi == "Jawa Tengah"
    assert rec.kabupaten_kota == "Kabupaten Banyumas"
    assert rec.jumlah_penduduk_jiwa == 1828500
    assert rec.kepadatan_penduduk_km2 == 1378.5
    assert rec.persentase_penduduk_miskin == 12.45
    assert rec.indeks_pembangunan_manusia_ipm == 73.85
    assert "Badan Pusat Statistik" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        kode_wilayah_kemendagri="32.04",
        provinsi="Jawa Barat",
        kabupaten_kota="Kabupaten Bandung",
    )
    assert rec.kode_wilayah_kemendagri == "32.04"
    assert rec.provinsi == "Jawa Barat"
    assert rec.kabupaten_kota == "Kabupaten Bandung"
    assert rec.jumlah_penduduk_jiwa == 0
    assert rec.kepadatan_penduduk_km2 == 0.0
    assert rec.indeks_pembangunan_manusia_ipm == 0.0


def test_helpers():
    """Verify parsing helper functions."""
    assert clean_str("  Kabupaten Banyumas  ") == "Kabupaten Banyumas"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("1,828,500") == 1828500
    assert parse_int_safe(1828500) == 1828500
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0

    assert parse_float_safe("12.45%") == 12.45
    assert parse_float_safe(73.85) == 73.85
    assert parse_float_safe("-") == 0.0
    assert parse_float_safe(None) == 0.0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Kode Wilayah": "33.02",
        "Provinsi": "Jawa Tengah",
        "Kabupaten/Kota": "Kabupaten Banyumas",
        "Penduduk (Jiwa)": 1828500,
        "Kepadatan (/km2)": 1378.5,
        "Kemiskinan (%)": 12.45,
        "TPT (%)": 5.12,
        "IPM": 73.85,
        "PDRB (%)": 5.24,
        "PDRB Berlaku (Juta Rp)": 62450800,
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["kode_wilayah_kemendagri"] == "33.02"
    assert item["provinsi"] == "Jawa Tengah"
    assert item["kabupaten_kota"] == "Kabupaten Banyumas"
    assert item["jumlah_penduduk_jiwa"] == 1828500
    assert item["indeks_pembangunan_manusia_ipm"] == 73.85


def test_extractor_offline_fallback():
    """Verify extractor returns reference socio-economic records."""
    ext = Extractor({"url": "http://invalid-bps-api.local", "max_records": 4, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 4
    assert records[0]["kode_wilayah_kemendagri"] == "33.02"
    assert records[0]["kabupaten_kota"] == "Kabupaten Banyumas"
    assert records[1]["kabupaten_kota"] == "Kabupaten Bandung"
