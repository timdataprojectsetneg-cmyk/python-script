"""Scaffold use case module folders/files from the SharePoint catalog.

Only sources with ``Eligible = true`` are scaffolded. Existing files are skipped
by default; callers can explicitly opt into overwriting them.
"""

from __future__ import annotations

import ast
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Set, Tuple

from .metadata_parser import derive_access, derive_module_name, publisher_slug, source_slug, to_pydantic_source

__all__ = ["merge_models_source", "remove_ineligible_sources", "scaffold_usecase"]

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
        + '    """TODO: fill fields from docs/<usecase>/dictionary_<source>.md."""\n\n'
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
    return f'''"""Extractor — {source_name}.

Scaffolded from the catalog Data Access '{access}'; the extractor may combine
several retrieval steps internally (e.g. scrape a page, then download the Excel
it links to).
"""

from __future__ import annotations

from .....{module} import {base}


class Extractor({base}):
    """Implemented per source; subclass the generic base and override as needed."""
'''


def _iter_fields(cls: ast.ClassDef):
    """Yield ``(name, node)`` for each Pydantic field (``name: T = Field(...)``)."""
    for node in cls.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            yield node.target.id, node


def _is_plain_field(segment: str) -> bool:
    """True when a field definition looks generated (safe to regenerate).

    Hand-customized fields (multi-line, custom ``validation_alias`` /
    ``AliasChoices``) are treated as custom code and left untouched.
    """
    stripped = segment.strip()
    return (
        "\n" not in stripped
        and "validation_alias" not in stripped
        and "AliasChoices" not in stripped
    )


def _field_insert_line(cls: ast.ClassDef) -> int:
    """Line before which new fields should be inserted (before methods/assigns)."""
    last_field_end: Optional[int] = None
    for node in cls.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            last_field_end = node.end_lineno
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign)):
            return node.lineno
    if last_field_end is not None:
        return last_field_end + 1
    if cls.body:
        return cls.body[0].lineno
    return cls.lineno + 1


def _field_segment(source: str, node: ast.AST) -> str:
    """Source text of a field, re-indented to its original column."""
    text = ast.get_source_segment(source, node) or ""
    if "\n" in text:
        return text
    return " " * getattr(node, "col_offset", 0) + text


def _import_insert_line(tree: ast.Module) -> int:
    """Line after which new import statements should be inserted."""
    last_import_end: Optional[int] = None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            last_import_end = node.end_lineno
        elif last_import_end is None and isinstance(node, ast.Expr):
            return node.end_lineno + 1
    if last_import_end is not None:
        return last_import_end + 1
    return 1


