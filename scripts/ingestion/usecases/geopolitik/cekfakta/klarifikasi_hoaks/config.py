"""Configuration for CekFakta Klarifikasi Hoaks Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://cekfakta.com/",
    "komdigi_url": "https://komdigi.go.id/kategori/isu-hoaks",
    "kemlu_url": "https://kemlu.go.id/berita/siaran-pers",
    "max_records": 50,
    "timeout": 20,
}
