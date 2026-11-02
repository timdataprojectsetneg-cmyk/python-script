"""Extractor — Survei Angkatan Kerja: Pengangguran: Menurut Tingkat Pendidikan (CEIC TB132402)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB132402"
