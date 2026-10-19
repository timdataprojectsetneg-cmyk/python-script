"""Configuration for Setpres Pertemuan Bilateral Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://www.setneg.go.id/baca/index/kunjungan_kenegaraan",
    "portal_url": "https://www.presidenri.go.id/siaran-pers/",
    "max_records": 50,
    "timeout": 20,
}
