"""Python-side validation of LLM records against the output contract.

Prompt instructions are not a guarantee: every record is checked here for field
names, required fields, types, nullable values and enums. Values are never
invented; missing optional fields become ``None`` and invalid records are
reported and dropped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from .schema_builder import OutputField, OutputSchema

__all__ = ["ValidationResult", "validate_records"]

_MISSING = {"", "-", "–", "—", "n/a", "na", "null", "none"}
_INT_RE = re.compile(r"^[+-]?\d+$")
_NUMBER_RE = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")


@dataclass
class ValidationResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _is_missing(value: Any) -> bool:
    return value is None or (
        isinstance(value, str) and value.strip().casefold() in _MISSING
    )


def _enum_contains(values: tuple[Any, ...] | None, value: Any) -> bool:
    if values is None:
        return True
    return any(value == candidate for candidate in values)


def _coerce(value: Any, output_field: OutputField, where: str, result: ValidationResult) -> Any:
    kind = output_field.type
    if kind == "any":
        return value
    if kind == "string":
        if isinstance(value, str):
            return value
        raise ValueError(f"expected string, got {type(value).__name__}")
    if kind == "integer":
        if isinstance(value, bool):
            raise ValueError("expected integer, got boolean")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and _INT_RE.fullmatch(value.strip()):
            result.warnings.append(f"{where}: coerced numeric string to integer")
            return int(value.strip())
        raise ValueError(f"expected integer, got {type(value).__name__}")
    if kind == "number":
        if isinstance(value, bool):
            raise ValueError("expected number, got boolean")
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str) and _NUMBER_RE.fullmatch(value.strip()):
            result.warnings.append(f"{where}: coerced numeric string to number")
            return float(value.strip().replace(",", "."))
        raise ValueError(f"expected number, got {type(value).__name__}")
    if kind == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().casefold() in ("true", "false"):
            result.warnings.append(f"{where}: coerced string to boolean")
            return value.strip().casefold() == "true"
        raise ValueError(f"expected boolean, got {type(value).__name__}")
    if kind == "date":
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            try:
                date.fromisoformat(value.strip())
                return value.strip()
            except ValueError as exc:
                raise ValueError(f"expected ISO date, got {value!r}") from exc
        raise ValueError(f"expected date, got {type(value).__name__}")
    if kind == "datetime":
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, str):
            try:
                datetime.fromisoformat(value.strip())
                return value.strip()
            except ValueError as exc:
                raise ValueError(f"expected ISO datetime, got {value!r}") from exc
        raise ValueError(f"expected datetime, got {type(value).__name__}")
    if kind == "object":
        if isinstance(value, dict):
            return value
        raise ValueError(f"expected object, got {type(value).__name__}")
    if kind == "array":
        if isinstance(value, list):
            return value
        raise ValueError(f"expected array, got {type(value).__name__}")
    return value


def validate_records(
    records: list[Any],
    schema: OutputSchema | None,
) -> ValidationResult:
    """Validate and clean ``records`` according to ``schema``.

    - Unknown fields are dropped when a schema is supplied.
    - Missing optional fields are filled with ``None``.
    - Required fields must exist and must not be null/missing.
    - Invalid records are dropped and listed in ``errors``.
    - Numeric/boolean strings are coerced only when unambiguous.
    """
    result = ValidationResult()
    if schema is None:
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                result.errors.append(f"record[{index}]: expected object, got {type(record).__name__}")
                continue
            result.records.append(dict(record))
        return result

    known = {field.name for field in schema.fields}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            result.errors.append(f"record[{index}]: expected object, got {type(record).__name__}")
            continue

        clean: dict[str, Any] = {}
        record_errors: list[str] = []
        unknown = [key for key in record if key not in known]
        if unknown:
            result.warnings.append(f"record[{index}]: dropped unknown fields {sorted(unknown)}")

        for output_field in schema.fields:
            name = output_field.name
            where = f"record[{index}].{name}"
            value = record.get(name)

            if _is_missing(value):
                if output_field.required:
                    record_errors.append(f"{where}: required value is missing")
                else:
                    clean[name] = None
                continue

            try:
                coerced = _coerce(value, output_field, where, result)
            except ValueError as exc:
                record_errors.append(f"{where}: {exc}")
                continue

            if coerced is not None and not _enum_contains(output_field.enum, coerced):
                record_errors.append(
                    f"{where}: {coerced!r} is not one of {list(output_field.enum or [])}"
                )
                continue
            clean[name] = coerced

        if record_errors:
            result.errors.extend(record_errors)
        else:
            result.records.append(clean)

    return result
