"""Extractor — Kemnaker Perusahaan WLKP.

Same satudata source (dataset 3677) as the other Kemnaker datasets; only the
workbook layout differs. The ``Data`` sheet has a two-row header (Excel rows
4-5): No. | Provinsi | Skala Perusahaan (Mikro/Kecil/Menengah/Besar/Belum
Teridentifikasi) | Jumlah. Parsing reuses the generic ``excel_automation`` engine
(output ``data``), whose wide table already flattens the merged header.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator

from .....core.extractors.excel_automation import extract_workbook, tables_to_records
from .._satudata import SatuDataExcelExtractor


class Extractor(SatuDataExcelExtractor):
    """Resolve the WLKP workbook URL from the satudata API, then parse it."""

    def extract(self) -> Iterator[Dict[str, Any]]:
        content = self._download(self._resolve_download_url()).content
        result = extract_workbook(content, outputs=["data"], profile=False, relations=False)
        for records in tables_to_records(result.tables).values():
            yield from records
