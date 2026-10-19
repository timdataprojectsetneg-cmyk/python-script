"""Configuration for GDELT Sentimen Wilayah Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": (
        "https://api.gdeltproject.org/api/v2/doc/doc?"
        "query=Indonesia%20(MBG%20OR%20koperasi%20OR%20stunting)&mode=artlist&format=json&maxrecords=50&sort=datedesc"
    ),
    "base_url": "https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/",
    "max_records": 50,
    "timeout": 20,
}
