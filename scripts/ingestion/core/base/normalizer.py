"""Abstract base class for all normalizers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator


class BaseNormalizer(ABC):
    """Maps raw records to the validated target schema."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        raise NotImplementedError
