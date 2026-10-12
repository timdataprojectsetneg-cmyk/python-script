"""Parse SharePoint catalog / Data Dictionary tables into a structured manifest."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

CATALOG_COLUMNS = {
    "source_name": ["Source Name", "nama sumber", "nama source", "source"],
    "module_name": ["Module Name", "Folder Name", "Alias", "Slug", "Nama Modul"],
    "publisher": ["Publisher", "penerbit", "instansi"],
    "data_dictionary": ["Data Dictionary", "kamus data"],
    "source_link": ["Source Link", "link sumber", "link"],
    "resource_url": ["Resource URL", "Resource Url", "resource url", "resource"],
    "data_access": ["Data Access", "akses data", "access"],
    "update_frequency": ["Update Frequency", "frekuensi", "frequency"],
    "is_official": ["Is Official", "official", "resmi"],
    "last_update": ["Last Update", "update terakhir"],
    "eligible": ["Eligible", "layak"],
    "data_engineer": ["Data Engineer"],
    "raw_minio_bucket": ["Raw Minio", "minio bucket"],
    "raw_es_index": ["Raw ES"],
    "raw_postgre_table": ["Raw Postgre", "raw postgres"],
    "raw_scheduler": ["Raw Scheduler"],
    "cleaned_es_index": ["Cleaned ES"],
    "cleaned_postgre_table": ["Cleaned Postgre", "cleaned postgres"],
    "cleaned_scheduler": ["Cleaned Scheduler"],
}

TARGET_FIELDS = (
    ("raw_minio_bucket", "Raw MinIO bucket"),
    ("raw_es_index", "Raw ES index"),
    ("raw_postgre_table", "Raw PostgreSQL schema"),
    ("raw_scheduler", "Raw scheduler"),
    ("cleaned_es_index", "Cleaned ES index"),
    ("cleaned_postgre_table", "Cleaned PostgreSQL schema"),
    ("cleaned_scheduler", "Cleaned scheduler"),
)


def split_postgre(value: Any) -> tuple[Optional[str], Optional[str]]:
    """Split ``schema.table`` into (schema, "schema.table"). Table-only -> (None, value)."""
    text = str(value or "").strip()
    if not text:
        return None, None
    if "." in text:
        schema, table = text.split(".", 1)
        schema = schema.strip()
        table = table.strip()
        return (schema or None), (f"{schema}.{table}" if schema else table)
    return None, text


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
    source["resource_url"] = source.get("resource_url") or _pick_link(links, ["Resource URL", "resource"])

    # Normalized load targets.
    source["minio_bucket"] = source.get("raw_minio_bucket")
    source["es_index"] = source.get("raw_es_index")
    schema, table = split_postgre(source.get("raw_postgre_table"))
    source["postgre_schema"] = schema
    source["postgre_table"] = table
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
    return bool(
        source.get("source_link")
        or source.get("resource_url")
        or source.get("data_access")
        or source.get("update_frequency")
    )


def effective_url(source: Dict[str, Any]) -> Any:
    """URL to ingest from: ``Resource URL`` when set, else ``Source Link``."""
    return source.get("resource_url") or source.get("source_link")


def source_slug(source: Dict[str, Any]) -> str:
    """Folder slug for a source: explicit Module Name override, else derived."""
    override = source.get("module_name")
    if override:
        return derive_module_name(str(override))
    return derive_module_name(str(source.get("source_name") or ""))


def publisher_slug(source: Dict[str, Any]) -> str:
    """Folder slug for a publisher (e.g. ``Kemnaker`` -> ``kemnaker``)."""
    return derive_module_name(str(source.get("publisher") or "")) or "unknown"


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

# Minimum columns needed to treat a row as a dictionary header.
DICTIONARY_REQUIRED_HEADERS = ("label", "type")


def _detect_dictionary_header(row: List[Any]) -> Optional[Dict[str, int]]:
    """Return column indexes for a Label/Tipe Data header row, else None.

    Matching is exact first, then substring, so headers such as
    ``Tipe Data (opsional)`` are still recognised.
    """
    normalized = [_normalize_key(cell) for cell in row]
    found: Dict[str, int] = {}
    for field, aliases in DICTIONARY_HEADER_ALIASES.items():
        for alias in aliases:
            key = _normalize_key(alias)
            if not key:
                continue
            if key in normalized:
                found[field] = normalized.index(key)
                break
            match = next((i for i, cell in enumerate(normalized) if key in cell), None)
            if match is not None:
                found[field] = match
                break
    if all(field in found for field in DICTIONARY_REQUIRED_HEADERS):
        return found
    return None


def _section_title(matrix: List[List[Any]], header_index: int) -> str:
    """Text of the nearest non-blank row above a header (e.g. ``Data Dictionary : putusan``)."""
    for index in range(header_index - 1, -1, -1):
        row = matrix[index]
        if all(_blank_cell(cell) for cell in row):
            continue
        text = " ".join(str(cell).strip() for cell in row if not _blank_cell(cell)).strip()
        if text:
            return text
    return ""


def _title_key(title: str) -> str:
    """Normalized key of a sub-table title: text after ``:`` (``Data Dictionary : putusan`` -> ``putusan``)."""
    text = title.split(":", 1)[1] if ":" in title else title
    return _normalize_key(text)


def _match_field(schema: List[Dict[str, Any]], key: str) -> Optional[Dict[str, Any]]:
    """Find the field a JSON sub-table belongs to, by name/label match."""
    if not key:
        return None
    partial: List[Dict[str, Any]] = []
    for field in schema:
        names = (_normalize_key(field.get("name")), _normalize_key(field.get("label")))
        if key in names:
            return field
        if any(key in name or name in key for name in names if name):
            partial.append(field)
    return partial[0] if len(partial) == 1 else None


def _parse_dictionary_rows(
    matrix: List[List[Any]], header_index: int, end_index: int, columns: Dict[str, int]
) -> List[Dict[str, Any]]:
    def value(row: List[Any], field: str) -> Any:
        idx = columns.get(field)
        if idx is None or idx >= len(row) or _blank_cell(row[idx]):
            return None
        return row[idx]

    rows: List[Dict[str, Any]] = []
    for row in matrix[header_index + 1 : end_index]:
        if all(_blank_cell(cell) for cell in row):
            continue
        label = value(row, "label")
        if label is None:
            continue
        rows.append(
            {
                "label": label,
                "name": to_snake_case(label),
                "type": value(row, "type"),
                "satuan": value(row, "satuan"),
                "deskripsi": value(row, "deskripsi"),
            }
        )
    return rows


def parse_dictionary_matrix(matrix: List[List[Any]]) -> List[Dict[str, Any]]:
    """Parse a Data Dictionary sheet from a raw matrix.

    The first ``Label / Tipe Data / Satuan / Deskripsi`` table is the record
    schema. Any later table introduced by a ``Data Dictionary : <field>`` title is
    attached as ``fields`` on the matching field, giving the shape of JSON
    columns. Column names are lower snake_case (``name``), keeping the original
    ``label``.
    """
    if not matrix:
        return []

    blocks: List[Dict[str, Any]] = []
    index = 0
    total = len(matrix)
    while index < total:
        header = _detect_dictionary_header(matrix[index]) if matrix[index] else None
        if header is None:
            index += 1
            continue
        end = index + 1
        while end < total and not all(_blank_cell(cell) for cell in matrix[end]):
            end += 1
        blocks.append(
            {
                "title": _section_title(matrix, index),
                "rows": _parse_dictionary_rows(matrix, index, end, header),
            }
        )
        index = end

    if not blocks:
        return []

    schema = blocks[0]["rows"]
    for block in blocks[1:]:
        target = _match_field(schema, _title_key(block["title"]))
        if target is not None and block["rows"]:
            target["fields"] = block["rows"]
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


PYDANTIC_TYPE_MAP = {
    "integer": "int",
    "int": "int",
    "number": "float",
    "float": "float",
    "decimal": "float",
    "date": "date",
    "datetime": "datetime",
    "boolean": "bool",
    "bool": "bool",
    "json": "dict[str, Any]",
    "object": "dict[str, Any]",
    "dict": "dict[str, Any]",
}


def _pascal_case(value: Any) -> str:
    parts = re.split(r"[^a-z0-9]+", str(value or "").lower())
    return "".join(part.capitalize() for part in parts if part) or "Nested"


def _field_description(field: Dict[str, Any]) -> Optional[str]:
    """Description for a field: its own ``Deskripsi``, else the nested JSON fields'."""
    desc = field.get("deskripsi")
    if isinstance(desc, str) and desc.strip():
        return desc.strip()
    parts = []
    for sub in field.get("fields") or []:
        sub_desc = sub.get("deskripsi")
        if isinstance(sub_desc, str) and sub_desc.strip():
            label = sub.get("name") or sub.get("label")
            parts.append(f"{label}: {sub_desc.strip()}")
    return "; ".join(parts) if parts else None


