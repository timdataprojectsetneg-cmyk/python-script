"""Offline tests for BMKG Gempa Dirasakan."""

import datetime as dt

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.bmkg.gempa_dirasakan.extractor import Extractor, parse_xml
from ingestion.usecases.geopolitik.bmkg.gempa_dirasakan.models import Record

XML = b"""<?xml version="1.0"?><Infogempa>
<gempa><Tanggal>25 Okt 2026</Tanggal><Jam>19:47:26 WIB</Jam>
<DateTime>2026-10-25T12:47:26+00:00</DateTime>
<point><coordinates>-0.73,131.39</coordinates></point>
<Lintang>0.73 LS</Lintang><Bujur>131.39 BT</Bujur><Magnitude>3.8</Magnitude>
<Kedalaman>6 km</Kedalaman>
<Wilayah>Pusat gempa berada di laut 13 km timur laut Kota Sorong</Wilayah>
<Dirasakan>II Kota Sorong</Dirasakan></gempa>
<gempa><Tanggal>22 Okt 2026</Tanggal><Jam>17:57:49 WIB</Jam>
<DateTime>2026-10-22T10:57:49+00:00</DateTime>
<point><coordinates>4.24,97.65</coordinates></point>
<Magnitude>4.7</Magnitude><Kedalaman>120 km</Kedalaman></gempa>
</Infogempa>"""


def test_parse_xml_splits_coordinates_and_depth():
    rows = parse_xml(XML)
    assert len(rows) == 2
    first = rows[0]
    assert first["point_coordinates"] == "-0.73,131.39"
    assert (first["latitude"], first["longitude"]) == (-0.73, 131.39)
    assert first["magnitude"] == 3.8
    assert first["kedalaman_km"] == 6.0
    assert rows[1]["dirasakan"] is None


def test_record_parses_datetime():
    rec = Record(**parse_xml(XML)[0])
    assert rec.datetime == dt.datetime(2026, 10, 25, 12, 47, 26, tzinfo=dt.timezone.utc)
    assert rec.wilayah.startswith("Pusat gempa")


def test_invalid_xml_raises():
    with pytest.raises(SourceUnavailable):
        parse_xml(b"<html>not xml")


def test_extractor_defaults_to_chrome_impersonation():
    assert Extractor({"url": "https://example.test"}).impersonate == "chrome"
