"""Extractor for World Bank country metadata (region, income group, capital, coordinates)."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator

from .....core.base.extractor import BaseExtractor
from ..wb_api import fetch_all

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://api.worldbank.org/v2/country?format=json&per_page=400"


def _label(obj: Any) -> Any:
    return obj.get("value") if isinstance(obj, dict) else obj


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url") or DEFAULT_URL
        self.timeout = int(config.get("timeout") or 60)

    def extract(self) -> Iterator[Dict[str, Any]]:
        for item in fetch_all(self.http, self.url, self.timeout):
            yield {
                "id": item.get("id"),
                "name": item.get("name"),
                "capitalCity": item.get("capitalCity"),
                "region": _label(item.get("region")),
                "incomeLevel": _label(item.get("incomeLevel")),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
            }
