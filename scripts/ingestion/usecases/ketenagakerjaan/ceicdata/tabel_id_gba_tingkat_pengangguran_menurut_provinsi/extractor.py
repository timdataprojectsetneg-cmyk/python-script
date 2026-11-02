"""Extractor — Tingkat Pengangguran: Menurut Provinsi (CEIC TB88627)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88627"
