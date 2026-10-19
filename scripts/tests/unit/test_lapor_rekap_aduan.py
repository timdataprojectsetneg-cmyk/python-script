"""Unit tests for SP4N-LAPOR! Rekapitulasi Aduan Wilayah Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.lapor.rekap_aduan_wilayah.models import Record, LaporRekapAduanRecord
from ingestion.usecases.kunjungan_presiden.lapor.rekap_aduan_wilayah.normalizer import (
    Normalizer,
    clean_kabupaten_name,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.lapor.rekap_aduan_wilayah.extractor import Extractor, OFFLINE_FALLBACK_DATA


def test_models_validation_valid():
    """Verify that a properly populated LAPOR record passes Pydantic validation."""
    data = {
        "id_aduan": "ADU-2026-8812",
        "tanggal_lapor": "2026-10-09",
        "kategori_program": "Makan Bergizi Gratis (MBG)",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Banyumas",
        "uraian_laporan": "Usulan penambahan variasi buah lokal pada menu siswa SD.",
        "status_tindak_lanjut": "Selesai",
        "instansi_tujuan": "Badan Gizi Nasional",
        "jumlah_aduan": 142,
        "tahun": 2024,
        "kode_wilayah": "33.02",
        "data_source": "SP4N-LAPOR! KemenPANRB, Kemensetneg & KSP",
    }
    rec = Record(**data)
    assert rec.id_aduan == "ADU-2026-8812"
    assert rec.kabupaten_kota == "Kabupaten Banyumas"
    assert rec.jumlah_aduan == 142
    assert rec.status_tindak_lanjut == "Selesai"


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        id_aduan="LAPOR-TEST-01",
        tanggal_lapor="2024-12-31",
        provinsi="DKI Jakarta",
        kabupaten_kota="Kota Jakarta Pusat",
        uraian_laporan="Aspirasi warga terkait infrastruktur jalan.",
        instansi_tujuan="Pemerintah Kota Jakarta Pusat"
    )
    assert rec.kategori_program == "Pelayanan Publik & Tata Kelola"
    assert rec.status_tindak_lanjut == "Selesai"
    assert rec.jumlah_aduan == 1
    assert rec.tahun == 2024


def test_clean_kabupaten_name():
    """Verify county and city naming normalization."""
    assert clean_kabupaten_name("Kota Bandung") == "Kota Bandung"
    assert clean_kabupaten_name("Kabupaten Banyumas") == "Kabupaten Banyumas"
    assert clean_kabupaten_name("Kab Cilacap") == "Kabupaten Cilacap"
    assert clean_kabupaten_name("Simeulue") == "Kabupaten Simeulue"
    assert clean_kabupaten_name("") == "Wilayah Nasional"


def test_normalize_single_maps_payload():
    """Verify normalization from raw datawarehouse maps payload."""
    raw = {
        "json_id": "162",
        "location_name": "Kota Jakarta Pusat",
        "total": "3,145",
        "provinsi": "DKI Jakarta",
        "kode_wilayah": "31.71",
        "object_key": "ID-31.71",
        "tahun": 2024
    }
    rec = normalize_single(raw)
    assert rec.id_aduan == "LAPOR-3171-2024"
    assert rec.kabupaten_kota == "Kota Jakarta Pusat"
    assert rec.provinsi == "DKI Jakarta"
    assert rec.jumlah_aduan == 3145
    assert rec.instansi_tujuan == "Pemerintah Kota Jakarta Pusat"
    assert rec.status_tindak_lanjut == "Selesai"


def test_normalizer_flow():
    """Verify normalizer yields valid dict records."""
    raw_items = [
        {
            "json_id": "185",
            "location_name": "Kota Bandung",
            "total": "2128",
            "provinsi": "Jawa Barat",
            "object_key": "ID-32.73",
            "tahun": 2024
        }
    ]
    norm = Normalizer()
    results = list(norm.normalize(iter(raw_items)))
    assert len(results) == 1
    item = results[0]
    assert item["id_aduan"] == "LAPOR-3273-2024"
    assert item["kabupaten_kota"] == "Kota Bandung"
    assert item["jumlah_aduan"] == 2128


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when remote URL is unreachable."""
    ext = Extractor({"url": "http://invalid-lapor-url.test", "max_records": 2})
    records = list(ext.extract())
    assert len(records) == 2
    assert records[0]["id_aduan"] == "ADU-2026-8812"
    assert records[0]["provinsi"] == "Jawa Tengah"
