"""Extractor for Indonesia's export/import value by partner (UN Comtrade preview API)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator

from .....core.base.extractor import BaseExtractor
from ..comtrade_preview import expand_periods, fetch_preview, to_record

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=360&period=2024"
    "&flowCode=X,M&cmdCode=TOTAL&partnerCode=156,840,392,458,702,356,36,410,276,764"
    "&motCode=0&partner2Code=0&customsCode=C00&maxRecords=100"
)


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url") or DEFAULT_URL
        self.timeout = int(config.get("timeout") or 60)

    def extract(self) -> Iterator[Dict[str, Any]]:
        for url in expand_periods(self.url, self.config.get("years")):
            rows = fetch_preview(self.http, url, self.timeout)
            logger.info("Comtrade preview returned %d rows", len(rows))
            for row in rows:
                yield to_record(row)
