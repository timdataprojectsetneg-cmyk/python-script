"""Unit tests for KKP Kampung Nelayan Merah Putih (KNMP) Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.kkp.kampung_nelayan_merah_putih.models import (
    Record,
    KkpKampungNelayanRecord,
)
from ingestion.usecases.kunjungan_presiden.kkp.kampung_nelayan_merah_putih.normalizer import (
    Normalizer,
    parse_float_safe,
    parse_int_safe,
    clean_wilayah,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.kkp.kampung_nelayan_merah_putih.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated KKP KNMP record passes Pydantic validation."""
    data = {
        "id_knmp": "KNMP-3301-01",
        "nama_desa_nelayan": "Kampung Nelayan Sentolo Cilacap",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Cilacap",
        "jumlah_nelayan": 850,
        "kapasitas_cold_storage_ton": 20.0,
        "produksi_es_ton_hari": 10.0,
        "status_operasional": "Beroperasi",
        "latitude": -7.7312,
        "longitude": 109.0125,
    }
    rec = Record(**data)
    assert rec.id_knmp == "KNMP-3301-01"
    assert rec.nama_desa_nelayan == "Kampung Nelayan Sentolo Cilacap"
    assert rec.provinsi == "Jawa Tengah"
    assert rec.kabupaten_kota == "Cilacap"
    assert rec.jumlah_nelayan == 850
    assert rec.kapasitas_cold_storage_ton == 20.0
    assert rec.produksi_es_ton_hari == 10.0
    assert rec.status_operasional == "Beroperasi"
    assert rec.latitude == -7.7312
    assert rec.longitude == 109.0125
    assert rec.data_source.startswith("Kementerian Kelautan dan Perikanan")


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        id_knmp="KNMP-9999",
        nama_desa_nelayan="Sentra Nelayan Pantai Timur",
        provinsi="Lampung",
        kabupaten_kota="Lampung Timur",
    )
    assert rec.id_knmp == "KNMP-9999"
    assert rec.nama_desa_nelayan == "Sentra Nelayan Pantai Timur"
    assert rec.status_operasional == "Beroperasi"
    assert rec.jumlah_nelayan is None
    assert rec.kapasitas_cold_storage_ton is None


def test_parse_helpers():
    """Verify numeric parser helpers."""
    assert parse_float_safe("20,5") == 20.5
    assert parse_float_safe("-") is None
    assert parse_float_safe(None) is None

    assert parse_int_safe("1,200") == 1200
    assert parse_int_safe("..") is None
    assert parse_int_safe(None) is None

    assert clean_wilayah(" Kab. Trenggalek ") == "Kab. Trenggalek"
    assert clean_wilayah(None) == "Indonesia"


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID KNMP": "KNMP-3501-02",
        "Nama Sentra Nelayan": "Sentra Nelayan Prigi Trenggalek",
        "Provinsi": "Jawa Timur",
        "Kabupaten/Kota": "Trenggalek",
        "Nelayan": "1200",
        "Cold Storage (Ton)": "30,0",
        "Pabrik Es (Ton/Hari)": "15,0",
        "Status": "Beroperasi",
        "Lat": "-8.2833",
        "Lon": "111.7167",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_knmp"] == "KNMP-3501-02"
    assert item["nama_desa_nelayan"] == "Sentra Nelayan Prigi Trenggalek"
    assert item["jumlah_nelayan"] == 1200
    assert item["kapasitas_cold_storage_ton"] == 30.0
    assert item["produksi_es_ton_hari"] == 15.0
    assert item["latitude"] == -8.2833
    assert item["longitude"] == 111.7167


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when URL is unreachable."""
    ext = Extractor({"url": "http://invalid-kkp-pipp-url.local", "max_records": 3})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_knmp"] == "KNMP-3301-01"
    assert records[0]["kabupaten_kota"] == "Cilacap"
    assert records[0]["jumlah_nelayan"] == 850
