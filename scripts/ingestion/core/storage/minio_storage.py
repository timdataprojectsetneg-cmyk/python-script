"""MinIO / S3 object storage backend.

Configuration — either a single URI, or the discrete ``MINIO__*`` keys:

    MINIO_URI         = minio://access:secret@host:9000/bucket?secure=true
    MINIO__ENDPOINT   = minio.example.local:9000
    MINIO__ACCESS_KEY = <secret>
    MINIO__SECRET_KEY = <secret>
    MINIO__BUCKET     = setneg-raw
    MINIO__SECURE     = false
"""

from __future__ import annotations

import io
from typing import Any, Dict
from urllib.parse import parse_qs, unquote, urlparse

from ...config import get_raw, get_uri
from ...exceptions import ConfigError, IngestionError
from ..base.storage import BaseStorage


def _parse_minio_uri(uri: str) -> Dict[str, Any]:
    """Parse ``minio://access:secret@host:port/bucket?secure=true``."""
    parsed = urlparse(uri)
    secure = str(parse_qs(parsed.query).get("secure", ["false"])[0]).lower() in ("1", "true", "yes")
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return {
        "endpoint": host,
        "access_key": unquote(parsed.username or ""),
        "secret_key": unquote(parsed.password or ""),
        "bucket": (parsed.path or "").lstrip("/"),
        "secure": secure,
    }


def split_minio_ref(uri: str) -> tuple[str, str]:
    """Split an object reference ``minio://bucket/key`` into ``(bucket, key)``.

    The connection (endpoint/credentials) still comes from ``MINIO_URI`` or the
    ``MINIO__*`` keys; only the object location is taken from this reference.
    """
    parsed = urlparse(uri)
    bucket = parsed.hostname or ""
    key = (parsed.path or "").lstrip("/")
    return bucket, key


class MinioStorage(BaseStorage):
    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        uri = get_uri("MINIO_URI")
        parsed: Dict[str, Any] = _parse_minio_uri(uri) if uri else {}
        self.endpoint = parsed.get("endpoint") or get_raw("MINIO__ENDPOINT")
        self.access_key = parsed.get("access_key") or get_raw("MINIO__ACCESS_KEY")
        self.secret_key = parsed.get("secret_key") or get_raw("MINIO__SECRET_KEY")
        secure_raw = parsed.get("secure")
        if secure_raw is None:
            secure_raw = str(get_raw("MINIO__SECURE", "false")).lower() in ("1", "true", "yes")
        self.secure = bool(secure_raw)
        self.bucket = (
            (self.config or {}).get("minio_bucket")
            or parsed.get("bucket")
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

    def download_bytes(self, object_key: str) -> bytes:
        """Read an object's bytes (used to ingest a file that already lives in MinIO)."""
        client = self._client()
        if not self.bucket:
            raise ConfigError("Missing MINIO__BUCKET")
        try:
            response = client.get_object(self.bucket, object_key)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
        except Exception as exc:  # pragma: no cover - network dependent
            raise IngestionError(f"MinIO download failed for {object_key}: {exc}") from exc

    def exists(self, object_key: str) -> bool:
        client = self._client()
        try:
            client.stat_object(self.bucket, object_key)
            return True
        except Exception:
            return False
