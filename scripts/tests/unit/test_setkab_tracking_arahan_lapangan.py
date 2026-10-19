"""Unit tests for Setkab Tracking Arahan Lapangan Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.setkab.tracking_arahan_lapangan.models import (
    Record,
    SetkabTrackingArahanLapanganRecord,
)
from ingestion.usecases.kunjungan_presiden.setkab.tracking_arahan_lapangan.normalizer import (
    Normalizer,
    clean_str,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.setkab.tracking_arahan_lapangan.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated directive tracking record passes Pydantic validation."""
    data = {
        "id_arahan": "ARH-2026-041",
        "tanggal_arahan": "2026-04-28",
        "lokasi_kunjungan": "Banyumas",
        "isi_arahan_presiden": "Percepat integrasi pengolahan pupuk organik dari sampah TPST BLE ke sentra tani",
        "instansi_pelaksana": "Kementan & Kementerian LH",
        "dokumen_dasar_tindak_lanjut": "Kepmentan No. 241/2026",
        "status_tindak_lanjut": "Sedang Berjalan",
    }
    rec = Record(**data)
    assert rec.id_arahan == "ARH-2026-041"
    assert rec.tanggal_arahan == "2026-04-28"
    assert rec.lokasi_kunjungan == "Banyumas"
    assert rec.instansi_pelaksana == "Kementan & Kementerian LH"
    assert rec.status_tindak_lanjut == "Sedang Berjalan"
    assert "Sekretariat Kabinet RI" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_arahan="ARH-TEST-01",
        lokasi_kunjungan="Semarang",
        isi_arahan_presiden="Normalisasi tanggul rob",
        instansi_pelaksana="Kementerian PU",
    )
    assert rec.id_arahan == "ARH-TEST-01"
    assert rec.lokasi_kunjungan == "Semarang"
    assert rec.status_tindak_lanjut == "Sedang Berjalan"
    assert rec.dokumen_dasar_tindak_lanjut is None


def test_clean_str_helper():
    """Verify clean_str helper function."""
    assert clean_str("  Kementan  ") == "Kementan"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Arahan": "ARH-2026-058",
        "Tanggal Arahan": "2026-08-10",
        "Lokasi": "Bandung Barat",
        "Isi Arahan Presiden": "Beri insentif subsidi listrik bagi dapur gizi SPPG yang beroperasi mandiri",
        "Instansi Pelaksana": "Kementerian ESDM & PLN",
        "Dasar Dokumen": "Surat Edaran Dirjen Ketenagalistrikan",
        "Status Tindak Lanjut": "Tercapai",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_arahan"] == "ARH-2026-058"
    assert item["lokasi_kunjungan"] == "Bandung Barat"
    assert item["status_tindak_lanjut"] == "Tercapai"
    assert item["instansi_pelaksana"] == "Kementerian ESDM & PLN"


def test_extractor_offline_fallback():
    """Verify extractor returns reference presidential directive records."""
    ext = Extractor({"url": "http://invalid-setkab.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_arahan"] == "ARH-2026-041"
    assert records[0]["lokasi_kunjungan"] == "Banyumas"
    assert records[1]["lokasi_kunjungan"] == "Bandung Barat"
