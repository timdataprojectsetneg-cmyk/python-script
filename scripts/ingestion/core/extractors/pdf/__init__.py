"""Dictionary-driven table & chart extraction engine for PDF sources.

The public entry point is :func:`extract_pdf`; :class:`PdfExtractor` in
``ingestion.core.extractors.pdf_extractor`` wraps it as a standard ingestion
extractor.

Quick start::

    from ingestion.core.extractors.pdf import extract_pdf

    result = extract_pdf(
        pdf_path="report.pdf",
        dictionary=Record,          # Pydantic model from the source's models.py
        marker="Primary Energy Supply",
        pages="12",
    )
    print(result.status, len(result.records))
"""
from __future__ import annotations

from .config import ExtractConfig, LLMConfig
from .dictionary_mapper import load_dictionary
from .extractor import extract_pdf
from .models import (
    Dictionary,
    DictionaryOptions,
    ExtractionKind,
    ExtractionMethod,
    ExtractionResult,
    FieldSpec,
    Provenance,
    SourceInfo,
    Status,
)

__all__ = [
    "extract_pdf",
    "load_dictionary",
    "ExtractConfig",
    "LLMConfig",
    "Dictionary",
    "DictionaryOptions",
    "FieldSpec",
    "ExtractionResult",
    "ExtractionKind",
    "ExtractionMethod",
    "Provenance",
    "SourceInfo",
    "Status",
]
