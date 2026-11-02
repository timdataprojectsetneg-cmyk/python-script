"""Extractor — Upah Rata-rata Bulanan: Menurut Industri (CEIC TB88620)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88620"
