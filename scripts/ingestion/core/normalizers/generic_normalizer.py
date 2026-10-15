"""Common normalization utilities.

The generic normalizer is used when a source does not provide its own
``normalizer.py``. It cleans values and, if the source exposes a Pydantic
``Record`` model, validates each record against it.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Iterator, List

from pydantic import BaseModel, ValidationError

from ..base.normalizer import BaseNormalizer

logger = logging.getLogger(__name__)


def clean_string(value: Any) -> Any:
    if isinstance(value, str):
        text = " ".join(value.split())
        return text or None
    return value


def clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {key: clean_string(val) for key, val in record.items()}


class GenericNormalizer(BaseNormalizer):
    """Cleans records and optionally validates against ``model``."""

    def __init__(self, config: Dict[str, Any] | None = None, model: type[BaseModel] | None = None):
        super().__init__(config)
        self.model = model

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            cleaned = clean_record(raw)
            if self.model is None:
                yield cleaned
                continue
            try:
                yield self.model(**cleaned).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed, record skipped: %s", exc)
                continue


class PassthroughNormalizer(BaseNormalizer):
    """Skip normalization: pass extracted records straight to the loader.

    Used when a source defines neither ``normalizer.py`` nor a ``Record`` model
    (dictionary). The registry logs a warning when this happens.
    """

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        return records
