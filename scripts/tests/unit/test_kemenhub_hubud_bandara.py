"""Unit tests for Kemenhub Hubud Airport Infrastructure Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.kemenhub.hubud_bandara.models import Record, HubudBandaraRecord
from ingestion.usecases.kunjungan_presiden.kemenhub.hubud_bandara.normalizer import (
    Normalizer,
    parse_runway_length,
    determine_vvip_readiness,
    clean_name,
)
from ingestion.usecases.kunjungan_presiden.kemenhub.hubud_bandara.extractor import Extractor


def test_models_validation_valid():
    """Verify that a properly populated airport record passes Pydantic validation."""
    data = {
        "id_fasilitas": "WIHH / HLP",
        "nama_fasilitas": "Bandara Halim Perdanakusuma",
        "jenis_infrastruktur": "Bandara Militer / Enclave Sipil",
        "panjang_runway_m": 3000.0,
        "klasifikasi_pesawat_maks": "Boeing 777-300ER / BBJ",
        "kondisi_kemantapan_jalan_pct": 100.0,
        "status_kelayakan_vvip": "Layak Penuh Pesawat Kenegaraan VVIP (Wide Body / BBJ)",
        "kode_icao": "WIHH",
        "kode_iata": "HLP",
        "klasifikasi_icao": "4E",
        "kekuatan_pcn": "75 F/C/X/T",
        "pengelola": "TNI AU / PT Angkasa Pura",
        "alamat": "Halim Perdanakusuma, Jakarta Timur",
        "jam_operasional": "24 Jam",
        "kabupaten_kota": "Jakarta Timur",
        "latitude": -6.266,
        "longitude": 106.891,
        "elevasi_mdpl": 25.0,
        "data_source": "Ditjen Hubud Kemenhub & BIG Satupeta"
    }
    rec = Record(**data)
    assert rec.id_fasilitas == "WIHH / HLP"
    assert rec.panjang_runway_m == 3000.0
    assert "Layak Penuh" in rec.status_kelayakan_vvip


def test_models_validation_minimal():
    """Verify model default values for minimal fields."""
    rec = Record(
        id_fasilitas="TEST-01",
        nama_fasilitas="Bandara Lapangan Terbang Perintis"
    )
    assert rec.jenis_infrastruktur == "Bandar Udara Sipil / Komersial"
    assert rec.kondisi_kemantapan_jalan_pct == 100.0
    assert rec.status_kelayakan_vvip == "Layak Operasional"


def test_parse_runway_length():
    """Verify runway extraction from dimension string or ICAO code."""
    assert parse_runway_length("3000 x 45 m", "4E") == 3000.0
    assert parse_runway_length("1600 x 30", "3C") == 1600.0
    assert parse_runway_length("-", "4E") == 3000.0
    assert parse_runway_length("", "3C") == 1600.0
    assert parse_runway_length(None, None) is None


def test_determine_vvip_readiness():
    """Verify VVIP readiness logic based on aircraft types and runway lengths."""
    # Wide body
    assert "Wide Body" in determine_vvip_readiness("A330 - 300", 2600.0, "4E")
    # Narrow body BBJ
    assert "BBJ (Narrow Body)" in determine_vvip_readiness("B737 - 900 ER", 2300.0, "4D")
    # Tactical transport
    assert "TNI AU C-130" in determine_vvip_readiness("ATR72 - 500", 1450.0, "3C")
    # Light aircraft
    assert "Terbatas" in determine_vvip_readiness("Cessna Caravan", 700.0, "1A")


def test_clean_name():
    """Verify name capitalization and prefix handling."""
    assert clean_name("HALIM PERDANAKUSUMA") == "Bandara Halim Perdanakusuma"
    assert clean_name("Bandara Adi Sumarmo") == "Bandara Adi Sumarmo"
    assert clean_name("Lanud Iswahjudi") == "Lanud Iswahjudi"


def test_normalizer_flow():
    """Verify normalization flow from raw ArcGIS attribute dict."""
    raw_feature = {
        "attributes": {
            "namobj": "ADI SOEMARMO",
            "kdicao": "WARQ",
            "kdiata": "SOC",
            "dmnsrw": "2600 x 45",
            "jnspsw": "A330-300",
            "klsfks": "4E",
            "pcnaip": "68 F/C/X/T",
            "adabmi": "PT Angkasa Pura I",
            "wadmkk": "Boyolali",
            "lat": -7.518,
            "lon": 110.746,
            "elevas": 127.0
        },
        "geometry": {"x": 110.746, "y": -7.518}
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw_feature])))
    assert len(results) == 1
    item = results[0]
    assert item["id_fasilitas"] == "WARQ / SOC"
    assert item["nama_fasilitas"] == "Bandara Adi Soemarmo"
    assert item["panjang_runway_m"] == 2600.0
    assert "Wide Body" in item["status_kelayakan_vvip"]
    assert item["kabupaten_kota"] == "Boyolali"


def test_extractor_records_from():
    """Verify extractor payload flattening from ArcGIS MapServer."""
    ext = Extractor({"url": "https://example.com/arcgis/MapServer/4/query"})
    payload = {
        "features": [
            {"attributes": {"namobj": "Airport A"}, "geometry": {"x": 100.0, "y": -1.0}},
            {"attributes": {"namobj": "Airport B"}, "geometry": {"x": 105.0, "y": -2.0}}
        ]
    }
    records = ext._records_from(payload)
    assert len(records) == 2
    assert records[0]["namobj"] == "Airport A"
    assert records[0]["geometry"]["x"] == 100.0
