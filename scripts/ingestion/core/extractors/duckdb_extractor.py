"""DuckDB extractors — compatibility module.

The implementation now lives in :mod:`ingestion.core.extractors.duckdb`
(location, connection, numbers, Excel and JSON). This module keeps the public
import path used by sources and the scaffold stable.
"""

from __future__ import annotations

from .duckdb import (
    EXTENSIONS,
    HTTP,
    JSON_FORMATS,
    LOCAL,
    S3,
    DuckDBExcelExtractor,
    DuckDBJSONExtractor,
    Location,
    open_duckdb,
    parse_id_number,
    resolve_location,
)

__all__ = [
    "DuckDBExcelExtractor",
    "DuckDBJSONExtractor",
    "EXTENSIONS",
    "HTTP",
    "JSON_FORMATS",
    "LOCAL",
    "Location",
    "S3",
    "open_duckdb",
    "parse_id_number",
    "resolve_location",
]
