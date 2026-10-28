"""Extractor for Kemendag monthly exports by sector (Satu Data Perdagangan)."""

from __future__ import annotations

from typing import Any, Dict, Iterator

from .....core.base.extractor import BaseExtractor
from .. import satudata_exim

TABLE_ID = "example"
COLUMNS = {
    "total": "total_ekspor",
    "migas": "migas",
    "non migas": "nonmigas",
    "agriculture": "pertanian",
    "industry": "industri",
    "mining": "pertambangan",
    "others": "lainnya",
}


class Extractor(BaseExtractor):
    """Monthly export table (Juta US$) per year; ``YEARS`` limits the years."""

    def extract(self) -> Iterator[Dict[str, Any]]:
        yield from satudata_exim.iter_records(
            self.http,
            self.config.get("url") or satudata_exim.DEFAULT_URL,
            self.config.get("years") or self.config.get("tahun"),
            TABLE_ID,
            COLUMNS,
        )
