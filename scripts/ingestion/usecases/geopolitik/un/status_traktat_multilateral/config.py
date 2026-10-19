"""Configuration for UN Status Traktat Multilateral Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://treaties.un.org/Pages/ParticipationStatus.aspx?clang=_en",
    "portal_url": "https://treaties.un.org/",
    "max_records": 50,
    "timeout": 20,
}
