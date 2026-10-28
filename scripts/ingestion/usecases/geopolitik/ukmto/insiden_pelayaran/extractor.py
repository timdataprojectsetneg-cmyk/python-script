"""UKMTO recent incidents (sccd.royalnavy.mod.uk API).

The API answers 403 to plain HTTP clients; it needs a browser TLS fingerprint,
so ``impersonate`` defaults to ``chrome`` (curl_cffi) and Referer/Origin point to
ukmto.org.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List

from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://sccd.royalnavy.mod.uk/api/ukmto/all"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.ukmto.org/",
    "Origin": "https://www.ukmto.org",
}


def parse_incidents(payload: Any) -> List[Dict[str, Any]]:
    """Lower-case the API keys so they match the dictionary column names."""
    if isinstance(payload, dict):
        payload = payload.get("incidents") or payload.get("data") or []
    if not isinstance(payload, list):
        raise SourceUnavailable("UKMTO API returned an unexpected payload")
    rows: List[Dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        row = {str(key).lower(): value for key, value in item.items()}
        if not row.get("sitecoreid"):
            continue
        rows.append(row)
    return rows


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        if not merged.get("impersonate"):
            merged["impersonate"] = "chrome"
        super().__init__(merged)

    def extract(self) -> Iterator[Dict[str, Any]]:
        url = self.config.get("url") or DEFAULT_URL
        resp = self.http.get(url, headers=HEADERS, timeout=60)
        try:
            payload = resp.json()
        except ValueError as exc:
            raise SourceUnavailable(f"UKMTO returned non-JSON from {url}") from exc
        rows = parse_incidents(payload)
        if not rows:
            raise SourceUnavailable(f"UKMTO returned no incidents from {url}")
        logger.info("UKMTO returned %d incidents", len(rows))
        yield from rows
