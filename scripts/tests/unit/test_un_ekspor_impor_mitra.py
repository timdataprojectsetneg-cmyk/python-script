from __future__ import annotations

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.un.comtrade_preview import partner_name
from ingestion.usecases.geopolitik.un.ekspor_impor_mitra.extractor import DEFAULT_URL, Extractor
from ingestion.usecases.geopolitik.un.ekspor_impor_mitra.models import Record
from ingestion.usecases.registry import resolve_extractor_class, resolve_normalizer

ROW = {
    "typeCode": "C",
    "period": "2024",
    "reporterCode": 360,
    "flowCode": "X",
    "partnerCode": 156,
    "cmdCode": "TOTAL",
    "primaryValue": 62_000_000_000.0,
    "isReported": False,
    "isAggregate": True,
    "cifvalue": 1.0,
}


class FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class FakeHttp:
    def __init__(self, payload):
        self.payload = payload
        self.urls = []

    def get(self, url, **kwargs):
        self.urls.append(url)
        return FakeResp(self.payload)


def make_extractor(payload):
    ex = Extractor({})
    ex.http = FakeHttp(payload)
    return ex


def test_default_url_is_catalog_query():
    assert Extractor({}).url == DEFAULT_URL
    assert "reporterCode=360" in DEFAULT_URL and "flowCode=X,M" in DEFAULT_URL


def test_model_accepts_api_aliases_and_field_names():
    by_alias = Record(**{k: v for k, v in ROW.items() if k != "typeCode"})
    by_name = Record(period=2024, reportercode=360, flowcode="X", partnercode=156, cmdcode="TOTAL")
    assert by_alias.period == 2024 and by_alias.reportercode == 360
    assert by_alias.primaryvalue == 62_000_000_000.0
    assert by_name.primaryvalue is None


def test_partner_name_mapping():
    assert partner_name(156) == "China"
    assert partner_name("840") == "USA"
    assert partner_name(0) == "World"
    assert partner_name(999999) is None
    assert partner_name(None) is None


def test_extract_maps_rows_and_partner_names():
    ex = make_extractor({"count": 1, "data": [ROW]})
    rows = list(ex.extract())
    assert len(rows) == 1
    assert rows[0]["partner_name"] == "China"
    assert rows[0]["cmdCode"] == "TOTAL"
    assert "cifvalue" not in rows[0]


def test_extract_api_error_raises():
    ex = make_extractor({"error": "quota exceeded", "data": []})
    with pytest.raises(SourceUnavailable):
        list(ex.extract())


def test_normalizer_validates_and_skips_bad_rows():
    normalizer = resolve_normalizer("geopolitik", "un", "ekspor_impor_mitra", {})
    ex = make_extractor({"data": [ROW, {**ROW, "cmdCode": None}]})
    out = list(normalizer.normalize(ex.extract()))
    assert len(out) == 1
    assert out[0]["period"] == 2024
    assert out[0]["partner_name"] == "China"
    assert out[0]["flowcode"] == "X"
    assert out[0]["isaggregate"] is True


def test_registry_resolves_extractor():
    assert resolve_extractor_class("geopolitik", "un", "ekspor_impor_mitra") is Extractor


def test_years_expand_to_one_request_per_period():
    from ingestion.usecases.geopolitik.un.comtrade_preview import expand_periods

    urls = expand_periods(DEFAULT_URL, "2022-2024")
    assert [u.split("period=")[1].split("&")[0] for u in urls] == ["2022", "2023", "2024"]
    assert expand_periods(DEFAULT_URL, "") == [DEFAULT_URL]

    ex = Extractor({"years": "2023,2024"})
    ex.http = FakeHttp({"data": [ROW]})
    assert len(list(ex.extract())) == 2
    assert len(ex.http.urls) == 2
