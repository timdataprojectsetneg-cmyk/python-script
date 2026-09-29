"""MinIO / S3 object storage backend.

Configuration (non-confidential in ``.env``, credentials via NiFi secrets):

    MINIO__ENDPOINT   = minio.example.local:9000
    MINIO__ACCESS_KEY = <secret>
    MINIO__SECRET_KEY = <secret>
    MINIO__BUCKET     = setneg-raw
    MINIO__SECURE     = false
"""

from __future__ import annotations

import io
from typing import Any, Dict

from ...config import get_raw
from ...exceptions import ConfigError, IngestionError
from ..base.storage import BaseStorage


class MinioStorage(BaseStorage):
    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self.endpoint = get_raw("MINIO__ENDPOINT")
        self.access_key = get_raw("MINIO__ACCESS_KEY")
        self.secret_key = get_raw("MINIO__SECRET_KEY")
        self.secure = str(get_raw("MINIO__SECURE", "false")).lower() in ("1", "true", "yes")
        self.bucket = (
            (self.config or {}).get("minio_bucket")
            or get_raw("MINIO__BUCKET")
        )

    def _client(self):
        try:
            from minio import Minio
        except ImportError as exc:
            raise ConfigError("MinIO storage requires the 'minio' package") from exc
        if not self.endpoint:
            raise ConfigError("Missing MINIO__ENDPOINT")
        return Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    def _ensure_bucket(self, client) -> None:
        if not self.bucket:
            raise ConfigError("Missing MINIO__BUCKET")
        if not client.bucket_exists(self.bucket):
            client.make_bucket(self.bucket)

    def upload_bytes(
        self, data: bytes, object_key: str, content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        client = self._client()
        self._ensure_bucket(client)
        try:
            result = client.put_object(
                self.bucket,
                object_key,
                io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
        except Exception as exc:  # pragma: no cover - network dependent
            raise IngestionError(f"MinIO upload failed for {object_key}: {exc}") from exc
        return {
            "bucket": self.bucket,
            "object_key": object_key,
            "etag": getattr(result, "etag", None),
            "size": len(data),
        }

    def exists(self, object_key: str) -> bool:
        client = self._client()
        try:
            client.stat_object(self.bucket, object_key)
            return True
        except Exception:
            return False
