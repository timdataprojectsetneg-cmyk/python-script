"""Offline tests for UKMTO Insiden Pelayaran."""

import datetime as dt

import pytest

from ingestion.exceptions import SourceUnavailable
from ingestion.usecases.geopolitik.ukmto.insiden_pelayaran.extractor import Extractor, parse_incidents
from ingestion.usecases.geopolitik.ukmto.insiden_pelayaran.models import Record

PAYLOAD = [
    {
        "incidentIssuer": "UKMTO",
        "incidentNumber": 144,
        "sitecoreId": "803461db-46dc-47f1-863f-f0083280a903",
        "utcDateCreated": "2026-09-30T09:30:23Z",
        "utcDateOfIncident": "2026-09-30T09:28:00Z",
        "pinColour": "Yellow",
        "incidentTypeName": "Attack",
        "incidentTypeLevel": 1,
        "locationLatitude": 26.4,
        "locationLongitude": 56.5,
        "locationLatitudeDDDMMSS": "262400N",
        "locationLongitudeDDDMMSS": "0563000E",
        "region": "IO",
        "place": "Strait of Hormuz",
        "vesselName": "TKR",
        "vesselType": "Tanker ",
        "vesselUnderPirateControl": False,
        "dateVesselTaken": None,
        "crewHeld": 0,
        "otherDetails": "Vessel struck.",
        "hideFromTicker": False,
        "extendTickerTime": True,
    },
    {"incidentNumber": 1},
]


def test_parse_incidents_lowercases_keys_and_drops_rows_without_id():
    rows = parse_incidents(PAYLOAD)
    assert len(rows) == 1
    assert rows[0]["sitecoreid"].startswith("803461db")
    assert "incidentTypeName" not in rows[0]


def test_parse_incidents_rejects_unexpected_payload():
    with pytest.raises(SourceUnavailable):
        parse_incidents("<html>")


def test_record_types():
    rec = Record(**parse_incidents(PAYLOAD)[0])
    assert rec.utcdateofincident == dt.datetime(2026, 9, 30, 9, 28, tzinfo=dt.timezone.utc)
    assert rec.locationlatitude == 26.4
    assert rec.datevesseltaken is None
    assert rec.vesselunderpiratecontrol is False


def test_extractor_defaults_to_chrome_impersonation():
    assert Extractor({"url": "https://example.test"}).impersonate == "chrome"
