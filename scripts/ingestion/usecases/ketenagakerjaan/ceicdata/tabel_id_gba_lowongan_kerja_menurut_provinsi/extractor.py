"""Extractor — Lowongan Kerja: Menurut Provinsi (CEIC TB88623)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88623"
