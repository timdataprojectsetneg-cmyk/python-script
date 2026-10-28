from __future__ import annotations

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.world_bank.lead_time_logistik.extractor import (
    DEFAULT_URL,
    Extractor,
    split_indicator_urls,
    unit_of,
)
from ingestion.usecases.geopolitik.world_bank.lead_time_logistik.models import Record
from ingestion.usecases.geopolitik.world_bank.wb_api import fetch_all
from ingestion.usecases.registry import resolve_extractor_class, resolve_normalizer

IMP = "Lead time to import, median case (days)"
EXP = "Lead time to export, median case (days)"


def item(code, name, year, value):
    return {"indicator": {"id": code, "value": name}, "country": {"id": "ID"}, "date": year, "value": value}


class FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class FakeHttp:
    def __init__(self, handler):
        self.handler = handler
        self.calls = []

    def get(self, url, params=None, **kwargs):
        self.calls.append((url, params))
        return FakeResp(self.handler(url, params))


def test_split_indicator_urls_per_code():
    urls = split_indicator_urls(DEFAULT_URL)
    assert urls == [
        "https://api.worldbank.org/v2/country/IDN/indicator/LP.IMP.DURS.MD?format=json&per_page=200",
        "https://api.worldbank.org/v2/country/IDN/indicator/LP.EXP.DURS.MD?format=json&per_page=200",
    ]
    assert split_indicator_urls("https://example.org/x") == ["https://example.org/x"]


def test_unit_of():
    assert unit_of(IMP) == "days"
    assert unit_of("Something without unit") == "days"
    assert unit_of("Share (%)") == "%"


def test_extract_skips_null_values_and_queries_each_indicator():
    def handler(url, params):
        if "LP.IMP.DURS.MD" in url:
            rows = [item("LP.IMP.DURS.MD", IMP, "2023", 4.2), item("LP.IMP.DURS.MD", IMP, "2022", None)]
        else:
            rows = [item("LP.EXP.DURS.MD", EXP, "2023", 2.1)]
        return [{"page": 1, "pages": 1, "total": len(rows)}, rows]

    ex = Extractor({})
    ex.http = FakeHttp(handler)
    rows = list(ex.extract())
    assert len(ex.http.calls) == 2
    assert [(r["indicator_code"], r["year"], r["value"], r["unit"]) for r in rows] == [
        ("LP.IMP.DURS.MD", 2023, 4.2, "days"),
        ("LP.EXP.DURS.MD", 2023, 2.1, "days"),
    ]


def test_fetch_all_follows_pagination():
    def handler(url, params):
        page = (params or {}).get("page", 1)
        return [{"page": page, "pages": 2}, [{"n": page}]]

    http = FakeHttp(handler)
    assert list(fetch_all(http, "https://api.worldbank.org/v2/x")) == [{"n": 1}, {"n": 2}]


def test_api_error_message_raises():
    http = FakeHttp(lambda url, params: [{"message": [{"id": "120", "key": "Invalid value"}]}])
    with pytest.raises(SourceUnavailable):
        list(fetch_all(http, "https://api.worldbank.org/v2/x"))


def test_normalizer_round_trip_and_registry():
    normalizer = resolve_normalizer("geopolitik", "world_bank", "lead_time_logistik", {})
    out = list(normalizer.normalize(iter([
        {"indicator_code": "LP.IMP.DURS.MD", "indicator_name": IMP, "year": 2023, "value": 4.2, "unit": "days"},
        {"indicator_code": "LP.IMP.DURS.MD", "year": "bukan-tahun", "value": 1},
    ])))
    assert len(out) == 1
    assert out[0]["year"] == 2023 and out[0]["value"] == 4.2
    assert Record(indicator_code="X", year=2020).value is None
    assert resolve_extractor_class("geopolitik", "world_bank", "lead_time_logistik") is Extractor
