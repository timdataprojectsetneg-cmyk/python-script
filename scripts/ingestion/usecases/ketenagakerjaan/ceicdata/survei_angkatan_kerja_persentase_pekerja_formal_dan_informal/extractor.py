"""Extractor — Survei Angkatan Kerja: Persentase Pekerja Formal dan Informal: Menurut Provinsi (CEIC TB5969657)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB5969657"
