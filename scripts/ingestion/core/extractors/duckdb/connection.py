"""DuckDB connection setup for S3/MinIO, HTTP and local files."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ....exceptions import ConfigError
from .location import HTTP, S3, Location
from .sql import literal

EXTENSIONS = ("httpfs", "excel")


def _load_extension(con: Any, name: str) -> None:
    try:
        con.execute(f"LOAD {name};")
    except Exception:  # noqa: BLE001 - not installed yet -> install then load
        con.execute(f"INSTALL {name}; LOAD {name};")


def _configure_s3(con: Any, config: Dict[str, Any] | None) -> None:
    from ...storage.minio_storage import MinioStorage

    storage = MinioStorage(config)
    if not storage.endpoint:
        raise ConfigError("DuckDB S3 read requires MINIO_URI or MINIO__ENDPOINT")
    con.execute(f"SET s3_endpoint={literal(storage.endpoint)}")
    con.execute(f"SET s3_access_key_id={literal(storage.access_key or '')}")
    con.execute(f"SET s3_secret_access_key={literal(storage.secret_key or '')}")
    con.execute(f"SET s3_use_ssl={'true' if storage.secure else 'false'}")
    con.execute("SET s3_url_style='path'")
    if storage.ca_cert:
        con.execute(f"SET ca_cert_file={literal(storage.ca_cert)}")


def open_duckdb(
    config: Dict[str, Any] | None = None,
    location: Optional[Location] = None,
    extra_extensions: tuple = (),
) -> Any:
    """Open a DuckDB connection prepared for ``location``.

    ``location=None`` is the legacy Excel path (``httpfs`` + ``excel`` + S3
    settings); ``S3`` wires MinIO credentials, ``HTTP`` loads only ``httpfs``,
    and ``LOCAL`` needs no network extension.
    """
    try:
        import duckdb
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ConfigError("The DuckDB extractor requires the 'duckdb' package") from exc

    if location is None:
        extensions = EXTENSIONS
        use_s3 = True
    else:
        extensions = ("httpfs",) if location.needs_httpfs else ()
        use_s3 = location.kind == S3

    con = duckdb.connect()
    for extension in (*extensions, *extra_extensions):
        _load_extension(con, extension)
    if use_s3:
        _configure_s3(con, config)
    return con
