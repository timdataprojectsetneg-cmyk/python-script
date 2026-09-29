"""Abstract storage backend (object storage such as MinIO / S3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseStorage(ABC):
    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    def upload_bytes(
        self, data: bytes, object_key: str, content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """Upload raw bytes and return a metadata dict (bucket, object_key, etag, size)."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, object_key: str) -> bool:
        raise NotImplementedError
