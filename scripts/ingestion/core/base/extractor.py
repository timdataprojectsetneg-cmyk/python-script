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


def is_truthy(value: Any) -> bool:
    """True for 1/true/yes/on (case-insensitive)."""
    return str(value).strip().lower() in ("1", "true", "yes", "on")


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

    def save_raw_to_minio(
        self, content: bytes, filename: str, content_type: str = "application/octet-stream"
    ) -> Dict[str, Any] | None:
        """Land the raw downloaded file in MinIO when ``SAVE_RAW`` is enabled.

        Object key: config ``object_key``, else ``<minio_prefix|source>/<filename>``.
        Returns the upload metadata, or ``None`` when disabled.
        """
        if not is_truthy(self.config.get("save_raw")):
            return None
        from ..storage.minio_storage import MinioStorage

        prefix = str(self.config.get("minio_prefix") or self.config.get("source") or "").strip("/")
        explicit = str(self.config.get("object_key") or "").strip("/")
        object_key = explicit or (f"{prefix}/{filename}" if prefix else filename)
        return MinioStorage(self.config).upload_bytes(content, object_key, content_type)

    @property
    def source_type(self) -> str:
        return self.__class__.__name__
