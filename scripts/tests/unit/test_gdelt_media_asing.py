"""Unit tests for GDELT Media Asing Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.gdelt.media_asing.models import (
    Record,
    GdeltMediaAsingRecord,
)
from ingestion.usecases.geopolitik.gdelt.media_asing.normalizer import (
    Normalizer,
    clean_str,
    parse_float_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.gdelt.media_asing.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated GDELT media record passes Pydantic validation."""
    data = {
        "tanggal_artikel": "2026-10-12",
        "judul_berita": "Indonesia Balances Regional Diplomacy Amid South China Sea Shifts",
        "nama_media_sumber": "Nikkei Asia",
        "negara_asal_media": "Jepang",
        "kawasan_media": "Asia Pasifik",
        "topik_utama": "Diplomasi & Geopolitik",
        "skor_sentimen_gdelt": 1.85,
        "url_artikel": "https://asia.nikkei.com/politics/indonesia-diplomacy-2026",
    }
    rec = Record(**data)
    assert rec.tanggal_artikel == "2026-10-12"
    assert rec.judul_berita == "Indonesia Balances Regional Diplomacy Amid South China Sea Shifts"
    assert rec.nama_media_sumber == "Nikkei Asia"
    assert rec.skor_sentimen_gdelt == 1.85
    assert "GDELT Project" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        judul_berita="Pemberitaan Internasional",
        nama_media_sumber="Reuters",
    )
    assert rec.judul_berita == "Pemberitaan Internasional"
    assert rec.nama_media_sumber == "Reuters"
    assert rec.skor_sentimen_gdelt == 0.0
    assert rec.topik_utama == "Diplomasi & Geopolitik"
    assert rec.tanggal_artikel is None


def test_parse_helpers():
    """Verify clean_str and parse_float_safe helper functions."""
    assert clean_str("  Nikkei Asia  ") == "Nikkei Asia"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_float_safe("1.85") == 1.85
    assert parse_float_safe("-2.45") == -2.45
    assert parse_float_safe("..") == 0.0
    assert parse_float_safe(None) == 0.0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Tanggal": "2026-10-11",
        "Judul Berita": "Indonesia Expands Nickel Smelting Standards to Align with Global ESG",
        "Media Sumber": "Reuters",
        "Negara Media": "Inggris",
        "Kawasan": "Eropa",
        "Topik Utama": "Investasi & Nikel",
        "Skor Sentimen": "2.10",
        "URL Artikel": "https://reuters.com/markets/commodities/indonesia-nickel-esg-2026",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["tanggal_artikel"] == "2026-10-11"
    assert item["nama_media_sumber"] == "Reuters"
    assert item["skor_sentimen_gdelt"] == 2.10
    assert item["topik_utama"] == "Investasi & Nikel"


def test_extractor_offline_fallback():
    """Verify extractor returns reference GDELT media records."""
    ext = Extractor({"url": "http://invalid-gdelt-api.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["nama_media_sumber"] == "Nikkei Asia"
    assert records[1]["nama_media_sumber"] == "Reuters"
