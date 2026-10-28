"""Offline unit tests for BPS Ekspor Impor Bulanan."""

import json
from types import SimpleNamespace

import pytest

from ingestion.exceptions import ConfigError, SourceUnavailable
from ingestion.usecases.geopolitik.bps.ekspor_impor_bulanan.extractor import (
    Extractor,
    parse_action_response,
    parse_years,
    rows_to_records,
)
from ingestion.usecases.geopolitik.bps.ekspor_impor_bulanan.models import Record

ROWS = [
    {"year": 2023, "month": 1, "eval": "22344650117.668", "enetwt": 51470150153.773, "ival": 18538361214.0, "inetwt": 15364545379.0},
    {"year": 2023, "month": 2, "eval": None, "enetwt": "-", "ival": 1, "inetwt": 2},
    {"year": 2023, "month": None, "eval": 1},
]


def _rsc(payload):
    return '0:{"a":"$@1","f":"","b":"x"}\n1:' + json.dumps(payload) + "\n"


def test_parse_years():
    assert parse_years("2023,2024") == [2023, 2024]
    assert parse_years("2020-2022") == [2020, 2021, 2022]
    assert parse_years("2024; 2022,2022") == [2022, 2024]
    default = parse_years(None)
    assert default[0] == 2020 and default == sorted(default)


def test_parse_action_response_ok():
    payload = {"status": True, "response": {"data": ROWS}}
    assert parse_action_response(_rsc(payload)) == payload


def test_parse_action_response_unrecognised():
    with pytest.raises(SourceUnavailable):
        parse_action_response('0:["nothing"]\n')


def test_rows_to_records():
    records = rows_to_records(ROWS)
    assert len(records) == 2
    assert records[0] == {
        "periode": "2023-01",
        "nilai_ekspor": 22344650117.668,
        "berat_ekspor": 51470150153.773,
        "nilai_impor": 18538361214.0,
        "berat_impor": 15364545379.0,
    }
    assert records[1]["nilai_ekspor"] is None and records[1]["berat_ekspor"] is None


def test_record_validation_and_alias():
    rec = Record(**rows_to_records(ROWS)[0])
    assert rec.periode == "2023-01" and rec.nilai_impor == 18538361214.0
    assert Record(**{"Periode": "2024-05", "Nilai Ekspor": 1}).nilai_ekspor == 1.0
    assert Record(periode="2024-05").berat_impor is None


class _StubHttp:
    def __init__(self, pages=None, post_payload=None):
        self.pages = pages or {}
        self.post_payload = post_payload
        self.posts = []

    def get(self, url, **kw):
        if url not in self.pages:
            raise SourceUnavailable(f"404 {url}")
        return SimpleNamespace(text=self.pages[url])

    def post(self, url, **kw):
        self.posts.append((url, kw))
        return SimpleNamespace(text=_rsc(self.post_payload))


def _extractor(**cfg):
    ext = Extractor({"url": "https://www.bps.go.id/id/exim", **cfg})
    return ext


def test_discover_action_id_from_lazy_chunk():
    action = "7f" + "a" * 40
    page = '<script src="/_next/static/chunks/webpack-abc.js"></script><script src="/_next/static/chunks/main-1.js"></script>'
    runtime = '"static/chunks/"+e+"."+({123:"0123456789abcdef"})[e]+".js"'
    lazy = 'x=(0,s.createServerReference)("%s",s.callServer,void 0,s.findSourceMapURL,"summaryMonthlyExim")' % action
    ext = _extractor()
    ext.http = _StubHttp(
        pages={
            "https://www.bps.go.id/id/exim": page,
            "https://www.bps.go.id/_next/static/chunks/webpack-abc.js": runtime,
            "https://www.bps.go.id/_next/static/chunks/main-1.js": "nothing",
            "https://www.bps.go.id/_next/static/chunks/123.0123456789abcdef.js": lazy,
        }
    )
    assert ext.discover_action_id() == action


def test_discover_action_id_missing_raises():
    ext = _extractor()
    ext.http = _StubHttp(pages={"https://www.bps.go.id/id/exim": "<html></html>"})
    with pytest.raises(SourceUnavailable):
        ext.discover_action_id()


def test_pinned_action_id_and_extract():
    payload = {"status": True, "response": {"data-availability": "available", "data": ROWS[:1]}}
    ext = _extractor(years="2023", params='{"action_id": "abc123"}')
    ext.http = _StubHttp(post_payload=payload)
    out = list(ext.extract())
    assert [r["periode"] for r in out] == ["2023-01"]
    url, kw = ext.http.posts[0]
    assert kw["headers"]["Next-Action"] == "abc123"
    assert json.loads(kw["data"]) == ["www.bps.go.id", "id", 2023]


def test_extract_no_data_raises():
    payload = {"status": True, "response": {"data-availability": "unavailable"}}
    ext = _extractor(years="2023", params={"action_id": "abc"})
    ext.http = _StubHttp(post_payload=payload)
    with pytest.raises(SourceUnavailable):
        list(ext.extract())


def test_invalid_params_raises():
    with pytest.raises(ConfigError):
        _extractor(params="{not json")
