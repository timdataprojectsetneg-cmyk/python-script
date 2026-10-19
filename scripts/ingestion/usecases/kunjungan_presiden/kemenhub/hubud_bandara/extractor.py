"""API Extractor for Kemenhub / BIG Airport Infrastructure (Bandara).

Queries the official Badan Informasi Geospasial (BIG) Satupeta Sarana Prasarana MapServer:
https://kspservices.big.go.id/satupeta/rest/services/PUBLIK/SARANA_PRASARANA/MapServer/4/query
Extracts airport facilities, runway dimensions, PCN, operational hours, and aircraft ratings.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .....core.extractors.api_extractor import ApiExtractor

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://kspservices.big.go.id/satupeta/rest/services/PUBLIK/SARANA_PRASARANA/MapServer/4/query"
)


class Extractor(ApiExtractor):
    """API extractor for Kemenhub / BIG Airport Infrastructure."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("url", DEFAULT_URL)

        # Default ArcGIS query parameters
        default_params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "f": "json",
            "orderByFields": "namobj ASC",
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
        """Extract airport features and inject coordinates into record dict."""
        records: List[Dict[str, Any]] = []
        if not isinstance(payload, dict):
            return records

        features = payload.get("features", [])
        for feat in features:
            if isinstance(feat, dict):
                attrs = feat.get("attributes", {})
                geom = feat.get("geometry", {})
                rec = dict(attrs)
                rec["geometry"] = geom
                records.append(rec)

        logger.info("Extracted %d airport infrastructure records from BIG Satupeta", len(records))
        return records
