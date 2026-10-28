"""Extractor for the World Bank Commodity Price Data ("Pink Sheet"), monthly sheet.

The workbook lives behind a content-hashed ``thedocs.worldbank.org`` URL that
changes on revisions; if the configured URL fails, the current link is scraped
from the commodity-markets landing page.
"""

from __future__ import annotations

import io
import logging
import re
from typing import Any, Dict, Iterator, List, Optional

from openpyxl import load_workbook

from .....core.base.extractor import BaseExtractor
from .....exceptions import AuthError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026"
    "/related/CMO-Historical-Data-Monthly.xlsx"
)
DEFAULT_PAGE_URL = "https://www.worldbank.org/en/research/commodity-markets"
SHEET_NAME = "Monthly Prices"
PERIOD_RE = re.compile(r"^(\d{4})M(\d{2})$")
LINK_RE = re.compile(r"https://thedocs\.worldbank\.org/[^\"'\s<>]*CMO-Historical-Data-Monthly\.xlsx")
MISSING = {"", "…", "...", "..", "-", "NA", "n/a"}


def parse_price(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text in MISSING:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def parse_monthly_prices(content: bytes, start_year: Optional[int] = None) -> Iterator[Dict[str, Any]]:
    """Melt the wide "Monthly Prices" sheet into (periode, komoditas, harga, satuan) rows."""
    wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    try:
        ws = wb[SHEET_NAME]
        names: List[Any] = []
        units: List[Any] = []
        history: List[tuple] = []
        for row in ws.iter_rows(values_only=True):
            label = str(row[0]).strip() if row and row[0] is not None else ""
            match = PERIOD_RE.match(label)
            if not match:
                history.append(row)
                continue
            if not names:
                if len(history) < 2:
                    raise SourceUnavailable(f"Unexpected layout in sheet '{SHEET_NAME}'")
                names, units = list(history[-2]), list(history[-1])
            year = int(match.group(1))
            if start_year and year < start_year:
                continue
            periode = f"{match.group(1)}-{match.group(2)}"
            for idx, name in enumerate(names):
                if idx == 0 or name is None or not str(name).strip():
                    continue
                unit = units[idx] if idx < len(units) else None
                yield {
                    "Periode": periode,
                    "Komoditas": " ".join(str(name).split()),
                    "Harga": parse_price(row[idx] if idx < len(row) else None),
                    "Satuan": str(unit).strip() if unit is not None else None,
                }
    finally:
        wb.close()


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url") or DEFAULT_URL
        self.page_url = config.get("source_link") or DEFAULT_PAGE_URL
        self.timeout = int(config.get("timeout") or 120)
        start = config.get("start_year")
        self.start_year = int(start) if start else None

    def _download(self) -> bytes:
        try:
            return self.http.get(self.url, timeout=self.timeout).content
        except (SourceUnavailable, AuthError) as exc:
            logger.warning("Configured CMO URL failed (%s); resolving link from %s", exc, self.page_url)
        page = self.http.get(self.page_url, timeout=self.timeout).text
        match = LINK_RE.search(page)
        if not match:
            raise SourceUnavailable(f"CMO-Historical-Data-Monthly.xlsx link not found on {self.page_url}")
        logger.info("Resolved CMO workbook: %s", match.group(0))
        return self.http.get(match.group(0), timeout=self.timeout).content

    def extract(self) -> Iterator[Dict[str, Any]]:
        yield from parse_monthly_prices(self._download(), self.start_year)
