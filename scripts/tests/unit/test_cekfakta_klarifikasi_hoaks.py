"""Unit tests for CekFakta Klarifikasi Hoaks Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.cekfakta.klarifikasi_hoaks.models import (
    Record,
    CekfaktaKlarifikasiHoaksRecord,
)
from ingestion.usecases.geopolitik.cekfakta.klarifikasi_hoaks.normalizer import (
    Normalizer,
    clean_str,
    normalize_single,
)
from ingestion.usecases.geopolitik.cekfakta.klarifikasi_hoaks.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated fact-check record passes Pydantic validation."""
    data = {
        "id_narasi": "NAR-2026-01",
        "isu_pemberitaan": "Kebijakan Hilirisasi Nikel Indonesia",
        "klaim_narasi": "Klaim media asing bahwa pasokan nikel Indonesia merusak pasar global tanpa standar ESG",
        "asal_media_sumber": "Portal Berita Asing & Forum X",
        "tingkat_sebaran": "Tinggi (Viral)",
        "hasil_verifikasi_cek_fakta": "Konteks Dimanipulasi",
        "tanggapan_resmi_pemerintah": "Pemerintah menegaskan komitmen keberlanjutan dan kepatuhan standar internasional pada forum OECD",
        "instansi_klarifikasi": "Kementerian Luar Negeri & Kemenko Marves",
        "tanggal_klarifikasi": "2026-08-20",
    }
    rec = Record(**data)
    assert rec.id_narasi == "NAR-2026-01"
    assert rec.isu_pemberitaan == "Kebijakan Hilirisasi Nikel Indonesia"
    assert rec.tingkat_sebaran == "Tinggi (Viral)"
    assert rec.hasil_verifikasi_cek_fakta == "Konteks Dimanipulasi"
    assert "CekFakta.com" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_narasi="NAR-TEST-01",
        isu_pemberitaan="Isu Pertahanan",
        klaim_narasi="Klaim pangkalan militer asing",
    )
    assert rec.id_narasi == "NAR-TEST-01"
    assert rec.isu_pemberitaan == "Isu Pertahanan"
    assert rec.tingkat_sebaran == "Sedang"
    assert rec.hasil_verifikasi_cek_fakta == "Konteks Dimanipulasi"
    assert rec.tanggal_klarifikasi is None


def test_clean_str_helper():
    """Verify clean_str helper function."""
    assert clean_str("  Kemenlu RI  ") == "Kemenlu RI"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Narasi": "NAR-2026-02",
        "Isu Pemberitaan": "Program Makan Bergizi Gratis (MBG)",
        "Klaim Narasi": "Narasi bias bahwa program MBG membebani fiskal di atas batas aman defisit APBN",
        "Media Asal": "Media Analis Ekonomi Asing",
        "Sebaran": "Sedang",
        "Hasil Verifikasi Cek Fakta": "Fakta Tidak Tepat",
        "Tanggapan Klarifikasi Pemerintah": "Menkeu dan Menlu menyampaikan penjelasan fiskal terukur pada forum investor internasional",
        "Instansi Juru Bicara": "Kementerian Keuangan & Komdigi",
        "Tanggal Klarifikasi": "2026-09-12",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_narasi"] == "NAR-2026-02"
    assert item["isu_pemberitaan"] == "Program Makan Bergizi Gratis (MBG)"
    assert item["instansi_klarifikasi"] == "Kementerian Keuangan & Komdigi"
    assert item["hasil_verifikasi_cek_fakta"] == "Fakta Tidak Tepat"


def test_extractor_offline_fallback():
    """Verify extractor returns reference fact-check records."""
    ext = Extractor({"url": "http://invalid-cekfakta.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_narasi"] == "NAR-2026-01"
    assert records[0]["isu_pemberitaan"] == "Kebijakan Hilirisasi Nikel Indonesia"
