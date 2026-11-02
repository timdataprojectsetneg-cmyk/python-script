"""Extractor — Survei Angkatan Kerja: Bekerja: Menurut Lapangan Usaha dan Provinsi: ISIC Rev.5 - KBLI 2025 (CEIC TB6799427)."""

from __future__ import annotations

from .._ceic import CeicTableExtractor


class Extractor(CeicTableExtractor):
    table_id = "TB6799427"
