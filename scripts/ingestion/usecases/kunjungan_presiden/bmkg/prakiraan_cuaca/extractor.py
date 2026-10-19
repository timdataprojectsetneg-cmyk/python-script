"""API Extractor for BMKG Prakiraan Cuaca.

Fetches 3-hourly weather forecast data per village/subdistrict (adm4)
from the official BMKG open API (api.bmkg.go.id).
Flattens the nested lokasi and cuaca hierarchies into flat records matching the schema.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .....core.extractors.api_extractor import ApiExtractor

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=31.71.03.1001"


class Extractor(ApiExtractor):
    """API extractor for BMKG Prakiraan Cuaca."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("url", DEFAULT_URL)
        super().__init__(merged)

    def _headers(self) -> Dict[str, str]:
        headers = super()._headers()
        headers.setdefault(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        headers.setdefault("Referer", "https://www.bmkg.go.id/")
        headers.setdefault("Accept", "application/json, text/plain, */*")
        return headers

    def _records_from(self, payload: Any) -> List[Dict[str, Any]]:
        """Flatten BMKG's nested lokasi and cuaca array into flat records."""
        records: List[Dict[str, Any]] = []
        if not isinstance(payload, dict):
            return records

        top_lokasi = payload.get("lokasi", {})
        data_list = payload.get("data", [])

        if not data_list and top_lokasi:
            # Fallback if cuaca is at top level
            data_list = [payload]

        for entry in data_list:
            if not isinstance(entry, dict):
                continue
            entry_lokasi = entry.get("lokasi") or top_lokasi
            cuaca_days = entry.get("cuaca", [])

            for day_data in cuaca_days:
                if isinstance(day_data, list):
                    for item in day_data:
                        if isinstance(item, dict):
                            rec = {**entry_lokasi, **item}
                            records.append(rec)
                elif isinstance(day_data, dict):
                    rec = {**entry_lokasi, **day_data}
                    records.append(rec)

        logger.info("Extracted %d forecast records from BMKG API", len(records))
        return records
