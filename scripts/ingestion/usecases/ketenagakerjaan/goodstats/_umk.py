"""Shared extractor for the GoodStats ``umk_*`` sources.

Every ``umk_<provinsi>`` source is an Excel file in object storage with the same
two columns — ``Kabupaten/Kota`` and ``UMK <tahun>`` (e.g. ``UMK 2026``) — so they
all reuse this class. Rows are read by
:class:`~ingestion.core.extractors.duckdb_extractor.DuckDBExcelExtractor` (DuckDB
``read_xlsx`` over S3/MinIO) and mapped here to the shared model:
``kabupaten_kota``, ``umk`` (int, ``Rp``/thousand separators stripped) and
``tahun`` (taken from the ``UMK <tahun>`` header, else the file name).
"""

from __future__ import annotations

import re
from typing import Any, Dict

from ....core.extractors.duckdb_extractor import DuckDBExcelExtractor

_NON_DIGIT = re.compile(r"\D")
_YEAR = re.compile(r"(20\d{2})")


class UMKExtractor(DuckDBExcelExtractor):
    """``Kabupaten/Kota`` + ``UMK <tahun>`` columns → the UMK model fields."""

    def transform_row(self, record: Dict[str, Any]) -> Dict[str, Any]:
        mapped: Dict[str, Any] = {}
        for label, value in record.items():
            key = str(label).strip().lower()
            if key.startswith("kabupaten"):
                mapped["kabupaten_kota"] = _clean(value)
            elif key.startswith("umk"):
                mapped["umk"] = _to_int(value)
                year = _YEAR.search(str(label))
                if year:
                    mapped["tahun"] = int(year.group(1))
        if mapped.get("tahun") is None:
            year = _YEAR.search(str(self.config.get("url") or ""))
            if year:
                mapped["tahun"] = int(year.group(1))
        return mapped


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip() or None


def _to_int(value: Any) -> int | None:
    """``'Rp4.162.965'`` → ``4162965`` (drops currency symbols/separators)."""
    if value is None:
        return None
    digits = _NON_DIGIT.sub("", str(value))
    return int(digits) if digits else None
