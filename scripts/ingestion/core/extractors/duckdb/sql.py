"""Small SQL quoting helpers."""

from __future__ import annotations


def literal(value: str) -> str:
    """SQL string literal (single quotes doubled)."""
    return "'" + str(value).replace("'", "''") + "'"


def ident(value: str) -> str:
    """SQL identifier (double quotes doubled)."""
    return '"' + str(value).replace('"', '""') + '"'


def as_bool(value, default: bool) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")
