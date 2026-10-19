"""Unit tests for GDACS Global Disaster Emergency Alerts Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.gdacs.kedaruratan_bencana.models import Record, GdacsKedaruratanBencanaRecord
from ingestion.usecases.geopolitik.gdacs.kedaruratan_bencana.normalizer import (
    Normalizer,
    parse_rfc_date,
    parse_coordinates,
    parse_population,
    evaluate_impact_on_indonesia,
)
from ingestion.usecases.geopolitik.gdacs.kedaruratan_bencana.extractor import Extractor


def test_models_validation_valid():
    """Verify that a properly populated GDACS record passes Pydantic validation."""
    data = {
        "id_peringatan": "GDACS-EQ1571367",
        "nama_kejadian": "Gempa Bumi M7.4 Pasifik Barat Daya",
        "negara_kawasan": "Vanuatu & Pasifik Selatan",
        "jenis_kedaruratan": "Gempa Bumi",
        "level_waspada": "Red Alert",
        "tanggal_kejadian": "2026-10-08",
        "estimasi_korban_terdampak": 45000,
        "potensi_imbas_ke_indonesia": "Potensi gangguan kabel optik bawah laut lintas Pasifik",
        "latitude": -15.5,
        "longitude": 167.2,
        "severity": "Magnitude 7.4M",
        "kode_event": "EQ",
        "deskripsi": "Severe earthquake detected.",
        "link_detail": "https://www.gdacs.org/report.aspx?eventtype=EQ&eventid=1571367",
        "data_source": "Global Disaster Alert and Coordination System (GDACS)"
    }
    rec = Record(**data)
    assert rec.id_peringatan == "GDACS-EQ1571367"
    assert rec.level_waspada == "Red Alert"
    assert rec.estimasi_korban_terdampak == 45000


def test_models_validation_defaults():
    """Verify model default values for minimal fields."""
    rec = Record(
        id_peringatan="GDACS-TC999",
        nama_kejadian="Tropical Cyclone Alpha",
        negara_kawasan="Madagascar",
        jenis_kedaruratan="Siklon Tropis",
        tanggal_kejadian="2026-10-14"
    )
    assert rec.level_waspada == "Green Alert"
    assert rec.data_source == "Global Disaster Alert and Coordination System (GDACS)"


def test_parse_rfc_date():
    """Verify RFC 822 date to ISO date parsing."""
    assert parse_rfc_date("Tue, 13 Oct 2026 19:02:33 GMT") == "2026-10-13"
    assert parse_rfc_date("Wed, 14 Oct 2026 03:00:25 GMT") == "2026-10-14"
    assert parse_rfc_date("") == ""


def test_parse_coordinates():
    """Verify 'lat lon' coordinate parsing."""
    lat, lon = parse_coordinates("-5.4832 152.1364")
    assert lat == -5.4832
    assert lon == 152.1364

    lat2, lon2 = parse_coordinates(None)
    assert lat2 is None and lon2 is None


def test_parse_population():
    """Verify population phrase parsing."""
    assert parse_population("0.823 million") == 823000
    assert parse_population("4 thousand") == 4000
    assert parse_population("120000 people") == 120000
    assert parse_population("None") is None
    assert parse_population("[unknown]") is None


def test_evaluate_impact():
    """Verify impact assessment on Indonesia."""
    assert "Ring 1" in evaluate_impact_on_indonesia("Papua New Guinea", "EQ", "Green")
    assert "pelayaran" in evaluate_impact_on_indonesia("South China Sea", "TC", "Orange")
    assert "Red Alert" in evaluate_impact_on_indonesia("Mexico", "TC", "Red")


def test_normalizer_flow():
    """Verify normalization flow from raw XML item dict."""
    raw_item = {
        "guid": "EQ12345",
        "title": "Earthquake in Indonesia",
        "country": "Indonesia",
        "eventtype": "EQ",
        "alertlevel": "Orange",
        "pubDate": "Mon, 12 Oct 2026 10:00:00 GMT",
        "point": "-6.2 106.8",
        "population": "50 thousand",
        "severity": "M 6.2",
        "description": "Earthquake near Java",
        "link": "https://gdacs.org/eq/12345"
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw_item])))
    assert len(results) == 1
    item = results[0]
    assert item["id_peringatan"] == "GDACS-EQ12345"
    assert item["jenis_kedaruratan"] == "Gempa Bumi"
    assert item["level_waspada"] == "Orange Alert"
    assert item["tanggal_kejadian"] == "2026-10-12"
    assert item["estimasi_korban_terdampak"] == 50000
    assert item["latitude"] == -6.2


def test_extractor_init_defaults():
    """Verify extractor initialization with default URL."""
    ext = Extractor({})
    assert "gdacs.org/xml/rss.xml" in ext.url
