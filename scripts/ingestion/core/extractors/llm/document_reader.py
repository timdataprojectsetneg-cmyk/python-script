"""Read PDF and Excel documents into text (and optional page images) for an LLM.

PDF text comes from the existing PyMuPDF reader used by the deterministic
extractor; scanned pages can be rendered to PNG so a vision-capable model can
read them. Excel rows are flattened to tab-separated text per sheet. Local paths,
``file://``, ``s3://``/``minio://`` and HTTP(S) are supported.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ....exceptions import ConfigError
from ..duckdb_extractor import S3, resolve_location
from ..pdf.pdf_reader import PdfOpenError, PdfSource
from ..pdf.page_selector import resolve_pages

__all__ = ["Document", "DocumentReadError", "Segment", "read_document"]

_EXCEL_SUFFIXES = {".xlsx", ".xlsm", ".xls"}
_PDF_SUFFIXES = {".pdf"}


class DocumentReadError(ConfigError):
    """Raised when a document cannot be read or its type is unsupported."""


@dataclass
class Segment:
    label: str
    text: str = ""
    page: int | None = None
    image: bytes | None = None


@dataclass
class Document:
    source: str
    kind: str
    segments: list[Segment] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    page_count: int | None = None

    @property
    def images(self) -> list[bytes]:
        return [segment.image for segment in self.segments if segment.image]


def _materialize(ref: str, config: dict[str, Any] | None) -> tuple[Path, Path | None]:
    """Return ``(local_path, temp_path_to_remove)`` for any supported reference."""
    location = resolve_location(ref)
    if location.kind == "local":
        return Path(location.uri), None

    parsed = urlparse(location.uri)
    if location.kind == "http":
        import requests

        response = requests.get(location.uri, timeout=120)
        response.raise_for_status()
        content = response.content
        suffix = Path(parsed.path).suffix or ".bin"
    elif location.kind == S3:
        from ..storage.minio_storage import MinioStorage

        bucket = parsed.netloc
        key = (parsed.path or "").lstrip("/")
        storage = MinioStorage(config)
        if bucket:
            storage.bucket = bucket
        content = storage.download_bytes(key)
        suffix = Path(key).suffix or ".bin"
    else:  # pragma: no cover - resolve_location only returns the three kinds
        raise DocumentReadError(f"Unsupported document location: {ref}")

    fd, name = tempfile.mkstemp(prefix="ingestion_llm_", suffix=suffix)
    with os.fdopen(fd, "wb") as handle:
        handle.write(content)
    return Path(name), Path(name)


def _detect_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in _PDF_SUFFIXES:
        return "pdf"
    if suffix in _EXCEL_SUFFIXES:
        return "excel"
    try:
        head = path.read_bytes()[:8]
    except OSError as exc:
        raise DocumentReadError(f"Cannot read document: {path}: {exc}") from exc
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"PK"):
        return "excel"
    raise DocumentReadError(f"Unsupported document type: {path.name or path}")


def _read_pdf(path: Path, *, pages: Any, render_images: bool, min_chars: int) -> Document:
    document = Document(source=str(path), kind="pdf")
    try:
        source = PdfSource(path)
    except PdfOpenError as exc:
        raise DocumentReadError(str(exc)) from exc

    with source:
        document.page_count = source.page_count
        # The standalone extractor reads the whole document by default; an
        # explicit ``pages``/``page`` spec restricts it (e.g. ``"1-2"``).
        numbers = (
            list(range(1, source.page_count + 1))
            if pages is None
            else resolve_pages(pages, source.page_count)
        )
        for number in numbers:
            view = source.page(number)
            text = view.normalised_text
            image = None
            if render_images and len(text.strip()) < min_chars:
                try:
                    pixmap = view.page.get_pixmap(dpi=200)
                    image = pixmap.tobytes("png")
                except Exception as exc:  # noqa: BLE001 - rendering is best effort
                    document.warnings.append(f"page {number}: cannot render image: {exc}")
            if not text.strip() and image is None:
                document.warnings.append(
                    f"page {number}: no text layer; enable render_images for a vision model"
                )
            document.segments.append(
                Segment(label=f"page {number}", text=text, page=number, image=image)
            )
    return document


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:  # noqa: BLE001
            pass
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " / ")


def _read_excel_openpyxl(path: Path, *, max_chars: int) -> Document:
    from openpyxl import load_workbook

    document = Document(source=str(path), kind="excel")
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        for worksheet in workbook.worksheets:
            lines: list[str] = []
            size = 0
            for row in worksheet.iter_rows(values_only=True):
                line = "\t".join(_cell(value) for value in row).rstrip("\t")
                lines.append(line)
                size += len(line) + 1
                if size >= max_chars:
                    document.warnings.append(
                        f"sheet {worksheet.title}: truncated at {max_chars} characters"
                    )
                    break
            document.segments.append(
                Segment(label=f"sheet {worksheet.title}", text="\n".join(lines))
            )
    finally:
        workbook.close()
    return document


def _read_excel_pandas(path: Path, *, max_chars: int) -> Document:
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - pandas is a project dependency
        raise DocumentReadError("Reading .xls requires pandas and xlrd") from exc
    try:
        sheets = pd.read_excel(path, sheet_name=None, header=None)
    except ImportError as exc:
        raise DocumentReadError(
            "Reading .xls requires the 'xlrd' package (pip install xlrd)"
        ) from exc
    document = Document(source=str(path), kind="excel")
    for name, frame in sheets.items():
        text = frame.to_csv(index=False, header=False, sep="\t")
        if len(text) > max_chars:
            text = text[:max_chars]
            document.warnings.append(f"sheet {name}: truncated at {max_chars} characters")
        document.segments.append(Segment(label=f"sheet {name}", text=text))
    return document


def read_document(
    file_path: str | Path,
    *,
    pages: Any = None,
    page: Any = None,
    render_images: bool = False,
    min_chars: int = 30,
    max_chars: int = 50_000,
    config: dict[str, Any] | None = None,
) -> Document:
    """Read ``file_path`` into segments suitable for an LLM prompt."""
    ref = str(file_path or "").strip()
    if not ref:
        raise DocumentReadError("Missing document path/URL")

    page_spec = pages if pages is not None else page
    local_path, temporary = _materialize(ref, config)
    try:
        kind = _detect_kind(local_path)
        if kind == "pdf":
            return _read_pdf(
                local_path,
                pages=page_spec,
                render_images=render_images,
                min_chars=min_chars,
            )
        if local_path.suffix.lower() == ".xls":
            return _read_excel_pandas(local_path, max_chars=max_chars)
        return _read_excel_openpyxl(local_path, max_chars=max_chars)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
