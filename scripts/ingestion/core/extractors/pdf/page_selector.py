

"""Page selection: parse a page spec and map printed page numbers.

Two numbering systems are supported (``--page-numbering``):

``physical`` (default)
    Page number in PDF order, 1-based.
``printed``
    The number printed in the document footer (many reports offset the
    printed number from the physical one, e.g. printed 18 == physical 34).
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from .pdf_reader import PdfSource

_ROMAN = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8,
    "ix": 9, "x": 10, "xi": 11, "xii": 12, "xiii": 13, "xiv": 14, "xv": 15,
    "xvi": 16, "xvii": 17, "xviii": 18, "xix": 19, "xx": 20, "xxi": 21,
    "xxii": 22, "xxiii": 23, "xxiv": 24, "xxv": 25, "xxvi": 26,
}


def parse_pages_spec(spec: str | Iterable[int] | int | None) -> list[int] | None:
    """Parse ``"1"``, ``"1,3,5"``, ``"5-8"``, ``"5,7-9"``, ``"all"``.

    Returns ``None`` for ``all`` (meaning: no restriction) and for ``None``
    (meaning: use the default, i.e. page 1).
    """
    if spec is None:
        return [1]
    if isinstance(spec, int):
        return [spec]
    if isinstance(spec, str):
        s = spec.strip()
        if not s or s.lower() == "all":
            return None
        pages: list[int] = []
        for part in s.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                try:
                    pages.extend(range(int(a), int(b) + 1))
                except ValueError as exc:
                    raise ValueError(f"rentang halaman tidak valid: {part!r}") from exc
            else:
                try:
                    pages.append(int(part))
                except ValueError as exc:
                    raise ValueError(f"nomor halaman tidak valid: {part!r}") from exc
        return sorted(set(pages))
    return sorted({int(p) for p in spec})


def resolve_pages(
    spec: str | Iterable[int] | int | None,
    page_count: int,
    default: list[int] | None = None,
) -> list[int]:
    """Resolve a page spec into a concrete list of physical pages."""
    parsed = parse_pages_spec(spec)
    if parsed is None:
        return list(range(1, page_count + 1))
    if not parsed:
        return list(default or [1])
    return [p for p in parsed if 1 <= p <= page_count]


# --------------------------------------------------------------------------
# printed page numbers
# --------------------------------------------------------------------------
def _as_number(token: str) -> int | None:
    t = token.strip().strip(".").lower()
    if t.isdigit():
        return int(t)
    return _ROMAN.get(t)


def _footer_number(page_view) -> int | None:
    """Best-effort detection of the page number printed in the footer."""
    height = page_view.rect.height
    if not height:
        return None
    bottom = page_view.rect.y1 - max(60.0, 0.12 * height)
    cands = [r_t for r_t in page_view.words if r_t[0].y0 >= bottom]
    nums = [(r, t, _as_number(t)) for r, t in cands]
    nums = [(r, t, n) for r, t, n in nums if n is not None]
    if not nums:
        return None
    # drop stacked (vertically split) numbers such as "20" / "25" of a year
    keep = []
    for r, t, n in nums:
        stacked = any(
            abs(o.x0 - r.x0) < 6 and abs(o.y0 - r.y0) < 12 and o is not r
            for o, _, _ in nums
        )
        if stacked:
            continue
        if 1900 <= n <= 2100:  # a year, not a page number
            continue
        keep.append((r, t, n))
    if not keep:
        return None
    # the page number sits on the lowest baseline; tie-break by x
    keep.sort(key=lambda x: (round(x[0].y0, 1), x[0].x0))
    max_y = max(round(x[0].y0, 1) for x in keep)
    lowest = [x for x in keep if round(x[0].y0, 1) >= max_y - 2]
    lowest.sort(key=lambda x: x[0].x0)
    return lowest[-1][2]


class PrintedPageIndex:
    """Map between printed and physical page numbers."""

    def __init__(self, source: PdfSource):
        self.detected: dict[int, int] = {}  # physical -> printed
        for n in range(1, source.page_count + 1):
            printed = _footer_number(source.page(n))
            if printed is not None:
                self.detected[n] = printed
        deltas = Counter(n - p for n, p in self.detected.items())
        self.dominant_delta = deltas.most_common(1)[0][0] if deltas else 0
        self.by_printed: dict[int, int] = {}
        for phys, printed in self.detected.items():
            self.by_printed.setdefault(printed, phys)

    def to_physical(self, printed: int, page_count: int) -> int | None:
        if printed in self.by_printed:
            return self.by_printed[printed]
        phys = printed + self.dominant_delta
        return phys if 1 <= phys <= page_count else None

    def to_printed(self, physical: int) -> int | None:
        return self.detected.get(physical, physical - self.dominant_delta)


def resolve_printed_pages(
    spec: str | Iterable[int] | int | None,
    source: PdfSource,
) -> tuple[list[int], dict[int, int]]:
    """Resolve a page spec given in *printed* numbers to physical pages.

    Returns ``(physical_pages, printed_to_physical_map)``.
    """
    parsed = parse_pages_spec(spec)
    index = PrintedPageIndex(source)
    if parsed is None:
        pages = list(range(1, source.page_count + 1))
        return pages, {i + 1 - index.dominant_delta: i + 1 for i in range(source.page_count)}
    if not parsed:
        parsed = [1]
    out: list[int] = []
    mapping: dict[int, int] = {}
    for p in parsed:
        phys = index.to_physical(p, source.page_count)
        if phys is not None:
            out.append(phys)
            mapping[p] = phys
    return sorted(set(out)), mapping