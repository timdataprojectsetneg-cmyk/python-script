"""Extractor — Kemnaker Perusahaan Melapor PP Table 1.

Downloads the satudata workbook (dataset 3679) and takes ``Tabel 1`` (jumlah
perusahaan yang melaporkan PP menurut provinsi dan skala perusahaan) from every
monthly sheet; see ``kemnaker/_multiple_table.py`` for the shared parsing.
"""

from __future__ import annotations

from .._multiple_table import MultipleTableExtractor


class Extractor(MultipleTableExtractor):
    table_marker = "Tabel 1"
