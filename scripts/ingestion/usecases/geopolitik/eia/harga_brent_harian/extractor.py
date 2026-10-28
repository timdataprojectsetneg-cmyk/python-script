"""EIA Brent spot price (RBRTE, daily) via the EIA Open Data API v2.

The published ``RBRTEd.xls`` needs the optional ``xlrd`` package, so the extractor
reads the same series (Thomson Reuters data) from the API instead:
https://api.eia.gov/v2/petroleum/pri/spt/data/
Config: ``url`` (endpoint), ``api_key`` (default ``DEMO_KEY``, rate limited),
``series`` (default ``RBRTE``), ``start`` (optional YYYY-MM-DD).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator, List

from .....core.base.extractor import BaseExtractor
from .....exceptions import AuthError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
DEFAULT_API_KEY = "DEMO_KEY"
DEFAULT_SERIES = "RBRTE"
SOURCE_VENDOR = "Thomson Reuters"
PAGE_SIZE = 5000


def check_payload(payload: Any, url: str = "") -> Dict[str, Any]:
    """Return ``payload['response']`` or raise on an EIA error envelope."""
    if not isinstance(payload, dict):
        raise SourceUnavailable(f"Unexpected EIA response from {url}")
    if payload.get("error"):
        message = str(payload.get("error"))
        if "api_key" in message.lower() or "api key" in message.lower():
            raise AuthError(f"EIA API key rejected: {message}")
        raise SourceUnavailable(f"EIA API error: {message}")
    response = payload.get("response")
    if not isinstance(response, dict):
        raise SourceUnavailable(f"EIA response without 'response' block from {url}")
    return response


def parse_rows(response: Dict[str, Any], series: str = DEFAULT_SERIES) -> List[Dict[str, Any]]:
    """Map EIA API rows to dictionary-named records, dropping empty prices."""
    rows: List[Dict[str, Any]] = []
    for item in response.get("data") or []:
        period = item.get("period")
        value = item.get("value")
        if not period or value in (None, "", "NA"):
            continue
        try:
            price = float(value)
        except (TypeError, ValueError):
            continue
        rows.append(
            {
                "day": str(period)[:10],
                "europe_brent_spot_price_fob_dollars_per_barrel": price,
                "series_id": item.get("series") or series,
                "source_vendor": SOURCE_VENDOR,
            }
        )
    return rows


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        url = self.config.get("url") or DEFAULT_URL
        series = str(self.config.get("series") or DEFAULT_SERIES)
        params: Dict[str, Any] = {
            "api_key": self.config.get("api_key") or DEFAULT_API_KEY,
            "frequency": "daily",
            "data[0]": "value",
            "facets[series][]": series,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "length": PAGE_SIZE,
        }
        if self.config.get("start"):
            params["start"] = self.config["start"]

        offset = 0
        total = None
        while True:
            resp = self.http.get(url, params={**params, "offset": offset}, timeout=60)
            try:
                payload = resp.json()
            except ValueError as exc:
                raise SourceUnavailable(f"EIA returned non-JSON from {url}") from exc
            response = check_payload(payload, url)
            if total is None:
                total = int(response.get("total") or 0)
            page = response.get("data") or []
            yield from parse_rows(response, series)
            offset += len(page)
            if not page or offset >= total:
                break
        if not total:
            raise SourceUnavailable(f"EIA returned no rows for series {series}")
