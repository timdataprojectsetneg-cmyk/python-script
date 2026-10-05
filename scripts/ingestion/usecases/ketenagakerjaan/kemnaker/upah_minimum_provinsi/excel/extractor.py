"""Excel access — Upah Minimum Provinsi (UMP)."""

from __future__ import annotations

from ......core.extractors.excel_extractor import ExcelExtractor


class Extractor(ExcelExtractor):
    """Implemented per source; falls back to the generic excel extractor."""
