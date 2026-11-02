"""Extractor — Rata-rata Jam Bekerja Mingguan: Menurut Industri (CEIC TB88636)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88636"
