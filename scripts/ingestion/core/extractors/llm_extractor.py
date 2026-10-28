"""Generic LLM document extractor (PDF and Excel).

Adapter for :mod:`ingestion.core.extractors.llm`: every parameter is explicit
(no PDF/LLM-specific env variables except the API key/model defaults). Use it as
a source base or from the command line::

    class Extractor(LLMExtractor):
        def __init__(self, config):
            super().__init__(
                config,
                url="https://example.org/report.pdf",
                instruction="Ekstrak kapasitas terpasang per jenis pembangkit 2025",
                metadata=Record,
            )

    python -m ingestion.core.extractors.llm_extractor report.pdf --env dev \
        --instruction "Ekstrak ..." --metadata schema.json [-o s3://raw/esdm/]

The CLI always writes the result: ``-o`` defaults to ``scripts/out/`` and also
accepts a file path or ``s3://bucket/prefix/`` (written with DuckDB, MinIO
settings from ``MINIO_URI``/``MINIO__*``). ``--env dev`` loads ``.env.dev``.
``--provider anthropic`` (or ``LLM_PROVIDER=anthropic``) switches from the
OpenAI-compatible client to the official Anthropic SDK.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Iterator

from ...exceptions import ConfigError, IngestionError, exit_code_for
from ..base.extractor import BaseExtractor
from .llm.llm_client import PROVIDERS
from .llm import (
    DocumentResult,
    LLMSettings,
    LLMUnavailable,
    extract_document,
    render_records,
    write_result,
)

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[3] / "out"

logger = logging.getLogger("ingestion")


class LLMExtractor(BaseExtractor):
    """Extract records from a PDF/Excel document using an LLM."""

    def __init__(
        self,
        config: Dict[str, Any] | None = None,
        *,
        url: str | None = None,
        source_file: str | None = None,
        instruction: str | None = None,
        metadata: Any = None,
        settings: LLMSettings | None = None,
        provider: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        api_key_env: str | None = None,
        temperature: float | None = None,
        max_retries: int | None = None,
        max_prompt_chars: int | None = None,
        json_mode: bool | None = None,
        max_tokens: int | None = None,
        pages: Any = None,
        page: Any = None,
        render_images: bool = False,
        min_chars: int = 30,
        max_chars: int = 50_000,
        output_path: str | Path | None = None,
        output_format: str = "json",
    ):
        super().__init__(dict(config or {}))
        self.source_ref = (
            source_file
            or url
            or self.config.get("url")
            or self.config.get("pdf_url")
        )
        self.instruction = instruction
        self.metadata = metadata
        self.pages = pages if pages is not None else page
        self.render_images = render_images
        self.min_chars = min_chars
        self.max_chars = max_chars
        self.output_path = str(output_path) if output_path else None
        self.output_format = output_format
        self.result: DocumentResult | None = None

        resolved = settings or LLMSettings.from_env()
        if provider:
            resolved.provider = provider.strip().lower()
        if model:
            resolved.model = model
        if base_url:
            resolved.base_url = base_url
        if api_key_env:
            resolved.api_key_env = api_key_env
        if temperature is not None:
            resolved.temperature = temperature
        if max_retries is not None:
            resolved.max_retries = max_retries
        if max_prompt_chars is not None:
            resolved.max_prompt_chars = max_prompt_chars
        if json_mode is not None:
            resolved.json_mode = json_mode
        if max_tokens is not None:
            resolved.max_tokens = max_tokens
        self.settings = resolved

    def extract(self) -> Iterator[Dict[str, Any]]:
        source = str(self.source_ref or "").strip()
        if not source:
            raise ConfigError("Missing document path/URL for LLMExtractor")
        if not str(self.instruction or "").strip():
            raise ConfigError("Missing instruction for LLMExtractor")

        output_path = self.output_path
        result = extract_document(
            source,
            self.instruction or "",
            self.metadata,
            settings=self.settings,
            config=self.config,
            pages=self.pages,
            render_images=self.render_images,
            min_chars=self.min_chars,
            max_chars=self.max_chars,
            output_path=output_path,
            output_format=self.output_format,
        )
        self.result = result
        name = Path(source).name

        for warning in result.warnings:
            logger.warning("LLM %s: %s", name, warning)
        for error in result.errors:
            logger.error("LLM %s: %s", name, error)

        if result.records:
            yield from result.records
            return
        detail = "; ".join(result.errors) or result.status
        raise IngestionError(f"LLM extraction failed for '{name}': {detail}")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ingestion.core.extractors.llm_extractor",
        description="Extract validated records from a PDF/Excel document with an LLM.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("source", help="local path, file://, s3://, minio://, or http(s) URL")
    parser.add_argument("--instruction", required=True, help="what to extract")
    parser.add_argument("--metadata", default=None, help="metadata JSON path/string or Pydantic .py path")
    parser.add_argument(
        "--provider",
        choices=PROVIDERS,
        default=None,
        help="openai = OpenAI-compatible chat API; anthropic = official Anthropic SDK "
        "(default: LLM_PROVIDER or openai)",
    )
    parser.add_argument("--model", default=None, help="LLM model (default: LLM_MODEL or gpt-4o-mini)")
    parser.add_argument("--base-url", default=None, help="provider base URL (default: LLM_BASE_URL)")
    parser.add_argument("--max-tokens", type=int, default=None, help="max output tokens (anthropic)")
    parser.add_argument("--api-key-env", default=None, help="env var holding the API key")
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--max-retries", type=int, default=None)
    parser.add_argument("--max-prompt-chars", type=int, default=None)
    parser.add_argument("--json-mode", action="store_true", default=None)
    parser.add_argument(
        "--pages",
        "--page",
        dest="pages",
        default=None,
        help="PDF pages: 1 | 1,3 | 5-8 | all (physical page numbers)",
    )
    parser.add_argument("--render-images", action="store_true", help="render low-text PDF pages for vision")
    parser.add_argument("--min-chars", type=int, default=30)
    parser.add_argument("--max-chars", type=int, default=50_000)
    parser.add_argument(
        "-o",
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help=(
            "output file or directory, local or s3://bucket/prefix/ (MinIO via DuckDB); "
            f"directories get <source>_<UTC timestamp>.<format> (default: {DEFAULT_OUTPUT_DIR})"
        ),
    )
    parser.add_argument("--format", choices=("json", "ndjson", "csv"), default="json")
    parser.add_argument(
        "--env",
        dest="env_profile",
        default=None,
        help="load settings from .env.<profile>, e.g. 'dev' -> .env.dev (LLM_API_KEY, LLM_MODEL, MINIO_URI)",
    )
    return parser


def _apply_env(profile: str | None) -> None:
    """Load ``.env`` plus the optional ``.env.<profile>`` before reading settings."""
    from ...config import env_profile_file, load_env, set_env_profile

    if profile:
        set_env_profile(profile)
        if not env_profile_file(profile):
            raise ConfigError(f"Env profile '.env.{profile}' not found")
    load_env()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _apply_env(args.env_profile)
    except ConfigError as exc:
        print(f"ERROR: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return exit_code_for(exc)
    extractor = LLMExtractor(
        {},
        source_file=None if args.source.lower().startswith(("http://", "https://", "s3://", "minio://", "file://")) else args.source,
        url=args.source,
        instruction=args.instruction,
        metadata=args.metadata,
        provider=args.provider,
        model=args.model,
        max_tokens=args.max_tokens,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        temperature=args.temperature,
        max_retries=args.max_retries,
        max_prompt_chars=args.max_prompt_chars,
        json_mode=args.json_mode,
        pages=args.pages,
        render_images=args.render_images,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        output_path=args.output,
        output_format=args.format,
    )
    try:
        list(extractor.extract())
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"ERROR: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        if extractor.result is not None and extractor.result.metadata.get("output"):
            print(f"written: {extractor.result.metadata['output']}", file=sys.stderr)
        return exit_code_for(exc) if not isinstance(exc, LLMUnavailable) else 1

    assert extractor.result is not None
    result = extractor.result
    written = result.metadata.get("output")
    if written:
        print(f"written: {written}", file=sys.stderr)
        return 0 if result.records else 1
    # Output write failed (see errors): fall back to stdout so the run is not lost.
    if args.format == "json":
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
    else:
        print(render_records(result.records, args.format))
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
