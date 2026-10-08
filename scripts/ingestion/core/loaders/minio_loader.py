"""DEV-only MinIO loader: writes normalized records as an NDJSON object.

Uploads the whole record batch as a single newline-delimited JSON object to
MinIO and returns the number of records written. Bucket/credential handling is
reused from :class:`MinioStorage`.

Configuration (credentials from ``.env.dev``):

    MINIO__ENDPOINT   = minio-api-sitroom.setneg.go.id
    MINIO__ACCESS_KEY = <secret>
    MINIO__SECRET_KEY = <secret>
    MINIO__BUCKET     = raw
    MINIO__SECURE     = true

Object key precedence: config ``object_key``, else
``<MINIO_PREFIX|source>/<UTC timestamp>_<source>.ndjson``.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

from ...exceptions import ConfigError
from ..base.loader import BaseLoader
from ..storage.minio_storage import MinioStorage


def _to_ndjson(records: list[Dict[str, Any]]) -> bytes:
    """Serialize records to newline-delimited JSON (one record per line)."""
    lines = (json.dumps(record, ensure_ascii=False, default=str) for record in records)
    return ("\n".join(lines) + "\n").encode("utf-8")


class MinioLoader(BaseLoader):
    """DEV MinIO loader writing one NDJSON object per batch."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config)
        self.storage = MinioStorage(self.config)
        if not self.storage.bucket:
            raise ConfigError("Missing MINIO__BUCKET")

    def _object_key(self) -> str:
        explicit = self.config.get("object_key")
        if explicit:
            return str(explicit).strip("/")
        source = str(self.config.get("source") or "ingestion")
        prefix = str(self.config.get("minio_prefix") or source).strip("/")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"{prefix}/{stamp}_{source}.ndjson"

    def load(self, records: Iterable[Dict[str, Any]]) -> int:
        rows = list(records)
        if not rows:
            return 0
        data = _to_ndjson(rows)
        self.storage.upload_bytes(data, self._object_key(), content_type="application/x-ndjson")
        return len(rows)
