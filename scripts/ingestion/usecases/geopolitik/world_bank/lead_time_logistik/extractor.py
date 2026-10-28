"""Extractor for Indonesia's logistics lead times (World Bank LPI survey indicators).

The multi-indicator form of the catalog URL is rejected by the API without an
explicit ``source``, so each indicator code in the URL path is queried on its own.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List

from .....core.base.extractor import BaseExtractor
from ..wb_api import fetch_all

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://api.worldbank.org/v2/country/IDN/indicator/"
    "LP.IMP.DURS.MD;LP.EXP.DURS.MD?format=json&per_page=200"
)


def split_indicator_urls(url: str) -> List[str]:
    """Expand ``.../indicator/A;B?query`` into one URL per indicator."""
    match = re.match(r"^(.*?/indicator/)([^?]+)(\?.*)?$", url)
    if not match:
        return [url]
    prefix, codes, query = match.group(1), match.group(2), match.group(3) or ""
    return [f"{prefix}{code}{query}" for code in codes.split(";") if code]


def unit_of(indicator_name: str) -> str:
    match = re.search(r"\(([^)]+)\)\s*$", indicator_name or "")
    return match.group(1) if match else "days"


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url") or DEFAULT_URL
        self.timeout = int(config.get("timeout") or 60)

    def extract(self) -> Iterator[Dict[str, Any]]:
        for url in split_indicator_urls(self.url):
            for item in fetch_all(self.http, url, self.timeout):
                value = item.get("value")
                year = str(item.get("date") or "")
                if value is None or not year.isdigit():
                    continue
                indicator = item.get("indicator") or {}
                name = indicator.get("value")
                yield {
                    "indicator_code": indicator.get("id"),
                    "indicator_name": name,
                    "year": int(year),
                    "value": value,
                    "unit": unit_of(name),
                }