def _imported_names(tree: ast.Module) -> Dict[str, Set[str]]:
    modules: Dict[str, Set[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            modules.setdefault(node.module or "", set()).update(a.name for a in node.names)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.setdefault(alias.name, set()).add(alias.name)
    return modules


def merge_models_source(existing: str, generated: str) -> str:
    """Sync generated Pydantic fields into an existing ``models.py``.

    Regenerates the model classes from the Data Dictionary (fields, nested
    classes, imports) while preserving hand-written code: the module docstring,
    extra imports, extra classes, methods, ``Record = <Custom>`` rebinds, and
    any custom field definition (multi-line or using ``validation_alias`` /
    ``AliasChoices``). New dictionary fields are added; plain generated fields
    are updated in place.
    """
    if not existing.strip():
        return generated
    try:
        existing_tree = ast.parse(existing)
        generated_tree = ast.parse(generated)
    except SyntaxError:
        return existing

    ex_classes = {n.name: n for n in existing_tree.body if isinstance(n, ast.ClassDef)}
    alias: Dict[str, str] = {}
    for node in existing_tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
            if isinstance(target, ast.Name) and isinstance(value, ast.Name):
                alias[target.id] = value.id

    lines = existing.splitlines()
    edits: List[Tuple[int, int, str]] = []
    appends: List[str] = []

    for gen_cls in (n for n in generated_tree.body if isinstance(n, ast.ClassDef)):
        target_name = gen_cls.name
        if gen_cls.name == "Record" and "Record" not in ex_classes:
            target_name = alias.get("Record", gen_cls.name)
        ex_cls = ex_classes.get(target_name)
        if ex_cls is None:
            appends.append(ast.get_source_segment(generated, gen_cls))
            continue

        ex_fields = {name: node for name, node in _iter_fields(ex_cls)}
        missing: List[str] = []
        for name, gen_node in _iter_fields(gen_cls):
            gen_segment = _field_segment(generated, gen_node)
            ex_node = ex_fields.get(name)
            if ex_node is None:
                missing.append(gen_segment)
                continue
            ex_segment = "\n".join(lines[ex_node.lineno - 1 : ex_node.end_lineno])
            if _is_plain_field(ex_segment):
                edits.append((ex_node.lineno, ex_node.end_lineno, gen_segment))
        if missing:
            insert_at = _field_insert_line(ex_cls)
            edits.append((insert_at, insert_at - 1, "\n".join(missing)))

    needed = _imported_names(generated_tree)
    have = _imported_names(existing_tree)
    import_lines = [
        f"from {module} import {', '.join(sorted(names - have.get(module, set())))}"
        for module, names in needed.items()
        if names - have.get(module, set())
    ]
    if import_lines:
        insert_at = _import_insert_line(existing_tree)
        edits.append((insert_at, insert_at - 1, "\n".join(import_lines)))

    for start, end, text in sorted(edits, key=lambda e: e[0], reverse=True):
        boundary = end if end >= start else start - 1
        lines[start - 1 : boundary] = text.splitlines()

    result = "\n".join(lines).rstrip("\n")
    for segment in appends:
        result += "\n\n\n" + segment
    return result + "\n"



def scaffold_usecase(
    root: str,
    usecase: str,
    sources: List[Dict[str, Any]],
    schemas: Dict[str, List[Dict[str, Any]]] | None = None,
    overwrite: bool = False,
) -> Tuple[List[str], List[str]]:
    """Create folders/files for eligible sources.

    Returns ``(created_or_overwritten, skipped)``. Existing files are only
    overwritten when ``overwrite`` is explicitly enabled.
    """
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

        models_path = source_dir / "models.py"
        files: Dict[Path, str] = {
            usecase_dir / publisher / "__init__.py": EMPTY,
            source_dir / "__init__.py": EMPTY,
            source_dir / "normalizer.py": _normalizer_source(source_name),
            source_dir / "extractor.py": _extractor_source(source_name, access),
        }

        generated_models = _models_source(source_name, schemas.get(slug, []))
        if models_path.exists() and not overwrite:
            current = models_path.read_text(encoding="utf-8")
            merged = merge_models_source(current, generated_models)
            if merged == current:
                skipped.append(str(models_path))
            else:
                models_path.write_text(merged, encoding="utf-8")
                created.append(str(models_path))
        else:
            files[models_path] = generated_models

        for path, content in files.items():
            if path.exists() and not overwrite:
                skipped.append(str(path))
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            created.append(str(path))

    return created, skipped


def remove_ineligible_sources(
    root: str,
    usecase: str,
    eligible_sources: List[Dict[str, Any]],
    publishers: Optional[Set[str]] = None,
    sources: Optional[Set[str]] = None,
) -> List[str]:
    """Remove generated source structures no longer marked eligible.

    Traversal is limited to ``publishers`` / ``sources`` when given, so a scoped
    run (``--publisher`` / ``--source``) never deletes other sources.
    """
    usecase_dir = Path(root) / derive_module_name(usecase)
    allowed = {(publisher_slug(source), source_slug(source)) for source in eligible_sources}
    removed: List[str] = []
    if not usecase_dir.is_dir():
        return removed
    for publisher_dir in usecase_dir.iterdir():
        if not publisher_dir.is_dir() or publisher_dir.name.startswith("__"):
            continue
        if publishers is not None and publisher_dir.name not in publishers:
            continue
        for source_dir in publisher_dir.iterdir():
            if not source_dir.is_dir():
                continue
            if sources is not None and source_dir.name not in sources:
                continue
            if (publisher_dir.name, source_dir.name) not in allowed:
                shutil.rmtree(source_dir)
                removed.append(str(source_dir))
        if not any(publisher_dir.iterdir()):
            publisher_dir.rmdir()
            removed.append(str(publisher_dir))
    return removed
