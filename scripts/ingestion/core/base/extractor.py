"""Abstract base class for all extractors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator

from .http import HttpClient

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
}


class BaseExtractor(ABC):
    """Yields raw records (dicts) from a data source."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.url = config.get("url") or config.get("pdf_url")
        self.impersonate = config.get("impersonate")
        self.http = HttpClient(default_headers=DEFAULT_HEADERS, impersonate=self.impersonate)

    @abstractmethod
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Yield raw records as dicts."""
        raise NotImplementedError

    @property
    def source_type(self) -> str:
        return self.__class__.__name__
