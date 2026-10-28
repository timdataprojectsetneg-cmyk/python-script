"""DuckDB-backed extractors for Excel and JSON.

The public compatibility module remains
:mod:`ingestion.core.extractors.duckdb_extractor`; this package contains the
implementation split by concern:

- ``location.py``   local/S3/HTTP detection
- ``connection.py`` DuckDB extensions and MinIO/S3 settings
- ``numbers.py``    Indonesian number parsing
- ``excel.py``      DuckDBExcelExtractor
- ``json.py``       DuckDBJSONExtractor
"""

from __future__ import annotations

from .connection import EXTENSIONS, open_duckdb
from .excel import DuckDBExcelExtractor
from .json import JSON_FORMATS, DuckDBJSONExtractor
from .location import HTTP, LOCAL, S3, Location, resolve_location
from .numbers import parse_id_number

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
