"""Normalizer for BMKG Prakiraan Cuaca."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)


class Normalizer(BaseNormalizer):
    """Maps raw weather records to validated Record instances."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                yield Record(**raw).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed for BMKG weather record: %s", exc)
