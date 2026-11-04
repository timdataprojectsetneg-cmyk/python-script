"""Extractor — Tabel 5.52 Daftar Kebutuhan Infrastruktur untuk mendukung Program Anti Blackout.

Scaffolded from the catalog Data Access 'json'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .....core.extractors.duckdb_extractor import DuckDBJSONExtractor


class Extractor(DuckDBJSONExtractor):
    """Implemented per source; subclass the generic base and override as needed."""
