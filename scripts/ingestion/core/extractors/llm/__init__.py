"""Provider-agnostic LLM extraction for PDF and Excel documents.

The deterministic PDF engine lives in :mod:`ingestion.core.extractors.pdf`;
this package handles the optional LLM path (and can be used standalone for
documents that are not PDFs). The PDF-specific fallback used by that engine is
in :mod:`ingestion.core.extractors.llm.pdf_assist`.

Library usage::

    from ingestion.core.extractors.llm import extract_document

    result = extract_document(
        "data/energy-statistics-2025.pdf",
        "Ekstrak data Natural Gas and Products tahun 2025",
        metadata={"tahun": {"type": "integer"}, "nilai": {"type": ["number", "null"]}},
    )
    print(result.status, result.records)
"""

from __future__ import annotations

from .document_reader import Document, DocumentReadError, Segment, read_document
from .extractor import DocumentResult, build_prompt, extract_document, resolve_output_path
from .llm_client import LLMClient, LLMSettings, LLMUnavailable, parse_json_response
from .output_writer import render_records, write_records, write_result, write_result_s3
from .schema_builder import OutputField, OutputSchema, build_schema, schema_to_json
from .validator import ValidationResult, validate_records

__all__ = [
    "Document",
    "DocumentReadError",
    "DocumentResult",
    "LLMClient",
    "LLMSettings",
    "LLMUnavailable",
    "OutputField",
    "OutputSchema",
    "Segment",
    "ValidationResult",
    "build_prompt",
    "build_schema",
    "extract_document",
    "parse_json_response",
    "read_document",
    "render_records",
    "resolve_output_path",
    "schema_to_json",
    "validate_records",
    "write_records",
    "write_result",
    "write_result_s3",
]
