"""Scaffold use case module folders/files from the SharePoint catalog.

Only sources with ``Eligible = true`` are scaffolded. Existing files are never
overwritten — they are reported as skipped.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from .metadata_parser import derive_access, derive_module_name, publisher_slug, source_slug, to_pydantic_source

EXTRACTOR_BASES = {
    "excel": ("ExcelExtractor", "core.extractors.excel_extractor"),
    "api": ("ApiExtractor", "core.extractors.api_extractor"),
    "scraper": ("WebScraper", "core.extractors.web_scraper"),
    "pdf": ("PdfExtractor", "core.extractors.pdf_extractor"),
}

EMPTY = ""


def _models_source(source_name: str, schema: List[Dict[str, Any]]) -> str:
    header = f'"""Pydantic schema — {source_name} (mirrors the Data Dictionary)."""\n\n'
    if schema:
        return header + to_pydantic_source("Record", schema) + "\n"
    return (
        header
        + "from pydantic import BaseModel, ConfigDict\n\n\n"
        + "class Record(BaseModel):\n"
        + '    """TODO: fill fields from docs/dictionary_<usecase>_<source>.md."""\n\n'
        + "    model_config = ConfigDict(extra=\"ignore\", populate_by_name=True)\n"
    )


def _normalizer_source(source_name: str) -> str:
    return f'''"""Normalizer — {source_name}."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterator

from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)


class Normalizer(BaseNormalizer):
    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                yield Record(**raw).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed, record skipped: %s", exc)
'''


def _extractor_source(source_name: str, access: str) -> str:
    base, module = EXTRACTOR_BASES.get(access, EXTRACTOR_BASES["excel"])
    return f'''"""{access.capitalize()} access — {source_name}."""

from __future__ import annotations

from ......{module} import {base}


class Extractor({base}):
    """Implemented per source; falls back to the generic {access} extractor."""
'''


def scaffold_usecase(
    root: str,
    usecase: str,
    sources: List[Dict[str, Any]],
    schemas: Dict[str, List[Dict[str, Any]]] | None = None,
) -> Tuple[List[str], List[str]]:
    """Create folders/files for eligible sources. Returns (created, skipped)."""
    schemas = schemas or {}
    usecase_dir = Path(root) / derive_module_name(usecase)
    created: List[str] = []
    skipped: List[str] = []

    for source in sources:
        slug = source_slug(source)
        if not slug:
            continue
        publisher = publisher_slug(source)
        source_dir = usecase_dir / publisher / slug
        access = derive_access(source.get("data_access"))
        source_name = str(source.get("source_name") or slug)

        files: Dict[Path, str] = {
            usecase_dir / publisher / "__init__.py": EMPTY,
            source_dir / "__init__.py": EMPTY,
            source_dir / "models.py": _models_source(source_name, schemas.get(slug, [])),
            source_dir / "normalizer.py": _normalizer_source(source_name),
            source_dir / access / "__init__.py": EMPTY,
            source_dir / access / "extractor.py": _extractor_source(source_name, access),
        }

        for path, content in files.items():
            if path.exists():
                skipped.append(str(path))
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created.append(str(path))

    return created, skipped
