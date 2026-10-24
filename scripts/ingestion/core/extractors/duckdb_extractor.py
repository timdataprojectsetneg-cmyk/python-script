"""DuckDB extractors — read Excel (xlsx) or JSON from local disk, S3/MinIO or HTTP(S).

Uses DuckDB so files are read in place (``httpfs`` for S3/HTTP, ``excel`` for xlsx,
``json`` for JSON) — no pandas/openpyxl in the hot path. S3 credentials come from
the same ``MINIO_URI`` / ``MINIO__*`` config as
:class:`~ingestion.core.storage.minio_storage.MinioStorage`.

Location detection (:func:`resolve_location`):

- ``s3://bucket/key``      -> S3 (read via httpfs with MinIO/S3 credentials)
- ``minio://bucket/key``   -> S3 (rewritten to ``s3://bucket/key``)
- ``http://`` / ``https://`` -> HTTP (read via httpfs, no S3 credentials needed)
- anything else            -> local file (macOS / Linux / Windows); ``~``, env vars,
  relative paths, ``file://`` and glob patterns (``data/*.json``) are supported.

Excel config (source keys):

- ``url`` — location of the workbook (see above).
- ``sheet`` — worksheet name (default: the first sheet).
- ``header`` — treat row 1 as the header (default ``true``).
- ``range`` — an A1 range to restrict the read (e.g. ``A1:C20``).
- ``all_varchar`` — return every cell as text (default ``true``).
- ``columns`` — optional ``Label:name`` mapping (see ``parse_fields``).

JSON config (source keys):

- ``url`` (or ``path``) — location of the JSON / NDJSON file(s).
- ``json_format`` — ``auto`` (default) | ``array`` | ``newline_delimited`` | ``unstructured``.
- ``root`` — top-level key holding the list of records, for files shaped like
  ``{"data": [ {...}, {...} ]}``.
- ``records`` — ``auto`` (default) | ``true`` | ``false`` (DuckDB ``records`` option).
- ``union_by_name`` — merge schemas when reading several files (default ``false``).
- ``ignore_errors`` — skip malformed rows (default ``false``).
- ``sample_size`` / ``maximum_object_size`` — DuckDB schema-detection tuning.
- ``number_columns`` — comma-separated columns holding Indonesian-formatted numbers
  as text (``"364.591,6"``, ``"(27.352,4)"``, ``""``); converted to ``float``/``None``.
- ``columns`` — optional ``Label:name`` mapping (see ``parse_fields``).

Subclasses override ``transform_row`` (or set ``columns``) to shape rows for their model.
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from ...exceptions import ConfigError
from ..base.extractor import BaseExtractor
from .utils import parse_fields

EXTENSIONS = ("httpfs", "excel")

LOCAL = "local"
S3 = "s3"
HTTP = "http"

JSON_FORMATS = ("auto", "array", "newline_delimited", "unstructured")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _literal(value: str) -> str:
    """SQL string literal (single quotes doubled)."""
    return "'" + str(value).replace("'", "''") + "'"


def _ident(value: str) -> str:
    """SQL identifier (double quotes doubled)."""
    return '"' + str(value).replace('"', '""') + '"'


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Location:
    """Where a file lives and the URI DuckDB should read."""

    kind: str  # LOCAL | S3 | HTTP
    uri: str

    @property
    def needs_httpfs(self) -> bool:
        return self.kind in (S3, HTTP)


def resolve_location(ref: Any) -> Location:
    """Classify ``ref`` as S3, HTTP(S) or local and normalise it for DuckDB.

    - ``s3://...``              -> ``Location("s3", ...)``
    - ``minio://bucket/key``    -> ``Location("s3", "s3://bucket/key")``
    - ``http://`` / ``https://`` -> ``Location("http", ...)``
    - otherwise                 -> ``Location("local", <absolute posix path>)``

    Local paths are returned with forward slashes (``C:/data/x.json`` on Windows),
    which DuckDB accepts on every platform. A local path that does not exist
    (and is not a glob pattern) raises :class:`ConfigError` early with a clear message.
    """
    text = str(ref or "").strip()
    if not text:
        raise ConfigError("Missing URL/path for DuckDB extraction")
    lowered = text.lower()

    if lowered.startswith("minio://"):
        from ..storage.minio_storage import split_minio_ref

        bucket, key = split_minio_ref(text)
        return Location(S3, f"s3://{bucket}/{key}")
    if lowered.startswith("s3://"):
        return Location(S3, text)
    if lowered.startswith(("http://", "https://")):
        return Location(HTTP, text)

    if lowered.startswith("file://"):
        text = text[len("file://"):]
        if re.match(r"^/[A-Za-z]:[\\/]", text):  # file:///C:/x -> C:/x
            text = text[1:]

    expanded = os.path.expandvars(os.path.expanduser(text))
    absolute = Path(os.path.abspath(expanded)).as_posix()
    if glob.has_magic(absolute):
        if not glob.glob(expanded):
            raise ConfigError(f"No local files match: {text}")
    elif not os.path.exists(expanded):
        raise ConfigError(f"Local file not found: {text}")
    return Location(LOCAL, absolute)


def _load_extension(con: Any, name: str) -> None:
    try:
        con.execute(f"LOAD {name};")
    except Exception:  # noqa: BLE001 - not installed yet -> install then load
        con.execute(f"INSTALL {name}; LOAD {name};")


def _configure_s3(con: Any, config: Dict[str, Any] | None) -> None:
    from ..storage.minio_storage import MinioStorage

    storage = MinioStorage(config)
    if not storage.endpoint:
        raise ConfigError("DuckDB S3 read requires MINIO_URI or MINIO__ENDPOINT")
    con.execute(f"SET s3_endpoint={_literal(storage.endpoint)}")
    con.execute(f"SET s3_access_key_id={_literal(storage.access_key or '')}")
    con.execute(f"SET s3_secret_access_key={_literal(storage.secret_key or '')}")
    con.execute(f"SET s3_use_ssl={'true' if storage.secure else 'false'}")
    con.execute("SET s3_url_style='path'")
    if storage.ca_cert:
        con.execute(f"SET ca_cert_file={_literal(storage.ca_cert)}")


def open_duckdb(
    config: Dict[str, Any] | None = None,
    location: Optional[Location] = None,
    extra_extensions: tuple = (),
) -> Any:
    """Open a DuckDB connection prepared for the given :class:`Location`.

    - ``location=None`` (legacy / Excel): loads ``httpfs`` + ``excel`` and wires the
      MinIO/S3 endpoint, exactly as before.
    - ``S3``: loads ``httpfs`` and wires the endpoint, keys and TLS settings from
      ``MINIO_URI`` / ``MINIO__*`` (path-style URLs, MinIO-compatible).
    - ``HTTP``: loads ``httpfs`` only — no S3 credentials required.
    - ``LOCAL``: loads no network extension and needs no MinIO config.
    """
    try:
        import duckdb
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise ConfigError("The DuckDB extractor requires the 'duckdb' package") from exc

    if location is None:
        extensions = EXTENSIONS
        use_s3 = True
    else:
        extensions = ("httpfs",) if location.needs_httpfs else ()
        use_s3 = location.kind == S3

    con = duckdb.connect()
    for extension in (*extensions, *extra_extensions):
        _load_extension(con, extension)
    if use_s3:
        _configure_s3(con, config)
    return con


def parse_id_number(value: Any) -> Any:
    """Parse an Indonesian-formatted number into ``float`` (``None`` if blank).

    ``"221,2"`` -> 221.2, ``"364.591,6"`` -> 364591.6, ``"(27.352,4)"`` -> -27352.4,
    ``"-17,2"`` -> -17.2, ``""`` / ``"-"`` -> ``None``. Native numbers pass through as
    ``float``; unparseable text is returned unchanged.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return float(value)
    text = str(value).strip().replace(" ", "")
    if text in ("", "-", "–", "n/a", "N/A", "NA"):
        return None
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1]
    if text.startswith("-"):
        negative = True
        text = text[1:]
    text = text.replace(".", "").replace(",", ".")
    try:
        number = float(text)
    except ValueError:
        return value
    return -number if negative else number


