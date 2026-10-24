
"""Multi-page table stitching (TDD section 9.2).

Two continuation patterns are supported:

vertical
    The same table continues on the next page (repeated header is dropped and
    the source pages are recorded).
horizontal
    A very wide table is split across pages: the left part keeps the row
    labels, the right part continues the columns.  Rows are joined by
    position / row label.
"""
from __future__ import annotations

import difflib
import logging
import re
from typing import Sequence

from .pdf_reader import normalise
from .table_extractor import TableBlock, split_bilingual

log = logging.getLogger("pdf_extractor.stitch")


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", normalise(text).lower()) if t]


def header_similarity(a: list[str], b: list[str]) -> float:
    """Similarity of two header rows (0..1)."""
    ta = " ".join(" ".join(_tokens(t)) for t in a if t).split()
    tb = " ".join(" ".join(_tokens(t)) for t in b if t).split()
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    sa, sb = set(ta), set(tb)
    jaccard = len(sa & sb) / len(sa | sb)
    ratio = difflib.SequenceMatcher(None, " ".join(ta), " ".join(tb)).ratio()
    return max(jaccard, ratio)


def _row_label(rows: list[list[str]], index: int) -> str:
    if index >= len(rows):
        return ""
    return split_bilingual(normalise(rows[index][0] if rows[index] else ""))


def _is_header_row(block: TableBlock, index: int, reference: list[str], tol: float = 0.6) -> bool:
    return header_similarity(block.rows[index], reference) >= tol


def stitch_vertical(
    blocks: list[TableBlock],
    reference_header: list[str],
    tolerance: float = 0.6,
) -> tuple[list[list[str]], list[int]]:
    """Merge ``blocks`` (same table, consecutive pages) into one row list.

    Returns ``(rows, source_pages)``.  Repeated header rows are dropped.
    """
    rows: list[list[str]] = []
    pages: list[int] = []
    for b in blocks:
        page_rows = []
        for i, r in enumerate(b.rows):
            # the caller prepends ``reference_header`` itself, so the header of
            # the *first* block has to be dropped as well -- hence the row is
            # compared unconditionally (not only once ``rows`` is non-empty).
            if _is_header_row(b, i, reference_header, tolerance):
                log.debug("header berulang di-skip: page %s row %s", b.page, i)
                continue
            if not any(normalise(c) for c in r):
                continue
            page_rows.append([normalise(c) for c in r])
        if page_rows:
            rows.extend(page_rows)
            if b.page not in pages:
                pages.append(b.page)
    return rows, pages


def _first_col_kind(rows: list[list[str]]) -> str:
    """``"label"``, ``"numeric"`` or ``"empty"`` for the leading column.

    A pure numbering column ("1", "2", "a.") is skipped -- many reports put
    the row labels in the *second* column.
    """
    for c in (0, 1):
        vals = [normalise(r[c]) for r in rows if len(r) > c]
        filled = [v for v in vals if v]
        if not filled:
            continue
        numeric = sum(1 for v in filled if re.fullmatch(r"-?[\d.,()%\s]+", v))
        if numeric > 0.5 * len(filled):
            continue  # numbering or value column, keep looking
        return "label"
    vals = [normalise(r[0]) for r in rows if r]
    filled = [v for v in vals if v]
    if not filled:
        return "empty"
    return "numeric"


def _numeric_cells(row: Sequence[str]) -> int:
    return sum(1 for c in row if normalise(c) and re.fullmatch(r"-?[\d.,()%\s]+", normalise(c)))


def _merge_label_rows(rows: list[list[str]]) -> list[list[str]]:
    """Join a wrapped label ("d. Coal" / "Processing Plant  0  0  ...").

    Only used while stitching a spread: the facing page repeats the same rows
    without labels, so both sides must have exactly one row per data row.
    """
    out: list[list[str]] = []
    i = 0
    while i < len(rows):
        r = [normalise(c) for c in rows[i]]
        filled = [j for j, c in enumerate(r) if c]
        numeric = [j for j in filled if _numeric_cells([r[j]])]
        nxt = rows[i + 1] if i + 1 < len(rows) else None
        if (not numeric and len(filled) == 1 and nxt is not None
                and _numeric_cells(nxt) >= 2):
            j = filled[0]
            merged = [normalise(c) for c in nxt]
            if j < len(merged):
                merged[j] = f"{r[j]} {merged[j]}".strip() if merged[j] else r[j]
            out.append(merged)
            i += 2
            continue
        out.append(r)
        i += 1
    return out


def can_stitch_horizontal(a: TableBlock, b: TableBlock) -> bool:
    """Heuristic: is ``b`` the right-hand continuation of ``a``?

    Wide energy balance tables are printed as a spread: one page carries the
    row labels plus the first block of columns, the facing page repeats the
    same rows with the remaining columns and no labels at all.
    """
    if a.page == b.page:
        return False
    ra, rb = a.rows, b.rows
    if len(ra) < 3 or len(rb) < 3:
        return False
    if abs(len(ra) - len(rb)) > max(3, 0.35 * len(ra)):
        return False
    # headers must differ (otherwise it is a vertical continuation)
    if header_similarity(a.rows[0], b.rows[0]) >= 0.6:
        return False
    ka, kb = _first_col_kind(ra), _first_col_kind(rb)
    return (ka == "label" and kb in ("empty", "numeric")) or \
           (kb == "label" and ka in ("empty", "numeric"))


def stitch_horizontal(
    a: TableBlock,
    b: TableBlock,
    right_header: Sequence[str] | None = None,
    max_offset: int = 3,
) -> TableBlock:
    """Join the columns of ``b`` onto ``a`` (row alignment by data density).

    ``right_header`` supplies the column names of the right-hand part when
    they are printed above its detected grid.
    """
    if _first_col_kind(a.rows) == "label":
        left, right = a, b
    else:
        left, right = b, a
    if right_header is None:
        right_header = right.rows[0] if right.rows else []
    # Wrapped labels ("d. Coal" / "Processing Plant  0  0 ...") must be folded
    # first: the facing page repeats the same rows *without* labels, so both
    # sides only line up once each side holds exactly one row per data row.
    left_rows = _merge_label_rows(left.rows)
    right_rows = _merge_label_rows(right.rows)
    best_offset, best_hits = 0, -1
    for off in range(-max_offset, max_offset + 1):
        hits = 0
        for i in range(1, len(left_rows)):
            j = i + off
            if 0 <= j < len(right_rows) and _numeric_cells(left_rows[i]) >= 2 \
                    and _numeric_cells(right_rows[j]) >= 2:
                hits += 1
        if hits > best_hits:
            best_offset, best_hits = off, hits
    log.debug("stitch_horizontal offset=%s hits=%s", best_offset, best_hits)
    rows: list[list[str]] = [left_rows[0] + [normalise(c) for c in right_header]]
    for i in range(1, len(left_rows)):
        j = i + best_offset
        right_row = right_rows[j] if 0 <= j < len(right_rows) else []
        rows.append(left_rows[i] + [normalise(c) for c in right_row])
    return TableBlock(
        page=left.page,
        bbox=left.bbox | right.bbox,
        rows=rows,
        strategy=f"{left.strategy}+horizontal",
    )