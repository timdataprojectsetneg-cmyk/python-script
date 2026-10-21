"""Extractor — Kemnaker Perusahaan Skala Upah Table 2.

Scaffolded from the catalog Data Access 'excel'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .._multiple_table import MultipleTableExtractor


class Extractor(MultipleTableExtractor):
    table_marker = "Tabel 2"