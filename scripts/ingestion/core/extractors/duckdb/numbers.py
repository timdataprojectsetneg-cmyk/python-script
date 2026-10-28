"""Indonesian number parsing for DuckDB values."""

from __future__ import annotations

from decimal import Decimal
from typing import Any


def parse_id_number(value: Any) -> Any:
    """Parse an Indonesian-formatted number into ``float`` (``None`` if blank).

    ``"221,2"`` -> 221.2, ``"364.591,6"`` -> 364591.6, ``"(27.352,4)"`` -> -27352.4,
    ``"-17,2"`` -> -17.2, ``""`` / ``"-"`` -> ``None``. Native numbers pass through
    as ``float``; unparseable text is returned unchanged.
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


def plain(value: Any) -> Any:
    """Make DuckDB values friendly for the loader (``Decimal`` -> ``float``)."""
    if isinstance(value, Decimal):
        return float(value)
    return value
