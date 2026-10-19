"""Configuration for Kemlu Rekapitulasi Kasus WNI Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://peduliwni.kemlu.go.id/",
    "portal_url": "https://kemlu.go.id/portal/en/read/siaran_pers/index",
    "max_records": 100,
    "timeout": 20,
}
