
"""Marker detection.

A marker is the mandatory starting point of every extraction.  The detector
is **position independent**: it records every occurrence of the marker and
lets the caller decide which table/chart below *or above* it is the intended
target (TDD section 5).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence

import pymupdf

from .pdf_reader import PageView, normalise

_PUNCT = re.compile(r"[^\w\s%&/()-]+", re.UNICODE)


def _tok(text: str) -> str:
    return _PUNCT.sub("", normalise(text).lower())


def marker_tokens(marker: str) -> list[str]:
    return [t for t in (_tok(m) for m in normalise(marker).split()) if t]


@dataclass
class MarkerMatch:
    """One occurrence of the marker on a page."""

    page: int
    text: str
    score: float
    kind: str  # "exact" | "normalized" | "fuzzy"
    rect: pymupdf.Rect | None = None
    token_index: int = 0

    @property
    def y(self) -> float:
        return (self.rect.y0 + self.rect.y1) / 2 if self.rect else 0.0

    @property
    def x(self) -> float:
        return (self.rect.x0 + self.rect.x1) / 2 if self.rect else 0.0

    def context_rect(self, radius: float, page_rect: pymupdf.Rect) -> pymupdf.Rect:
        """Area above and below the marker that may hold the related data."""
        if self.rect is None:
            return page_rect
        box = pymupdf.Rect(
            page_rect.x0,
            max(page_rect.y0, self.rect.y0 - radius),
            page_rect.x1,
            min(page_rect.y1, self.rect.y1 + radius),
        )
        return box & page_rect


def _window_score(page_toks: Sequence[str], start: int, m_toks: Sequence[str]) -> float:
    matched = 0
    for i, mt in enumerate(m_toks):
        if start + i < len(page_toks) and page_toks[start + i] == mt:
            matched += 1
    return matched / len(m_toks) if m_toks else 0.0


def _fuzzy_score(page_toks: Sequence[str], start: int, m_toks: Sequence[str]) -> float:
    window = [t for t in page_toks[start : start + len(m_toks)] if t]
    if not window:
        return 0.0
    mset, wset = set(m_toks), set(window)
    if not mset:
        return 0.0
    return len(mset & wset) / len(mset)


def find_marker_on_page(
    page: PageView,
    marker: str,
    match_mode: str = "normalized",
    threshold: float = 0.6,
) -> list[MarkerMatch]:
    """Find all occurrences of ``marker`` on a single page."""
    m_toks = marker_tokens(marker)
    if not m_toks:
        return []
    # separators such as "|" tokenise to "" and would shift every window, so
    # they are dropped before the sliding window is built
    words = [(r, t) for r, t in page.words if _tok(t)]
    page_toks = [_tok(t) for _, t in words]
    if not page_toks:
        return []

    matches: list[MarkerMatch] = []
    n = len(m_toks)
    for start in range(0, max(0, len(page_toks) - n + 1)):
        exact = _window_score(page_toks, start, m_toks)
        if exact >= 1.0:
            kind, score = "exact", 1.0
        elif match_mode in ("normalized", "fuzzy") and exact >= threshold:
            kind, score = "normalized", exact
        elif match_mode == "fuzzy":
            fz = _fuzzy_score(page_toks, start, m_toks)
            if fz >= threshold:
                kind, score = "fuzzy", fz
            else:
                continue
        else:
            continue
        rect = pymupdf.Rect(words[start][0])
        for r, _ in words[start + 1 : start + n]:
            rect |= r
        text = normalise(" ".join(t for _, t in words[start : start + n]))
        matches.append(
            MarkerMatch(page=page.number, text=text, score=score, kind=kind,
                        rect=rect, token_index=start)
        )
    return _dedupe(matches)


def _dedupe(matches: list[MarkerMatch]) -> list[MarkerMatch]:
    """Collapse overlapping matches, keeping the highest score."""
    out: list[MarkerMatch] = []
    for m in sorted(matches, key=lambda x: (-x.score, x.page, x.y)):
        if any(
            o.page == m.page and o.rect and m.rect and (o.rect & m.rect).get_area() > 0
            for o in out
        ):
            continue
        out.append(m)
    return sorted(out, key=lambda x: (x.page, x.y))


def find_markers(
    pages: Sequence[PageView],
    marker: str,
    match_mode: str = "normalized",
    threshold: float = 0.6,
) -> list[MarkerMatch]:
    """Find the marker on every selected page (all occurrences kept)."""
    found: list[MarkerMatch] = []
    for page in pages:
        found.extend(find_marker_on_page(page, marker, match_mode, threshold))
    return found


@dataclass
class MarkerSearchResult:
    matches: list[MarkerMatch] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def best(self) -> MarkerMatch | None:
        return self.matches[0] if self.matches else None