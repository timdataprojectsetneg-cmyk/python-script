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


def _structure_tree(usecase: str, grouped: Dict[tuple, Dict[str, Any]]) -> str:
    """Nested tree: usecases/<usecase>/<publisher>/<source>/<access>."""
    usecase_slug = derive_module_name(usecase)
    lines = [f"usecases/{usecase_slug}/"]

    by_publisher: Dict[str, List[str]] = {}
    for publisher, source in grouped:
        by_publisher.setdefault(publisher, []).append(source)

    publishers = list(by_publisher.keys())
    for p_index, publisher in enumerate(publishers):
        p_last = p_index == len(publishers) - 1
        lines.append(f"{'└── ' if p_last else '├── '}{publisher}/")
        p_stem = "    " if p_last else "│   "
        sources = by_publisher[publisher]
        for s_index, source in enumerate(sources):
            s_last = s_index == len(sources) - 1
            lines.append(f"{p_stem}{'└── ' if s_last else '├── '}{source}/")
            s_stem = p_stem + ("    " if s_last else "│   ")
            lines.append(f"{s_stem}├── models.py            # from docs/dictionary_{usecase_slug}_{source}.md")
            lines.append(f"{s_stem}├── normalizer.py")
            accesses = grouped[(publisher, source)]["accesses"] or ["excel"]
            for a_index, access in enumerate(accesses):
                a_last = a_index == len(accesses) - 1
                lines.append(f"{s_stem}{'└── ' if a_last else '├── '}{access}/")
                a_stem = s_stem + ("    " if a_last else "│   ")
                lines.append(f"{a_stem}└── extractor.py")
    return "\n".join(lines)


def env_lines(usecase: str, sources: List[Dict[str, Any]]) -> List[str]:
    """Env var lines for eligible sources: {UC}__{PUBLISHER}__{SOURCE}__{ACCESS}__{KEY}."""
    usecase_slug = derive_module_name(usecase)
    lines: List[str] = []
    for source in sources:
        if not is_eligible(source):
            continue
        publisher = publisher_slug(source)
        slug = source_slug(source)
        access = derive_access(source.get("data_access"))
        prefix = f"{usecase_slug}__{publisher}__{slug}__{access}".upper()
        lines.append(f"{prefix}__URL={source.get('source_link') or ''}")
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
    return lines


def render_usecase_markdown(usecase: str, sources: List[Dict[str, Any]], catalog_path: str = "") -> str:
    usecase_slug = derive_module_name(usecase)
    grouped = _group_sources(sources)
    eligible_grouped = {slug: entry for slug, entry in grouped.items() if entry["eligible"]}
    skipped = [entry["name"] for slug, entry in grouped.items() if not entry["eligible"]]

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
        "| # | Source Name | Publisher | Data Access | Update Frequency | Is Official | Eligible | Last Update | Source Link | Data Dictionary |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for index, source in enumerate(sources, 1):
        out.append(
            "| {i} | {name} | {pub} | {access} | {freq} | {official} | {eligible} | {updated} | {link} | {dict} |".format(
                i=index,
                name=_cell(source.get("source_name")),
                pub=_cell(source.get("publisher")),
                access=_cell(source.get("data_access")),
                freq=_cell(source.get("update_frequency")),
                official=_cell(source.get("is_official")),
                eligible=_cell(source.get("eligible")),
                updated=_cell(source.get("last_update")),
                link=_link_cell(source.get("source_link"), source.get("source_link")),
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
        "## Proposed module structure (eligible sources only)",
        "",
        "> Only sources with `Eligible = true` are scaffolded. Ineligible sources are listed below.",
        "",
        "```",
        _structure_tree(usecase, eligible_grouped) if eligible_grouped else f"usecases/{usecase_slug}/  (no eligible sources)",
        "```",
        "",
    ]

    if skipped:
        out += ["### Skipped (not eligible)", ""]
        out += [f"- {name}" for name in skipped]
        out += [""]

    out += ["## Environment variables", "", "```bash"]
    out += env_lines(usecase, sources)
    out += ["```", ""]

    out += [
        "## Next steps",
        "",
        f"1. Scaffold eligible sources: `python -m ingestion.cli docs --usecase {usecase_slug} --scaffold`",
        "   (or copy the structure above by hand).",
        "2. For each source, open `docs/dictionary_<usecase>_<source>.md` and copy the Pydantic model into `models.py`.",
        "3. Implement `normalizer.py` (or rely on the generic normalizer validating against `Record`).",
        "4. Implement `<access>/extractor.py` (class `Extractor`), or rely on the generic extractor.",
        "5. Register the environment variables above and run in DEV mode.",
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
        out.append(
            "| {label} | `{name}` | {type} | {satuan} | {desc} |".format(
                label=_cell(field.get("label")),
                name=_cell(field.get("name") or to_snake_case(field.get("label"))),
                type=_cell(field.get("type")),
                satuan=_cell(field.get("satuan")),
                desc=_cell(field.get("deskripsi")),
            )
        )
    if not schema:
        out.append("| - | - | - | - | No fields parsed from the Data Dictionary. |")

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
