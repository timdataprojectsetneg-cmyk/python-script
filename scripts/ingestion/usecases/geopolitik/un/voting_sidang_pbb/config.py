"""Configuration for UN Voting Sidang PBB Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://digitallibrary.un.org/search?ln=en&cc=Voting+Data",
    "portal_url": "https://digitallibrary.un.org/",
    "max_records": 50,
    "timeout": 20,
}
