"""Extractor — Tabel ID.GBA: Pengangguran: Menurut Usia (CEIC TB88628)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88628"
