"""Read the generated Markdown docs back into catalog/schema structures.

``docs`` writes ``docs/<usecase>/usecase.md`` and
``docs/<usecase>/dictionary_<source>.md``. ``docs --scaffold`` consumes those
local files instead of syncing the catalog, so scaffolding works offline from
the docs written by a previous ``docs`` run.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ..exceptions import ConfigError
from .metadata_parser import derive_module_name, to_snake_case

__all__ = ["read_dictionary_schemas", "read_usecase_sources", "SOURCE_COLUMNS"]

SOURCE_COLUMNS = {
    "source_name": "Source Name",
    "publisher": "Publisher",
    "data_access": "Data Access",
    "update_frequency": "Update Frequency",
    "is_official": "Is Official",
    "eligible": "Eligible",
    "last_update": "Last Update",
    "source_link": "Source Link",
    "resource_url": "Resource URL",
    "data_dictionary": "Data Dictionary",
}

FIELD_COLUMNS = {
    "label": "Label",
    "name": "Name (column)",
    "type": "Tipe Data",
    "satuan": "Satuan",
    "deskripsi": "Deskripsi",
}

_LINK = re.compile(r"^\[(?P<text>.*)\]\((?P<url>[^)]*)\)$", re.DOTALL)
_JSON_HEADING = re.compile(r"^###\s+JSON field:\s+`(?P<name>[^`]+)`\s*(?:\((?P<label>.*)\))?\s*$")


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _cells(line: str) -> List[str]:
    """Split a Markdown table row on unescaped ``|`` and unescape ``\\|``."""
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    return [cell.replace("\\|", "|").strip() for cell in re.split(r"(?<!\\)\|", text)]


def _is_separator(cells: List[str]) -> bool:
    return bool(cells) and all(cell and set(cell) <= set("-: ") for cell in cells)


def _cell_text(value: str) -> str:
    """Normalize a cell: drop ``-`` placeholders, code ticks, and link markup."""
    text = value.strip()
    if text == "-":
        return ""
    text = text.strip("`").strip()
    match = _LINK.match(text)
    if match:
        label, url = match.group("text").strip(), match.group("url").strip()
        return label if label and label != "link" else url
    return text


def _table_after(lines: List[str], heading: str) -> Tuple[List[str], List[List[str]]]:
    """Return the ``(header, rows)`` of the Markdown table following ``heading``."""
    start = next((index for index, line in enumerate(lines) if line.strip() == heading), None)
    if start is None:
        return [], []
    index = start + 1
    while index < len(lines) and not lines[index].lstrip().startswith("|"):
        index += 1
    if index >= len(lines):
        return [], []
    header = _cells(lines[index])
    index += 1
    if index < len(lines) and _is_separator(_cells(lines[index])):
        index += 1
    rows: List[List[str]] = []
    while index < len(lines) and lines[index].lstrip().startswith("|"):
        rows.append(_cells(lines[index]))
        index += 1
    return header, rows


def _column_indexes(header: List[str], columns: Dict[str, str]) -> Dict[str, int]:
    normalized = {_norm(cell): index for index, cell in enumerate(header)}
    return {field: normalized[_norm(name)] for field, name in columns.items() if _norm(name) in normalized}


def _row_value(row: List[str], indexes: Dict[str, int], field: str) -> str:
    index = indexes.get(field)
    if index is None or index >= len(row):
        return ""
    return _cell_text(row[index])


def read_usecase_sources(docs_dir: Path) -> List[Dict[str, Any]]:
    """Parse the Sources table of ``docs/<usecase>/usecase.md``."""
    path = Path(docs_dir) / "usecase.md"
    if not path.is_file():
        raise ConfigError(
            f"Local docs not found: {path}. Generate them first with "
            "'python -m ingestion docs --usecase <usecase> --env <profile>'."
        )
    header, rows = _table_after(path.read_text(encoding="utf-8").splitlines(), "## Sources")
    indexes = _column_indexes(header, SOURCE_COLUMNS)
    if not indexes.get("source_name"):
        raise ConfigError(f"No Sources table found in {path}")
    sources = [
        {field: _row_value(row, indexes, field) for field in SOURCE_COLUMNS}
        for row in rows
    ]
    return [source for source in sources if source.get("source_name")]


def _read_fields(lines: List[str], heading: str) -> List[Dict[str, Any]]:
    header, rows = _table_after(lines, heading)
    indexes = _column_indexes(header, FIELD_COLUMNS)
    fields: List[Dict[str, Any]] = []
    for row in rows:
        label = _row_value(row, indexes, "label")
        if not label:
            continue
        fields.append(
            {
                "label": label,
                "name": _row_value(row, indexes, "name") or to_snake_case(label),
                "type": _row_value(row, indexes, "type") or None,
                "satuan": _row_value(row, indexes, "satuan") or None,
                "deskripsi": _row_value(row, indexes, "deskripsi") or None,
            }
        )
    return fields


def read_dictionary_schema(docs_dir: Path, filename: str) -> List[Dict[str, Any]]:
    """Parse one ``dictionary_<source>.md`` into its field schema.

    Nested ``### JSON field: <name>`` tables are attached as ``fields`` on the
    matching field, mirroring ``parse_dictionary_matrix``.
    """
    return _schema_from_lines(
        (Path(docs_dir) / filename).read_text(encoding="utf-8").splitlines()
    )


def _schema_from_lines(lines: List[str]) -> List[Dict[str, Any]]:
    schema = _read_fields(lines, "## Fields")
    for line in lines:
        match = _JSON_HEADING.match(line.strip())
        if not match:
            continue
        name = match.group("name").strip()
        target = next(
            (
                field
                for field in schema
                if name in (field["name"], field.get("label"))
                or _norm(name) in (_norm(field["name"]), _norm(field.get("label")))
            ),
            None,
        )
        nested = _read_fields(lines, line.strip())
        if target is not None and nested:
            target["fields"] = nested
    return schema


def _source_name(lines: List[str]) -> str:
    return next(
        (
            line.split(":", 1)[1].strip().strip("`").strip()
            for line in lines
            if line.strip().startswith("- Source:")
        ),
        "",
    )


def read_dictionary_schemas(docs_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Map ``derive_module_name(<source name>)`` to its dictionary schema."""
    schemas: Dict[str, List[Dict[str, Any]]] = {}
    for path in sorted(Path(docs_dir).glob("dictionary_*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        schema = _schema_from_lines(lines)
        if not schema:
            continue
        name = _source_name(lines) or path.stem.removeprefix("dictionary_")
        schemas[derive_module_name(name)] = schema
    return schemas
