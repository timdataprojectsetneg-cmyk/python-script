"""Normalizer — Kemnaker Perusahaan Skala Upah Table 1."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator

from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)


class Normalizer(BaseNormalizer):
    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                # Extract metadata from special keys if present
                # Excel automation adds _sheet_name
                sheet_name = raw.get("_sheet_name")
                if sheet_name:
                    raw["bulan"] = sheet_name
                
                raw["tahun"] = "2026"

                yield Record(**raw).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed, record skipped: %s", exc)

