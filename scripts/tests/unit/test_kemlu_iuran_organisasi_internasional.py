"""Unit tests for Kemlu Iuran Organisasi Internasional Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.kemlu.iuran_organisasi_internasional.models import (
    Record,
    KemluIuranOrganisasiInternasionalRecord,
)
from ingestion.usecases.geopolitik.kemlu.iuran_organisasi_internasional.normalizer import (
    Normalizer,
    clean_str,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.kemlu.iuran_organisasi_internasional.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated OI fee record passes Pydantic validation."""
    data = {
        "id_organisasi": "OI-UN-001",
        "nama_organisasi_internasional": "United Nations (Regular Budget PBB)",
        "kategori_oi": "PBB & Badan Khusus",
        "dasar_hukum_keanggotaan": "Keppres No. 104 Tahun 1950",
        "kl_focal_point": "Kemenlu RI",
        "besaran_iuran_tahunan_valas": 5240000.0,
        "mata_uang": "USD",
        "ekuivalen_rupiah_miliar": 83.84,
        "evaluasi_kemanfaatan": "Tinggi / Mandatori",
        "status_iuran_terakhir": "Lunas",
    }
    rec = Record(**data)
    assert rec.id_organisasi == "OI-UN-001"
    assert rec.nama_organisasi_internasional == "United Nations (Regular Budget PBB)"
    assert rec.kategori_oi == "PBB & Badan Khusus"
    assert rec.besaran_iuran_tahunan_valas == 5240000.0
    assert rec.mata_uang == "USD"
    assert rec.ekuivalen_rupiah_miliar == 83.84
    assert "Kementerian Luar Negeri RI" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_organisasi="OI-TEST-01",
        nama_organisasi_internasional="International Maritime Organization",
    )
    assert rec.id_organisasi == "OI-TEST-01"
    assert rec.nama_organisasi_internasional == "International Maritime Organization"
    assert rec.kategori_oi == "PBB & Badan Khusus"
    assert rec.besaran_iuran_tahunan_valas == 0.0
    assert rec.evaluasi_kemanfaatan == "Tinggi / Strategis"
    assert rec.status_iuran_terakhir == "Lunas"


def test_parse_helpers():
    """Verify clean_str and parse_float_safe helper functions."""
    assert clean_str("  Kemenlu RI  ") == "Kemenlu RI"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_float_safe("5240000") == 5240000.0
    assert parse_float_safe("83.84") == 83.84
    assert parse_float_safe("1,250,000.50") == 1250000.50
    assert parse_float_safe("..") == 0.0
    assert parse_float_safe(None) == 0.0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID OI": "OI-IMO-012",
        "Nama Organisasi": "International Maritime Organization (IMO)",
        "Kategori": "Badan Khusus PBB",
        "Dasar Hukum": "Keppres No. 18 Tahun 1961",
        "KL Focal Point": "Kemenhub RI",
        "Iuran (Valas)": "420000",
        "Mata Uang": "GBP",
        "Ekuivalen (Miliar Rp)": "8.40",
        "Evaluasi Kemanfaatan": "Tinggi / Strategis Pelayaran",
        "Status Iuran": "Lunas",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_organisasi"] == "OI-IMO-012"
    assert item["nama_organisasi_internasional"] == "International Maritime Organization (IMO)"
    assert item["kl_focal_point"] == "Kemenhub RI"
    assert item["besaran_iuran_tahunan_valas"] == 420000.0
    assert item["mata_uang"] == "GBP"


def test_extractor_offline_fallback():
    """Verify extractor returns reference international organization records."""
    ext = Extractor({"url": "http://invalid-kemlu-domain.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_organisasi"] == "OI-UN-001"
    assert records[0]["nama_organisasi_internasional"] == "United Nations (Regular Budget PBB)"
    assert records[0]["evaluasi_kemanfaatan"] == "Tinggi / Mandatori"
