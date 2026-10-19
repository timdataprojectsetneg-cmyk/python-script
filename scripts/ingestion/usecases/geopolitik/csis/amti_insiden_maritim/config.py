"""Configuration for CSIS AMTI Insiden Maritim Indo-Pasifik Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://amti.csis.org/tracker/",
    "base_url": "https://amti.csis.org/",
    "max_records": 50,
    "timeout": 20,
}
