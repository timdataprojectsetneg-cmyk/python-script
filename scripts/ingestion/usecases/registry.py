"""Convention-based discovery of use case modules.

Naming convention (no core changes needed to add a use case):

    usecases/<usecase>/<publisher>/<source>/extractor.py   -> class Extractor
    usecases/<usecase>/<publisher>/<source>/normalizer.py  -> class Normalizer
    usecases/<usecase>/<publisher>/<source>/models.py      -> class Record (optional)

Each source owns exactly one extractor, which is free to combine several
retrieval steps internally (e.g. scrape a landing page, then download the Excel
it links to). There is no per-source data-access dimension.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from ..core.base.extractor import BaseExtractor
from ..core.base.normalizer import BaseNormalizer
from ..core.normalizers.generic_normalizer import GenericNormalizer, PassthroughNormalizer
from ..exceptions import ConfigError

logger = logging.getLogger("ingestion")


def _import(module_path: str) -> Optional[Any]:
    try:
        return importlib.import_module(module_path)
    except ModuleNotFoundError:
        return None


def _package_path(module_path: str) -> Optional[Path]:
    try:
        spec = importlib.util.find_spec(module_path)
    except (ModuleNotFoundError, ValueError):
        return None
    if not spec or not spec.submodule_search_locations:
        return None
    return Path(next(iter(spec.submodule_search_locations)))


def base_module(usecase: str, publisher: str, source: str) -> str:
    return f"ingestion.usecases.{usecase}.{publisher}.{source}"


def list_usecases() -> List[str]:
    """Use case folders under ``ingestion/usecases``."""
    directory = _package_path("ingestion.usecases")
    if not directory or not directory.is_dir():
        return []
    return sorted(
        item.name
        for item in directory.iterdir()
        if item.is_dir() and not item.name.startswith("_") and item.name != "__pycache__"
    )


def list_publishers(usecase: str) -> List[str]:
    """Publisher folders under a use case."""
    directory = _package_path(f"ingestion.usecases.{usecase}")
    if not directory or not directory.is_dir():
        return []
    return sorted(
        item.name
        for item in directory.iterdir()
        if item.is_dir() and not item.name.startswith("_") and item.name != "__pycache__"
    )


def list_sources(usecase: str, publisher: str) -> List[str]:
    """Source folders under a use case publisher."""
    directory = _package_path(f"ingestion.usecases.{usecase}.{publisher}")
    if not directory or not directory.is_dir():
        return []
    return sorted(
        item.name
        for item in directory.iterdir()
        if item.is_dir() and not item.name.startswith("_") and item.name != "__pycache__"
    )


def find_publisher(usecase: str, source: str) -> Optional[str]:
    """Locate the publisher folder that contains ``source``."""
    for publisher in list_publishers(usecase):
        if _package_path(f"ingestion.usecases.{usecase}.{publisher}.{source}"):
            return publisher
    return None


def resolve_extractor_class(usecase: str, publisher: str, source: str) -> Type[BaseExtractor]:
    """Concrete ``Extractor`` class for a source."""
    mod = _import(f"{base_module(usecase, publisher, source)}.extractor")
    if mod is not None and hasattr(mod, "Extractor"):
        return mod.Extractor
    raise ConfigError(
        f"No extractor found for '{usecase}/{publisher}/{source}'. "
        "Add <source>/extractor.py exposing class Extractor."
    )


def resolve_extractor(usecase: str, publisher: str, source: str, config: Dict[str, Any]) -> BaseExtractor:
    return resolve_extractor_class(usecase, publisher, source)(config)


def resolve_normalizer(usecase: str, publisher: str, source: str, config: Dict[str, Any]) -> BaseNormalizer:
    mod = _import(f"{base_module(usecase, publisher, source)}.normalizer")
    if mod is not None and hasattr(mod, "Normalizer"):
        return mod.Normalizer(config)
    model_mod = _import(f"{base_module(usecase, publisher, source)}.models")
    if model_mod is None:
        model_mod = _import(f"ingestion.usecases.{usecase}.models")
    model = getattr(model_mod, "Record", None) if model_mod else None
    if model is None:
        # No normalizer and no Pydantic Record/dictionary: skip normalization.
        logger.warning(
            "No normalizer/Record (dictionary/model) for %s/%s/%s — skipping normalization "
            "(extractor → load, records passed through as-is)",
            usecase,
            publisher,
            source,
        )
        return PassthroughNormalizer(config)
    return GenericNormalizer(config, model=model)
