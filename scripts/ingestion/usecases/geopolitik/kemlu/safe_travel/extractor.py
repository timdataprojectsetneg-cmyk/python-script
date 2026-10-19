"""API Extractor for Kemlu RI Safe Travel Appeals.

Queries the official Kemlu Safe Travel endpoint:
https://safetravel.kemlu.go.id/api/appeal
Extracts official Indonesian diplomatic travel advisories, alerts, and notices for citizens abroad.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .....core.extractors.api_extractor import ApiExtractor

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://safetravel.kemlu.go.id/api/appeal"


class Extractor(ApiExtractor):
    """API extractor for Kemlu RI Safe Travel appeals."""

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
        headers.setdefault("Accept", "application/json, text/plain, */*")
        return headers

    def _records_from(self, payload: Any) -> List[Dict[str, Any]]:
        """Extract appeals records from Kemlu API response."""
        if isinstance(payload, list):
            logger.info("Extracted %d travel advisories from Kemlu Safe Travel API", len(payload))
            return payload
        elif isinstance(payload, dict):
            for key in ("data", "appeals", "items", "results"):
                if key in payload and isinstance(payload[key], list):
                    logger.info("Extracted %d travel advisories from payload['%s']", len(payload[key]), key)
                    return payload[key]
        logger.warning("Unrecognized Kemlu Safe Travel payload format: %s", type(payload))
        return []
