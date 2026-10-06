"""Excel access — Upah Minimum Provinsi (UMP).

Same satudata source as the other Kemnaker datasets; only the workbook layout
differs. The data sheet has a single header on Excel row 4 (0-based 3):
No | Provinsi | Upah Minimum (Rp).
"""

from __future__ import annotations

from typing import Any, Dict

from .._satudata import SatuDataExcelExtractor

SHEET = "data"
HEADER_ROW = 3
# Drop the aggregate 'Rata-Rata' row and the 'Sumber: ...' footer.
REQUIRE_COLUMNS = "Provinsi"
SKIP_ROW_PREFIXES = "sumber,rata-rata"


class Extractor(SatuDataExcelExtractor):
    """Resolve the UMP workbook URL from the satudata API, then parse its rows."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("sheet", SHEET)
        merged.setdefault("header_row", HEADER_ROW)
        merged.setdefault("require_columns", REQUIRE_COLUMNS)
        merged.setdefault("skip_row_prefixes", SKIP_ROW_PREFIXES)
        super().__init__(merged)
