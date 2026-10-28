"""Shared helper for the World Bank Open Data v2 JSON API."""

from __future__ import annotations

from typing import Any, Dict, Iterator

from ....core.base.http import HttpClient
from ....exceptions import SourceUnavailable


def fetch_all(http: HttpClient, url: str, timeout: int = 60) -> Iterator[Dict[str, Any]]:
    """Yield every row of a v2 ``format=json`` query, following pagination."""
    page = 1
    while True:
        resp = http.get(url, params={"page": page} if page > 1 else None, timeout=timeout)
        payload = resp.json()
        if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
            detail = payload[0] if isinstance(payload, list) and payload else payload
            raise SourceUnavailable(f"World Bank API returned no data for {url}: {detail}")
        meta, rows = payload[0], payload[1]
        yield from rows
        if page >= int(meta.get("pages") or 1):
            return
        page += 1
