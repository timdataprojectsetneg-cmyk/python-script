"""Generic PDF extractor — tables/charts driven by a marker and a schema.

The heavy lifting lives in :mod:`ingestion.core.extractors.pdf` (deterministic
table/chart extraction, optional LLM fallback). This module only adapts it to the
ingestion contract: resolve/download the PDF, run the engine on a temporary
file, then yield the produced records.

Everything is passed explicitly — there are no PDF-specific env variables:

    source (url/pdf_url/source_file), dictionary, marker, pages, mode,
    page_numbering, model_class, save_raw, llm

Example source extractor::

    from .....core.extractors.pdf_extractor import PdfExtractor
    from .models import Record

    class Extractor(PdfExtractor):
        def __init__(self, config):
            super().__init__(
                config,                       # optional; only for MinIO settings
                url="https://example.org/handbook.pdf",
                dictionary=Record,
                marker="Primary Energy Supply",
                pages="12",
            )

Direct use (notebooks/scripts)::

    extractor = PdfExtractor(
        dictionary="dict.json",
        marker="Primary Energy Supply",
        source_file="handbook.pdf",       # or url="https://.../file.pdf"
        pages="12",
    )
    records = list(extractor.extract())
    extractor.result.status

CLI::

    python -m ingestion.core.extractors.pdf_extractor handbook.pdf \
        --dictionary dict.json --marker "Primary Energy Supply" --pages 12
    python -m ingestion.core.extractors.pdf_extractor https://.../file.pdf \
        --dictionary dict.json --marker "..." --pages 12 --format ndjson -o out.ndjson
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterator
from urllib.parse import unquote, urlparse

from ...exceptions import (
    ConfigError,
    IngestionError,
    SourceUnavailable,
    exit_code_for,
)
from ..base.extractor import BaseExtractor
from .pdf import ExtractionResult, extract_pdf

logger = logging.getLogger("ingestion")


class PdfExtractor(BaseExtractor):
    """Extract structured records from a PDF table or chart."""

    def __init__(
        self,
        config: Dict[str, Any] | None = None,
        dictionary: Any = None,
        marker: str | None = None,
        pages: Any = None,
        mode: str | None = None,
        page_numbering: str | None = None,
        model_class: str | None = None,
        llm: Any = None,
        url: str | None = None,
        pdf_url: str | None = None,
        source_file: str | None = None,
        save_raw: bool = False,
    ):
        super().__init__(dict(config or {}))
        self.dictionary = dictionary
        self.marker = marker
        self.pages = pages
        self.mode = mode
        self.page_numbering = page_numbering
        self.model_class = model_class
        self.llm = llm
        self.source_ref = source_file or url or pdf_url
        self.save_raw = bool(save_raw)
        self.result: ExtractionResult | None = None

    # -- configuration ----------------------------------------------------
    def _dictionary(self) -> Any:
        if self.dictionary is None:
            raise ConfigError(
                "Missing PDF dictionary: pass dictionary=Record, a path to a "
                ".json/.py dictionary, a dict, or a JSON string."
            )
        dictionary = self.dictionary
        if isinstance(dictionary, str):
            text = dictionary.strip()
            if text.startswith(("{", "[")):
                try:
                    return json.loads(text)
                except json.JSONDecodeError as exc:
                    raise ConfigError(f"The JSON dictionary is not valid: {exc}") from exc
        return dictionary

    def _marker(self) -> str:
        marker = str(self.marker or "").strip()
        if not marker:
            raise ConfigError("Missing PDF marker: pass marker=... to PdfExtractor.")
        return marker

    def _pages(self) -> Any:
        return self.pages

    def _mode(self) -> str:
        return str(self.mode or "auto")

    def _page_numbering(self) -> str:
        return str(self.page_numbering or "auto")

    def _model_class(self) -> str | None:
        value = self.model_class
        return str(value) if value else None

    # -- input ------------------------------------------------------------
    def _source_ref(self) -> str:
        ref = str(self.source_ref or "").strip()
        if not ref:
            raise ConfigError(
                "Missing PDF source: pass url=..., pdf_url=..., or source_file=..."
            )
        return ref

    @staticmethod
    def _filename_from_url(url: str) -> str:
        name = Path(unquote(urlparse(url).path)).name
        if not name:
            return "document.pdf"
        return name if name.lower().endswith(".pdf") else f"{name}.pdf"

    def _read_source(self) -> tuple[bytes, str, bool]:
        """Return ``(content, filename, from_object_store)``."""
        ref = self._source_ref()
        lowered = ref.lower()

        if lowered.startswith("minio://"):
            from ..storage.minio_storage import MinioStorage, split_minio_ref

            bucket, key = split_minio_ref(ref)
            storage = MinioStorage(self.config)
            if bucket:
                storage.bucket = bucket
            name = Path(key).name or "document.pdf"
            return storage.download_bytes(key), name, True

        if lowered.startswith(("http://", "https://")):
            response = self.http.get(ref, timeout=120)
            return response.content, self._filename_from_url(ref), False

        path = Path(ref).expanduser()
        if not path.exists():
            raise SourceUnavailable(f"PDF file not found: {path}")
        return path.read_bytes(), path.name, False

    def _extract_records(self, content: bytes, filename: str) -> ExtractionResult:
        if b"%PDF" not in content[:1024]:
            raise SourceUnavailable(f"Not a PDF file: {filename}")

        name = Path(filename).name or "document.pdf"
        with tempfile.TemporaryDirectory(prefix="ingestion_pdf_") as tmp:
            path = Path(tmp) / name
            path.write_bytes(content)
            return extract_pdf(
                pdf_path=path,
                dictionary=self._dictionary(),
                marker=self._marker(),
                pages=self._pages(),
                mode=self._mode(),
                page_numbering=self._page_numbering(),
                llm=self.llm,
                model_class=self._model_class(),
            )

    # -- extraction -------------------------------------------------------
    def extract(self) -> Iterator[Dict[str, Any]]:
        content, filename, from_object_store = self._read_source()
        if not from_object_store and self.save_raw:
            self.save_raw_to_minio(content, filename, "application/pdf")

        result = self._extract_records(content, filename)
        self.result = result

        for warning in result.warnings:
            logger.warning("PDF %s: %s", filename, warning)
        for error in result.errors:
            logger.error("PDF %s: %s", filename, error)

        if result.records:
            yield from result.records
            return

        if result.status.is_ok:
            raise IngestionError(
                f"No records extracted from PDF '{filename}' (status: {result.status.value})"
            )
        detail = "; ".join(result.errors or result.warnings) or result.status.value
        raise IngestionError(
            f"PDF extraction failed ({result.status.value}) for '{filename}': {detail}"
        )


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ingestion.core.extractors.pdf_extractor",
        description="Extract table/chart records from a PDF using a marker and a dictionary.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("source", help="local PDF path, http(s) URL, or minio://bucket/key.pdf")
    parser.add_argument(
        "--dictionary",
        required=True,
        help="dictionary path (.json/.py) or a JSON object string",
    )
    parser.add_argument("--marker", required=True, help="text identifying the wanted table/chart")
    parser.add_argument("--pages", default=None, help="1 | 1,3,5 | 5-8 | all (default: page 1)")
    parser.add_argument("--mode", choices=("auto", "table", "chart"), default="auto")
    parser.add_argument(
        "--page-numbering",
        choices=("auto", "physical", "printed"),
        default="auto",
        help="interpret --pages as physical order or printed page numbers",
    )
    parser.add_argument("--model-class", default=None, help="model class inside a .py dictionary")
    parser.add_argument("-o", "--output", default=None, help="write to this file instead of stdout")
    parser.add_argument(
        "--format",
        choices=("json", "ndjson", "csv"),
        default="json",
        help="json = full result (status/warnings/records); ndjson/csv = records only",
    )
    parser.add_argument(
        "--save-raw",
        action="store_true",
        help="upload the downloaded PDF to MinIO (MINIO_URI / MINIO__* must be set)",
    )
    return parser


def _render_result(result: ExtractionResult, output_format: str) -> str:
    """Render the full result as JSON, or just the records as NDJSON/CSV."""
    if output_format == "json":
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)

    if output_format == "ndjson":
        return "\n".join(
            json.dumps(record, ensure_ascii=False, default=str) for record in result.records
        )

    columns: list[str] = []
    for record in result.records:
        for key in record:
            if key not in columns:
                columns.append(key)
    if not columns:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader()
    writer.writerows(result.records)
    return buffer.getvalue().rstrip("\r\n")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    is_url = args.source.lower().startswith(("http://", "https://", "minio://"))
    extractor = PdfExtractor(
        dictionary=args.dictionary,
        marker=args.marker,
        pages=args.pages,
        mode=args.mode,
        page_numbering=args.page_numbering,
        model_class=args.model_class,
        url=args.source if is_url else None,
        source_file=None if is_url else args.source,
        save_raw=args.save_raw,
    )

    try:
        list(extractor.extract())
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"ERROR: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return exit_code_for(exc)

    assert extractor.result is not None
    text = _render_result(extractor.result, args.format)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + ("\n" if text else ""), encoding="utf-8")
        print(f"written: {path}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
