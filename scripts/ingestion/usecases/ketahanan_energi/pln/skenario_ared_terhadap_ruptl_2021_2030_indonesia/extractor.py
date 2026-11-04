"""Extractor — PLN - Tabel 5.18 Perubahan RUPTL 2025 – 2034 Skenario ARED terhadap RUPTL 2021 – 2030 Indonesia.

Scaffolded from the catalog Data Access 'json'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .....core.extractors.duckdb_extractor import DuckDBJSONExtractor


class Extractor(DuckDBJSONExtractor):
    """Implemented per source; subclass the generic base and override as needed."""
