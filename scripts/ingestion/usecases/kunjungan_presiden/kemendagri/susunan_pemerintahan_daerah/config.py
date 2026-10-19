"""Configuration for Kemendagri Susunan Pemerintahan Daerah Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://otda.kemendagri.go.id/",
    "pelita_url": "https://pelita.kemendagri.go.id/pemda",
    "max_records": 100,
    "timeout": 15,
}
