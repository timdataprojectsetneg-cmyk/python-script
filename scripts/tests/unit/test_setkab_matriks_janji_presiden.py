"""Unit tests for Setkab Matriks Janji & Arahan Presiden Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.setkab.matriks_janji_presiden.models import (
    Record,
    SetkabMatriksJanjiRecord,
)
from ingestion.usecases.kunjungan_presiden.setkab.matriks_janji_presiden.normalizer import (
    Normalizer,
    clean_str,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.setkab.matriks_janji_presiden.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated Setkab matriks janji record passes Pydantic validation."""
    data = {
        "id_komitmen": "JNJ-2026-001",
        "program_strategis": "Pengolahan Sampah Terpadu (TPST)",
        "substansi_komitmen": "Percepatan pembangunan fasilitas pengolahan sampah modern di Banyumas",
        "tanggal_penyampaian": "2026-04-28",
        "forum_agenda": "Kunjungan Kerja Peninjauan TPST BLE",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Banyumas",
        "desa_lokasi": "Desa Watuagung",
        "kl_penanggung_jawab": "Kementerian Lingkungan Hidup / Pemkab Banyumas",
        "status_pemenuhan": "On Progress",
        "catatan_progres_sekdukkab": "Mesin pemilah sampah terpasang 80%",
        "koordinasi_kemenko": "Kemenko Pangan & Lingkungan",
    }
    rec = Record(**data)
    assert rec.id_komitmen == "JNJ-2026-001"
    assert rec.program_strategis == "Pengolahan Sampah Terpadu (TPST)"
    assert rec.provinsi == "Jawa Tengah"
    assert rec.kabupaten_kota == "Banyumas"
    assert rec.status_pemenuhan == "On Progress"
    assert "Sekretariat Kabinet" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        id_komitmen="JNJ-2026-999",
        program_strategis="Program Prioritas",
        substansi_komitmen="Arahan Presiden untuk percepatan pelayanan masyarakat.",
    )
    assert rec.id_komitmen == "JNJ-2026-999"
    assert rec.program_strategis == "Program Prioritas"
    assert rec.status_pemenuhan == "On Progress"
    assert rec.tanggal_penyampaian is None
    assert rec.provinsi is None


def test_parse_helpers():
    """Verify clean_str helper function."""
    assert clean_str("  Banyumas  ") == "Banyumas"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str("NaN") is None
    assert clean_str("") is None
    assert clean_str(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Komitmen": "JNJ-2026-042",
        "Program Strategis": "Swasembada Beras & Saluran Irigasi",
        "Substansi Komitmen": "Pembangunan bendung dan saluran sekunder sawah 5000 ha",
        "Tanggal": "2026-07-15",
        "Forum/Agenda": "Panen Raya Bersama",
        "Provinsi": "Sulawesi Selatan",
        "Kabupaten/Kota": "Wajo",
        "Desa/Lokasi": "Desa Salobulo",
        "K/L PIC": "Kementerian Pekerjaan Umum",
        "Status": "Selesai",
        "Catatan Progres": "Saluran tersier rampung dan air mengalir",
        "Kemenko Pengampu": "Kemenko Infrastruktur",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_komitmen"] == "JNJ-2026-042"
    assert item["program_strategis"] == "Swasembada Beras & Saluran Irigasi"
    assert item["provinsi"] == "Sulawesi Selatan"
    assert item["kabupaten_kota"] == "Wajo"
    assert item["status_pemenuhan"] == "Selesai"
    assert item["kl_penanggung_jawab"] == "Kementerian Pekerjaan Umum"


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when URL is unreachable."""
    ext = Extractor({"url": "http://invalid-setkab-portal.local", "max_records": 3})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_komitmen"] == "JNJ-2026-001"
    assert records[0]["program_strategis"] == "Pengolahan Sampah Terpadu (TPST)"
    assert records[0]["kabupaten_kota"] == "Banyumas"
