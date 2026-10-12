"""Render SharePoint catalog / Data Dictionary data as Markdown reference docs.

Outputs (written to the ``docs/`` folder by the ``docs`` CLI command):

- ``usecase_<usecase>.md``                        — source catalog + proposed module structure
- ``dictionary_<usecase>_<source>.md``            — field dictionary + generated Pydantic model

These documents are intended as the working reference for scaffolding a use
case's folder/file structure and for writing its Pydantic models.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .metadata_parser import (
    TARGET_FIELDS,
    derive_access,
    derive_module_name,
    effective_url,
    is_eligible,
    publisher_slug,
    source_slug,
    split_postgre,
    to_pydantic_source,
    to_snake_case,
)


def usecase_filename(usecase: str) -> str:
    return f"usecase_{derive_module_name(usecase)}.md"


def dictionary_filename(usecase: str, source: str) -> str:
    return f"dictionary_{derive_module_name(usecase)}_{derive_module_name(source)}.md"


def _cell(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _field_row(field: Dict[str, Any]) -> str:
    """One Markdown table row for a Data Dictionary field."""
    return "| {label} | `{name}` | {type} | {satuan} | {desc} |".format(
        label=_cell(field.get("label")),
        name=_cell(field.get("name") or to_snake_case(field.get("label"))),
        type=_cell(field.get("type")),
        satuan=_cell(field.get("satuan")),
        desc=_cell(field.get("deskripsi")),
    )


def _link_cell(value: Any, url: Any) -> str:
    """Markdown cell, hyperlinking the display text when a URL is available."""
    if value in (None, "") and url:
        return f"[link]({url})"
    if value in (None, ""):
        return "-"
    text = _cell(value)
    if url:
        return f"[{text}]({url})"
    return text


def _group_sources(sources: List[Dict[str, Any]]) -> Dict[tuple, Dict[str, Any]]:
    grouped: Dict[tuple, Dict[str, Any]] = {}
    for source in sources:
        name = source.get("source_name")
        if not name:
            continue
        key = (publisher_slug(source), source_slug(source))
        entry = grouped.setdefault(
            key, {"name": name, "accesses": [], "eligible": False}
        )
        access = derive_access(source.get("data_access"))
        if access not in entry["accesses"]:
            entry["accesses"].append(access)
        entry["eligible"] = entry["eligible"] or is_eligible(source)
    return grouped


def env_lines(
    usecase: str, sources: List[Dict[str, Any]], preserved: Dict[str, str] | None = None
) -> List[str]:
    """Env var lines for eligible sources: {UC}__{PUBLISHER}__{SOURCE}__{KEY}.

    ``preserved`` maps an existing env var name to its current value (read from a
    previously generated ``.env``); ``METHOD``/``UNIQUE_KEY`` keep those values
    instead of being reset to the defaults.
    """
    preserved = preserved or {}
    usecase_slug = derive_module_name(usecase)
    lines: List[str] = []
    for source in sources:
        if not is_eligible(source):
            continue
        publisher = publisher_slug(source)
        slug = source_slug(source)
        prefix = f"{usecase_slug}__{publisher}__{slug}".upper()
        lines.append(f"{prefix}__URL={effective_url(source) or ''}")
        schema, postgre_table = split_postgre(source.get("raw_postgre_table"))
        targets = (
            ("POSTGRE_SCHEMA", schema),
            ("POSTGRE_TABLE", postgre_table),
            ("ES_INDEX", source.get("raw_es_index")),
            ("MINIO_BUCKET", source.get("raw_minio_bucket")),
        )
        for key, value in targets:
            if value:
                lines.append(f"{prefix}__{key}={value}")
        lines.append(f"{prefix}__METHOD={preserved.get(f'{prefix}__METHOD') or 'replace'}")
        lines.append(f"{prefix}__UNIQUE_KEY={preserved.get(f'{prefix}__UNIQUE_KEY', '')}")
    return lines


def render_usecase_markdown(usecase: str, sources: List[Dict[str, Any]], catalog_path: str = "") -> str:
    usecase_slug = derive_module_name(usecase)
    grouped = _group_sources(sources)
    eligible_grouped = {slug: entry for slug, entry in grouped.items() if entry["eligible"]}

    out: List[str] = [
        f"# Use Case: {usecase}",
        "",
        f"> Generated from SharePoint catalog `{catalog_path or 'Available Data Source per Usecase.xlsx'}`. "
        "Do not edit manually — regenerate with `python -m ingestion.cli docs --usecase "
        f"{usecase_slug} --env <profile>`.",
        "",
        f"Source count: **{len(grouped)}** · eligible for implementation: **{len(eligible_grouped)}**",
        "",
        "## Sources",
        "",
        "| # | Source Name | Publisher | Data Access | Update Frequency | Is Official | Eligible | Last Update | Source Link | Resource URL | Data Dictionary |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for index, source in enumerate(sources, 1):
        out.append(
            "| {i} | {name} | {pub} | {access} | {freq} | {official} | {eligible} | {updated} | {link} | {resource} | {dict} |".format(
                i=index,
                name=_cell(source.get("source_name")),
                pub=_cell(source.get("publisher")),
                access=_cell(source.get("data_access")),
                freq=_cell(source.get("update_frequency")),
                official=_cell(source.get("is_official")),
                eligible=_cell(source.get("eligible")),
                updated=_cell(source.get("last_update")),
                link=_link_cell(source.get("source_link"), source.get("source_link")),
                resource=_link_cell(source.get("resource_url"), source.get("resource_url")),
                dict=_link_cell(source.get("data_dictionary"), source.get("data_dictionary_link")),
            )
        )

    if any(source.get(field) for source in sources for field, _ in TARGET_FIELDS):
        out += [
            "",
            "## Targets",
            "",
            "| Source | " + " | ".join(label for _, label in TARGET_FIELDS) + " |",
            "|---" * (1 + len(TARGET_FIELDS)) + "|",
        ]
        for source in sources:
            row = " | ".join(_cell(source.get(field)) for field, _ in TARGET_FIELDS)
            out.append(f"| {_cell(source.get('source_name'))} | {row} |")

    out += [
        "",
        "## Next steps",
        "",
        f"1. Scaffold eligible sources: `python -m ingestion.cli docs --usecase {usecase_slug} --scaffold`",
        "2. For each source, open `docs/dictionary_<usecase>_<source>.md` and copy the Pydantic model into `models.py`.",
        "3. Implement `normalizer.py` (or rely on the generic normalizer validating against `Record`).",
        "4. Implement `<source>/extractor.py` (class `Extractor`), subclassing the generic base.",
        "5. Register the source environment variables and run in DEV mode.",
        "",
    ]
    return "\n".join(out)


def render_dictionary_markdown(
    usecase: str,
    source_name: str,
    schema: List[Dict[str, Any]],
    source_meta: Dict[str, Any] | None = None,
    module_path: str = "",
) -> str:
    source_meta = source_meta or {}
    class_name = derive_module_name(source_name).title().replace("_", "") + "Record" or "Record"
    model_source = to_pydantic_source(class_name, schema)

    out: List[str] = [
        f"# Data Dictionary: {source_name}",
        "",
        "> Generated from the SharePoint Data Dictionary. Use this as the reference for the "
        "Pydantic model in `models.py`.",
        "",
        f"- Use case: `{usecase}`",
        f"- Source: `{source_name}`",
        f"- Publisher: {_cell(source_meta.get('publisher'))}",
        f"- Data access: `{derive_access(source_meta.get('data_access'))}`",
        f"- Update frequency: {_cell(source_meta.get('update_frequency'))}",
        f"- Eligible: `{is_eligible(source_meta)}`",
        f"- Data Dictionary file: {_link_cell(source_meta.get('data_dictionary'), source_meta.get('data_dictionary_link'))}",
        f"- Target module: `{module_path}`",
        "",
        "## Fields",
        "",
        "| Label | Name (column) | Tipe Data | Satuan | Deskripsi |",
        "|---|---|---|---|---|",
    ]
    for field in schema:
        out.append(_field_row(field))
    if not schema:
        out.append("| - | - | - | - | No fields parsed from the Data Dictionary. |")

    for field in schema:
        nested = field.get("fields")
        if not nested:
            continue
        out += [
            "",
            f"### JSON field: `{_cell(field.get('name'))}` ({_cell(field.get('label'))})",
            "",
            "| Label | Name (column) | Tipe Data | Satuan | Deskripsi |",
            "|---|---|---|---|---|",
        ]
        out += [_field_row(sub) for sub in nested]

    out += [
        "",
        "## Generated Pydantic model",
        "",
        "```python",
        model_source.rstrip(),
        "```",
        "",
        "> Adjust types, enums and validation constraints (`ge=0`, aliases) before committing. "
        "Keep `extra=\"ignore\"` so new source columns do not break validation.",
        "",
    ]
    return "\n".join(out)


def write_markdown(text: str, output_dir: str, filename: str) -> Path:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    path = target / filename
    path.write_text(text, encoding="utf-8")
    return path
