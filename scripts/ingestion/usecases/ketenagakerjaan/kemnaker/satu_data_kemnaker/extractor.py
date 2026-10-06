"""REST API access — Satu Data Kemnaker.

The ``list_data`` endpoint wraps its rows in a kemnaker envelope::

    {"status": 200, "message": "Success",
     "data": {"total": 3247, "data": [ {...}, ... ]}}

so the generic ``ApiExtractor`` (which looks for a top-level list) finds
nothing. This extractor unwraps ``data.data`` and paginates using ``total``.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator
from urllib.parse import parse_qsl, urlsplit

from .....core.extractors.api_extractor import ApiExtractor
from .....exceptions import SourceUnavailable


class Extractor(ApiExtractor):
    """Unwrap the kemnaker envelope and page through ``data.data``."""

    DEFAULT_PAGE_SIZE = 1000

    def _base_request(self) -> tuple:
        """Split the configured URL into a query-free base and its static params.

        ``requests`` appends ``params`` to the URL's existing query, so a URL that
        already carries ``page=1&limit=1000`` would shadow our pagination values.
        """
        parts = urlsplit(self.url or "")
        base = f"{parts.scheme}://{parts.netloc}{parts.path}"
        return base, dict(parse_qsl(parts.query))

    def _page_records(self, payload: Any) -> tuple:
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            return [], None
        records = data.get("data")
        if not isinstance(records, list):
            return [], data.get("total")
        return [item for item in records if isinstance(item, dict)], data.get("total")

    def extract(self) -> Iterator[Dict[str, Any]]:
        base, base_params = self._base_request()
        page = int(self.config.get("start_page", 1) or 1)
        page_size = int(self.config.get("page_size", self.DEFAULT_PAGE_SIZE) or self.DEFAULT_PAGE_SIZE)
        max_pages = int(self.config.get("max_pages", 0) or 0)

        seen = 0
        pages = 0
        while True:
            params = {**base_params, "page": page, "limit": page_size}
            resp = self.http.request(
                "GET", base, headers=self._headers(), params=params, timeout=60
            )
            try:
                payload = resp.json()
            except ValueError as exc:
                raise SourceUnavailable(f"Invalid JSON response from {self.url}") from exc

            records, total = self._page_records(payload)
            for record in records:
                yield record

            seen += len(records)
            pages += 1
            if not records or (max_pages and pages >= max_pages):
                break
            if isinstance(total, int) and seen >= total:
                break
            page += 1
