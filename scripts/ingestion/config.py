"""Configuration loader.

Environment variable naming convention:

    {USECASE}__{SOURCE}__{ACCESS}__{KEY}

All uppercase, double underscore as segment delimiter. Non-confidential values
live in ``scripts/.env`` (loaded via python-dotenv); confidential values are
injected by the NiFi ``ExecuteStreamCommand`` processor into the process env.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .exceptions import ConfigError

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dotenv is a soft dependency
    load_dotenv = None

_loaded = False
_profile: Optional[str] = None

# Keys that are safe/expected at the {USECASE}__{SOURCE}__{ACCESS}__ level.
KNOWN_KEYS = (
    "URL",
    "SCHEMA",
    "TABLE",
    "TARGET",
    "METHOD",
    "HEADERS",
    "PARAMS",
    "API_KEY",
    "TOKEN",
    "PAGINATION_TYPE",
    "PAGINATION_PARAM",
    "START_PAGE",
    "MAX_PAGES",
    "PAGE_SIZE",
    "DATA_PATH",
    "NEXT_PATH",
    "SELECTOR",
    "ITEM_SELECTOR",
    "FIELDS",
    "COLUMNS",
    "SHEET",
    "HEADER_ROW",
    "DOWNLOAD_SELECTOR",
    "DOWNLOAD_URL",
    "DYNAMIC",
    "PDF_URL",
    "FILENAME",
    "MINIO_BUCKET",
    "MINIO_PREFIX",
    "OBJECT_KEY",
)


def set_env_profile(profile: Optional[str]) -> None:
    """Select an extra env file (``.env.<profile>``) for secret values."""
    global _profile, _loaded
    profile = (profile or "").strip() or None
    if profile != _profile:
        _profile = profile
        _loaded = False


def get_env_profile() -> Optional[str]:
    return _profile


def _env_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "..")


def _env_files() -> list[tuple[str, bool]]:
    """(path, override) pairs, loaded in order. The profile file wins."""
    files: list[tuple[str, bool]] = [
        (".env", False),
        (os.path.join(_env_dir(), ".env"), False),
    ]
    if _profile:
        files += [
            (f".env.{_profile}", True),
            (os.path.join(_env_dir(), f".env.{_profile}"), True),
        ]
    return files


def env_profile_file(profile: str) -> Optional[str]:
    """Return the existing ``.env.<profile>`` path, or None."""
    for candidate in (f".env.{profile}", os.path.join(_env_dir(), f".env.{profile}")):
        if os.path.exists(candidate):
            return candidate
    return None


def load_env() -> None:
    """Load ``.env`` and the optional ``.env.<profile>`` (no-op without dotenv)."""
    global _loaded
    if _loaded or load_dotenv is None:
        return
    for candidate, override in _env_files():
        if os.path.exists(candidate):
            load_dotenv(candidate, override=override)
    _loaded = True


def env_key(usecase: str, source: str, access: str, key: str) -> str:
    return f"{usecase}__{source}__{access}__{key}".upper()


def get(usecase: str, source: str, access: str, key: str, default: Any = None) -> Any:
    load_env()
    return os.environ.get(env_key(usecase, source, access, key), default)


def get_raw(key: str, default: Any = None) -> Any:
    load_env()
    return os.environ.get(key, default)


def load_config(usecase: str, source: str, access: str, require_url: bool = True) -> Dict[str, Any]:
    """Build the flattened config dict for a usecase/source/access triple.

    ``require_url=False`` is used for later pipeline steps that receive their URL
    from a preceding extractor (e.g. scraper -> excel).
    """
    if not usecase or not source or not access:
        raise ConfigError("usecase, source and access are required")

    usecase = usecase.strip().lower()
    source = source.strip().lower()
    access = access.strip().lower()

    cfg: Dict[str, Any] = {
        "usecase": usecase,
        "source": source,
        "access": access,
        "raw": {},
    }
    for key in KNOWN_KEYS:
        value = get(usecase, source, access, key)
        if value is not None:
            cfg[key.lower()] = value
            cfg["raw"][key] = value

    cfg.setdefault("method", "GET")
    cfg.setdefault("target", "none" if access == "pdf" else "postgres")

    if require_url and not cfg.get("url") and not cfg.get("pdf_url"):
        raise ConfigError(
            f"Missing required configuration: {env_key(usecase, source, access, 'URL')}"
        )

    return cfg


def resolve_credentials(usecase: str, source: str, access: str) -> Dict[str, Optional[str]]:
    """Return credential-like values without ever logging them."""
    return {
        "api_key": get(usecase, source, access, "API_KEY"),
        "token": get(usecase, source, access, "TOKEN"),
    }
