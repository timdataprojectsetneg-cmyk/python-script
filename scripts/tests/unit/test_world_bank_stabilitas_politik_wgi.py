from __future__ import annotations

import io
import zipfile

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.world_bank.stabilitas_politik_wgi.extractor import (
    DEFAULT_URL,
    Extractor,
    parse_archive,
)
from ingestion.usecases.geopolitik.world_bank.stabilitas_politik_wgi.models import Record
from ingestion.usecases.registry import resolve_extractor_class, resolve_normalizer

IND = "Political Stability - Governance estimate (approx. -2.5 to +2.5)"

DATA_CSV = (
    '"Data Source","Worldwide Governance Indicators",\r\n'
    "\r\n"
    '"Last Updated Date","2026-09-25",\r\n'
    "\r\n"
    '"Country Name","Country Code","Indicator Name","Indicator Code","1996","1998","2000","2002",\r\n'
    f'"Indonesia","IDN","{IND}","GOV_WGI_PV.EST","-1.2","","-1.8","-1.1",\r\n'
    f'"Aruba","ABW","{IND}","GOV_WGI_PV.EST","","","","1.1",\r\n'
    f'"World","WLD","{IND}","GOV_WGI_PV.EST","0.1","0.2","","",\r\n'
)
META_CSV = (
    '"Country Code","Region","IncomeGroup","SpecialNotes","TableName",\r\n'
    '"IDN","East Asia & Pacific","Upper middle income","Catatan\r\nmultibaris","Indonesia",\r\n'
    '"ABW","Latin America & Caribbean","High income","","Aruba",\r\n'
    '"WLD","","","","World",\r\n'
)


def make_zip(data=DATA_CSV, meta=META_CSV):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("Metadata_Indicator_API_GOV_WGI_PV.EST_DS3_en_csv_v2_1.csv", "x\r\n")
        zf.writestr("API_GOV_WGI_PV.EST_DS3_en_csv_v2_1.csv", "﻿" + data)
        zf.writestr("Metadata_Country_API_GOV_WGI_PV.EST_DS3_en_csv_v2_1.csv", "﻿" + meta)
    return buf.getvalue()


class FakeResp:
    def __init__(self, content):
        self.content = content


def test_parse_archive_melts_years_and_drops_aggregates():
    rows = list(parse_archive(make_zip()))
    assert {r["Country Code"] for r in rows} == {"IDN", "ABW"}
    idn = {r["year"]: r["value"] for r in rows if r["Country Code"] == "IDN"}
    assert idn == {1996: -1.2, 2000: -1.8, 2002: -1.1}
    first = rows[0]
    assert first["Region"] == "East Asia & Pacific"
    assert first["IncomeGroup"] == "Upper middle income"
    assert first["Indicator Code"] == "GOV_WGI_PV.EST"


def test_include_aggregates_keeps_blank_region_rows():
    rows = list(parse_archive(make_zip(), include_aggregates=True))
    wld = [r for r in rows if r["Country Code"] == "WLD"]
    assert len(wld) == 2 and wld[0]["Region"] is None


def test_bad_archive_and_missing_header_raise():
    with pytest.raises(SourceUnavailable):
        list(parse_archive(b"<html>not a zip</html>"))
    with pytest.raises(SourceUnavailable):
        list(parse_archive(make_zip(data='"a","b"\r\n"1","2"\r\n')))


def test_extractor_uses_config_flag_and_default_url():
    ex = Extractor({"include_aggregates": "true"})
    assert ex.url == DEFAULT_URL and ex.include_aggregates is True
    assert Extractor({}).include_aggregates is False
    ex.http = type("H", (), {"get": lambda self, url, **kw: FakeResp(make_zip())})()
    assert {r["Country Code"] for r in ex.extract()} == {"IDN", "ABW", "WLD"}


def test_normalizer_round_trip_and_registry():
    normalizer = resolve_normalizer("geopolitik", "world_bank", "stabilitas_politik_wgi", {})
    ex = Extractor({})
    ex.http = type("H", (), {"get": lambda self, url, **kw: FakeResp(make_zip())})()
    out = list(normalizer.normalize(ex.extract()))
    assert len(out) == 4
    rec = [r for r in out if r["country_code"] == "IDN" and r["year"] == 1996][0]
    assert rec["value"] == -1.2
    assert rec["country_name"] == "Indonesia"
    assert rec["region"] == "East Asia & Pacific"
    assert rec["income_group"] == "Upper middle income"
    assert Record(country_name="X", country_code="XXX", indicator_code="C", year=2000, value=0.5).region is None
    assert resolve_extractor_class("geopolitik", "world_bank", "stabilitas_politik_wgi") is Extractor
