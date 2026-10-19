"""Unit tests for Kemlu Treaty Room Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.kemlu.treaty_room.models import (
    Record,
    KemluTreatyRoomRecord,
)
from ingestion.usecases.geopolitik.kemlu.treaty_room.normalizer import (
    Normalizer,
    clean_str,
    normalize_single,
)
from ingestion.usecases.geopolitik.kemlu.treaty_room.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated Treaty Room record passes Pydantic validation."""
    data = {
        "id_perjanjian": "TR-2026-US-04",
        "negara_mitra": "Amerika Serikat",
        "judul_perjanjian": "Perjanjian Kerja Sama Pertahanan (DCA) Komprehensif",
        "bidang_kerja_sama": "Hankam",
        "tahapan": "Diratifikasi",
        "tanggal_penandatanganan": "2026-02-14",
        "dasar_pengesahan_uu_perpres": "UU No. 12 Tahun 2026",
        "instansi_penanggung_jawab_kl": "Kementerian Pertahanan RI",
    }
    rec = Record(**data)
    assert rec.id_perjanjian == "TR-2026-US-04"
    assert rec.negara_mitra == "Amerika Serikat"
    assert rec.bidang_kerja_sama == "Hankam"
    assert rec.tahapan == "Diratifikasi"
    assert rec.tanggal_penandatanganan == "2026-02-14"
    assert "Kementerian Pertahanan" in rec.instansi_penanggung_jawab_kl
    assert "Kementerian Luar Negeri" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        id_perjanjian="TR-TEST-01",
        negara_mitra="Australia",
        judul_perjanjian="Perjanjian Kerja Sama Bilateral",
    )
    assert rec.id_perjanjian == "TR-TEST-01"
    assert rec.negara_mitra == "Australia"
    assert rec.bidang_kerja_sama == "Ekonomi & Perdagangan"
    assert rec.tahapan == "Ditandatangani"
    assert rec.tanggal_penandatanganan is None
    assert rec.dasar_pengesahan_uu_perpres is None


def test_parse_helpers():
    """Verify clean_str helper function."""
    assert clean_str("  Amerika Serikat  ") == "Amerika Serikat"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str("NaN") is None
    assert clean_str("") is None
    assert clean_str(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Perjanjian": "TR-2026-CN-02",
        "Negara Mitra": "Tiongkok",
        "Judul Perjanjian": "MoU Riset Hilirisasi Mineral Kritis",
        "Bidang": "Ekonomi & Energi",
        "Tahapan": "Dilaksanakan",
        "Tanggal TTD": "2026-05-18",
        "Dasar Pengesahan": "Perpres No. 45 Tahun 2026",
        "Instansi PJ": "Kemenko Pangan & Kementerian ESDM",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_perjanjian"] == "TR-2026-CN-02"
    assert item["negara_mitra"] == "Tiongkok"
    assert item["bidang_kerja_sama"] == "Ekonomi & Energi"
    assert item["tahapan"] == "Dilaksanakan"
    assert item["tanggal_penandatanganan"] == "2026-05-18"


def test_extractor_offline_fallback():
    """Verify extractor returns reference treaty records."""
    ext = Extractor({"url": "http://invalid-treaty.local", "portal_url": "http://invalid-portal.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_perjanjian"] == "TR-2026-US-04"
    assert records[0]["negara_mitra"] == "Amerika Serikat"
    assert records[0]["tahapan"] == "Diratifikasi"
