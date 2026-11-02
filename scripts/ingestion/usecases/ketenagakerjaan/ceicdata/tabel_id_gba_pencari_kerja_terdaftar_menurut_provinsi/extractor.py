"""Extractor — Pencari Kerja Terdaftar: Menurut Provinsi (CEIC TB88622)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88622"
