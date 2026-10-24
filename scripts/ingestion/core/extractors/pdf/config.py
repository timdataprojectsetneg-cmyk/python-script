


"""Configuration objects for :mod:`pdf_extractor`.

Everything is optional: the package must work with pure defaults and without
any LLM (TDD section 11.1 -- "LLM tidak boleh menjadi prasyarat").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


@dataclass
class LLMConfig:
    """Optional OpenAI-compatible LLM integration.

    The API key is **never** read from a CLI argument; it is taken from an
    environment variable (default ``PDF_EXTRACTOR_API_KEY``).
    """

    enabled: bool = False
    base_url: str | None = None
    model: str | None = None
    api_key_env: str = "PDF_EXTRACTOR_API_KEY"
    mode: str = "fallback"  # "fallback" | "all"
    timeout: float = 60.0
    max_retries: int = 2
    temperature: float = 0.0
    max_pages_per_request: int = 2
    max_prompt_chars: int = 24_000

    def api_key(self) -> str | None:
        import os

        return os.environ.get(self.api_key_env)

    def is_ready(self) -> bool:
        return bool(self.enabled and self.model and self.api_key())


@dataclass
class ExtractConfig:
    """Full extraction configuration (CLI and Python API share this)."""

    # -- pages ------------------------------------------------------------
    pages: Iterable[int] | str | None = None
    #: "physical" (PDF order, 1-based) or "printed" (page number as printed
    #: in the footer/header of the document)
    page_numbering: str = "physical"

    # -- extraction -------------------------------------------------------
    mode: str = "auto"  # auto | table | chart
    model_class: str | None = None

    # -- text layer preflight --------------------------------------------
    min_chars: int = 30
    max_garbled: float = 0.2

    # -- marker -----------------------------------------------------------
    #: "normalized" (default): whitespace/case insensitive substring match.
    #: "fuzzy": also accept token-overlap matches above ``marker_threshold``.
    marker_match: str = "normalized"
    marker_threshold: float = 0.6
    #: vertical distance (points) searched above/below a marker for data
    search_radius: float = 220.0
    #: allow looking at neighbouring pages for continued tables
    allow_cross_page: bool = True
    max_neighbour_pages: int = 2

    # -- tables -----------------------------------------------------------
    keep_totals: bool = True
    header_scan_rows: int = 3
    header_match_threshold: float = 0.55
    #: maximum number of rows scanned when looking for a repeated header
    stitch_header_tolerance: float = 0.8

    # -- charts -----------------------------------------------------------
    min_bars: int = 2
    calibrate: bool = True

    # -- quality ----------------------------------------------------------
    min_confidence: float = 0.5
    max_records: int | None = None

    # -- llm --------------------------------------------------------------
    llm: LLMConfig = field(default_factory=LLMConfig)

    # -- misc -------------------------------------------------------------
    verbose: bool = False
    output: Path | None = None
    output_format: str = "json"  # json | ndjson | csv

    def resolved_pages(self, page_count: int) -> list[int]:
        """Return the list of physical pages to inspect.

        ``None`` means *page 1* (TDD section 4.2: default ``--pages`` is 1).
        """
        from .page_selector import resolve_pages

        return resolve_pages(self.pages, page_count, default=[1])