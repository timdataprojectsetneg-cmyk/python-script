"""Extractor for Indonesia's strategic-commodity imports by supplier (UN Comtrade preview API).

Partner rows come from the configured query; the Indonesian total per HS group
(partnerCode=0) is fetched with a second query and used as the share denominator.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .....core.base.extractor import BaseExtractor
from ..comtrade_preview import expand_periods, fetch_preview, to_record

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=360&period=2024"
    "&flowCode=M&cmdCode=10,27,72,85&partnerCode=156,840,392,458,702,356,36,410,276,764"
    "&motCode=0&partner2Code=0&customsCode=C00&maxRecords=100"
)

TotalKey = Tuple[str, Any, str]


def totals_url(url: str) -> str:
    """Same query as ``url`` but for the world total (partnerCode=0)."""
    return re.sub(r"partnerCode=[^&]*", "partnerCode=0", url)


def _key(row: Dict[str, Any]) -> TotalKey:
    return (str(row.get("period")), row.get("flowCode"), str(row.get("cmdCode")))


def _num(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url") or DEFAULT_URL
        self.timeout = int(config.get("timeout") or 60)

    def extract(self) -> Iterator[Dict[str, Any]]:
        for url in expand_periods(self.url, self.config.get("years")):
            yield from self._extract_one(url)

    def _extract_one(self, url: str) -> Iterator[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = fetch_preview(self.http, url, self.timeout)
        totals: Dict[TotalKey, float] = {
            _key(r): _num(r.get("primaryValue")) or 0.0 for r in rows if r.get("partnerCode") == 0
        }
        if not totals:
            for r in fetch_preview(self.http, totals_url(url), self.timeout):
                if r.get("partnerCode") == 0:
                    totals[_key(r)] = _num(r.get("primaryValue")) or 0.0
        logger.info("Comtrade preview: %d rows, %d HS totals", len(rows), len(totals))

        for row in rows:
            if row.get("partnerCode") == 0:
                continue
            rec = to_record(row)
            total = totals.get(_key(row))
            value = _num(row.get("primaryValue"))
            rec["totalCommodityValue"] = total
            rec["supplierShare"] = round(value / total, 6) if total and value is not None else None
            yield rec
