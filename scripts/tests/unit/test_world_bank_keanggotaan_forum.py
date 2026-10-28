"""Offline tests for World Bank Group membership (Keanggotaan Forum)."""

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.world_bank.keanggotaan_forum.extractor import (
    Extractor,
    build_records,
    parse_members,
    parse_membership_date,
)
from ingestion.usecases.geopolitik.world_bank.keanggotaan_forum.models import Record

HTML = """
<html><body>
<h3>International Bank for Reconstruction and Development</h3>
<p>189 countries</p>
<table>
  <tr><td><b>Date of Membership</b></td></tr>
  <tr><td><b>Indonesia</b>, Apr 13, 1967</td><td><b>Albania</b>, Oct 15, 1991</td></tr>
</table>
<h3>International Finance Corporation</h3>
<p>186 countries</p>
<table>
  <tr><td><b>Date of Membership</b></td></tr>
  <tr><td><b>Indonesia</b>, Apr 23, 1968</td><td><b>Chad</b>, Jan 1, 1970</td></tr>
</table>
</body></html>
"""


def test_parse_membership_date():
    assert parse_membership_date("Apr 13, 1967") == "1967-04-13"
    assert parse_membership_date(", Sep 1, 2000 ") == "2000-09-01"
    assert parse_membership_date("unknown") is None


def test_parse_members_reads_each_organisation_table():
    parsed = parse_members(HTML)
    assert [name for name, _ in parsed] == [
        "International Bank for Reconstruction and Development",
        "International Finance Corporation",
    ]
    assert parsed[0][1]["Indonesia"] == "Apr 13, 1967"
    assert parsed[1][1]["Chad"] == "Jan 1, 1970"


def test_build_records_filters_country_case_insensitively():
    records = build_records(HTML, "indonesia", "https://example.org/members")
    assert [(r["organisasi_forum"], r["tanggal_tahun_periode"]) for r in records] == [
        ("International Bank for Reconstruction and Development", "1967-04-13"),
        ("International Finance Corporation", "1968-04-23"),
    ]
    assert all(r["status_peran"] == "Member" and r["url_sumber"] == "https://example.org/members" for r in records)
    assert Record(**records[0]).negara == "Indonesia"


def test_build_records_unknown_country_is_empty():
    assert build_records(HTML, "Atlantis", "u") == []


def test_extractor_reads_source_file(tmp_path):
    path = tmp_path / "members.html"
    path.write_text(HTML, encoding="utf-8")
    rows = list(Extractor({"source_file": str(path), "country": "Albania"}).extract())
    assert len(rows) == 1 and rows[0]["tanggal_tahun_periode"] == "1991-10-15"


def test_extractor_raises_when_country_missing(tmp_path):
    path = tmp_path / "members.html"
    path.write_text(HTML, encoding="utf-8")
    with pytest.raises(SourceUnavailable):
        list(Extractor({"source_file": str(path), "country": "Atlantis"}).extract())
