"""Unit tests for Kemendagri Susunan Pemerintahan Daerah Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.kemendagri.susunan_pemerintahan_daerah.models import (
    Record,
    KemendagriSusunanPemdaRecord,
)
from ingestion.usecases.kunjungan_presiden.kemendagri.susunan_pemerintahan_daerah.normalizer import (
    Normalizer,
    clean_str,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.kemendagri.susunan_pemerintahan_daerah.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated Kemendagri susunan pemda record passes Pydantic validation."""
    data = {
        "kode_daerah": "33.02",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Banyumas",
        "nama_kepala_daerah": "Dr. Ir. Achmad Husein, M.Si",
        "status_jabatan": "Definitif",
        "partai_pengusung_koalisi": "Koalisi PDI-P, PKB, PAN",
        "nama_ketua_dprd": "dr. Budhi Setiawan",
        "partai_ketua_dprd": "PDI-P",
        "komposisi_kursi_dprd": "PDI-P: 17, PKB: 9, Gerindra: 7, Golkar: 6, Lainnya: 11",
    }
    rec = Record(**data)
    assert rec.kode_daerah == "33.02"
    assert rec.provinsi == "Jawa Tengah"
    assert rec.kabupaten_kota == "Kabupaten Banyumas"
    assert rec.nama_kepala_daerah == "Dr. Ir. Achmad Husein, M.Si"
    assert rec.status_jabatan == "Definitif"
    assert rec.partai_ketua_dprd == "PDI-P"
    assert "Kementerian Dalam Negeri" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        kode_daerah="32.00",
        provinsi="Jawa Barat",
        kabupaten_kota="Wilayah Terpilih",
        nama_kepala_daerah="Pj Bupati",
    )
    assert rec.kode_daerah == "32.00"
    assert rec.status_jabatan == "Definitif"
    assert rec.partai_pengusung_koalisi is None
    assert rec.nama_ketua_dprd is None


def test_parse_helpers():
    """Verify clean_str helper function."""
    assert clean_str("  Kabupaten Banyumas  ") == "Kabupaten Banyumas"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str("NaN") is None
    assert clean_str("") is None
    assert clean_str(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Kode Daerah": "32.04",
        "Provinsi": "Jawa Barat",
        "Kabupaten/Kota": "Kabupaten Bandung",
        "Kepala Daerah": "H. M. Dadang Supriatna, S.Ip., M.Si",
        "Status": "Definitif",
        "Koalisi Pengusung": "Koalisi PKB, NasDem, Demokrat",
        "Ketua DPRD": "H. Renie Rahayu Fauzi",
        "Partai DPRD": "PKB",
        "Komposisi Kursi": "PKB: 12, Golkar: 10, PKS: 7, Demokrat: 7, Lainnya: 19",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["kode_daerah"] == "32.04"
    assert item["provinsi"] == "Jawa Barat"
    assert item["kabupaten_kota"] == "Kabupaten Bandung"
    assert item["nama_kepala_daerah"] == "H. M. Dadang Supriatna, S.Ip., M.Si"
    assert item["partai_ketua_dprd"] == "PKB"
    assert "PKB: 12" in item["komposisi_kursi_dprd"]


def test_extractor_offline_fallback():
    """Verify extractor returns reference records when URL is unreachable."""
    ext = Extractor({"url": "http://invalid-otda.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["kode_daerah"] == "33.02"
    assert records[0]["kabupaten_kota"] == "Kabupaten Banyumas"
    assert records[0]["status_jabatan"] == "Definitif"
