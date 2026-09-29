"""Parse SharePoint catalog / Data Dictionary tables into a structured manifest."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

CATALOG_COLUMNS = {
    "source_name": ["Source Name", "nama sumber", "nama source", "source"],
    "module_name": ["Module Name", "Folder Name", "Alias", "Slug", "Nama Modul"],
    "publisher": ["Publisher", "penerbit", "instansi"],
    "data_dictionary": ["Data Dictionary", "kamus data"],
    "source_link": ["Source Link", "link sumber", "link"],
    "data_access": ["Data Access", "akses data", "access"],
    "update_frequency": ["Update Frequency", "frekuensi", "frequency"],
    "is_official": ["Is Official", "official", "resmi"],
    "last_update": ["Last Update", "update terakhir"],
    "eligible": ["Eligible", "layak"],
    "data_engineer": ["Data Engineer"],
    "raw_minio_bucket": ["Raw Minio", "minio bucket"],
    "raw_es_index": ["Raw ES"],
    "raw_postgre_schema": ["Raw Postgre", "raw postgres"],
    "raw_scheduler": ["Raw Scheduler"],
    "cleaned_es_index": ["Cleaned ES"],
    "cleaned_postgre_schema": ["Cleaned Postgre", "cleaned postgres"],
    "cleaned_scheduler": ["Cleaned Scheduler"],
}

TARGET_FIELDS = (
    ("raw_minio_bucket", "Raw MinIO bucket"),
    ("raw_es_index", "Raw ES index"),
    ("raw_postgre_schema", "Raw PostgreSQL schema"),
    ("raw_scheduler", "Raw scheduler"),
    ("cleaned_es_index", "Cleaned ES index"),
    ("cleaned_postgre_schema", "Cleaned PostgreSQL schema"),
    ("cleaned_scheduler", "Cleaned scheduler"),
)


def _normalize_key(key: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(key or "").lower())


def _pick(row: Dict[str, Any], aliases: List[str]) -> Any:
    normalized = {_normalize_key(k): v for k, v in row.items()}
    for alias in aliases:
        key = _normalize_key(alias)
        if key in normalized and normalized[key] not in (None, ""):
            return normalized[key]
    # Fallback: substring match (handles headers like "Eligible\n(Layak ...)").
    for alias in aliases:
        key = _normalize_key(alias)
        if not key:
            continue
        for norm_key, value in normalized.items():
            if key in norm_key and value not in (None, ""):
                return value
    return None


def parse_catalog_row(row: Dict[str, Any]) -> Dict[str, Any]:
    source = {field: _pick(row, aliases) for field, aliases in CATALOG_COLUMNS.items()}
    links = row.get("_links") or {}
    source["data_dictionary_link"] = _pick_link(links, ["Data Dictionary", "kamus data"])
    source["source_link"] = source.get("source_link") or _pick_link(links, ["Source Link", "link sumber"])
    return source


def _pick_link(links: Dict[str, str], aliases: List[str]) -> Any:
    for alias in aliases:
        key = _normalize_key(alias)
        for column, url in links.items():
            if key and (key == _normalize_key(column) or key in _normalize_key(column)):
                return url
    return None


def is_eligible(source: Dict[str, Any]) -> bool:
    """Eligible is true only for the sources that should be implemented."""
    value = source.get("eligible")
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in ("true", "yes", "y", "1", "ya")


def is_source_row(source: Dict[str, Any]) -> bool:
    """Keep real data-source rows; drop section titles and empty filler rows."""
    if not source.get("source_name"):
        return False
    return bool(source.get("source_link") or source.get("data_access") or source.get("update_frequency"))


def source_slug(source: Dict[str, Any]) -> str:
    """Folder slug for a source: explicit Module Name override, else derived."""
    override = source.get("module_name")
    if override:
        return derive_module_name(str(override))
    return derive_module_name(str(source.get("source_name") or ""))


def to_snake_case(value: Any) -> str:
    """Lowercase with underscore separators, e.g. ``Jenis_Perselisihan`` -> ``jenis_perselisihan``."""
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _blank_cell(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and value != value:  # NaN
        return True
    return isinstance(value, str) and not value.strip()


DICTIONARY_HEADER_ALIASES = {
    "label": ("label", "nama kolom", "kolom", "field", "variabel"),
    "type": ("tipe data", "data type", "tipe", "type"),
    "satuan": ("satuan", "unit"),
    "deskripsi": ("deskripsi", "description", "keterangan"),
}


def parse_dictionary_matrix(matrix: List[List[Any]]) -> List[Dict[str, Any]]:
    """Parse a Data Dictionary sheet from a raw matrix.

    Reading **starts** at the header row containing Label / Tipe Data / Satuan /
    Deskripsi and **ends** at the first fully-empty row. Column names are
    normalized to lower snake_case (``name``), keeping the original ``label``.
    """
    if not matrix:
        return []

    header_index = None
    columns: Dict[str, int] = {}
    for index, row in enumerate(matrix):
        normalized = [_normalize_key(cell) for cell in row]
        found: Dict[str, int] = {}
        for field, aliases in DICTIONARY_HEADER_ALIASES.items():
            for alias in aliases:
                key = _normalize_key(alias)
                if key and key in normalized:
                    found[field] = normalized.index(key)
                    break
        if len(found) == len(DICTIONARY_HEADER_ALIASES):
            header_index, columns = index, found
            break

    if header_index is None:
        return []

    def value(row: List[Any], field: str) -> Any:
        idx = columns[field]
        if idx >= len(row) or _blank_cell(row[idx]):
            return None
        return row[idx]

    schema: List[Dict[str, Any]] = []
    for row in matrix[header_index + 1:]:
        if all(_blank_cell(cell) for cell in row):
            break  # end of the dictionary table
        label = value(row, "label")
        if label is None:
            continue
        schema.append(
            {
                "label": label,
                "name": to_snake_case(label),
                "type": value(row, "type"),
                "satuan": value(row, "satuan"),
                "deskripsi": value(row, "deskripsi"),
            }
        )
    return schema


MAX_SLUG_LENGTH = 48


def derive_module_name(source_name: str) -> str:
    """Slug a name into a snake_case module/folder name.

    Parentheticals are dropped and long names are capped on a word boundary.
    Use the catalog ``Module Name`` column to override with a preferred acronym.
    """
    text = re.sub(r"\([^)]*\)", " ", str(source_name or "").strip())
    name = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    if len(name) > MAX_SLUG_LENGTH:
        parts: List[str] = []
        total = 0
        for word in name.split("_"):
            extra = len(word) + (1 if parts else 0)
            if total + extra > MAX_SLUG_LENGTH:
                break
            parts.append(word)
            total += extra
        name = "_".join(parts) or name[:MAX_SLUG_LENGTH].rstrip("_")
    return name


def to_pydantic_source(class_name: str, schema: List[Dict[str, Any]]) -> str:
    """Generate a Pydantic model source snippet from Data Dictionary entries."""
    type_map = {
        "integer": "int",
        "int": "int",
        "number": "float",
        "float": "float",
        "decimal": "float",
        "date": "str",
        "datetime": "str",
        "boolean": "bool",
        "bool": "bool",
    }
    lines = ["from pydantic import BaseModel, Field", "", "", f"class {class_name}(BaseModel):"]
    for field in schema:
        label = field.get("label") or "field"
        field_type = type_map.get(str(field.get("type") or "").strip().lower(), "str")
        safe_name = field.get("name") or to_snake_case(label) or "field"
        lines.append(
            f"    {safe_name}: {field_type} | None = Field(default=None, alias=\"{label}\")"
        )
    lines.append("")
    lines.append('    model_config = {"populate_by_name": True, "extra": "ignore"}')
    lines.append("")
    return "\n".join(lines)


ACCESS_KEYWORDS = (
    ("pdf", "pdf"),
    ("excel", "excel"),
    ("xls", "excel"),
    ("api", "api"),
    ("scrap", "scraper"),
    ("web", "scraper"),
    ("crawl", "scraper"),
)


def normalize_name(value: str) -> str:
    """Lowercase and strip every non-alphanumeric character (``Kasus Perselisihan`` -> ``kasusperselisihan``)."""
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def derive_access(data_access: Any) -> str:
    """Map a free-text Data Access value to a leaf module name."""
    text = str(data_access or "").strip().lower()
    for keyword, access in ACCESS_KEYWORDS:
        if re.search(rf"(?<![a-z]){re.escape(keyword)}", text):
            return access
    return "excel"


def resolve_sheet_name(sheet_names: List[str], target: str) -> str | None:
    """Find the catalog/dictionary sheet matching ``target`` (usecase or source name)."""
    wanted = normalize_name(target)
    if not wanted:
        return None
    normalized = {normalize_name(name): name for name in sheet_names}
    if wanted in normalized:
        return normalized[wanted]
    for norm, original in normalized.items():
        if norm and (norm in wanted or wanted in norm):
            return original
    return None
