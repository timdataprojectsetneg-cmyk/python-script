
"""Validation of the extracted records (TDD section 14).

Validation never *invents* data: a record that does not satisfy the schema is
reported through warnings/errors and, when it cannot be repaired, kept but
marked so the caller can quarantine it.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Sequence

from .models import Dictionary, Status
from .page_context import coerce

log = logging.getLogger("pdf_extractor.validate")

_INTERNAL = ("_is_total", "_label")


def strip_internal(records: Sequence[dict]) -> list[dict]:
    return [{k: v for k, v in r.items() if k not in _INTERNAL} for r in records]


def validate_records(
    records: Sequence[dict[str, Any]],
    dictionary: Dictionary,
    min_confidence: float = 0.5,
    max_records: int | None = None,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Coerce every record to the dictionary and collect warnings/errors.

    Returns ``(records, warnings, errors)``.
    """
    warnings: list[str] = []
    errors: list[str] = []
    specs = {f.name: f for f in dictionary.fields}
    out: list[dict[str, Any]] = []
    seen: set[tuple] = set()

    for i, raw in enumerate(records):
        record: dict[str, Any] = {}
        for name, value in raw.items():
            if name in _INTERNAL:
                continue
            spec = specs.get(name)
            if spec is None:
                # unknown field: keep it, but say so
                warnings.append(f"record {i}: field '{name}' tidak ada di dictionary")
                record[name] = value
                continue
            if value is None:
                if spec.required:
                    warnings.append(f"record {i}: field wajib '{name}' kosong")
                record[name] = None
                continue
            kind = spec.kind
            before, after = value, coerce(value, kind)
            if kind in ("int", "float") and isinstance(after, str):
                warnings.append(
                    f"record {i}: '{name}' tidak bisa diparsing sebagai angka ({before!r})"
                )
            elif kind == "str" and not isinstance(after, str):
                after = str(after)
            record[name] = after

        for spec in dictionary.fields:
            if spec.required and record.get(spec.name) in (None, ""):
                warnings.append(f"record {i}: field wajib '{spec.name}' tidak terisi")

        key = tuple((f.name, record.get(f.name)) for f in dictionary.fields)
        if key and key in seen:
            warnings.append(f"record {i}: duplikasi terdeteksi")
        seen.add(key)
        out.append(record)

    if max_records is not None and len(out) > max_records:
        errors.append(
            f"jumlah record ({len(out)}) melebihi batas {max_records} -- "
            "kemungkinan tabel yang salah terpilih"
        )
    if not out:
        errors.append("tidak ada record yang berhasil diekstrak")
    return out, warnings, errors


def status_from(warnings: Sequence[str], errors: Sequence[str]) -> Status:
    if any("wajib" in w or "melebihi" in w or "tidak ada record" in w for w in errors):
        return Status.VALIDATION_FAILED
    if errors:
        return Status.VALIDATION_FAILED
    return Status.PARTIAL if warnings else Status.SUCCESS