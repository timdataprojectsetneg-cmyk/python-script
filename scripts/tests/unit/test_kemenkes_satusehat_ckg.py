"""Unit tests for Kemenkes SATUSEHAT CKG Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.kemenkes.satusehat_ckg.models import (
    Record,
    KemenkesSatusehatCkgRecord,
)
from ingestion.usecases.kunjungan_presiden.kemenkes.satusehat_ckg.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.kemenkes.satusehat_ckg.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated SATUSEHAT CKG record passes Pydantic validation."""
    data = {
        "id_fasyankes": "P33020101",
        "nama_puskesmas_klinik": "Puskesmas Purwokerto Timur",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Banyumas",
        "jumlah_skrining_balita": 620,
        "jumlah_skrining_dewasa": 1850,
        "jumlah_skrining_lansia": 540,
        "kasus_terindikasi_stunting": 14,
        "kasus_dirujuk_ke_rs": 8,
    }
    rec = Record(**data)
    assert rec.id_fasyankes == "P33020101"
    assert rec.nama_puskesmas_klinik == "Puskesmas Purwokerto Timur"
    assert rec.provinsi == "Jawa Tengah"
    assert rec.jumlah_skrining_balita == 620
    assert rec.jumlah_skrining_dewasa == 1850
    assert rec.kasus_terindikasi_stunting == 14
    assert "Kementerian Kesehatan" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_fasyankes="P32040102",
        nama_puskesmas_klinik="Puskesmas Soreang",
        provinsi="Jawa Barat",
        kabupaten_kota="Bandung",
    )
    assert rec.id_fasyankes == "P32040102"
    assert rec.jumlah_skrining_balita == 0
    assert rec.kasus_terindikasi_stunting == 0


def test_helpers():
    """Verify parsing helper functions."""
    assert clean_str("  Puskesmas Soreang  ") == "Puskesmas Soreang"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("1,850") == 1850
    assert parse_int_safe(620) == 620
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Fasyankes": "P33020101",
        "Nama Puskesmas/Klinik": "Puskesmas Purwokerto Timur",
        "Provinsi": "Jawa Tengah",
        "Kabupaten/Kota": "Banyumas",
        "Skrining Balita": 620,
        "Skrining Dewasa": 1850,
        "Skrining Lansia": 540,
        "Indikasi Stunting": 14,
        "Rujukan RS": 8,
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_fasyankes"] == "P33020101"
    assert item["nama_puskesmas_klinik"] == "Puskesmas Purwokerto Timur"
    assert item["provinsi"] == "Jawa Tengah"
    assert item["jumlah_skrining_balita"] == 620
    assert item["kasus_terindikasi_stunting"] == 14


def test_extractor_offline_fallback():
    """Verify extractor returns reference CKG screening records."""
    ext = Extractor({"url": "http://invalid-satusehat-api.local", "max_records": 4, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 4
    assert records[0]["id_fasyankes"] == "P33020101"
    assert records[0]["nama_puskesmas_klinik"] == "Puskesmas Purwokerto Timur"
    assert records[1]["id_fasyankes"] == "P32040102"