def _field_kwargs(field: Dict[str, Any]) -> str:
    label = field.get("label") or field.get("name") or "field"
    args = ["default=None", f'alias="{label}"']
    desc = _field_description(field)
    if desc:
        escaped = desc.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
        args.append(f'description="{escaped}"')
    return ", ".join(args)


def to_pydantic_source(class_name: str, schema: List[Dict[str, Any]]) -> str:
    """Generate a Pydantic model source snippet from Data Dictionary entries.

    Fields with a nested ``fields`` list become their own ``BaseModel`` class, so
    JSON columns are typed instead of stringified. Dictionary descriptions become
    ``Field(description=...)``; the PostgreSQL loader reuses them as column
    comments.
    """
    classes: List[str] = []
    used_names = {class_name}
    needs_any = False
    needs_date = False
    needs_datetime = False

    def render(name: str, fields: List[Dict[str, Any]]) -> None:
        nonlocal needs_any, needs_date, needs_datetime
        body: List[str] = []
        for field in fields:
            label = field.get("label") or "field"
            safe_name = field.get("name") or to_snake_case(label) or "field"
            nested = field.get("fields")
            if nested:
                nested_name = _pascal_case(field.get("name") or label)
                while nested_name in used_names:
                    nested_name += "Item"
                used_names.add(nested_name)
                render(nested_name, nested)
                annotation = nested_name
            else:
                annotation = PYDANTIC_TYPE_MAP.get(
                    str(field.get("type") or "").strip().lower(), "str"
                )
                needs_any = needs_any or annotation == "dict[str, Any]"
                needs_date = needs_date or annotation == "date"
                needs_datetime = needs_datetime or annotation == "datetime"
            body.append(
                f"    {safe_name}: {annotation} | None = Field({_field_kwargs(field)})"
            )
        body.append("")
        body.append('    model_config = {"populate_by_name": True, "extra": "ignore"}')
        classes.append(f"class {name}(BaseModel):\n" + "\n".join(body))

    render(class_name, schema)

    imports: List[str] = []
    datetime_names = [n for n, flag in (("date", needs_date), ("datetime", needs_datetime)) if flag]
    if datetime_names:
        imports.append("from datetime import " + ", ".join(datetime_names))
    if needs_any:
        imports.append("from typing import Any")
    imports.append("from pydantic import BaseModel, Field")
    return "\n".join(imports) + "\n\n\n" + "\n\n\n".join(classes) + "\n"


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
