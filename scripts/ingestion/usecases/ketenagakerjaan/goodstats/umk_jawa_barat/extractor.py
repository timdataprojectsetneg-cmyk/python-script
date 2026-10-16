"""Extractor — UMK Jawa Barat (GoodStats).

The UMK workbook lives in object storage (``s3://``) and is read with DuckDB
``read_xlsx`` through the shared GoodStats UMK extractor.
"""

from __future__ import annotations

from .._umk import UMKExtractor


class Extractor(UMKExtractor):
    """``Kabupaten/Kota`` + ``UMK <tahun>`` columns → the shared UMK model."""
