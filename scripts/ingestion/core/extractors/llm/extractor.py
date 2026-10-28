"""End-to-end LLM document extraction.

``extract_document`` is the library entry point: read the PDF/Excel document,
build the optional output contract, ask an OpenAI-compatible model for records,
validate them in Python, and optionally write the result.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

from .document_reader import Document, read_document
from .llm_client import LLMClient, LLMSettings, LLMUnavailable, parse_json_response
from .output_writer import write_result
from .schema_builder import OutputSchema, build_schema
from .validator import validate_records

__all__ = ["DocumentResult", "build_prompt", "extract_document", "resolve_output_path"]

log = logging.getLogger("ingestion.llm")

_SYSTEM = (
    "You extract structured data from documents. Return ONLY a JSON object with "
    "a \"records\" key holding a list of objects. Use exactly the field names in "
    "the supplied schema. Do not invent values: use null when a value is not "
    "present in the document. Do not convert numbers or units unless the schema "
    "explicitly says so. Return an empty list when no matching data exists."
)


@dataclass
class DocumentResult:
    status: str = "failed"  # success | partial | failed
    records: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return bool(self.records) and not self.errors

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _schema_for_prompt(schema: OutputSchema | None) -> str:
    if schema is None:
        return (
            "No explicit schema was supplied. Choose a stable set of snake_case "
            "field names from the instruction, use the same fields in every record, "
            "and keep raw values (do not add totals or convert units)."
        )
    return (
        "The schema below is a contract. Every record must use exactly these "
        "fields and respect the types, enums, and nullability:\n"
        + json.dumps(schema.json_schema(), ensure_ascii=False, indent=2)
    )


def _document_text(document: Document, max_chars: int) -> tuple[str, bool]:
    parts: list[str] = []
    budget = max_chars
    truncated = False
    for segment in document.segments:
        header = f"--- {segment.label} ---"
        text = segment.text.strip()
        if not text and segment.image is not None:
            text = "[image attached for vision]"
        block = header + "\n" + text
        if len(block) > budget:
            parts.append(block[: max(0, budget)].rstrip())
            truncated = True
            break
        parts.append(block)
        budget -= len(block) + 2
        if budget <= 0:
            truncated = True
            break
    return "\n\n".join(parts), truncated


def build_prompt(
    instruction: str,
    schema: OutputSchema | None,
    document: Document,
    max_chars: int = 24_000,
) -> tuple[str, bool]:
    """Return ``(user_prompt, truncated)``."""
    body, truncated = _document_text(document, max_chars)
    prompt = (
        f"Instruction:\n{instruction.strip()}\n\n"
        f"Output contract:\n{_schema_for_prompt(schema)}\n\n"
        f"Document ({document.kind}, {len(document.segments)} segment(s)):\n{body}"
    )
    return prompt, truncated


def resolve_output_path(
    file_path: str,
    output_path: str | Path,
    output_format: str = "json",
) -> Path:
    """Use ``output_path`` as a file, or create a timestamped file in a directory."""
    target = Path(output_path)
    if target.exists() and target.is_dir():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(urlparse(str(file_path)).path).stem or "result")
        suffix = {"json": ".json", "ndjson": ".ndjson", "csv": ".csv"}.get(
            (output_format or "json").lower(), ".json"
        )
        target = target / f"{stem}_{stamp}{suffix}"
    return target


def extract_document(
    file_path: str,
    instruction: str,
    metadata: Any = None,
    *,
    settings: LLMSettings | None = None,
    config: dict[str, Any] | None = None,
    pages: Any = None,
    page: Any = None,
    render_images: bool = False,
    min_chars: int = 30,
    max_chars: int = 50_000,
    output_path: str | None = None,
    output_format: str = "json",
) -> DocumentResult:
    """Extract structured records from a PDF/Excel document using an LLM."""
    settings = settings or LLMSettings.from_env()
    result = DocumentResult(
        metadata={
            "file": str(file_path),
            "instruction": instruction,
            "model": settings.model,
            "base_url": settings.base_url,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    if not str(instruction or "").strip():
        result.errors.append("missing_instruction")
        return result

    try:
        document = read_document(
            file_path,
            pages=pages,
            page=page,
            render_images=render_images,
            min_chars=min_chars,
            max_chars=max_chars,
            config=config,
        )
    except Exception as exc:  # noqa: BLE001 - reported as a result
        result.errors.append(f"document_read_failed: {exc}")
        return result

    result.metadata.update(
        {
            "document_kind": document.kind,
            "segments": len(document.segments),
            "page_count": document.page_count,
            "images": len(document.images),
        }
    )
    result.warnings.extend(document.warnings)

    if not document.images and not any(segment.text.strip() for segment in document.segments):
        result.errors.append(
            "no_readable_text: enable render_images for scanned/image-only documents"
        )
        return result

    try:
        schema = build_schema(metadata)
    except Exception as exc:  # noqa: BLE001 - reported as a result
        result.errors.append(f"invalid_metadata: {exc}")
        return result
    result.metadata["schema"] = schema.json_schema() if schema is not None else None

    prompt, truncated = build_prompt(
        instruction, schema, document, settings.max_prompt_chars
    )
    if truncated:
        result.warnings.append(
            f"prompt truncated at {settings.max_prompt_chars} characters"
        )

    try:
        completion = LLMClient(settings).complete(
            _SYSTEM, prompt, images=document.images or None
        )
    except LLMUnavailable as exc:
        result.errors.append(f"llm_request_failed: {exc}")
        return result

    result.metadata["usage"] = completion.usage
    try:
        raw_records = parse_json_response(completion.text)
    except Exception as exc:  # noqa: BLE001 - invalid provider output
        result.errors.append(f"invalid_json: {exc}")
        result.metadata["response_excerpt"] = completion.text[:500]
        return result

    validation = validate_records(raw_records, schema)
    result.records = validation.records
    result.warnings.extend(validation.warnings)
    result.errors.extend(validation.errors)

    if result.records and not result.errors:
        result.status = "partial" if result.warnings else "success"
    elif result.records:
        result.status = "partial"
    else:
        result.status = "failed"
        if not result.errors:
            result.errors.append("no_records")

    result.metadata["finished_at"] = datetime.now(timezone.utc).isoformat()

    if output_path:
        target = resolve_output_path(file_path, output_path, output_format)
        try:
            write_result(result, target, output_format)
            result.metadata["output"] = str(target)
        except Exception as exc:  # noqa: BLE001 - result still usable
            result.errors.append(f"output_write_failed: {exc}")

    return result
