"""Unit tests for Setpres Pertemuan Bilateral Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.setpres.pertemuan_bilateral.models import (
    Record,
    SetpresPertemuanBilateralRecord,
)
from ingestion.usecases.geopolitik.setpres.pertemuan_bilateral.normalizer import (
    Normalizer,
    clean_str,
    normalize_single,
)
from ingestion.usecases.geopolitik.setpres.pertemuan_bilateral.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated bilateral meeting record passes Pydantic validation."""
    data = {
        "id_pertemuan": "BIL-2026-01",
        "tanggal_kegiatan": "2026-05-15",
        "negara_mitra": "Singapura",
        "lokasi_kota_negara": "Istana Singapura",
        "format_pertemuan": "Retret Pemimpin RI-Singapura",
        "tokoh_pemimpin_mitra": "PM Lawrence Wong",
        "isu_utama_dibahas": "Penguatan ekspor energi hijau & investasi digital IKN",
        "kesepakatan_konkret": "Penandatanganan 3 MoU koridor energi lintas batas",
    }
    rec = Record(**data)
    assert rec.id_pertemuan == "BIL-2026-01"
    assert rec.tanggal_kegiatan == "2026-05-15"
    assert rec.negara_mitra == "Singapura"
    assert rec.lokasi_kota_negara == "Istana Singapura"
    assert rec.format_pertemuan == "Retret Pemimpin RI-Singapura"
    assert rec.tokoh_pemimpin_mitra == "PM Lawrence Wong"
    assert "Sekretariat Presiden RI" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_pertemuan="BIL-TEST-01",
        negara_mitra="Australia",
        lokasi_kota_negara="Canberra",
        tokoh_pemimpin_mitra="PM Australia",
    )
    assert rec.id_pertemuan == "BIL-TEST-01"
    assert rec.negara_mitra == "Australia"
    assert rec.format_pertemuan == "Pertemuan Bilateral"
    assert rec.tanggal_kegiatan is None
    assert rec.isu_utama_dibahas is None
    assert rec.kesepakatan_konkret is None


def test_clean_str_helper():
    """Verify clean_str helper function."""
    assert clean_str("  Australia  ") == "Australia"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Pertemuan": "BIL-2026-02",
        "Tanggal": "2026-08-22",
        "Negara Mitra": "Australia",
        "Lokasi": "Canberra, Australia",
        "Format": "Kunjungan Kenegaraan Resmi",
        "Pemimpin Mitra": "PM Anthony Albanese",
        "Isu Utama": "Peningkatan kuota visa kerja dan kerja sama transisi energi",
        "Hasil Kesepakatan": "Pengesahan ratifikasi peningkatan status traktat DCA",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_pertemuan"] == "BIL-2026-02"
    assert item["negara_mitra"] == "Australia"
    assert item["tokoh_pemimpin_mitra"] == "PM Anthony Albanese"
    assert "DCA" in item["kesepakatan_konkret"]


def test_extractor_offline_fallback():
    """Verify extractor returns reference bilateral meeting records."""
    ext = Extractor({"url": "http://invalid-url.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_pertemuan"] == "BIL-2026-01"
    assert records[0]["negara_mitra"] == "Singapura"
    assert records[1]["negara_mitra"] == "Australia"
