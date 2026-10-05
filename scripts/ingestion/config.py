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
_loaded_usecase_files: set[str] = set()
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
    "COOKIE",
    "USER_AGENT",
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
    "SOURCE_FILE",
    "HTML_PATH",
    "TAHUN",
    "WILAYAH_PREFIXES",
    "PDF_URL",
    "FILENAME",
    "MINIO_BUCKET",
    "MINIO_PREFIX",
    "OBJECT_KEY",
    "POSTGRE_SCHEMA",
    "POSTGRE_TABLE",
    "ES_INDEX",
    "UNIQUE_KEY",
    "WRITE_DISPOSITION",
    "LOAD_TIMESTAMP_COLUMN",
    "HTTP_METHOD",
    "IMPERSONATE",
)

# HTTP verbs accepted by ``HTTP_METHOD`` / legacy ``METHOD`` for API extraction.
# Any other ``METHOD`` value is a load strategy (``replace``/``upsert``).
HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"})


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


def load_env(usecase: Optional[str] = None) -> None:
    """Load base/profile env files and the generated use-case env fragment."""
    global _loaded
    if _loaded or load_dotenv is None:
        pass
    else:
        for candidate, override in _env_files():
            if os.path.exists(candidate):
                load_dotenv(candidate, override=override)
        _loaded = True

    if not usecase or load_dotenv is None:
        return
    fragment = os.path.join(_env_dir(), "docs", f"usecase_{usecase.strip().lower()}.env")
    if fragment not in _loaded_usecase_files and os.path.exists(fragment):
        load_dotenv(fragment, override=False)
        _loaded_usecase_files.add(fragment)


def env_key(usecase: str, publisher: str, source: str, access: str, key: str) -> str:
    return f"{usecase}__{publisher}__{source}__{access}__{key}".upper()


def get(usecase: str, publisher: str, source: str, access: str, key: str, default: Any = None) -> Any:
    load_env(usecase)
    return os.environ.get(env_key(usecase, publisher, source, access, key), default)


def get_raw(key: str, default: Any = None) -> Any:
    load_env()
    return os.environ.get(key, default)


def load_config(
    usecase: str, publisher: str, source: str, access: str, require_url: bool = True
) -> Dict[str, Any]:
    """Build the flattened config dict for a usecase/publisher/source/access tuple.

    ``require_url=False`` is used for later pipeline steps that receive their URL
    from a preceding extractor (e.g. scraper -> excel).
    """
    if not usecase or not publisher or not source or not access:
        raise ConfigError("usecase, publisher, source and access are required")

    usecase = usecase.strip().lower()
    publisher = publisher.strip().lower()
    source = source.strip().lower()
    access = access.strip().lower()

    cfg: Dict[str, Any] = {
        "usecase": usecase,
        "publisher": publisher,
        "source": source,
        "access": access,
        "raw": {},
    }
    for key in KNOWN_KEYS:
        value = get(usecase, publisher, source, access, key)
        if value is not None:
            cfg[key.lower()] = value
            cfg["raw"][key] = value

    cfg.setdefault("target", "none" if access == "pdf" else "postgres")

    if require_url and not (cfg.get("url") or cfg.get("pdf_url") or cfg.get("source_file")):
        raise ConfigError(
            f"Missing required configuration: {env_key(usecase, publisher, source, access, 'URL')}"
        )

    return cfg


def resolve_credentials(usecase: str, publisher: str, source: str, access: str) -> Dict[str, Optional[str]]:
    """Return credential-like values without ever logging them."""
    return {
        "api_key": get(usecase, publisher, source, access, "API_KEY"),
        "token": get(usecase, publisher, source, access, "TOKEN"),
    }
