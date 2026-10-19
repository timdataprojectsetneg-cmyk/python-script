"""API Extractor for IMF PortWatch Daily Chokepoints.

Queries the official IMF PortWatch ArcGIS FeatureServer endpoint:
https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query
Extracts maritime transit call statistics for strategic global chokepoints
(Suez Canal, Bab el-Mandeb, Malacca Strait, Strait of Hormuz, etc.).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .....core.extractors.api_extractor import ApiExtractor

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query"
)


class Extractor(ApiExtractor):
    """API extractor for IMF PortWatch Daily Chokepoints."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("url", DEFAULT_URL)
        # Setup default ArcGIS query params
        default_params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
            "orderByFields": "date DESC",
        }
        if "params" in merged and isinstance(merged["params"], dict):
            merged["params"] = {**default_params, **merged["params"]}
        else:
            merged["params"] = default_params

        super().__init__(merged)

    def _headers(self) -> Dict[str, str]:
        headers = super()._headers()
        headers.setdefault(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        headers.setdefault("Accept", "application/json, text/plain, */*")
        return headers

    def _records_from(self, payload: Any) -> List[Dict[str, Any]]:
        """Extract attributes from ArcGIS features array."""
        records: List[Dict[str, Any]] = []
        if not isinstance(payload, dict):
            return records

        features = payload.get("features", [])
        for feat in features:
            if isinstance(feat, dict):
                attrs = feat.get("attributes")
                if isinstance(attrs, dict):
                    records.append(attrs)

        logger.info("Extracted %d chokepoint transit records from IMF PortWatch", len(records))
        return records
