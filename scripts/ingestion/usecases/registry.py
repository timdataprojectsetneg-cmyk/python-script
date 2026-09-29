"""Convention-based discovery of use case modules.

Naming convention (no core changes needed to add a use case):

    usecases/<usecase>/<source>/normalizer.py       -> class Normalizer
    usecases/<usecase>/<source>/models.py           -> class Record (optional)
    usecases/<usecase>/<source>/<access>/extractor.py -> class Extractor

When a source does not define its own extractor, the generic implementation for
the access type is used.
"""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any, Dict, List, Optional, Type

from ..core.base.extractor import BaseExtractor
from ..core.base.normalizer import BaseNormalizer
from ..core.extractors.api_extractor import ApiExtractor
from ..core.extractors.excel_extractor import ExcelExtractor
from ..core.extractors.pdf_extractor import PdfExtractor
from ..core.extractors.web_scraper import WebScraper
from ..core.normalizers.generic_normalizer import GenericNormalizer
from ..exceptions import ConfigError

GENERIC_EXTRACTORS: Dict[str, Type[BaseExtractor]] = {
    "excel": ExcelExtractor,
    "api": ApiExtractor,
    "scraper": WebScraper,
    "pdf": PdfExtractor,
}

SUPPORTED_ACCESSES = ("excel", "api", "scraper", "pdf")

ACCESS_ALIASES = {"web": "scraper", "webscraper": "scraper", "scrape": "scraper"}


def normalize_access(access: str) -> str:
    key = (access or "").strip().lower()
    return ACCESS_ALIASES.get(key, key)


def _import(module_path: str) -> Optional[Any]:
    try:
        return importlib.import_module(module_path)
    except ModuleNotFoundError:
        return None


def _has_module(module_path: str) -> bool:
    try:
        return importlib.util.find_spec(module_path) is not None
    except (ModuleNotFoundError, ValueError):
        return False


def base_module(usecase: str, source: str) -> str:
    return f"ingestion.usecases.{usecase}.{source}"


def resolve_extractor_class(usecase: str, source: str, access: str) -> Type[BaseExtractor]:
    """Concrete extractor class for a source/access (source-specific or generic)."""
    access = normalize_access(access)
    mod = _import(f"{base_module(usecase, source)}.{access}.extractor")
    if mod is not None and hasattr(mod, "Extractor"):
        return mod.Extractor
    generic = GENERIC_EXTRACTORS.get(access)
    if generic is None:
        raise ConfigError(f"Unsupported data access: {access}")
    return generic


def resolve_extractor(usecase: str, source: str, access: str, config: Dict[str, Any]) -> BaseExtractor:
    return resolve_extractor_class(usecase, source, access)(config)


def available_accesses(usecase: str, source: str) -> List[str]:
    """Access methods with a source-specific ``<access>/extractor.py`` module."""
    return [
        access
        for access in SUPPORTED_ACCESSES
        if _has_module(f"{base_module(usecase, source)}.{access}.extractor")
    ]


def default_accesses(usecase: str, source: str) -> List[str]:
    """Resolve the access chain when ``--access`` is omitted.

    Order of precedence:
    1. ``EXTRACTORS`` (or ``ACCESS``) declared in ``usecases/<usecase>/<source>/config.py``.
    2. The single source-specific extractor module found on disk.
    """
    config_mod = _import(f"{base_module(usecase, source)}.config")
    declared = None
    if config_mod is not None:
        declared = getattr(config_mod, "EXTRACTORS", None) or getattr(config_mod, "ACCESS", None)
    if declared:
        if isinstance(declared, str):
            declared = [declared]
        return [normalize_access(item) for item in declared]

    available = available_accesses(usecase, source)
    if len(available) == 1:
        return available
    if len(available) > 1:
        raise ConfigError(
            f"Source '{source}' has multiple extractors ({', '.join(available)}); "
            "pass --access in order, or declare EXTRACTORS in the source config.py."
        )
    raise ConfigError(
        f"No extractor found for '{usecase}/{source}'. Pass --access (one of "
        f"{', '.join(SUPPORTED_ACCESSES)})."
    )


def resolve_normalizer(usecase: str, source: str, config: Dict[str, Any]) -> BaseNormalizer:
    mod = _import(f"{base_module(usecase, source)}.normalizer")
    if mod is not None and hasattr(mod, "Normalizer"):
        return mod.Normalizer(config)
    model_mod = _import(f"{base_module(usecase, source)}.models")
    if model_mod is None:
        model_mod = _import(f"ingestion.usecases.{usecase}.models")
    model = getattr(model_mod, "Record", None) if model_mod else None
    return GenericNormalizer(config, model=model)
