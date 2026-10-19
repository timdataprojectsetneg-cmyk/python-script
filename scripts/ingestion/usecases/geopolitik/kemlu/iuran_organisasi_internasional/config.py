"""Configuration for Kemlu Iuran Organisasi Internasional Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://satudata.kemlu.go.id/data/jumlah-keanggotaan-indonesia-dalam-oi",
    "portal_url": "https://kemlu.go.id",
    "max_records": 50,
    "timeout": 20,
}
