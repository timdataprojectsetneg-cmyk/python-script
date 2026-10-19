"""Configuration for Kemlu Sebaran WNI & PMI Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://satudata.kemlu.go.id/data/jumlah-persebaran-wni-lapor-diri-2018-2025",
    "portal_url": "https://satudata.kemlu.go.id/",
    "max_records": 100,
    "timeout": 20,
}
