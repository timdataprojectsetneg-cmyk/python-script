"""Extractor — Survei Angkatan Kerja: Tingkat Partisipasi (CEIC TB88619)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88619"