def _plain(value: Any) -> Any:
    """Make DuckDB values friendly for the loader (``Decimal`` -> ``float``)."""
    if isinstance(value, Decimal):
        return float(value)
    return value


# --------------------------------------------------------------------------- #
# Excel
# --------------------------------------------------------------------------- #
class DuckDBExcelExtractor(BaseExtractor):
    """Yield records from an Excel file read with DuckDB ``read_xlsx``."""

    def reference(self) -> str:
        """The ``read_xlsx`` path: ``s3://``/``minio://``, local, or http(s)."""
        ref = str(self.config.get("url") or "").strip()
        if not ref:
            raise ConfigError("Missing URL for DuckDB Excel extraction")
        if ref.lower().startswith("minio://"):
            from ..storage.minio_storage import split_minio_ref

            bucket, key = split_minio_ref(ref)
            return f"s3://{bucket}/{key}"
        return ref

    def read_xlsx_sql(self, ref: str) -> str:
        options: List[str] = []
        sheet = self.config.get("sheet")
        if sheet:
            options.append(f"sheet={_literal(str(sheet))}")
        if self.config.get("header") is not None:
            header = _as_bool(self.config.get("header"), True)
            options.append(f"header={'true' if header else 'false'}")
        rng = self.config.get("range")
        if rng:
            options.append(f"range={_literal(str(rng))}")
        if _as_bool(self.config.get("all_varchar"), True):
            options.append("all_varchar=true")
        suffix = ", " + ", ".join(options) if options else ""
        return f"SELECT * FROM read_xlsx({_literal(ref)}{suffix})"

    def apply_columns(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Optional ``columns`` (``Label:name``) rename, mirroring ExcelExtractor."""
        field_map = parse_fields(self.config.get("columns"))
        if not field_map:
            return record
        mapped: Dict[str, Any] = {}
        for field in field_map:
            label = field.get("label") or field.get("source")
            target = field.get("name") or field.get("target") or label
            if label in record:
                mapped[target] = record.get(label)
            elif target in record:
                mapped[target] = record.get(target)
        for key, value in record.items():
            mapped.setdefault(key, value)
        return mapped

    def transform_row(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Hook: adapt a raw row before it leaves the extractor (default: as-is)."""
        return record

    def extract(self) -> Iterator[Dict[str, Any]]:
        ref = self.reference()
        con = open_duckdb(self.config)
        try:
            cursor = con.execute(self.read_xlsx_sql(ref))
            columns = [description[0] for description in cursor.description]
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                yield self.transform_row(self.apply_columns(record))
        finally:
            con.close()


# --------------------------------------------------------------------------- #
# JSON
# --------------------------------------------------------------------------- #
class DuckDBJSONExtractor(DuckDBExcelExtractor):
    """Yield records from JSON / NDJSON read with DuckDB ``read_json``.

    The source can be a local file (mac/Windows/Linux), ``s3://`` / ``minio://``
    or ``http(s)://``. Each row is yielded as ``Dict[str, Any]`` with native Python
    types (``int``, ``float``, ``str``, ``None``; nested objects/arrays as
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
            options.append(f"format={_literal(json_format)}")

        records = str(self.config.get("records") or "").strip().lower()
        if records:
            if records not in ("auto", "true", "false"):
                raise ConfigError("records must be 'auto', 'true' or 'false'")
            options.append(f"records={_literal(records)}")

        for key in ("sample_size", "maximum_object_size"):
            if self.config.get(key) not in (None, ""):
                try:
                    options.append(f"{key}={int(self.config[key])}")
                except (TypeError, ValueError) as exc:
                    raise ConfigError(f"{key} must be an integer") from exc

        if _as_bool(self.config.get("union_by_name"), False):
            options.append("union_by_name=true")
        if _as_bool(self.config.get("ignore_errors"), False):
            options.append("ignore_errors=true")

        suffix = ", " + ", ".join(options) if options else ""
        base = f"read_json({_literal(ref)}{suffix})"

        root = str(self.config.get("root") or "").strip()
        if root:
            return f"SELECT r.* FROM (SELECT UNNEST({_ident(root)}) AS r FROM {base})"
        return f"SELECT * FROM {base}"

    def apply_numbers(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ``number_columns`` from Indonesian-formatted text to float/None."""
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
                    record = {col: _plain(val) for col, val in zip(columns, row)}
                    record = self.apply_numbers(self.apply_columns(record))
                    yield self.transform_row(record)
        finally:
            con.close()