"""Configuration for AirNav NOTAM & Kesiapan Evakuasi WNI Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://pia.airnavindonesia.co.id/",
    "faa_url": "https://notams.aim.faa.gov/notamSearch/",
    "max_records": 100,
    "timeout": 20,
}
