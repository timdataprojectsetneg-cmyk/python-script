"""Manual JSON access — BPS Inflasi YoY.

The catalog's Resource URL points to a curated JSON file, so read it with
DuckDB instead of scraping the BPS page.
"""

from __future__ import annotations

from typing import Any, Dict

from .....core.extractors.duckdb_extractor import DuckDBJSONExtractor


class Extractor(DuckDBJSONExtractor):
    """Read the curated BPS inflation JSON from S3/local."""

    def transform_row(self, record: Dict[str, Any]) -> Dict[str, Any]:
        # The curated file uses tanggal/nilai; the model uses the dictionary
        # aliases Periode/Inflasi_YoY.
        if "tanggal" in record or "nilai" in record:
            record = dict(record)
            if "tanggal" in record:
                tanggal = record["tanggal"]
                if hasattr(tanggal, "isoformat"):
                    tanggal = tanggal.isoformat()
                record.setdefault("Periode", tanggal)
            if "nilai" in record:
                record.setdefault("Inflasi_YoY", record["nilai"])
        return record
