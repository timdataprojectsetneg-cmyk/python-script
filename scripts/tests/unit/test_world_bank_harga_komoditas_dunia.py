from __future__ import annotations

import io

import pytest
from openpyxl import Workbook

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.world_bank.harga_komoditas_dunia.extractor import (
    Extractor,
    parse_monthly_prices,
    parse_price,
)
from ingestion.usecases.geopolitik.world_bank.harga_komoditas_dunia.models import Record
from ingestion.usecases.registry import resolve_extractor_class, resolve_normalizer


def workbook_bytes(sheet="Monthly Prices"):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    ws.append(["World Bank Commodity Price Data (The Pink Sheet)"])
    ws.append(["monthly prices in nominal US dollars, 1960 to present"])
    ws.append([])
    ws.append(["Updated on October 02, 2026"])
    ws.append([None, "Crude oil, Brent", "Coal, Australian", "Natural gas, US", None])
    ws.append([None, "($/bbl)", "($/mt)", "($/mmbtu)", None])
    ws.append(["1960M01", 1.6, "…", 0.14, None])
    ws.append(["2025M12", 62.5, 110.25, 3.1, None])
    ws.append(["2026M09", 116.8, "..", 2.95, None])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class FakeResp:
    def __init__(self, content=b"", text=""):
        self.content = content
        self.text = text


def test_parse_price():
    assert parse_price(1.6) == 1.6
    assert parse_price("…") is None
    assert parse_price("..") is None
    assert parse_price(None) is None
    assert parse_price("1,234.5") == 1234.5


def test_parse_monthly_prices_melts_with_exact_units():
    rows = list(parse_monthly_prices(workbook_bytes()))
    assert len(rows) == 9
    first = rows[0]
    assert first == {"Periode": "1960-01", "Komoditas": "Crude oil, Brent", "Harga": 1.6, "Satuan": "($/bbl)"}
    missing = [r for r in rows if r["Periode"] == "1960-01" and r["Komoditas"] == "Coal, Australian"][0]
    assert missing["Harga"] is None and missing["Satuan"] == "($/mt)"
    assert {r["Satuan"] for r in rows} == {"($/bbl)", "($/mt)", "($/mmbtu)"}


def test_start_year_filter():
    rows = list(parse_monthly_prices(workbook_bytes(), start_year=2025))
    assert {r["Periode"] for r in rows} == {"2025-12", "2026-09"}


def test_unexpected_layout_raises():
    wb = Workbook()
    wb.active.title = "Monthly Prices"
    wb.active.append(["2020M01", 1])
    buf = io.BytesIO()
    wb.save(buf)
    with pytest.raises(SourceUnavailable):
        list(parse_monthly_prices(buf.getvalue()))


def test_download_falls_back_to_landing_page_link():
    new_link = "https://thedocs.worldbank.org/en/doc/abc123-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
    calls = []

    class Http:
        def get(self, url, **kwargs):
            calls.append(url)
            if url == ex.url:
                raise SourceUnavailable("404")
            if url == ex.page_url:
                return FakeResp(text=f'<a href="{new_link}">Monthly</a>')
            return FakeResp(content=workbook_bytes())

    ex = Extractor({"url": "https://thedocs.worldbank.org/old/CMO-Historical-Data-Monthly.xlsx"})
    ex.http = Http()
    rows = list(ex.extract())
    assert calls[-1] == new_link
    assert len(rows) == 9


def test_fallback_without_link_raises():
    class Http:
        def get(self, url, **kwargs):
            if url == ex.url:
                raise SourceUnavailable("404")
            return FakeResp(text="<html>no link</html>")

    ex = Extractor({})
    ex.http = Http()
    with pytest.raises(SourceUnavailable):
        list(ex.extract())


def test_normalizer_round_trip_and_registry():
    normalizer = resolve_normalizer("geopolitik", "world_bank", "harga_komoditas_dunia", {})
    ex = Extractor({})
    ex.http = type("H", (), {"get": lambda self, url, **kw: FakeResp(content=workbook_bytes())})()
    out = list(normalizer.normalize(ex.extract()))
    assert len(out) == 9
    brent = [r for r in out if r["komoditas"] == "Crude oil, Brent" and r["periode"] == "2026-09"][0]
    assert brent["harga"] == 116.8 and brent["satuan"] == "($/bbl)"
    assert Record(Periode="2026-01", Komoditas="X").harga is None
    assert resolve_extractor_class("geopolitik", "world_bank", "harga_komoditas_dunia") is Extractor
