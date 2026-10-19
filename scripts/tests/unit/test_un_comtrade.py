"""Unit tests for UN Comtrade Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.un.comtrade.models import (
    Record,
    UnComtradeRecord,
)
from ingestion.usecases.geopolitik.un.comtrade.normalizer import (
    Normalizer,
    clean_str,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.un.comtrade.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated UN Comtrade record passes Pydantic validation."""
    data = {
        "periode_bulan": "2026-08",
        "kode_hs_2digit": "75",
        "deskripsi_komoditas": "Nikel dan Produk Turunan Smelter",
        "arus_perdagangan": "Ekspor",
        "negara_mitra_utama": "Tiongkok",
        "volume_ribu_ton": 1450.0,
        "nilai_fob_cif_juta_usd": 1850.5,
        "pertumbuhan_tahunan_pct": 14.2,
    }
    rec = Record(**data)
    assert rec.periode_bulan == "2026-08"
    assert rec.kode_hs_2digit == "75"
    assert rec.deskripsi_komoditas == "Nikel dan Produk Turunan Smelter"
    assert rec.arus_perdagangan == "Ekspor"
    assert rec.volume_ribu_ton == 1450.0
    assert "UN Comtrade" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        periode_bulan="2026-08",
        kode_hs_2digit="15",
        deskripsi_komoditas="Minyak Kelapa Sawit (CPO)",
        arus_perdagangan="Ekspor",
        negara_mitra_utama="India",
    )
    assert rec.periode_bulan == "2026-08"
    assert rec.kode_hs_2digit == "15"
    assert rec.volume_ribu_ton == 0.0
    assert rec.nilai_fob_cif_juta_usd == 0.0


def test_helpers():
    """Verify parsing helper functions."""
    assert clean_str("  Nikel Smelter  ") == "Nikel Smelter"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_float_safe("1,850.5") == 1850.5
    assert parse_float_safe("14.2%") == 14.2
    assert parse_float_safe(-3.5) == -3.5
    assert parse_float_safe("-") == 0.0
    assert parse_float_safe(None) == 0.0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Periode": "2026-08",
        "HS Code": "75",
        "Komoditas Strategis": "Nikel dan Produk Turunan Smelter",
        "Arus Dagang": "Ekspor",
        "Negara Mitra": "Tiongkok",
        "Volume (Ribu Ton)": 1450.0,
        "Nilai (Juta USD)": 1850.5,
        "Pertumbuhan (%)": 14.2,
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["periode_bulan"] == "2026-08"
    assert item["kode_hs_2digit"] == "75"
    assert item["deskripsi_komoditas"] == "Nikel dan Produk Turunan Smelter"
    assert item["arus_perdagangan"] == "Ekspor"
    assert item["negara_mitra_utama"] == "Tiongkok"
    assert item["volume_ribu_ton"] == 1450.0
    assert item["nilai_fob_cif_juta_usd"] == 1850.5


def test_extractor_offline_fallback():
    """Verify extractor returns reference trade flow records."""
    ext = Extractor({"url": "http://invalid-comtrade-api.local", "max_records": 4, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 4
    assert records[0]["kode_hs_2digit"] == "75"
    assert records[0]["deskripsi_komoditas"] == "Nikel dan Produk Turunan Smelter"
    assert records[1]["kode_hs_2digit"] == "10"
    assert records[1]["deskripsi_komoditas"] == "Gandum dan Meslin (Bahan Pangan)"
