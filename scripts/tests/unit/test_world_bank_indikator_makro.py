"""Unit tests for World Bank Macroeconomic Indicators Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.world_bank.indikator_makro.models import (
    Record,
    WorldBankIndikatorMakroRecord,
)
from ingestion.usecases.geopolitik.world_bank.indikator_makro.normalizer import (
    Normalizer,
    parse_float_safe,
    parse_int_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.world_bank.indikator_makro.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated World Bank indicator record passes validation."""
    data = {
        "negara": "Jepang",
        "kode_iso3": "JPN",
        "kawasan": "Asia Timur",
        "tahun": 2024,
        "populasi_juta_jiwa": 124.5,
        "pdb_nominal_miliar_usd": 4210.0,
        "pdb_per_kapita_usd": 33815.0,
        "pertumbuhan_pdb_pct": 1.25,
        "inflasi_pct": 2.45,
        "nilai_ekspor_ri_ke_mitra_usd": 21850000000.0,
        "nilai_impor_ri_dari_mitra_usd": 16420000000.0,
        "neraca_perdagangan_ri_usd": 5430000000.0,
    }
    rec = Record(**data)
    assert rec.negara == "Jepang"
    assert rec.kode_iso3 == "JPN"
    assert rec.kawasan == "Asia Timur"
    assert rec.tahun == 2024
    assert rec.populasi_juta_jiwa == 124.5
    assert rec.pdb_nominal_miliar_usd == 4210.0
    assert rec.pdb_per_kapita_usd == 33815.0
    assert rec.pertumbuhan_pdb_pct == 1.25
    assert rec.inflasi_pct == 2.45
    assert rec.neraca_perdagangan_ri_usd == 5430000000.0
    assert rec.data_source.startswith("World Bank")


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        negara="Indonesia",
        kode_iso3="IDN",
        tahun=2024,
    )
    assert rec.negara == "Indonesia"
    assert rec.kode_iso3 == "IDN"
    assert rec.tahun == 2024
    assert rec.populasi_juta_jiwa is None
    assert rec.pdb_nominal_miliar_usd is None


def test_parse_helpers():
    """Verify numeric parser helpers."""
    assert parse_float_safe("1,396.30") == 1396.30
    assert parse_float_safe("5.03") == 5.03
    assert parse_float_safe("..") is None
    assert parse_float_safe(None) is None

    assert parse_int_safe("2024") == 2024
    assert parse_int_safe("NA") is None
    assert parse_int_safe(None) is None


def test_normalizer_flow():
    """Verify normalizer auto-computes trade balance and assigns geographic regions."""
    raw = {
        "country": "Tiongkok",
        "iso3": "CHN",
        "year": "2024",
        "populasi": "1408.98",
        "pdb_miliar": "18729.67",
        "pdb_kapita": "13293.00",
        "pertumbuhan_pdb": "4.96",
        "inflasi": "0.22",
        "ekspor_ri": "68420000000",
        "impor_ri": "64180000000",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["negara"] == "Tiongkok"
    assert item["kode_iso3"] == "CHN"
    assert item["kawasan"] == "Asia Timur"
    assert item["tahun"] == 2024
    assert item["populasi_juta_jiwa"] == 1408.98
    assert item["pdb_nominal_miliar_usd"] == 18729.67
    assert item["neraca_perdagangan_ri_usd"] == 4240000000.0


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when URL is unreachable."""
    ext = Extractor({"url": "http://invalid-worldbank-api.local", "max_records": 3})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["kode_iso3"] == "IDN"
    assert records[0]["tahun"] == 2024
    assert records[0]["pertumbuhan_pdb_pct"] == 5.05
