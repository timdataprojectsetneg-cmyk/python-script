"""Offline unit tests for Kemendag Perjanjian Perdagangan."""

from types import SimpleNamespace

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.kemendag.perjanjian_perdagangan.extractor import (
    Extractor,
    parse_agreements,
    parse_status,
)
from ingestion.usecases.geopolitik.kemendag.perjanjian_perdagangan.models import Record

HTML = """
<html><body>
<nav><a href="https://ftasupportcenter.kemendag.go.id/tentang">Tentang</a>
<a href="https://ftacenter.kemendag.go.id/tentang">Tentang Kami</a></nav>
<div class="content">
<p><span>Di bawah ini adalah negara&nbsp;yang sudah memiliki FTA dengan Indonesia (per Juni 2025).</span></p>
<ul>
<li><a href="https://ftacenter.kemendag.go.id/atiga"><span>ASEAN Trade&nbsp;In&nbsp;Goods Agreement (ATIGA)</span></a></li>
<li><a href="https://ftacenter.kemendag.go.id/aanzfta"><span>ASEAN-Australia-New Zealand FTA (AANZFTA)</span></a></li>
<li><a href="http://ftacenter.kemendag.go.id/ik-cepa"><span>Indonesia-Korea&nbsp;Comprehensive Economic Partnership</span></a>
    <a href="http://ftacenter.kemendag.go.id/ik-cepa"><p>(IK-CEPA)</p></a></li>
<li><a href="/aanzfta"><p>ASEAN-Australia-New Zealand FTA (AANZFTA)</p></a></li>
<li><a href="https://ftacenter.kemendag.go.id/layanan-konsultasi">kami</a></li>
<li><a href="https://example.org/other">External</a></li>
</ul></div></body></html>
"""


def test_parse_status():
    assert parse_status("negara (per Juni 2025).") == "Berlaku menurut daftar per Juni 2025"
    assert parse_status("(PER   juni   2025)") == "Berlaku menurut daftar per juni 2025"
    assert parse_status("tanpa periode") is None


def test_parse_agreements_dedupe_merge_and_status():
    recs = parse_agreements(HTML, "https://ftasupportcenter.kemendag.go.id/sekilas-tentang-fta")
    assert [r["nama_perjanjian"] for r in recs] == [
        "ASEAN Trade In Goods Agreement (ATIGA)",
        "ASEAN-Australia-New Zealand FTA (AANZFTA)",
        "Indonesia-Korea Comprehensive Economic Partnership (IK-CEPA)",
    ]
    assert {r["status_menurut_sumber"] for r in recs} == {"Berlaku menurut daftar per Juni 2025"}
    assert recs[2]["tautan_detail"] == "http://ftacenter.kemendag.go.id/ik-cepa"
    for r in recs:
        Record(**r)


def test_parse_agreements_no_status_is_none():
    html = HTML.replace("(per Juni 2025)", "")
    assert all(r["status_menurut_sumber"] is None for r in parse_agreements(html))


def test_parse_agreements_empty():
    assert parse_agreements("<html><body><a href='/x'>x</a></body></html>") == []


def test_extractor_yields_and_raises_on_empty():
    ext = Extractor({"url": "https://example.test/fta"})
    ext.http = SimpleNamespace(get=lambda url, **kw: SimpleNamespace(text=HTML))
    assert len(list(ext.extract())) == 3

    ext.http = SimpleNamespace(get=lambda url, **kw: SimpleNamespace(text="<html></html>"))
    with pytest.raises(SourceUnavailable):
        list(ext.extract())
