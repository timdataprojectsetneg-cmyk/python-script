"""Extractor — Survei Angkatan Kerja: Pekerja Formal dan Informal: Menurut Provinsi (CEIC TB6320767)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB6320767"
