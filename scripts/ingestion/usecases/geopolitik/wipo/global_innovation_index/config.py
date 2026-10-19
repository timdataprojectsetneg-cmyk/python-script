"""Configuration for WIPO Global Innovation Index Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://www.wipo.int/en/web/global-innovation-index",
    "report_url": "https://www.wipo.int/edocs/pubdocs/en/wipo-pub-2000-2026-en-global-innovation-index-2026.pdf",
    "max_records": 50,
    "timeout": 20,
}
