"""Extractor — Penempatan Kerja: Luar Negeri (CEIC TB88649)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88649"
