"""Extractor — Daftar Penyalur Badan Usaha Niaga Umum Bahan Bakar Minyak melalui selain di Stasiun Pengisian (Agen BBM Industri) – KBLI 47302 Semester I Tahun 2026.

Scaffolded from the catalog Data Access 'json'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .....core.extractors.duckdb_extractor import DuckDBJSONExtractor


class Extractor(DuckDBJSONExtractor):
    """Implemented per source; subclass the generic base and override as needed."""
