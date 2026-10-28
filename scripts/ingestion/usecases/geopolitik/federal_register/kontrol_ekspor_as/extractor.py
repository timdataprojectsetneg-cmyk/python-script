"""Kontrol Ekspor AS: BIS (Bureau of Industry and Security) rules from the Federal Register API.

Public documented API: ``https://www.federalregister.gov/api/v1/documents.json``, filtered to
agency ``industry-and-security-bureau`` and document type ``RULE``, newest first. Optional
keys: ``PAGE_SIZE`` (default 100), ``MAX_PAGES`` (default unlimited; debug cap), ``PUBLICATION_DATE_GTE``
(YYYY-MM-DD) and ``AGENCY`` (default ``industry-and-security-bureau``). All pages are followed;
when a query passes the API's 10,000-result window, the query restarts from the oldest date seen.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List, Optional, Set

from .....config import get as env_get
from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable
from .config import PUBLISHER, SOURCE

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.federalregister.gov/api/v1/documents.json"
DEFAULT_AGENCY = "industry-and-security-bureau"
DEFAULT_PAGE_SIZE = 100
API_RESULT_WINDOW = 10000
FIELDS = ["title", "publication_date", "html_url", "effective_on"]
DOCUMENT_NUMBER_RE = re.compile(r"/documents/\d{4}/\d{2}/\d{2}/([^/?#]+)")


def document_number_from_url(html_url: Optional[str]) -> Optional[str]:
    match = DOCUMENT_NUMBER_RE.search(html_url or "")
    return match.group(1) if match else None


def parse_result(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Map one API result to the dictionary fields (+ derived document_number / is_correction)."""
    html_url = item.get("html_url")
    number = document_number_from_url(html_url)
    if not number:
        logger.warning("Federal Register result without document number skipped: %s", html_url)
        return None
    return {
        "title": item.get("title"),
        "publication_date": item.get("publication_date"),
        "effective_on": item.get("effective_on"),
        "html_url": html_url,
        "document_number": number,
        "is_correction": number.upper().startswith("C1-"),
    }


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = (config.get("url") or DEFAULT_URL).split("?")[0]
        if self.base_url.rstrip("/").endswith("/documents"):
            self.base_url = self.base_url.rstrip("/") + ".json"
        self.page_size = int(self._opt("page_size", DEFAULT_PAGE_SIZE))
        max_pages = int(self._opt("max_pages", 0))
        self.max_pages = max_pages if max_pages > 0 else None

    def _opt(self, key: str, default: Any = None) -> Any:
        value = self.config.get(key.lower())
        if value in (None, ""):
            value = env_get(self.config.get("usecase", "geopolitik"), PUBLISHER, SOURCE, key.upper())
        return default if value in (None, "") else value

    def build_params(self, page: int, date_lte: Optional[str] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "conditions[agencies][]": self._opt("agency", DEFAULT_AGENCY),
            "conditions[type][]": "RULE",
            "fields[]": FIELDS,
            "order": "newest",
            "per_page": self.page_size,
            "page": page,
        }
        gte = self._opt("publication_date_gte")
        if gte:
            params["conditions[publication_date][gte]"] = gte
        if date_lte:
            params["conditions[publication_date][lte]"] = date_lte
        return params

    def extract(self) -> Iterator[Dict[str, Any]]:
        seen: Set[str] = set()
        date_lte: Optional[str] = None
        fetched = 0
        page = 0
        last_date: Optional[str] = None
        while self.max_pages is None or fetched < self.max_pages:
            page += 1
            fetched += 1
            resp = self.http.get(self.base_url, params=self.build_params(page, date_lte), timeout=60)
            try:
                payload = resp.json()
            except ValueError as exc:
                raise SourceUnavailable(f"Federal Register returned non-JSON response: {exc}") from exc
            if "results" not in payload:
                raise SourceUnavailable("Federal Register response has no 'results' (API contract changed?)")
            results: List[Dict[str, Any]] = payload["results"] or []
            for item in results:
                row = parse_result(item)
                if row is not None and row["document_number"] not in seen:
                    seen.add(row["document_number"])
                    last_date = row["publication_date"] or last_date
                    yield row
            if not results or page >= int(payload.get("total_pages") or 0):
                return
            if page * self.page_size >= API_RESULT_WINDOW and last_date:
                date_lte, page = last_date, 0
        logger.warning("Federal Register: stopped at MAX_PAGES=%s; unset MAX_PAGES to fetch the rest", self.max_pages)
