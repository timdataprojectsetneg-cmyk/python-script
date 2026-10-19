"""Configuration for GDELT Media Asing Ingestion."""

from typing import Any, Dict

CONFIG: Dict[str, Any] = {
    "url": "https://api.gdeltproject.org/api/v2/doc/doc?query=Indonesia%20(geopolitics%20OR%20diplomacy%20OR%20ASEAN%20OR%20nickel%20OR%20trade)%20sourcelang%3Aenglish&mode=artlist&format=json&maxrecords=50&sort=datedesc",
    "base_url": "https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/",
    "max_records": 50,
    "timeout": 20,
}
