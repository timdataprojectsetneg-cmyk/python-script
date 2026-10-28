"""Write LLM extraction results to JSON, NDJSON or CSV."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

__all__ = ["render_records", "write_records", "write_result"]


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


def write_result(result: Any, path: str | Path, fmt: str = "json") -> Path:
    """Write the complete result (JSON) or only its records (NDJSON/CSV)."""
    fmt = (fmt or "json").lower()
    if fmt == "json":
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict() if hasattr(result, "to_dict") else result
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return target
    return write_records(result.records, path, fmt)
