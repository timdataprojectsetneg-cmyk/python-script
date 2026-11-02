"""Extractor — Survei Angkatan Kerja: Pengangguran: Menurut Umur (CEIC TB132400)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB132400"
