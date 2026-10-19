"""Unit tests for Kemendesa Indeks Desa Membangun (IDM) Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.kemendesa.idm.models import Record, KemendesaIdmRecord
from ingestion.usecases.kunjungan_presiden.kemendesa.idm.normalizer import (
    Normalizer,
    calculate_dimension_score,
    classify_status,
    estimate_village_breakdown,
    normalize_single,
    IKS_DIMENSIONS,
    IKE_DIMENSIONS,
    IKL_DIMENSIONS,
)
from ingestion.usecases.kunjungan_presiden.kemendesa.idm.extractor import Extractor, OFFLINE_FALLBACK_DATA


def test_models_validation_valid():
    """Verify that a properly populated IDM record passes Pydantic validation."""
    data = {
        "id_kabupaten": "3302",
        "provinsi": "Jawa Tengah",
        "kabupaten_kota": "Kabupaten Banyumas",
        "total_desa": 301,
        "total_kecamatan": 23,
        "desa_mandiri": 142,
        "desa_maju": 125,
        "desa_berkembang": 34,
        "desa_tertinggal": 0,
        "desa_sangat_tertinggal": 0,
        "indeks_ketahanan_sosial": 0.8420,
        "indeks_ketahanan_ekonomi": 0.7650,
        "indeks_ketahanan_lingkungan": 0.7710,
        "skor_idm": 0.7927,
        "status_idm": "MAJU",
        "tahun": 2024,
        "data_source": "Kementerian Desa PDTT - IDM Open API"
    }
    rec = Record(**data)
    assert rec.id_kabupaten == "3302"
    assert rec.total_desa == 301
    assert rec.desa_mandiri == 142
    assert rec.status_idm == "MAJU"
    assert rec.skor_idm == 0.7927


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        provinsi="Jawa Barat",
        kabupaten_kota="Kabupaten Bogor",
        total_desa=416
    )
    assert rec.provinsi == "Jawa Barat"
    assert rec.kabupaten_kota == "Kabupaten Bogor"
    assert rec.total_desa == 416
    assert rec.status_idm == "BERKEMBANG"
    assert rec.tahun == 2024


def test_calculate_dimension_score():
    """Verify calculation of dimension scores from components."""
    components = [
        {
            "dimensi": "KESEHATAN",
            "total": {"terpenuhi": 100, "prioritas": 50, "super_prioritas": 50}
        },
        {
            "dimensi": "PENDIDIKAN",
            "total": {"terpenuhi": 150, "prioritas": 30, "super_prioritas": 20}
        },
        {
            "dimensi": "PERDAGANGAN",
            "total": {"terpenuhi": 80, "prioritas": 40, "super_prioritas": 80}
        }
    ]
    # Score for KESEHATAN = (100*1.0 + 50*0.5 + 50*0.1) / 200 = 130 / 200 = 0.65
    # Score for PENDIDIKAN = (150*1.0 + 30*0.5 + 20*0.1) / 200 = 167 / 200 = 0.835
    # IKS average = (0.65 + 0.835) / 2 = 0.7425
    iks = calculate_dimension_score(components, IKS_DIMENSIONS)
    assert iks == 0.7425

    # Non-existent dimension
    empty = calculate_dimension_score([], IKL_DIMENSIONS)
    assert empty == 0.0


def test_classify_status():
    """Verify classification thresholds per Permendesa 2/2016."""
    assert classify_status(0.85) == "MANDIRI"
    assert classify_status(0.8155) == "MANDIRI"
    assert classify_status(0.75) == "MAJU"
    assert classify_status(0.7072) == "MAJU"
    assert classify_status(0.65) == "BERKEMBANG"
    assert classify_status(0.5989) == "BERKEMBANG"
    assert classify_status(0.52) == "TERTINGGAL"
    assert classify_status(0.4907) == "TERTINGGAL"
    assert classify_status(0.40) == "SANGAT TERTINGGAL"


def test_estimate_village_breakdown():
    """Verify estimation of village status breakdown."""
    components = [
        {"total": {"terpenuhi": 200, "prioritas": 50, "super_prioritas": 50}}
    ]
    breakdown = estimate_village_breakdown(300, 0.78, components)
    assert breakdown["desa_mandiri"] + breakdown["desa_maju"] + breakdown["desa_berkembang"] + breakdown["desa_tertinggal"] + breakdown["desa_sangat_tertinggal"] == 300
    assert breakdown["desa_mandiri"] > 0
    assert breakdown["desa_maju"] > 0


def test_normalizer_flow():
    """Verify normalization flow from raw Kemendesa API response."""
    raw_payload = {
        "status": 200,
        "error": False,
        "mapData": {
            "summaries": {
                "id_prov": "33",
                "nama_provinsi": "JAWA TENGAH",
                "id_kabupaten": "3302",
                "nama_kab_kota": "BANYUMAS",
                "total_desa": 301,
                "total_kec": 23,
                "total_desa_verified": "301"
            },
            "komponen": [
                {
                    "dimensi": "KESEHATAN",
                    "total": {"terpenuhi": 250, "prioritas": 30, "super_prioritas": 21}
                },
                {
                    "dimensi": "PERDAGANGAN",
                    "total": {"terpenuhi": 220, "prioritas": 50, "super_prioritas": 31}
                },
                {
                    "dimensi": "KUALITAS LINGKUNGAN",
                    "total": {"terpenuhi": 260, "prioritas": 25, "super_prioritas": 16}
                }
            ]
        }
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw_payload])))
    assert len(results) == 1
    rec = results[0]
    assert rec["id_kabupaten"] == "3302"
    assert rec["provinsi"] == "Jawa Tengah"
    assert rec["kabupaten_kota"] == "Kabupaten Banyumas"
    assert rec["total_desa"] == 301
    assert rec["total_kecamatan"] == 23
    assert rec["skor_idm"] is not None
    assert rec["status_idm"] in ["MAJU", "MANDIRI", "BERKEMBANG"]
    assert rec["desa_mandiri"] + rec["desa_maju"] + rec["desa_berkembang"] == 301


def test_extractor_offline_fallback():
    """Verify extractor yields offline fallback when network is unavailable."""
    ext = Extractor({"url": "http://invalid-non-existent-url.org/api", "max_kabupaten": 2})
    records = list(ext.extract())
    assert len(records) == 2
    assert records[0]["id_kabupaten"] == "3302"
    assert records[0]["kabupaten_kota"] == "Kabupaten Banyumas"
