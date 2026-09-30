"""Normalizer — Satu Data Kemnaker."""

from __future__ import annotations

import html
import logging
import re
from typing import Any, Dict, Iterator

from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)

_TAG = re.compile(r"<[^>]+>")


def _strip_html(value: Any) -> Any:
    """Turn ``abstraksi`` HTML into plain text (keeps the content, drops markup)."""
    if not isinstance(value, str):
        return value
    text = html.unescape(_TAG.sub(" ", value))
    text = " ".join(text.split())
    return text or None


class Normalizer(BaseNormalizer):
    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                record = Record(**raw).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed, record skipped: %s", exc)
                continue
            record["abstraksi"] = _strip_html(record.get("abstraksi"))
            yield record
