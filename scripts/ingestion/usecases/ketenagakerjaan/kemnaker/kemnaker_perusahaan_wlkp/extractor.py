"""Extractor — Kemnaker Perusahaan WLKP.

Scaffolded from the catalog Data Access 'excel'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .....core.extractors.excel_extractor import ExcelExtractor


class Extractor(ExcelExtractor):
    """Implemented per source; subclass the generic base and override as needed."""
