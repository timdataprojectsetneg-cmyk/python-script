"""Abstract base class for DEV-only loaders (PROD uses NiFi PutDatabaseRecord)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Iterator


class BaseLoader(ABC):
    """Consumes normalized records and writes them to the destination."""

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    def load(self, records: Iterable[Dict[str, Any]]) -> int:
        """Load records and return the number written."""
        raise NotImplementedError
