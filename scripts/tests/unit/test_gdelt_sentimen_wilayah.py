"""Unit tests for GDELT Sentimen Wilayah Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.gdelt.sentimen_wilayah.models import (
    Record,
    GdeltSentimenWilayahRecord,
)
from ingestion.usecases.kunjungan_presiden.gdelt.sentimen_wilayah.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.gdelt.sentimen_wilayah.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
    _detect_program,
    _detect_provinsi,
)


def test_models_validation_valid():
    """Verify that a properly populated sentiment record passes Pydantic validation."""
    data = {
        "tanggal_pemantauan": "2026-10-13",
        "nama_program_prioritas": "Makan Bergizi Gratis (MBG)",
        "provinsi_wilayah": "Jawa Tengah",
        "volume_percakapan_media": 1420,
        "sentimen_positif_pct": 78.4,
        "sentimen_netral_pct": 15.2,
        "sentimen_negatif_pct": 6.4,
        "isu_dominan_diperbincangkan": "Kualitas menu makanan bergizi dan pelibatan pedagang pasar tradisional",
        "kanal_utama_sumber": "Media Daring & X/Twitter",
    }
    rec = Record(**data)
    assert rec.tanggal_pemantauan == "2026-10-13"
    assert rec.nama_program_prioritas == "Makan Bergizi Gratis (MBG)"
    assert rec.provinsi_wilayah == "Jawa Tengah"
    assert rec.volume_percakapan_media == 1420
    assert rec.sentimen_positif_pct == 78.4
    assert "GDELT Project" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        nama_program_prioritas="Koperasi Desa Merah Putih",
        provinsi_wilayah="Jawa Barat",
    )
    assert rec.nama_program_prioritas == "Koperasi Desa Merah Putih"
    assert rec.provinsi_wilayah == "Jawa Barat"
    assert rec.volume_percakapan_media == 0
    assert rec.sentimen_positif_pct == 0.0
    assert rec.tanggal_pemantauan is None


def test_helpers():
    """Verify parsing and detection helper functions."""
    assert clean_str("  Jawa Tengah  ") == "Jawa Tengah"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("1,420") == 1420
    assert parse_int_safe(850) == 850
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0

    assert parse_float_safe("78.4%") == 78.4
    assert parse_float_safe(15.2) == 15.2
    assert parse_float_safe("-") == 0.0
    assert parse_float_safe(None) == 0.0

    assert _detect_program("Pemberian menu makan bergizi gratis di sekolah") == "Makan Bergizi Gratis (MBG)"
    assert _detect_program("Pembentukan koperasi desa merah putih") == "Koperasi Desa Merah Putih"
    assert _detect_program("Pencegahan stunting pada balita") == "Penurunan Stunting"
    assert _detect_program("Layanan skrining kesehatan gratis puskesmas") == "Cek Kesehatan Gratis (CKG)"

    assert _detect_provinsi("Kunjungan ke Semarang, Jawa Tengah") == "Jawa Tengah"
    assert _detect_provinsi("Penyaluran beras di Jatim") == "Jawa Timur"
    assert _detect_provinsi("Bantuan di Kupang, NTT") == "Nusa Tenggara Timur"
    assert _detect_provinsi("Rapat kabinet di Istana Negara") == "Nasional / Multi-Wilayah"


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Tanggal": "2026-10-13",
        "Program": "Makan Bergizi Gratis (MBG)",
        "Provinsi": "Jawa Tengah",
        "Volume Percakapan": 1420,
        "Positif (%)": 78.4,
        "Netral (%)": 15.2,
        "Negatif (%)": 6.4,
        "Isu Dominan": "Kualitas menu makanan bergizi",
        "Kanal Sumber": "Media Daring & X/Twitter",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["tanggal_pemantauan"] == "2026-10-13"
    assert item["nama_program_prioritas"] == "Makan Bergizi Gratis (MBG)"
    assert item["provinsi_wilayah"] == "Jawa Tengah"
    assert item["volume_percakapan_media"] == 1420
    assert item["sentimen_positif_pct"] == 78.4


def test_extractor_offline_fallback():
    """Verify extractor returns reference sentimen wilayah records."""
    ext = Extractor({"url": "http://invalid-gdelt-api.local", "max_records": 4, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 4
    assert records[0]["nama_program_prioritas"] == "Makan Bergizi Gratis (MBG)"
    assert records[0]["provinsi_wilayah"] == "Jawa Tengah"
    assert records[1]["nama_program_prioritas"] == "Koperasi Desa Merah Putih"
