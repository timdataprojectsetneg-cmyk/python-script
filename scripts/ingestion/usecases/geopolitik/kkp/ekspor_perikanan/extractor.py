"""Ekspor Perikanan KKP: nilai ekspor hasil perikanan per komoditas utama (USD 1.000).

The Portal Data KKP page (``.../exim/tbl-statis/d/156``) is a React SPA; its table
is served by a JSON endpoint on the ``/sttk`` backend:
``GET <origin>/sttk/api/static_table/view/detail?id=<id>``. The table id is taken
from the ``/d/<id>`` segment of the configured URL.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urlsplit

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://portaldata.kkp.go.id/portals/data-statistik/exim/tbl-statis/d/156"
API_PATH = "/sttk/api/static_table/view/detail"
YEAR_KEY = re.compile(r"^\d{4}$")


def table_id_from_url(url: str) -> str:
    match = re.search(r"/d/(\d+)", urlsplit(url).path)
    if not match:
        raise ConfigError(f"KKP URL must contain /d/<table id>: {url}")
    return match.group(1)


def parse_table(payload: Any) -> List[Dict[str, Any]]:
    """One record per commodity row: ``komoditas`` plus one key per year column."""
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise SourceUnavailable("KKP API returned an unexpected payload")
    rows: List[Dict[str, Any]] = []
    for item in payload["data"]:
        if not isinstance(item, dict):
            continue
        name: Optional[str] = None
        years: Dict[str, Any] = {}
        for key, value in item.items():
            if YEAR_KEY.match(str(key)):
                years[str(key)] = value
            elif name is None:
                name = " ".join(str(value or "").split()) or None
        if not name:
            continue
        rows.append({"komoditas": name, **years})
    return rows


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        page_url = self.url or DEFAULT_URL
        parts = urlsplit(page_url)
        origin = f"{parts.scheme}://{parts.netloc}"
        resp = self.http.get(
            origin + API_PATH,
            params={"id": table_id_from_url(page_url)},
            headers={"Accept": "application/json", "Referer": page_url},
            timeout=60,
        )
        try:
            payload = resp.json()
        except ValueError as exc:
            raise SourceUnavailable(f"KKP API returned non-JSON for {page_url}") from exc
        rows = parse_table(payload)
        if not rows:
            raise SourceUnavailable(f"KKP table {page_url} has no rows")
        logger.info("KKP %s: %d rows", payload.get("judul"), len(rows))
        yield from rows
