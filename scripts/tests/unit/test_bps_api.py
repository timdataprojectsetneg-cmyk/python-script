"""Tests for the BPS WebAPI extractors (CPI + Inflasi MoM)."""

import pytest

from ingestion.exceptions import ConfigError
from ingestion.usecases.ketenagakerjaan.bps._webapi import BpsWebApiExtractor, to_float
from ingestion.usecases.ketenagakerjaan.bps.bps_consumer_price_index.extractor import (
    Extractor as CpiExtractor,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_consumer_price_index.models import (
    Record as CpiRecord,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_inflasi_mom.extractor import (
    Extractor as MomExtractor,
)
from ingestion.usecases.ketenagakerjaan.bps.bps_inflasi_mom.models import Record as MomRecord


def test_extractors_subclass_shared_base():
    assert issubclass(CpiExtractor, BpsWebApiExtractor)
    assert issubclass(MomExtractor, BpsWebApiExtractor)
    assert CpiExtractor.ENTITY_FIELD == "provinsi"
    assert MomExtractor.ENTITY_FIELD == "kota_inflasi"


def test_extract_requires_api_key(monkeypatch):
    monkeypatch.delenv("BPS_WEBAPI_KEY", raising=False)
    monkeypatch.delenv("BPS_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        list(CpiExtractor({"url": "https://webapi.bps.go.id/x/th/126/key/WebAPI_KEY"}).extract())


def test_to_float():
    assert to_float("105,5") == 105.5
    assert to_float("-") is None
    assert to_float(None) is None
    assert to_float("") is None


def test_cpi_parse_payload():
    payload = {
        "status": "OK",
        "data-availability": "available",
        "var": [{"val": 2261}],
        "vervar": [{"val": 1, "label": "INDONESIA"}, {"val": 2, "label": "ACEH"}],
        "turvar": [{"val": 0, "label": "General"}],
        "tahun": [{"val": 126, "label": "2026"}],
        "turtahun": [{"val": 1, "label": "January"}, {"val": 13, "label": "Annual"}],
        "datacontent": {"1226101261": "105,5", "2226101261": 99.1},
    }
    rows = CpiExtractor({"url": "https://webapi.bps.go.id/x"})._rows_from(payload, 2026)
    assert rows[0]["provinsi"] == "INDONESIA"
    assert rows[0]["januari"] == 105.5
    assert rows[0]["februari"] is None
    assert rows[0]["tahun"] == 2026
    assert CpiRecord(**rows[0]).model_dump()["januari"] == 105.5


def test_mom_parse_payload_maps_tahunan():
    payload = {
        "status": "OK",
        "data-availability": "available",
        "var": [{"val": 1}],
        "vervar": [{"val": 10, "label": "KOTA MEDAN"}],
        "turvar": [],
        "tahun": [{"val": 126, "label": "2026"}],
        "turtahun": [{"val": 1, "label": "Januari"}, {"val": 13, "label": "Tahunan"}],
        "datacontent": {"10101261": 0.4, "101012613": 3.2},
    }
    rows = MomExtractor({"url": "https://webapi.bps.go.id/x"})._rows_from(payload, 2026)
    assert rows[0]["kota_inflasi"] == "KOTA MEDAN"
    assert rows[0]["januari"] == 0.4
    assert rows[0]["tahunan"] == 3.2
    assert MomRecord(**rows[0]).model_dump()["tahunan"] == 3.2
