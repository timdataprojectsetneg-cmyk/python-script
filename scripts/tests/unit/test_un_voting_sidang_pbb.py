"""Unit tests for UN Voting Sidang PBB Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.un.voting_sidang_pbb.models import (
    Record,
    UnVotingSidangPbbRecord,
)
from ingestion.usecases.geopolitik.un.voting_sidang_pbb.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.un.voting_sidang_pbb.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated UN voting record passes Pydantic validation."""
    data = {
        "nomor_resolusi": "A/RES/79/112",
        "badan_pbb": "UN General Assembly",
        "tanggal_voting": "2026-09-18",
        "judul_resolusi": "Tuntutan Pengakhiran Pendudukan Ilegal di Wilayah Palestina",
        "posisi_indonesia": "In Favor (Mendukung Penuh)",
        "total_suara_in_favor": 124,
        "total_suara_against": 14,
        "total_abstain": 43,
        "posisi_negara_mitra_utama": "ASEAN solid In Favor; Tiongkok In Favor; AS Against",
    }
    rec = Record(**data)
    assert rec.nomor_resolusi == "A/RES/79/112"
    assert rec.badan_pbb == "UN General Assembly"
    assert rec.tanggal_voting == "2026-09-18"
    assert rec.posisi_indonesia == "In Favor (Mendukung Penuh)"
    assert rec.total_suara_in_favor == 124
    assert rec.total_suara_against == 14
    assert rec.total_abstain == 43
    assert "United Nations Digital Library" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        nomor_resolusi="A/RES/TEST-01",
        judul_resolusi="Resolusi Perlindungan HAM",
    )
    assert rec.nomor_resolusi == "A/RES/TEST-01"
    assert rec.badan_pbb == "UN General Assembly"
    assert rec.posisi_indonesia == "In Favor"
    assert rec.total_suara_in_favor == 0
    assert rec.tanggal_voting is None
    assert rec.posisi_negara_mitra_utama is None


def test_parse_helpers():
    """Verify clean_str and parse_int_safe helper functions."""
    assert clean_str("  UN General Assembly  ") == "UN General Assembly"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("124") == 124
    assert parse_int_safe("1,250") == 1250
    assert parse_int_safe("..") == 0
    assert parse_int_safe(None) == 0


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "Nomor Resolusi": "A/RES/79/045",
        "Badan PBB": "UN General Assembly",
        "Tanggal Voting": "2026-06-12",
        "Judul Resolusi": "Resolusi Pengendalian Senjata Nuklir dan Non-Proliferasi Global",
        "Posisi Indonesia": "In Favor",
        "In Favor": "145",
        "Against": "3",
        "Abstain": "22",
        "Posisi Mitra Kunci": "Indonesia & Non-Blok In Favor; P5 terbelah",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["nomor_resolusi"] == "A/RES/79/045"
    assert item["total_suara_in_favor"] == 145
    assert item["total_suara_against"] == 3
    assert item["total_abstain"] == 22
    assert "Non-Blok" in item["posisi_negara_mitra_utama"]


def test_extractor_offline_fallback():
    """Verify extractor returns reference UN voting records."""
    ext = Extractor({"url": "http://invalid-un-library.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["nomor_resolusi"] == "A/RES/79/112"
    assert records[0]["total_suara_in_favor"] == 124
