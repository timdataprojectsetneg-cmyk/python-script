"""Locate a file for DuckDB: local disk, S3/MinIO or HTTP(S)."""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ....exceptions import ConfigError

LOCAL = "local"
S3 = "s3"
HTTP = "http"


@dataclass(frozen=True)
class Location:
    """Where a file lives and the URI DuckDB should read."""

    kind: str  # LOCAL | S3 | HTTP
    uri: str

    @property
    def needs_httpfs(self) -> bool:
        return self.kind in (S3, HTTP)


def resolve_location(ref: Any) -> Location:
    """Classify ``ref`` as S3, HTTP(S) or local and normalise it for DuckDB.

    - ``s3://...``               -> ``Location("s3", ...)``
    - ``minio://bucket/key``     -> ``Location("s3", "s3://bucket/key")``
    - ``http://`` / ``https://`` -> ``Location("http", ...)``
    - otherwise                  -> ``Location("local", <absolute posix path>)``

    Local paths use forward slashes (``C:/data/x.json`` on Windows), which
    DuckDB accepts on every platform. A missing local file/glob raises
    :class:`ConfigError` early.
    """
    text = str(ref or "").strip()
    if not text:
        raise ConfigError("Missing URL/path for DuckDB extraction")
    lowered = text.lower()

    if lowered.startswith("minio://"):
        from ...storage.minio_storage import split_minio_ref

        bucket, key = split_minio_ref(text)
        return Location(S3, f"s3://{bucket}/{key}")
    if lowered.startswith("s3://"):
        return Location(S3, text)
    if lowered.startswith(("http://", "https://")):
        return Location(HTTP, text)

    if lowered.startswith("file://"):
        text = text[len("file://") :]
        if re.match(r"^/[A-Za-z]:[\\/]", text):  # file:///C:/x -> C:/x
            text = text[1:]

    expanded = os.path.expandvars(os.path.expanduser(text))
    absolute = Path(os.path.abspath(expanded)).as_posix()
    if glob.has_magic(absolute):
        if not glob.glob(expanded):
            raise ConfigError(f"No local files match: {text}")
    elif not os.path.exists(expanded):
        raise ConfigError(f"Local file not found: {text}")
    return Location(LOCAL, absolute)
