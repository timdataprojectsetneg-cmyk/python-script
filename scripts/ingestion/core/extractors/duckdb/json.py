"""JSON / NDJSON extraction with DuckDB ``read_json``."""

from __future__ import annotations

from typing import Any, Dict, Iterator, List

from ....exceptions import ConfigError
from .connection import open_duckdb
from .excel import DuckDBExcelExtractor
from .location import Location, resolve_location
from .numbers import parse_id_number, plain
from .sql import as_bool, ident, literal

JSON_FORMATS = ("auto", "array", "newline_delimited", "unstructured")


class DuckDBJSONExtractor(DuckDBExcelExtractor):
    """Yield records from JSON / NDJSON read with DuckDB ``read_json``.

    The source can be a local file (mac/Windows/Linux), ``s3://`` / ``minio://``
    or ``http(s)://``. Each row is yielded as ``Dict[str, Any]`` with native
    Python types (``int``, ``float``, ``str``, ``None``; nested objects/arrays as
    ``dict``/``list``), which is what ``PostgresLoader.load`` expects.
    """

    batch_size = 5000

    def location(self) -> Location:
        return resolve_location(self.config.get("url") or self.config.get("path"))

    def reference(self) -> str:  # keep the parent's API, now location-aware
        return self.location().uri

    def read_json_sql(self, ref: str) -> str:
        options: List[str] = []

        json_format = str(self.config.get("json_format") or "").strip().lower()
        if json_format:
            if json_format not in JSON_FORMATS:
                raise ConfigError(f"json_format must be one of {', '.join(JSON_FORMATS)}")
            options.append(f"format={literal(json_format)}")

        records = str(self.config.get("records") or "").strip().lower()
        if records:
            if records not in ("auto", "true", "false"):
                raise ConfigError("records must be 'auto', 'true' or 'false'")
            options.append(f"records={literal(records)}")

        for key in ("sample_size", "maximum_object_size"):
            if self.config.get(key) not in (None, ""):
                try:
                    options.append(f"{key}={int(self.config[key])}")
                except (TypeError, ValueError) as exc:
                    raise ConfigError(f"{key} must be an integer") from exc

        if as_bool(self.config.get("union_by_name"), False):
            options.append("union_by_name=true")
        if as_bool(self.config.get("ignore_errors"), False):
            options.append("ignore_errors=true")

        suffix = ", " + ", ".join(options) if options else ""
        base = f"read_json({literal(ref)}{suffix})"

        root = str(self.config.get("root") or "").strip()
        if root:
            return f"SELECT r.* FROM (SELECT UNNEST({ident(root)}) AS r FROM {base})"
        return f"SELECT * FROM {base}"

    def apply_numbers(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ``number_columns`` from Indonesian text to float/None."""
        raw = self.config.get("number_columns")
        if isinstance(raw, (list, tuple)):
            names = [str(item).strip() for item in raw]
        else:
            names = [item.strip() for item in str(raw or "").split(",")]
        for name in filter(None, names):
            if name in record:
                record[name] = parse_id_number(record[name])
        return record

    def extract(self) -> Iterator[Dict[str, Any]]:
        location = self.location()
        con = open_duckdb(self.config, location, extra_extensions=("json",))
        try:
            cursor = con.execute(self.read_json_sql(location.uri))
            columns = [description[0] for description in cursor.description]
            while True:
                batch = cursor.fetchmany(self.batch_size)
                if not batch:
                    break
                for row in batch:
                    record = {col: plain(val) for col, val in zip(columns, row)}
                    record = self.apply_numbers(self.apply_columns(record))
                    yield self.transform_row(record)
        finally:
            con.close()
