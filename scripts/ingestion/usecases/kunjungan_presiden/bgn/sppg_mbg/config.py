"""Configuration for BGN SPPG MBG Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://gina.bgn.go.id/api/v1/sppg",
    "base_url": "https://www.bgn.go.id/",
    "max_records": 50,
    "timeout": 20,
}
