"""Unit tests for Kemenkes SIRANAP Referral Hospital Facilities Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.kemenkes.siranap_rs_rujukan.models import Record, SiranapRsRujukanRecord
from ingestion.usecases.kunjungan_presiden.kemenkes.siranap_rs_rujukan.normalizer import (
    Normalizer,
    classify_hospital,
    estimate_bor,
)
from ingestion.usecases.kunjungan_presiden.kemenkes.siranap_rs_rujukan.extractor import Extractor


def test_models_validation_valid():
    """Verify that a properly populated hospital record passes Pydantic validation."""
    data = {
        "kode_rs": "3302012",
        "nama_rumah_sakit": "RSUD Prof. Dr. Margono Soekarjo",
        "kelas_rs": "Kelas A (Rujukan Utama)",
        "jarak_dari_lokasi_km": 4.5,
        "waktu_tempuh_menit": 12,
        "ketersediaan_icu_vvip": 4,
        "bed_occupancy_rate_pct": 76.5,
        "kesiapan_ambulans_vvip": "Siap Siaga 24 Jam",
        "alamat_rs": "Jl. Dr. Gumbreg No. 1 Purwokerto",
        "total_bed_kosong": 50,
        "total_ruangan_terdata": 45,
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Banyumas",
        "data_source": "Kementerian Kesehatan RI - SIRANAP"
    }
    rec = Record(**data)
    assert rec.kode_rs == "3302012"
    assert rec.ketersediaan_icu_vvip == 4
    assert rec.bed_occupancy_rate_pct == 76.5


def test_models_validation_minimal():
    """Verify model default values for minimal fields."""
    rec = Record(
        kode_rs="1234567",
        nama_rumah_sakit="RSUD Daerah"
    )
    assert rec.kelas_rs == "Kelas B (Rujukan Daerah)"
    assert rec.kesiapan_ambulans_vvip == "Siap Siaga 24 Jam"
    assert rec.data_source == "Kementerian Kesehatan RI - SIRANAP"


def test_classify_hospital():
    """Verify hospital classification based on institutional naming."""
    assert "Kelas A" in classify_hospital("RSUP Fatmawati")
    assert "Kelas A" in classify_hospital("RSUP Dr Cipto Mangunkusumo")
    assert "TNI/Polri" in classify_hospital("RS Umum AL Cilandak")
    assert "TNI/Polri" in classify_hospital("Rumkit Bhayangkara")
    assert "Kelas B" in classify_hospital("RSUD Pasar Minggu")
    assert "RS Swasta" in classify_hospital("RS Pondok Indah")


def test_estimate_bor():
    """Verify BOR calculation logic based on remaining empty beds."""
    assert estimate_bor(90) == 58.0
    assert estimate_bor(45) == 68.5
    assert estimate_bor(25) == 78.0
    assert estimate_bor(10) == 88.5
    assert estimate_bor(0) == 96.0


def test_normalizer_flow():
    """Verify end-to-end normalization from raw scraped card dict."""
    raw_card = {
        "kode_rs": "3171012",
        "nama_rs": "RSUP Fatmawati",
        "alamat_rs": "Jl. RS Fatmawati",
        "total_bed_kosong": 40,
        "bed_icu_vvip_kosong": 2,
        "total_ruangan": 178,
        "provinsi": "DKI Jakarta",
        "kabupaten_kota": "Jakarta Selatan"
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw_card])))
    assert len(results) == 1
    item = results[0]
    assert item["kode_rs"] == "3171012"
    assert "Kelas A" in item["kelas_rs"]
    assert item["ketersediaan_icu_vvip"] == 2
    assert item["total_bed_kosong"] == 40
    assert item["kesiapan_ambulans_vvip"] == "Siap Siaga 24 Jam"


def test_extractor_init_defaults():
    """Verify extractor initialization with default config."""
    ext = Extractor({})
    assert "keslan.kemkes.go.id" in ext.url
    assert ext.jenis == "2"
    assert ext.propinsi == "31prop"
    assert ext.kabkota == "3171"
