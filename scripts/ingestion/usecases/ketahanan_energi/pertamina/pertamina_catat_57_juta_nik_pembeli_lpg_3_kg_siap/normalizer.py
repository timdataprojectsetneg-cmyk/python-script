"""Normalizer — Artikel KONTAN - Pertamina Catat 57 Juta NIK Pembeli LPG 3 Kg, Siap Jalankan Subsidi Tepat Sasaran."""

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
                yield Record(**raw).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed, record skipped: %s", exc)
