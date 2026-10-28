"""Shared PDF loading for Kemlu Dit. PWNI document sources (kemlu.go.id/files/repositori)."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, List, Optional

from ....exceptions import ConfigError, SourceUnavailable


def load_pdf(http: Any, url: Optional[str], source_file: Optional[str], default_url: str) -> tuple:
    """(bytes, origin). SOURCE_FILE wins over URL; URL falls back to ``default_url``."""
    local = (source_file or "").strip()
    if local:
        path = Path(local)
        if not path.is_file():
            raise ConfigError(f"SOURCE_FILE not found: {local}")
        return path.read_bytes(), path.name
    pdf_url = (url or "").strip() or default_url
    content = http.get(pdf_url, timeout=240).content
    if not content.startswith(b"%PDF"):
        raise SourceUnavailable(f"{pdf_url} did not return a PDF")
    return content, pdf_url


def read_pages(content: bytes, layout: bool = False) -> List[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("pypdf is required for Kemlu PDF sources (pip install pypdf)") from exc
    try:
        reader = PdfReader(io.BytesIO(content))
        if layout:
            return [(p.extract_text(extraction_mode="layout") or "") for p in reader.pages]
        return [(p.extract_text() or "") for p in reader.pages]
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the Kemlu PDF: {exc}") from exc
