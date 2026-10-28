from __future__ import annotations

from ingestion.usecases.geopolitik.un.impor_komoditas_strategis.extractor import (
    DEFAULT_URL,
    Extractor,
    totals_url,
)
from ingestion.usecases.geopolitik.un.impor_komoditas_strategis.models import Record
from ingestion.usecases.registry import resolve_extractor_class, resolve_normalizer


def row(partner, cmd, value, flow="M"):
    return {
        "period": "2024",
        "reporterCode": 360,
        "flowCode": flow,
        "partnerCode": partner,
        "cmdCode": cmd,
        "primaryValue": value,
        "isReported": False,
        "isAggregate": True,
    }


class FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class FakeHttp:
    def __init__(self, partners, totals):
        self.partners = partners
        self.totals = totals
        self.urls = []

    def get(self, url, **kwargs):
        self.urls.append(url)
        data = self.totals if "partnerCode=0" in url else self.partners
        return FakeResp({"data": data})


def make_extractor(partners, totals):
    ex = Extractor({})
    ex.http = FakeHttp(partners, totals)
    return ex


def test_totals_url_replaces_only_partner_code():
    url = totals_url(DEFAULT_URL)
    assert "partnerCode=0&" in url
    assert "cmdCode=10,27,72,85" in url and "flowCode=M" in url
    assert "156,840" not in url


def test_supplier_share_uses_world_total():
    ex = make_extractor(
        [row(156, "27", 25.0), row(702, "27", 75.0), row(156, "10", 5.0)],
        [row(0, "27", 100.0), row(0, "10", 20.0)],
    )
    rows = {(r["partnerCode"], r["cmdCode"]): r for r in ex.extract()}
    assert rows[(156, "27")]["supplierShare"] == 0.25
    assert rows[(702, "27")]["supplierShare"] == 0.75
    assert rows[(156, "10")]["supplierShare"] == 0.25
    assert rows[(156, "27")]["totalCommodityValue"] == 100.0
    assert rows[(702, "27")]["partner_name"] == "Singapore"
    assert len(ex.http.urls) == 2


def test_world_rows_in_main_query_are_used_and_not_emitted():
    ex = make_extractor([row(0, "27", 100.0), row(156, "27", 50.0)], [])
    rows = list(ex.extract())
    assert len(ex.http.urls) == 1
    assert [r["partnerCode"] for r in rows] == [156]
    assert rows[0]["supplierShare"] == 0.5


def test_missing_or_zero_total_gives_null_share():
    ex = make_extractor([row(156, "27", 50.0), row(156, "85", 10.0)], [row(0, "85", 0.0)])
    rows = {r["cmdCode"]: r for r in ex.extract()}
    assert rows["27"]["totalCommodityValue"] is None and rows["27"]["supplierShare"] is None
    assert rows["85"]["supplierShare"] is None


def test_normalizer_round_trip():
    normalizer = resolve_normalizer("geopolitik", "un", "impor_komoditas_strategis", {})
    ex = make_extractor([row(156, "27", 25.0)], [row(0, "27", 100.0)])
    out = list(normalizer.normalize(ex.extract()))
    assert len(out) == 1
    assert out[0]["suppliershare"] == 0.25
    assert out[0]["totalcommodityvalue"] == 100.0
    assert out[0]["partner_name"] == "China"
    assert out[0]["cmdcode"] == "27"


def test_model_defaults_and_registry():
    rec = Record(period=2024, reportercode=360, flowcode="M", partnercode=156, cmdcode="27")
    assert rec.suppliershare is None and rec.totalcommodityvalue is None
    assert resolve_extractor_class("geopolitik", "un", "impor_komoditas_strategis") is Extractor
