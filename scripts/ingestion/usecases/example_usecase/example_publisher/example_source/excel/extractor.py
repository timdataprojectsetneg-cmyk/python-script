"""Excel access for the example source (Kemnaker satudata pattern)."""

from __future__ import annotations

from typing import Any, Dict

from ......core.extractors.excel_extractor import ExcelExtractor

# CSS class of the download button on the landing page (varies per use case/source).
DOWNLOAD_SELECTOR = "bg-satudata-800"


class Extractor(ExcelExtractor):
    """Downloads the Excel file and yields raw rows."""

    def __init__(self, config: Dict[str, Any]):
        merged = dict(config)
        merged.setdefault("download_selector", DOWNLOAD_SELECTOR)
        super().__init__(merged)
