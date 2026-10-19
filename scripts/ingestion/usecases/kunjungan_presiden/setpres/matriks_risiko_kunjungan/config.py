"""Configuration for Setpres Matriks Risiko Kunjungan Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://www.setneg.go.id/baca/index/kunjungan_kenegaraan",
    "regulasi_url": "https://www.peraturan.go.id/files/uu9-2010bt.pdf",
    "max_records": 50,
    "timeout": 20,
}
