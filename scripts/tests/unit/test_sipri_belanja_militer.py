"""Unit tests for SIPRI Military Expenditure Database Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.sipri.belanja_militer.models import Record, SipriBelanjaMiliterRecord
from ingestion.usecases.geopolitik.sipri.belanja_militer.normalizer import (
    Normalizer,
    clean_percentage,
    clean_expenditure,
)
from ingestion.usecases.geopolitik.sipri.belanja_militer.extractor import Extractor


def test_models_validation_valid():
    """Verify that a properly populated SIPRI record passes Pydantic validation."""
    data = {
        "negara": "Singapura",
        "tahun": 2024,
        "belanja_militer_juta_usd": 15061.03,
        "belanja_militer_pct_pdb": 2.84,
        "belanja_militer_pct_apbn": 20.13,
        "peringkat_belanja_dunia": 23,
        "tren_modernisasi_alutsista": "Pesawat Tempur Siluman F-35B dan Kapal Selam Invincible-class",
        "kawasan": "Asia Tenggara",
        "data_source": "Stockholm International Peace Research Institute (SIPRI)"
    }
    rec = Record(**data)
    assert rec.negara == "Singapura"
    assert rec.tahun == 2024
    assert rec.belanja_militer_juta_usd == 15061.03
    assert rec.belanja_militer_pct_pdb == 2.84
    assert rec.peringkat_belanja_dunia == 23


def test_models_validation_minimal():
    """Verify model default values for minimal fields."""
    rec = Record(
        negara="Indonesia",
        tahun=2024,
        belanja_militer_juta_usd=11042.84
    )
    assert rec.belanja_militer_pct_pdb is None
    assert rec.kawasan == "Internasional"
    assert rec.data_source == "Stockholm International Peace Research Institute (SIPRI)"


def test_clean_percentage():
    """Verify ratio to percentage transformation."""
    assert clean_percentage(0.0284) == 2.84
    assert clean_percentage(0.0078) == 0.78
    assert clean_percentage(2.5) == 2.5
    assert clean_percentage(". .") is None
    assert clean_percentage("xxx") is None
    assert clean_percentage(None) is None


def test_clean_expenditure():
    """Verify numerical expenditure value parsing."""
    assert clean_expenditure(11042.8438) == 11042.84
    assert clean_expenditure("15000.5") == 15000.5
    assert clean_expenditure(". .") is None
    assert clean_expenditure(None) is None


def test_normalizer_flow():
    """Verify normalization flow from raw SIPRI dict."""
    raw_point = {
        "country": "Indonesia",
        "year": 2024,
        "expenditure_usd_million": 11042.84,
        "gdp_pct": 0.0078,
        "govt_pct": 0.046,
        "rank": 26
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw_point])))
    assert len(results) == 1
    item = results[0]
    assert item["negara"] == "Indonesia"
    assert item["tahun"] == 2024
    assert item["kawasan"] == "Asia Tenggara"
    assert item["belanja_militer_pct_pdb"] == 0.78
    assert item["belanja_militer_pct_apbn"] == 4.60
    assert "Rafale" in item["tren_modernisasi_alutsista"]


def test_extractor_init_defaults():
    """Verify extractor initialization with default config."""
    ext = Extractor({})
    assert "SIPRI-Milex-data" in ext.url
    assert 2024 in ext.target_years
