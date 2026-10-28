"""Write LLM extraction results to JSON, NDJSON or CSV (local or S3/MinIO)."""

from __future__ import annotations

import csv
import io
import json
import tempfile
from pathlib import Path
from typing import Any

__all__ = ["render_records", "write_records", "write_result", "write_result_s3"]


def _rows(records: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    columns: list[str] = []
    for record in records:
        for key in record:
            if key not in columns:
                columns.append(key)
    return columns, records


def render_records(records: list[dict[str, Any]], fmt: str = "json") -> str:
    """Render only the records as a JSON array, NDJSON, or CSV text."""
    fmt = (fmt or "json").lower()
    if fmt == "json":
        return json.dumps(records, ensure_ascii=False, indent=2, default=str)
    if fmt == "ndjson":
        return "\n".join(
            json.dumps(record, ensure_ascii=False, default=str) for record in records
        )
    if fmt == "csv":
        columns, rows = _rows(records)
        buffer = io.StringIO()
        if columns:
            writer = csv.DictWriter(buffer, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        return buffer.getvalue()
    raise ValueError(f"Unsupported output format: {fmt}")


def write_records(
    records: list[dict[str, Any]],
    path: str | Path,
    fmt: str = "json",
) -> Path:
    """Write only the records (JSON array, NDJSON, or CSV)."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_records(records, fmt), encoding="utf-8")
    return target


_RESULT_COLUMNS = (
    "{'status': 'VARCHAR', 'records': 'JSON', 'warnings': 'JSON', "
    "'errors': 'JSON', 'metadata': 'JSON'}"
)


def write_result_s3(
    result: Any,
    uri: str,
    fmt: str = "json",
    config: dict[str, Any] | None = None,
) -> str:
    """Write the result to ``s3://bucket/key`` with DuckDB (MinIO settings from env).

    The payload is staged in a temp file, then ``COPY ... TO`` the S3 URI; JSON
    columns are emitted as raw JSON so the object matches the local output.
    """
    from ..duckdb import S3, Location, open_duckdb
    from ..duckdb.sql import literal

    fmt = (fmt or "json").lower()
    if fmt not in ("json", "ndjson", "csv"):
        raise ValueError(f"Unsupported output format: {fmt}")
    if fmt != "json" and not result.records:
        raise ValueError("no records to write")

    with tempfile.TemporaryDirectory(prefix="ingestion_llm_out_") as tmp:
        staged = Path(tmp) / "payload.json"
        if fmt == "json":
            write_result(result, staged, "json")
            source = f"read_json({literal(staged.as_posix())}, columns={_RESULT_COLUMNS})"
            options = "FORMAT JSON"
        else:
            write_records(result.records, staged, "ndjson")
            source = f"read_json({literal(staged.as_posix())}, format='newline_delimited')"
            options = "FORMAT CSV, HEADER true" if fmt == "csv" else "FORMAT JSON"

        con = open_duckdb(config, Location(S3, uri))
        try:
            con.execute(f"COPY (SELECT * FROM {source}) TO {literal(uri)} ({options})")
        finally:
            con.close()
    return uri


def write_result(
    result: Any,
    path: str | Path,
    fmt: str = "json",
    config: dict[str, Any] | None = None,
) -> Path | str:
    """Write the complete result (JSON) or only its records (NDJSON/CSV).

    ``path`` may be a local path or an ``s3://`` URI (written via DuckDB).
    """
    if str(path).lower().startswith("s3://"):
        return write_result_s3(result, str(path), fmt, config)
    fmt = (fmt or "json").lower()
    if fmt == "json":
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict() if hasattr(result, "to_dict") else result
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return target
    return write_records(result.records, path, fmt)
