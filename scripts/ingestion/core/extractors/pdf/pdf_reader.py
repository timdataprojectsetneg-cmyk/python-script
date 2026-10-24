

"""PDF reading primitives: text layer access, geometry and preflight checks.

Wraps PyMuPDF so the rest of the package never imports it directly (single
place to swap the PDF backend later).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

import pymupdf

_WS = re.compile(r"\s+")


class PdfOpenError(Exception):
    """Raised when a file cannot be opened as a PDF."""


def normalise(text: str) -> str:
    """Normalise whitespace and unicode punctuation for robust matching."""
    if not text:
        return ""
    t = text.replace("\u00a0", " ")
    t = (
        t.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )
    return _WS.sub(" ", t).strip()


def normalise_lower(text: str) -> str:
    return normalise(text).lower()


@dataclass
class PageView:
    """Convenience wrapper around a single PDF page."""

    number: int  # 1-based physical page number
    _page: Any = field(repr=False)

    @property
    def page(self) -> pymupdf.Page:
        return self._page

    @property
    def rect(self) -> pymupdf.Rect:
        return self._page.rect

    @cached_property
    def text(self) -> str:
        try:
            return self._page.get_text("text") or ""
        except Exception:  # noqa: BLE001 - corrupted page
            return ""

    @cached_property
    def normalised_text(self) -> str:
        return normalise(self.text)

    @cached_property
    def words(self) -> list[tuple[pymupdf.Rect, str]]:
        """All words with their bounding box, in document order."""
        try:
            raw = self._page.get_text("words")
        except Exception:  # noqa: BLE001
            return []
        return [(pymupdf.Rect(w[:4]), str(w[4])) for w in raw]

    @cached_property
    def drawings(self) -> list[dict]:
        try:
            return self._page.get_drawings() or []
        except Exception:  # noqa: BLE001
            return []

    @cached_property
    def has_images(self) -> bool:
        try:
            return bool(self._page.get_images(full=True))
        except Exception:  # noqa: BLE001
            return False

    def word_rects(self, pattern: str) -> list[tuple[pymupdf.Rect, str]]:
        rx = re.compile(pattern)
        return [(r, t) for r, t in self.words if rx.search(t)]

    def text_in_rect(self, rect) -> str:
        try:
            txt = self._page.get_text("text", clip=pymupdf.Rect(rect))
        except Exception:  # noqa: BLE001
            return ""
        return normalise(txt)

    # -- preflight --------------------------------------------------------
    def check_text_layer(self, min_chars: int = 30, max_garbled: float = 0.2) -> tuple[bool, str]:
        """Validate that the page has a usable text layer (TDD section 7)."""
        chars = [c for c in self.text if not c.isspace()]
        if len(chars) < min_chars:
            hint = " (ada gambar, kemungkinan hasil scan)" if self.has_images else ""
            return False, f"tidak ada text layer{hint}"
        bad = sum(1 for c in chars if c == "\ufffd" or not c.isprintable())
        if bad / len(chars) > max_garbled:
            return False, f"teks rusak/garbled ({bad / len(chars):.0%})"
        return True, "ok"


class PdfSource:
    """Opened PDF document with lazily built :class:`PageView` objects."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        try:
            self._doc = pymupdf.open(self.path)
        except Exception as exc:  # noqa: BLE001
            raise PdfOpenError(f"gagal membuka PDF {self.path}: {exc}") from exc
        if getattr(self._doc, "needs_pass", False):
            self._doc.close()
            raise PdfOpenError(f"PDF terenkripsi: {self.path}")
        self._pages: dict[int, PageView] = {}

    # -- context manager --------------------------------------------------
    def __enter__(self) -> "PdfSource":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def close(self) -> None:
        try:
            self._doc.close()
        except Exception:  # noqa: BLE001
            pass

    # -- access -----------------------------------------------------------
    @property
    def page_count(self) -> int:
        return self._doc.page_count

    def page(self, number: int) -> PageView:
        if not 1 <= number <= self.page_count:
            raise IndexError(f"halaman {number} di luar jangkauan (total {self.page_count})")
        if number not in self._pages:
            self._pages[number] = PageView(number=number, _page=self._doc[number - 1])
        return self._pages[number]

    def pages(self, numbers) -> list[PageView]:
        return [self.page(n) for n in numbers]

    @cached_property
    def file_name(self) -> str:
        return self.path.name