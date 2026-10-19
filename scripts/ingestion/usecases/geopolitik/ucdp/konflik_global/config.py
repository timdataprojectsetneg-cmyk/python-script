"""Configuration for UCDP Konflik Global (Peta Konflik Bersenjata Global) Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_8.csv",
    "backup_url": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_7.csv",
    "max_records": 100,
    "timeout": 30,
}
