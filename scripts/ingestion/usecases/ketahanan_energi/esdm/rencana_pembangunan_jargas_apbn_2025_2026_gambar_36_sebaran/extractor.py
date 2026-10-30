"""Extractor — Gambar 33- Rencana Pembangunan Jargas APBN 2025-2026 , Gambar 36 Sebaran Kilang Minyak Bumi.

Scaffolded from the catalog Data Access 'json'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .....core.extractors.duckdb_extractor import DuckDBJSONExtractor


class Extractor(DuckDBJSONExtractor):
    """Implemented per source; subclass the generic base and override as needed."""
