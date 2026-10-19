"""Configuration for Kemenkop SIMKOPDES (Koperasi Desa Merah Putih) Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://simkopdes.go.id/",
    "api_provinces_url": "https://api.simkopdes.go.id/api/provinces",
    "max_records": 100,
    "timeout": 15,
}
