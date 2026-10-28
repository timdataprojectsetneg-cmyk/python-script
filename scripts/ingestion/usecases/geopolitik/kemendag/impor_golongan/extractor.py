"""Extractor for Kemendag monthly imports by economic category (Satu Data Perdagangan)."""

from __future__ import annotations

from typing import Any, Dict, Iterator

from .....core.base.extractor import BaseExtractor
from .. import satudata_exim

TABLE_ID = "impor"
COLUMNS = {
    "total": "total_impor",
    "consumption goods": "barang_konsumsi",
    "raw material support": "bahan_baku_penolong",
    "capital goods": "barang_modal",
}


class Extractor(BaseExtractor):
    """Monthly import table (Juta US$) per year; ``YEARS`` limits the years."""

    def extract(self) -> Iterator[Dict[str, Any]]:
        yield from satudata_exim.iter_records(
            self.http,
            self.config.get("url") or satudata_exim.DEFAULT_URL,
            self.config.get("years") or self.config.get("tahun"),
            TABLE_ID,
            COLUMNS,
        )
