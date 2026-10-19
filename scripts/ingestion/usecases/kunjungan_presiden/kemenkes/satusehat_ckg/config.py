"""Configuration for Kemenkes SATUSEHAT CKG Ingestion."""

import os
from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://satusehat.kemkes.go.id/platform/fhir-id/v1/Observation",
    "base_url": "https://ayockg.kemkes.go.id/",
    "client_id": os.environ.get("KUNJUNGAN_PRESIDEN__KEMENKES__SATUSEHAT_CKG__CLIENT_ID", ""),
    "client_secret": os.environ.get("KUNJUNGAN_PRESIDEN__KEMENKES__SATUSEHAT_CKG__CLIENT_SECRET", ""),
    "max_records": 50,
    "timeout": 20,
}
