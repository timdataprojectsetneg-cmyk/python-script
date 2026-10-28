"""FAO Food Price Index (monthly CSV).

The landing page links ``food_price_indices_data.csv`` with a rotating
``?sfvrsn=`` token, so the link is discovered from the page every run. A direct
``.csv`` ``url`` skips discovery.
"""

from __future__ import annotations

import csv
import io
import logging
import re
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin

from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.fao.org/worldfoodsituation/foodpricesindex/en/"
CSV_NAME = "food_price_indices_data.csv"
COLUMNS = ["date", "food_price_index", "meat", "dairy", "cereals", "oils", "sugar"]
_MONTH = re.compile(r"^\d{4}-\d{2}$")


def find_csv_link(html: str, base_url: str) -> Optional[str]:
    """Return the absolute URL of the FFPI CSV found on the landing page."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.find_all("a", href=True):
        if CSV_NAME in anchor["href"]:
            return urljoin(base_url, anchor["href"])
    return None


def _number(value: str) -> Optional[float]:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_csv(text: str) -> List[Dict[str, Any]]:
    """Skip the title/unit/blank rows; keep rows whose first cell is YYYY-MM."""
    rows: List[Dict[str, Any]] = []
    for cells in csv.reader(io.StringIO(text.lstrip("﻿"))):
        if not cells or not _MONTH.match(cells[0].strip()):
            continue
        padded = (cells + [""] * len(COLUMNS))[: len(COLUMNS)]
        record: Dict[str, Any] = {"date": padded[0].strip()}
        for name, value in zip(COLUMNS[1:], padded[1:]):
            record[name] = _number(value)
        rows.append(record)
    return rows


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        url = self.config.get("url") or DEFAULT_URL
        if ".csv" not in url.lower():
            page = self.http.get(url, timeout=60)
            link = find_csv_link(page.text, url)
            if not link:
                raise SourceUnavailable(f"No {CSV_NAME} link found on {url}")
            url = link
        logger.info("Downloading FAO FFPI CSV: %s", url)
        resp = self.http.get(url, timeout=120)
        rows = parse_csv(resp.content.decode("utf-8-sig", errors="replace"))
        if not rows:
            raise SourceUnavailable(f"FAO CSV at {url} contained no monthly rows")
        yield from rows
