"""Configuration for Setkab Tracking Arahan Lapangan Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://setkab.go.id/kategori/berita/",
    "portal_url": "https://setkab.go.id/",
    "max_records": 50,
    "timeout": 20,
}
