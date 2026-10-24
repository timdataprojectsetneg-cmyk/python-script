
"""Deterministic table extraction (TDD section 9).

PyMuPDF's table finder gives good *column boundaries* but its row/cell
structure is unreliable on real world reports: merged cells (``GigaJoule
(GJ)`` spanning three rows) collapse a whole row into one cell, and tables
without full grid lines are cut after two rows.

The extractor therefore works in two steps:

1. take the column boundaries from the table finder (fallback: text strategy);
2. rebuild the rows from the page words inside the table area, assigning every
   word to the column whose x-range contains its centre.

Merged (sparse) columns are propagated downwards so grouped tables keep their
unit / category on every record.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Sequence

import pymupdf

from .pdf_reader import PageView, normalise

log = logging.getLogger("pdf_extractor.table")

#: a *whole* cell that is only a footnote marker is not a group header
_GROUP_STOP = re.compile(
    r"(?i)^(catatan|notes?|sumber|source|keterangan|description|figure|gambar)\s*[:.]?$"
)


@dataclass
class TableBlock:
    """A table found on a page."""

    page: int
    bbox: pymupdf.Rect
    rows: list[list[str]]
    strategy: str = "lines"
    col_bounds: list[float] = field(default_factory=list)
    #: True for rows that are a *merged* line (title / group header)
    merged_flags: list[bool] = field(default_factory=list)

    @property
    def ncols(self) -> int:
        return max((len(r) for r in self.rows), default=0)

    def row_text(self, index: int) -> str:
        return normalise(" ".join(c for c in self.rows[index] if c))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def split_bilingual(cell: str) -> str:
    """Keep the first (usually Indonesian) side of ``"Coal | Batu Bara"``."""
    if not cell:
        return ""
    parts = [normalise(p) for p in re.split(r"\s*\|\s*", cell)]
    parts = [p for p in parts if p]
    return parts[0] if parts else ""


def _col_bounds_from_table(tab) -> list[float]:
    xs: set[float] = set()
    for row in tab.rows:
        for c in row.cells:
            if c:
                xs.add(round(float(c[0]), 1))
                xs.add(round(float(c[2]), 1))
    return sorted(xs)


def _cell_text(page: PageView, rect) -> str:
    txt = page.text_in_rect(pymupdf.Rect(rect.x0 + 0.6, rect.y0 + 0.6, rect.x1 - 0.6, rect.y1 - 0.6))
    if not txt:
        txt = page.text_in_rect(rect)
    return txt


def _rows_from_cells(page: PageView, tab) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in tab.rows:
        cells: list[str] = []
        for c in row.cells:
            cells.append(_cell_text(page, pymupdf.Rect(c)) if c else "")
        rows.append(cells)
    return rows


def _cluster(items, key, tol: float):
    """Group ``items`` by ``key`` (tolerance ``tol``).

    The *document order* inside a group is preserved -- PyMuPDF returns words
    in reading order and reports usually print "Indonesian | English", which
    would be swapped by a plain sort on the y coordinate.
    """
    order = {id(it): i for i, it in enumerate(items)}
    items = sorted(items, key=key)
    groups: list[list] = []
    for it in items:
        if groups and key(it) - key(groups[-1][-1]) <= tol:
            groups[-1].append(it)
        else:
            groups.append([it])
    return [sorted(g, key=lambda it: order[id(it)]) for g in groups]


_NUM_WORD = re.compile(r"^-?[\d.,]+%?$|^\([\d.,]+\)$|^-?\d{1,3}(\.\d{3})*(,\d+)?$")

#: lines that close a table (footnotes, captions, source notes)
_STOP_LINE = re.compile(
    r"(?i)^\s*((keterangan|catatan|notes?|sumber|source|description|ket)\s*[:.]"
    r"|[\u2022\u25cf\u00b7\u2043\u25aa\u2219])"
)


def _row_tolerance(words) -> float:
    heights = [r.y1 - r.y0 for r, _ in words if r.y1 > r.y0]
    if not heights:
        return 4.0
    heights.sort()
    med = heights[len(heights) // 2]
    return max(3.0, min(8.0, med * 0.9))


def _column_of(col_bounds: list[float], cx: float) -> int:
    for i in range(len(col_bounds) - 1):
        if col_bounds[i] - 1.5 <= cx <= col_bounds[i + 1] + 1.5:
            return i
    return min(
        range(len(col_bounds) - 1),
        key=lambda i: abs((col_bounds[i] + col_bounds[i + 1]) / 2 - cx),
    )


def _is_continuous(line, max_baseline_spread: float = 4.0) -> bool:
    """True when the words of a line form one unbroken text block.

    Such a line is either a group header or a wrapped label -- in both cases
    it must not be split across columns.  A *stacked* header ("Hydro" /
    "Power" on the next baseline) is not one block: its words belong to
    different columns even though they sit close together.
    """
    if len(line) < 2:
        return False
    centres = [(w[0].y0 + w[0].y1) / 2 for w in line]
    if max(centres) - min(centres) > max_baseline_spread:
        return False
    ordered = sorted(line, key=lambda w: w[0].x0)
    for a, b in zip(ordered, ordered[1:]):
        if b[0].x0 - a[0].x1 > 12:
            return False
    return True


def rebuild_rows(
    page: PageView,
    col_bounds: list[float],
    y0: float,
    y1: float,
    max_gap_without_data: int = 4,
) -> list[list[str]]:
    """Wrapper around :func:`rebuild_rows_with_flags` (rows only)."""
    rows, _ = rebuild_rows_with_flags(page, col_bounds, y0, y1, max_gap_without_data)
    return rows


def rebuild_rows_with_flags(
    page: PageView,
    col_bounds: list[float],
    y0: float,
    y1: float,
    max_gap_without_data: int = 4,
) -> tuple[list[list[str]], list[bool]]:
    """Rebuild table rows from the words between ``y0`` and ``y1``.

    Scanning stops after ``max_gap_without_data`` consecutive lines without a
    numeric cell, which keeps footers and body text out of the table.
    """
    if len(col_bounds) < 2:
        return []
    x0, x1 = col_bounds[0], col_bounds[-1]
    ncols = len(col_bounds) - 1
    words = [
        (r, t) for r, t in page.words
        if r.y0 >= y0 - 2 and r.y1 <= y1 + 2
        and (r.x0 + r.x1) / 2 >= x0 - 4 and (r.x0 + r.x1) / 2 <= x1 + 4
    ]
    if not words:
        return []
    tol = _row_tolerance(words)
    lines = _cluster(words, lambda w: (w[0].y0 + w[0].y1) / 2, tol)

    rows: list[list[str]] = []
    flags: list[bool] = []
    last_data = 0
    for idx, line in enumerate(lines):
        cells = [""] * ncols
        merged = _is_continuous(line)
        if merged:
            first_col = _column_of(col_bounds, min(w[0].x0 for w in line) + 0.5)
            # keep the *document* order: it preserves "Indonesian | English"
            text = normalise(" ".join(t for _, t in line))
            cells[first_col] = text
        else:
            for r, t in sorted(line, key=lambda w: (round(w[0].y0, 1), w[0].x0)):
                i = _column_of(col_bounds, (r.x0 + r.x1) / 2)
                cells[i] = (cells[i] + " " + t).strip() if cells[i] else t
            cells = [normalise(c) for c in cells]
        # footnote markers never belong to a record
        for i, c in enumerate(cells):
            if c and _STOP_LINE.match(c):
                cells[i] = ""
        numeric = sum(1 for c in cells if c and _NUM_WORD.match(c))
        filled = sum(1 for c in cells if c)
        # footnotes / captions below the table must never become records
        if not filled:
            continue
        if numeric >= 2 or (merged and numeric >= 1):
            last_data = idx
        elif numeric == 0 and filled and idx - last_data > max_gap_without_data:
            break
        if filled:
            rows.append(cells[:ncols])
            flags.append(merged)
    return _merge_wrapped_labels(rows, flags)


def _merge_wrapped_labels(
    rows: list[list[str]], merged_flags: list[bool]
) -> tuple[list[list[str]], list[bool]]:
    """Join rows that belong together.

    Two patterns are handled:

    * a wrapped label -- a row with a single non numeric cell continues the
      label of the previous row;
    * a *values only* row -- a row whose filled cells are all numeric belongs
      to the previous (label only) row.  This happens whenever a tall label
      cell pushes the numbers onto another text line.
    """
    out: list[list[str]] = []
    flags: list[bool] = []
    for i, r in enumerate(rows):
        if not out:
            out.append(list(r))
            flags.append(merged_flags[i] if i < len(merged_flags) else False)
            continue
        is_merged = merged_flags[i] if i < len(merged_flags) else False
        filled = [j for j, c in enumerate(r) if c]
        numeric = [j for j in filled if _NUM_WORD.match(r[j])]
        prev = out[-1]
        if not is_merged and not numeric and len(filled) == 1:
            j = filled[0]
            if j < len(prev):
                prev[j] = f"{prev[j]} {r[j]}".strip() if prev[j] else r[j]
            continue
        prev_filled = [c for c in prev if c]
        if (
            numeric
            and len(numeric) == len(filled)
            and not any(_NUM_WORD.match(c) for c in prev if c)
            # a header row ("Coal | Briquette | ...") must never swallow the
            # first row of values -- only a wrapped *label* does that
            and not (len(out) == 1 and len(prev_filled) >= 2)
        ):
            for j, c in enumerate(r):
                if c and j < len(prev):
                    prev[j] = c
            continue
        out.append(list(r))
        flags.append(is_merged)
    return out, flags


def _propagate_merged(
    rows: list[list[str]],
    merged_flags: list[bool] | None = None,
    max_gap_rows: int = 4,
) -> list[list[str]]:
    """Fill sparse columns (merged cells such as a shared unit).

    Rows flagged as *merged* (group headers, table titles) are left alone:
    copying values into them would silently turn a label row into data.
    """
    if not rows:
        return rows
    flags = merged_flags or [False] * len(rows)
    ncols = max(len(r) for r in rows)
    body = [i for i in range(len(rows)) if not flags[i]]
    if not body:
        return [r[:ncols] for r in rows]
    fill_rate = [
        sum(1 for i in body if len(rows[i]) > c and rows[i][c]) / len(body)
        for c in range(ncols)
    ]
    out = [list(r) + [""] * (ncols - len(r)) for r in rows]
    for c in range(ncols):
        if fill_rate[c] >= 0.6:  # dense column: nothing to propagate
            continue
        # upwards (first row(s) of a merged block) -- runs first so that a
        # value cell shared by several rows is not overwritten by the header
        next_value, next_index = None, 10**9
        for i in range(len(out) - 1, -1, -1):
            if flags[i]:
                next_value, next_index = None, 10**9  # group header: reset
                continue
            if out[i][c]:
                next_value, next_index = out[i][c], i
            elif next_value is not None and next_index - i <= max_gap_rows:
                out[i][c] = next_value
        # downwards (merged cell starting at its first row)
        last_value, last_index = None, -99
        for i in range(len(out)):
            if flags[i]:
                last_value, last_index = None, -99  # group header: reset
                continue
            if out[i][c]:
                last_value, last_index = out[i][c], i
            elif last_value is not None and i - last_index <= max_gap_rows:
                out[i][c] = last_value
    return [r[:ncols] for r in out]


def header_band(page: PageView, block: TableBlock, band: float = 48.0) -> list[str]:
    """Column names printed just above ``block``.

    A facing page of a wide table repeats the numbers but not the labels, so
    its header often sits above the detected grid and has to be read from the
    band of text right on top of it.
    """
    bounds = block.col_bounds or []
    if len(bounds) < 2:
        return []
    y1 = block.bbox.y0 - 1
    y0 = max(0.0, block.bbox.y0 - band)
    words = [(r, t) for r, t in page.words if y0 <= (r.y0 + r.y1) / 2 <= y1]
    if not words:
        return []
    cells = [""] * (len(bounds) - 1)
    for r, t in sorted(words, key=lambda w: (round(w[0].y0, 1), w[0].x0)):
        i = _column_of(bounds, (r.x0 + r.x1) / 2)
        cells[i] = (cells[i] + " " + t).strip() if cells[i] else t
    return [normalise(c) for c in cells]


def _text_lines_in_bbox(page: PageView, bbox, tol: float = 3.0) -> int:
    """Number of distinct text baselines inside ``bbox``."""
    ys = sorted({round(r.y0, 1) for r, _ in page.words
                 if bbox.y0 - 1 <= r.y0 <= bbox.y1 + 1})
    count, prev = 0, None
    for y in ys:
        if prev is None or y - prev > tol:
            count += 1
        prev = y
    return count


def extract_table_blocks(
    page: PageView,
    strategies: tuple[str, ...] = ("lines", "text"),
) -> list[TableBlock]:
    """All tables on ``page``.

    Tables sharing the same column boundaries are treated as one table that
    was split by the grid detection (very common in real reports).
    """
    for strategy in strategies:
        try:
            found = page.page.find_tables(strategy=strategy).tables
        except Exception as exc:  # noqa: BLE001
            log.debug("find_tables(%s) gagal: %s", strategy, exc)
            continue
        if not found:
            continue
        groups: dict[tuple, list] = {}
        for tab in found:
            bounds = _col_bounds_from_table(tab)
            if len(bounds) < 3:
                continue
            key = tuple(round(b, 0) for b in bounds)
            groups.setdefault(key, []).append((tab, bounds))
        blocks: list[TableBlock] = []
        for bounds_group in groups.values():
            tabs = [t for t, _ in bounds_group]
            bounds = bounds_group[0][1]
            bbox = pymupdf.Rect(tabs[0].bbox)
            for t in tabs[1:]:
                bbox |= pymupdf.Rect(t.bbox)
            cells = [r for t in tabs for r in _rows_from_cells(page, t)]
            total = sum(len(r) for r in cells) or 1
            filled = sum(1 for r in cells for c in r if c)
            merged_flags: list[bool] = []
            rows: list[list[str]] | None = None
            if filled / total >= 0.55 and len(cells) >= 3 and sum(len(r) for r in cells) >= 6:
                # The grid of a report table often only surrounds the *group*
                # rows, so the cell grid hides most of the data.  When the same
                # area holds far more text lines than the grid produced rows,
                # the word based rebuild is the better source.
                lines = _text_lines_in_bbox(page, bbox)
                if not (lines >= 8 and len(cells) * 2 < lines):
                    rows = [[normalise(c) for c in r] for r in cells]
                    used = "cells"
            if rows is None:
                bottom = page.rect.y1 - max(24.0, 0.05 * page.rect.height)
                raw, flags = rebuild_rows_with_flags(page, bounds, bbox.y0 - 2, bottom)
                rows = _propagate_merged(raw, flags)
                merged_flags = flags[: len(rows)]
                used = "words"
            if len(rows) < 2:
                continue
            blocks.append(
                TableBlock(
                    page=page.number,
                    bbox=bbox,
                    rows=rows,
                    strategy=f"{strategy}:{used}",
                    col_bounds=bounds,
                    merged_flags=merged_flags,
                )
            )
        if blocks:
            return blocks
    return []


# --------------------------------------------------------------------------
# structure helpers
# --------------------------------------------------------------------------
def looks_like_group_row(cells: list[str], ncols: int) -> bool:
    """A row whose only filled cell is a non numeric label -> group header."""
    filled = [i for i, c in enumerate(cells) if normalise(c)]
    if len(filled) != 1:
        return False
    value = normalise(cells[filled[0]])
    if not value or _GROUP_STOP.match(value):
        return False
    if re.fullmatch(r"[\d.,]+", value):
        return False
    return True


def _norm_tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9%]+", normalise(text).lower()) if t]


def _name_score(cell: str, names: Sequence[str]) -> float:
    """How well ``cell`` matches one of the wanted field names (0..1)."""
    if not cell or not names:
        return 0.0
    ct = set(_norm_tokens(cell))
    low = normalise(cell).lower()
    best = 0.0
    for name in names:
        nt = _norm_tokens(name)
        if not nt:
            continue
        overlap = len(set(nt) & ct) / len(set(nt))
        contained = 1.0 if normalise(name).lower() in low else 0.0
        best = max(best, overlap, contained)
    return best


def _header_like(cells: Sequence[str]) -> bool:
    filled = [c for c in cells if normalise(c)]
    if not filled:
        return False
    return not any(_NUM_WORD.match(c) for c in filled)


def detect_header_index(
    rows: Sequence[Sequence[str]],
    field_names: Sequence[str] | None = None,
    scan: int = 8,
) -> int:
    """Find the row that holds the column names.

    Scoring favours rows whose cells match the requested dictionary fields and
    which are directly followed by numeric data -- this works for tables with
    a stacked title, with a bilingual header or with no header at all.
    """
    if not rows:
        return 0
    limit = min(scan, len(rows))
    best_idx, best_score = 0, float("-inf")
    for i in range(limit):
        cells = [normalise(c) for c in rows[i]]
        filled = [c for c in cells if c]
        if not filled:
            continue
        numeric = sum(1 for c in filled if _NUM_WORD.match(c))
        score = 1.5 * (len(filled) - numeric) - 2.0 * numeric
        if field_names:
            score += 4.0 * sum(_name_score(c, field_names) for c in filled)
        nxt = rows[i + 1] if i + 1 < len(rows) else []
        if sum(1 for c in nxt if c and _NUM_WORD.match(normalise(c))) >= 2:
            score += 2.0
        if score > best_score:
            best_idx, best_score = i, score
    return best_idx


def join_header(rows: Sequence[Sequence[str]], index: int) -> tuple[int, list[str]]:
    """Return ``(first_header_row, joined_header)`` for a stacked header."""
    start = index
    while start > 0 and len([c for c in rows[start - 1] if normalise(c)]) >= 2 and _header_like(rows[start - 1]):
        start -= 1
    ncols = max((len(r) for r in rows[start : index + 1]), default=0)
    header: list[str] = []
    for c in range(ncols):
        parts: list[str] = []
        for r in rows[start : index + 1]:
            v = normalise(r[c]) if c < len(r) else ""
            if v and v not in parts:
                parts.append(v)
        header.append(" | ".join(parts))
    return start, header


@dataclass
class TableStructure:
    """Header position + group labels resolved for one table."""

    header_index: int | None = None
    header_start: int = 0
    header: list[str] = field(default_factory=list)
    groups: dict[int, str] = field(default_factory=dict)
    data_rows: list[int] = field(default_factory=list)
    total_rows: set[int] = field(default_factory=set)


def analyse_structure(
    block: TableBlock,
    header_index: int | None = None,
    total_pattern: str = r"(?i)^(grand\s+)?(total|jumlah|subtotal)\b",
    field_names: Sequence[str] | None = None,
) -> TableStructure:
    """Locate the header row and collect group labels / data rows."""
    st = TableStructure()
    rows = block.rows
    if not rows:
        return st
    if header_index is None:
        header_index = detect_header_index(rows, field_names)
    st.header_index = header_index
    st.header_start, st.header = join_header(rows, header_index)

    current_group: str | None = None
    i = header_index + 1
    while i < len(rows):
        cells = [normalise(c) for c in rows[i]]
        if not any(cells):
            i += 1
            continue
        if looks_like_group_row(cells, block.ncols):
            # a bilingual group header is printed on two lines -- join them
            parts = [next(c for c in cells if c)]
            j = i
            while j + 1 < len(rows):
                nxt = [normalise(c) for c in rows[j + 1]]
                if not any(nxt) or not looks_like_group_row(nxt, block.ncols):
                    break
                parts.append(next(c for c in nxt if c))
                j += 1
            label = split_bilingual(" | ".join(parts))
            for k in range(i, j + 1):
                st.groups[k] = label
            current_group = label
            if re.match(total_pattern, label):
                st.total_rows.update(range(i, j + 1))
            i = j + 1
            continue
        st.data_rows.append(i)
        if current_group:
            st.groups[i] = current_group
        first = next((c for c in cells if c), "")
        if re.match(total_pattern, split_bilingual(first)):
            st.total_rows.add(i)
        i += 1
    return st