"""Extractor — Upah Rata-rata Bulanan: Bersih: Menurut Provinsi (CEIC TB132397)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB132397"
