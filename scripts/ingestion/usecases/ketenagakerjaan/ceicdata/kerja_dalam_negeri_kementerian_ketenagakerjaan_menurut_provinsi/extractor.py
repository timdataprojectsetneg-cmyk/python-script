"""Extractor — Penempatan Kerja: Dalam Negeri: Kementerian Ketenagakerjaan: Menurut Provinsi (CEIC TB88637)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB88637"
