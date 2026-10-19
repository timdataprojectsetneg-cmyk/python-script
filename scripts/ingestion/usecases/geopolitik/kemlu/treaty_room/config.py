"""Configuration for Kemlu Treaty Room (Perjanjian Internasional RI) Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://treaty.kemlu.go.id/",
    "portal_url": "https://kemlu.go.id/",
    "max_records": 100,
    "timeout": 20,
}
