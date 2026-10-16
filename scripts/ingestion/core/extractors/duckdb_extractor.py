"""DuckDB extractor — read an Excel (xlsx) file straight from S3/MinIO.

Uses DuckDB's ``httpfs`` + ``excel`` extensions so ``read_xlsx`` streams the
workbook from object storage — no full download and no pandas/openpyxl in the hot
path. S3 credentials come from the same ``MINIO_URI`` / ``MINIO__*`` config as
:class:`~ingestion.core.storage.minio_storage.MinioStorage`.

Config (source keys):

- ``url`` — ``s3://bucket/key.xlsx`` (or ``minio://bucket/key``, a local path, or
  an http(s) URL). ``s3://``/``minio://`` are read in place.
- ``sheet`` — worksheet name (default: the first sheet).
- ``header`` — treat row 1 as the header (default ``true``).
- ``range`` — an A1 range to restrict the read (e.g. ``A1:C20``).
- ``all_varchar`` — return every cell as text (default ``true``).
- ``columns`` — optional ``Label:name`` mapping (see ``parse_fields``).

Subclasses override :meth:`DuckDBExcelExtractor.transform_row` (or set
``columns``) to shape rows for their model.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List

from ...exceptions import ConfigError
from ..base.extractor import BaseExtractor
from .utils import parse_fields

EXTENSIONS = ("httpfs", "excel")


def _literal(value: str) -> str:
    """SQL string literal (single quotes doubled)."""
    return "'" + str(value).replace("'", "''") + "'"


def _as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def open_duckdb(config: Dict[str, Any] | None = None) -> Any:
    """Open a DuckDB connection wired to the MinIO/S3 endpoint.

    Loads ``httpfs``/``excel`` (installing them on first use) and points ``httpfs``
    at the endpoint, keys and TLS settings from ``MINIO_URI`` / ``MINIO__*``,
    using path-style URLs (MinIO-compatible).
    """
    try:
        import duckdb
    except ImportError as exc:  # pragma: no cover - depends on the environment
        raise ConfigError("The DuckDB extractor requires the 'duckdb' package") from exc

    con = duckdb.connect()
    for extension in EXTENSIONS:
        try:
            con.execute(f"LOAD {extension};")
        except Exception:  # noqa: BLE001 - not installed yet -> install then load
            con.execute(f"INSTALL {extension}; LOAD {extension};")

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
    return con


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
