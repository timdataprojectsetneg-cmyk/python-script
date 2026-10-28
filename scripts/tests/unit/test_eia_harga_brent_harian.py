"""Offline tests for EIA Harga Brent Harian."""

import datetime as dt

import pytest

from ingestion.exceptions import AuthError, SourceUnavailable
from ingestion.usecases.geopolitik.eia.harga_brent_harian.extractor import check_payload, parse_rows
from ingestion.usecases.geopolitik.eia.harga_brent_harian.models import Record

PRICE = "europe_brent_spot_price_fob_dollars_per_barrel"

PAYLOAD = {
    "response": {
        "total": "3",
        "data": [
            {"period": "2026-10-19", "series": "RBRTE", "value": "91.25"},
            {"period": "2026-10-20", "series": "RBRTE", "value": None},
            {"period": "2026-10-21", "series": "RBRTE", "value": "92.5"},
        ],
    }
}


def test_parse_rows_skips_empty_prices_and_types_values():
    rows = parse_rows(check_payload(PAYLOAD))
    assert [r["day"] for r in rows] == ["2026-10-19", "2026-10-21"]
    assert rows[0][PRICE] == 91.25
    assert rows[0]["series_id"] == "RBRTE"
    assert rows[0]["source_vendor"] == "Thomson Reuters"


def test_check_payload_errors():
    with pytest.raises(AuthError):
        check_payload({"error": "API_KEY_INVALID: api_key missing"})
    with pytest.raises(SourceUnavailable):
        check_payload({"error": "boom"})
    with pytest.raises(SourceUnavailable):
        check_payload([])


def test_record_parses_iso_and_us_dates():
    iso = Record(**parse_rows(check_payload(PAYLOAD))[0])
    assert iso.day == dt.date(2026, 10, 19)
    us = Record(day="10/9/2026", **{PRICE: 90.0})
    assert us.day == dt.date(2026, 10, 9)
    assert us.series_id == "RBRTE"
