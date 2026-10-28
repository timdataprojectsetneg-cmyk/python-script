"""Offline tests for WTO dispute chronology (Sengketa Dagang)."""

from datetime import date

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.wto.sengketa_dagang.extractor import (
    parse_case_page,
    parse_catalogue,
    parse_date,
)
from ingestion.usecases.geopolitik.wto.sengketa_dagang.models import Record

URL = "https://www.wto.org/english/tratop_e/dispu_e/cases_e/ds593_e.htm"

PAGE = """<html><head><title>WTO | DISPUTE SETTLEMENT - DS593: European Union and certain member States - Measures concerning palm oil</title></head>
<body><h2 id="summary">Summary of the dispute to date</h2>
<p>Consultations requested on 9 December 2019. Panel established on 29 April 2021; The report was circulated on 10 January 2025.</p>
<p>The panel found a violation.</p>
<div class="panel-group"><p>Accordion text on 1 January 2000.</p></div>
<p>dd Month yyyy goes here</p>
<h2>Next section</h2><p>Ignored on 5 May 2026.</p></body></html>"""

CATALOGUE = """
ds_array[592] = {
  origin: "IDN",
  destination: "EUR",
  start_date: "2019-12-09"
};
ds_array[100] = {
  origin: "IDN",
  destination: "USA",
  start_date: "1998-01-01"
};
ds_array[600] = {
  origin: "BRA#ARG",
  destination: "CHN",
  start_date: "2020-01-01"
};
ds_array[610] = {
  origin: "CHN",
  destination: "EUR#IDN",
  start_date: "2021-03-04"
};
"""


def test_parse_date():
    assert parse_date("on 9 December 2019.") == date(2019, 12, 9)
    assert parse_date("no date here") is None


def test_parse_catalogue_filters_indonesia_and_year():
    assert parse_catalogue(CATALOGUE, since_year=2019) == ["592", "610"]


def test_parse_case_page_milestones():
    rows = parse_case_page(PAGE, URL)
    assert [r["tanggal_tahapan"] for r in rows] == ["2019-12-09", "2021-04-29", "2025-01-10"]
    assert all(r["nomor_sengketa"] == "DS593" for r in rows)
    assert rows[0]["isu"].startswith("European Union")
    assert "The panel found a violation." in rows[2]["tahapan"]
    assert not any("Accordion" in r["tahapan"] or "Ignored" in r["tahapan"] for r in rows)
    record = Record(**rows[0])
    assert record.tanggal_tahapan == date(2019, 12, 9)
    assert record.url_kasus == URL
    assert [r["urutan_tahapan"] for r in rows] == [1, 2, 3]
    assert record.urutan_tahapan == 1


def test_parse_case_page_rejects_unknown_layout():
    with pytest.raises(SourceUnavailable):
        parse_case_page("<html><head><title>Other</title></head></html>", URL)
    with pytest.raises(SourceUnavailable):
        parse_case_page("<html><head><title>DS1: x</title></head><body></body></html>", URL)


def test_parse_case_page_old_layout_title_without_name():
    html = """<html><head><title>WTO | dispute settlement - the disputes - DS54</title></head><body>
<h1>WORLD TRADE ORGANIZATION</h1><h2>DS54:Indonesia — Certain Measures Affecting the Automobile Industry</h2>
<h2 id="summary">Summary</h2>
<p>Consultations requested on 3 October 1996. Panel established on 12 June 1997.</p></body></html>"""
    rows = parse_case_page(html, "https://www.wto.org/english/tratop_e/dispu_e/cases_e/ds54_e.htm")
    assert rows[0]["nomor_sengketa"] == "DS54"
    assert rows[0]["isu"].startswith("Indonesia - Certain Measures")
    assert len(rows) == 2
