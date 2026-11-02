"""Extractor — Jumlah Karyawan: Pemutusan Hubungan Kerja (CEIC TB88655)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88655"
