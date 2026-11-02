"""Extractor — Jumlah Karyawan: Tenaga Kerja Asing (CEIC TB88621)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88621"
