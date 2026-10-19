"""Unit tests for Setpres Statistik Kunjungan Kerja Presiden Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.setpres.statistik_kunjungan_presiden.models import (
    Record,
    SetpresStatistikKunjunganRecord,
)
from ingestion.usecases.kunjungan_presiden.setpres.statistik_kunjungan_presiden.normalizer import (
    Normalizer,
    parse_int_safe,
    clean_text,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.setpres.statistik_kunjungan_presiden.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated Setpres kunker record passes Pydantic validation."""
    data = {
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Banyumas",
        "frekuensi_kunjungan_total": 3,
        "kunjungan_terakhir": "2026-04-28",
        "agenda_utama": "Peninjauan TPST BLE dan Pasar Tradisional",
        "durasi_kunjungan_hari": 1,
        "pejabat_pendamping_utama": "Mensesneg Prasetyo Hadi; Seskab Teddy Indra Wijaya",
    }
    rec = Record(**data)
    assert rec.provinsi == "Jawa Tengah"
    assert rec.kabupaten_kota == "Kabupaten Banyumas"
    assert rec.frekuensi_kunjungan_total == 3
    assert rec.kunjungan_terakhir == "2026-04-28"
    assert rec.agenda_utama == "Peninjauan TPST BLE dan Pasar Tradisional"
    assert rec.durasi_kunjungan_hari == 1
    assert rec.pejabat_pendamping_utama == "Mensesneg Prasetyo Hadi; Seskab Teddy Indra Wijaya"
    assert rec.data_source.startswith("Sekretariat Presiden")


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        provinsi="Jawa Barat",
        kabupaten_kota="Kabupaten Bogor",
        frekuensi_kunjungan_total=7,
    )
    assert rec.provinsi == "Jawa Barat"
    assert rec.kabupaten_kota == "Kabupaten Bogor"
    assert rec.frekuensi_kunjungan_total == 7
    assert rec.durasi_kunjungan_hari == 1
    assert rec.kunjungan_terakhir is None
    assert rec.agenda_utama is None


def test_parse_helpers():
    """Verify numeric and text helper functions."""
    assert parse_int_safe("4") == 4
    assert parse_int_safe("12,500") == 12500
    assert parse_int_safe("..") is None
    assert parse_int_safe(None) is None

    assert clean_text("  Kabupaten Magelang  ") == "Kabupaten Magelang"
    assert clean_text("-") is None
    assert clean_text(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Provinsi": "Jawa Barat",
        "Kabupaten/Kota": "Kabupaten Bandung Barat",
        "Frekuensi Kunjungan": "4",
        "Kunjungan Terakhir": "2026-08-10",
        "Agenda Utama": "Peresmian SPPG Percontohan dan Sentra Tani",
        "Durasi (Hari)": "1",
        "Pejabat Pendamping": "Menko Pangan Hanif Faisol; Kepala BGN Dadan Hindayana",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["provinsi"] == "Jawa Barat"
    assert item["kabupaten_kota"] == "Kabupaten Bandung Barat"
    assert item["frekuensi_kunjungan_total"] == 4
    assert item["kunjungan_terakhir"] == "2026-08-10"
    assert item["durasi_kunjungan_hari"] == 1
    assert "Menko Pangan" in item["pejabat_pendamping_utama"]


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when URL is unreachable."""
    ext = Extractor({"url": "http://invalid-wiki-kunker.local", "max_records": 3})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["provinsi"] == "Jawa Tengah"
    assert records[0]["kabupaten_kota"] == "Kabupaten Banyumas"
    assert records[0]["frekuensi_kunjungan_total"] == 3
