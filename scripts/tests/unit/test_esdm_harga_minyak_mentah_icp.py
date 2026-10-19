"""Unit tests for ESDM Indonesian Crude Price (ICP) Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.esdm.harga_minyak_mentah_icp.models import (
    Record,
    EsdmHargaIcpRecord,
)
from ingestion.usecases.geopolitik.esdm.harga_minyak_mentah_icp.normalizer import (
    Normalizer,
    parse_float_safe,
    parse_int_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.esdm.harga_minyak_mentah_icp.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
    _clean_price,
)


def test_models_validation_valid():
    """Verify that a properly populated ESDM ICP record passes Pydantic validation."""
    data = {
        "periode_data": "2026-09",
        "tahun": 2026,
        "bulan": "September",
        "icp_usd": 112.81,
        "icp_perubahan_usd": 23.38,
        "brent_ice_usd": 102.02,
        "wti_nymex_usd": 95.69,
        "dated_brent_usd": 116.77,
        "basket_opec_usd": 110.73,
        "nomor_kepmen": "Keputusan Menteri ESDM Nomor 395.K/MG.03/MEM.M/2026",
        "faktor_geopolitik_pasar": "Ketegangan geopolitik Timur Tengah.",
        "sumber_dokumen_url": "https://www.esdm.go.id/id/media-center/arsip-berita/icp-september",
    }
    rec = Record(**data)
    assert rec.periode_data == "2026-09"
    assert rec.tahun == 2026
    assert rec.bulan == "September"
    assert rec.icp_usd == 112.81
    assert rec.brent_ice_usd == 102.02
    assert rec.wti_nymex_usd == 95.69
    assert rec.dated_brent_usd == 116.77
    assert rec.basket_opec_usd == 110.73
    assert rec.nomor_kepmen.startswith("Keputusan Menteri")


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        periode_data="2026-08",
        tahun=2026,
        bulan="Agustus",
        icp_usd=89.43,
    )
    assert rec.periode_data == "2026-08"
    assert rec.icp_usd == 89.43
    assert rec.brent_ice_usd is None
    assert rec.data_source.startswith("Kementerian Energi dan Sumber Daya Mineral")


def test_parse_float_safe():
    """Verify parsing floats with Indonesian commas and currencies."""
    assert parse_float_safe("112,81") == 112.81
    assert parse_float_safe("US$ 89,43") == 89.43
    assert parse_float_safe("83.97/bbl") == 83.97
    assert parse_float_safe(102.02) == 102.02
    assert parse_float_safe("-") is None
    assert parse_float_safe(None) is None


def test_clean_price():
    """Verify clean price helper in extractor."""
    assert _clean_price("US$112,81") == 112.81
    assert _clean_price(" 89.43 ") == 89.43
    assert _clean_price(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "periode_data": "2026-09",
        "tahun": "2026",
        "bulan": "September",
        "icp_usd": "112,81",
        "icp_perubahan_usd": "23,38",
        "brent_ice_usd": "102,02",
        "wti_nymex_usd": "95,69",
        "dated_brent_usd": "116,77",
        "basket_opec_usd": "110,73",
        "nomor_kepmen": "Kepmen No 395/2026",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["tahun"] == 2026
    assert item["bulan"] == "September"
    assert item["icp_usd"] == 112.81
    assert item["brent_ice_usd"] == 102.02


def test_extractor_offline_fallback():
    """Verify extractor returns offline fallback records when network is unavailable."""
    ext = Extractor({
        "news_url": "http://invalid-esdm-url.local",
        "migas_url": "http://invalid-migas-url.local",
        "max_records": 2,
    })
    records = list(ext.extract())
    assert len(records) == 2
    assert records[0]["periode_data"] == "2026-09"
    assert records[0]["icp_usd"] == 112.81
