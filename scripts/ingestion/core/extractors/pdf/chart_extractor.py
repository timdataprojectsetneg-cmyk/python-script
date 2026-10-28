
"""Chart extraction (TDD section 10).

Charts are read from the *vector* content of the page: filled rectangles are
the bars of a (stacked / grouped) bar chart, arc paths are the slices of a pie
or donut chart.  Values are taken from the printed data labels whenever they
exist -- only when a segment carries no label is the value estimated from the
pixel height of the segment, and such values are flagged as
``chart_calibrated`` so a caller can tell them apart from printed ones.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Sequence

import pymupdf

from .pdf_reader import PageView, normalise

log = logging.getLogger("pdf_extractor.chart")

_NUM = re.compile(r"^-?\d{1,3}([.,]\d{3})*([.,]\d+)?%?$|^-?\d+([.,]\d+)?%?$|^\(-?[\d.,]+\)$")
_INT = re.compile(r"^(19|20)\d{2}$")


# --------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------
@dataclass
class ChartData:
    """Everything we managed to read from one chart."""

    page: int
    kind: str = "bar"                     # bar | stacked_bar | grouped_bar | pie | line
    title: str = ""
    title_years: list[int] = field(default_factory=list)
    unit: str | None = None
    bbox: tuple[float, float, float, float] = (0, 0, 0, 0)
    series: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    values: dict[tuple[str, str], float] = field(default_factory=dict)
    value_sources: dict[tuple[str, str], str] = field(default_factory=dict)
    shares: dict[str, float] = field(default_factory=dict)
    total: float | None = None
    total_source: str | None = None
    legend: dict[str, str] = field(default_factory=dict)  # colour key -> name
    confidence: float = 1.0
    warnings: list[str] = field(default_factory=list)

    def value(self, series: str, category: str) -> float | None:
        return self.values.get((series, category))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _colour_key(fill) -> str | None:
    """Coarse colour key (1 decimal) so near-identical fills stay together.

    PDF writers round colours differently per drawing call, so the same series
    often appears as ``0.19`` in one bar and ``0.18`` in the next.
    """
    if not fill:
        return None
    try:
        return "|".join(f"{float(c):.1f}" for c in fill[:3])
    except (TypeError, ValueError):
        return None


def _num_words(page: PageView):
    out = []
    for r, t in page.words:
        if _NUM.match(t.strip()):
            out.append((r, t))
    return out


def _parse_number(text: str) -> float | None:
    from .page_context import to_number

    try:
        return to_number(text)
    except ValueError:
        return None


def _cluster(items, key, tol: float):
    order = {id(it): i for i, it in enumerate(items)}
    groups: list[list] = []
    for it in sorted(items, key=key):
        if groups and key(it) - key(groups[-1][-1]) <= tol:
            groups[-1].append(it)
        else:
            groups.append([it])
    return [sorted(g, key=lambda it: order[id(it)]) for g in groups]


def _bar_rects(page: PageView) -> list[tuple[pymupdf.Rect, str, str]]:
    """Filled rectangles that look like bar segments (``(rect, colour, kind)``)."""
    area = page.rect.width * page.rect.height
    out: list[tuple[pymupdf.Rect, str, str]] = []
    for d in page.drawings:
        fill = d.get("fill")
        key = _colour_key(fill)
        if key is None:
            continue
        r = pymupdf.Rect(d["rect"])
        w, h = r.width, r.height
        if w <= 0.2 or h <= 0.2:
            continue
        if w * h > 0.02 * area or w > 0.7 * page.rect.width:
            continue
        kinds = {i[0] for i in d.get("items", [])}
        kind = "pie" if "c" in kinds else "rect"
        out.append((r, key, kind))
    return out


def _legend(page: PageView, swatches: Sequence[tuple[pymupdf.Rect, str]]) -> dict[str, str]:
    """Map colour -> legend name by reading the text right of each swatch."""
    words = page.words
    legend: dict[str, str] = {}
    for r, key in swatches:
        cy = (r.y0 + r.y1) / 2
        right = [
            (wr, t) for wr, t in words
            if wr.x0 >= r.x1 - 2 and wr.x0 <= r.x1 + 220
            and abs((wr.y0 + wr.y1) / 2 - cy) <= max(4.0, r.height)
        ]
        if not right:
            continue
        right.sort(key=lambda w: w[0].x0)
        parts: list[str] = [right[0][1]]
        last_x1 = right[0][0].x1
        for wr, t in right[1:]:
            if wr.x0 - last_x1 > 12:
                break
            parts.append(t)
            last_x1 = wr.x1
        name = normalise(" ".join(parts))
        if name:
            legend[key] = name
    return legend


def _is_swatch(r: pymupdf.Rect) -> bool:
    size_ok = 2.5 <= r.width <= 14 and 2.5 <= r.height <= 14
    return size_ok and 0.6 <= (r.width / r.height) <= 1.7


def _pie_regions(page: PageView, rects) -> list[pymupdf.Rect]:
    """Union the slice paths of every pie / donut on the page."""
    pies = [pymupdf.Rect(r) for r, _, kind in rects if kind == "pie"]
    if not pies:
        return []
    boxes: list[pymupdf.Rect] = []
    for group in _cluster(pies, lambda r: (r.y0 + r.y1) / 2, 40.0):
        box = pymupdf.Rect(group[0])
        for r in group[1:]:
            box |= r
        boxes.append(box)
    return [b for b in boxes if b.width > 12 and b.height > 12]


# --------------------------------------------------------------------------
# main entry point
# --------------------------------------------------------------------------
def extract_charts(
    page: PageView,
    min_bars: int = 2,
    calibrate: bool = True,
) -> list[ChartData]:
    """Extract every bar / pie chart found on ``page``."""
    rects = _bar_rects(page)
    if not rects:
        return []

    swatches = [(r, k) for r, k, kind in rects if kind == "rect" and _is_swatch(r)]
    swatch_ids = {id(r) for r, _ in swatches}
    bars = [(r, k) for r, k, kind in rects if kind == "rect" and id(r) not in swatch_ids]
    pies = _pie_regions(page, rects)

    charts: list[ChartData] = []
    if bars:
        charts.extend(_bar_charts(page, bars, swatches, pies, min_bars, calibrate))
    if not charts and pies:
        charts.append(_pie_chart(page, pies, _legend(page, swatches)))
    for c in charts:
        _attach_title(page, c)
    return charts


def _split_stacks(x_stacks) -> list[list]:
    """Split an x-cluster at vertical gaps -> one entry per real bar.

    Two charts drawn above each other use the same x positions, so a plain
    x-cluster would merge them.
    """
    bars: list[list] = []
    for stack in x_stacks:
        stack = sorted(stack, key=lambda b: -b[0].y1)  # bottom first
        current = [stack[0]]
        for b in stack[1:]:
            gap = current[-1][0].y0 - b[0].y1
            if gap > 12:
                bars.append(current)
                current = [b]
            else:
                current.append(b)
        bars.append(current)
    return bars


def _bar_charts(page, bars, swatches, pies, min_bars, calibrate) -> list[ChartData]:
    """Group bar segments into charts (one chart per baseline)."""
    x_stacks = _cluster(bars, lambda b: (b[0].x0 + b[0].x1) / 2, 3.0)
    stacks = _split_stacks(x_stacks)
    if len(stacks) < min_bars:
        return []

    # group bars that sit on the same baseline
    baseline = lambda s: round(max(b[0].y1 for b in s), 0)
    groups = _cluster(stacks, baseline, 4.0)
    charts: list[ChartData] = []
    for group in groups:
        if len(group) < min_bars:
            continue
        group = sorted(group, key=lambda s: (s[0][0].x0 + s[0][0].x1) / 2)
        charts.append(_build_chart(page, group, swatches, pies, calibrate))
    return charts


def _build_chart(page, stacks, swatches, pies, calibrate) -> ChartData:
    box = pymupdf.Rect(stacks[0][0][0])
    for s in stacks:
        for r, _ in s:
            box |= r
    baseline = max(r.y1 for s in stacks for r, _ in s)
    # the legend of *this* chart only
    legend = _legend(
        page,
        [(r, k) for r, k in swatches if box.y0 - 80 <= (r.y0 + r.y1) / 2 <= box.y1 + 80],
    )
    mid = (box.y0 + box.y1) / 2
    pies = [p for p in pies if abs((p.y0 + p.y1) / 2 - mid) < 80 and p.x0 > box.x0 - 5]
    for p in pies:
        box |= p

    # -- series order: bottom -> top of the richest stack -------------------
    richest = max(stacks, key=len)
    order: list[str] = []
    for r, key in richest:
        if key not in order:
            order.append(key)
    for s in stacks:
        for r, key in s:
            if key not in order:
                order.append(key)
    names: list[str] = []
    for key in order:
        name = legend.get(key) or key
        if name not in names:
            names.append(name)

    # -- categories (labels under the baseline) ----------------------------
    categories: list[str] = []
    for stack in stacks:
        xs = [r for r, _ in stack]
        x0, x1 = min(r.x0 for r in xs), max(r.x1 for r in xs)
        words = [
            (r, t) for r, t in page.words
            if r.y0 >= baseline - 3 and r.y0 <= baseline + 16
            and x0 - 8 <= (r.x0 + r.x1) / 2 <= x1 + 8
        ]
        numeric = [(r, t) for r, t in words if _NUM.match(t.strip())]
        chosen = numeric or words
        text = normalise(" ".join(t for _, t in sorted(chosen, key=lambda w: w[0].x0)))
        categories.append(text)

    # -- data labels --------------------------------------------------------
    numbers = _num_words(page)
    values: dict[tuple[str, str], float] = {}
    sources: dict[tuple[str, str], str] = {}
    used: set[int] = set()
    scale_samples: list[float] = []
    for ci, stack in enumerate(stacks):
        cat = categories[ci]
        for r, key in stack:
            series = legend.get(key) or key
            value = None
            for ni, (nr, nt) in enumerate(numbers):
                if ni in used or "%" in nt:
                    continue
                cx, cy = (nr.x0 + nr.x1) / 2, (nr.y0 + nr.y1) / 2
                if r.x0 - 2 <= cx <= r.x1 + 2 and r.y0 - 3 <= cy <= r.y1 + 3:
                    value = _parse_number(nt)
                    if value is not None:
                        used.add(ni)
                        break
            if value is None:
                # a thin segment often carries its label just above it
                best = None
                for ni, (nr, nt) in enumerate(numbers):
                    if ni in used or "%" in nt:
                        continue
                    cx, cy = (nr.x0 + nr.x1) / 2, (nr.y0 + nr.y1) / 2
                    if r.x0 - 3 <= cx <= r.x1 + 3 and 0 <= (r.y0 - cy) <= 9:
                        best = (ni, nt)
                        break
                if best is not None:
                    value = _parse_number(best[1])
                    used.add(best[0])
            if value is not None:
                values[(series, cat)] = value
                sources[(series, cat)] = "chart_data_label"
                if r.height > 0.5:
                    scale_samples.append(value / r.height)
            elif calibrate:
                values.pop((series, cat), None)

    # -- calibrate the segments without a label ----------------------------
    if calibrate and scale_samples:
        scale = sorted(scale_samples)[len(scale_samples) // 2]
        for ci, stack in enumerate(stacks):
            cat = categories[ci]
            for r, key in stack:
                series = legend.get(key) or key
                if (series, cat) in values:
                    continue
                values[(series, cat)] = round(r.height * scale, 3)
                sources[(series, cat)] = "chart_calibrated"

    # -- total: printed (pie centre / annotation) or sum of the segments ----
    total, total_source = _find_total(page, stacks, values, categories, pies, used, numbers)
    if total is None:
        latest = categories[-1] if categories else None
        parts = [v for (s, c), v in values.items() if c == latest]
        if parts:
            total, total_source = sum(parts), "derived"

    # -- shares: printed percentages or value / total ----------------------
    shares = _find_shares(page, numbers, used, values, categories, total)

    chart = ChartData(
        page=page.number,
        kind="stacked_bar" if len(richest) > 1 else ("grouped_bar" if len(stacks) > 1 else "bar"),
        bbox=(box.x0, box.y0, box.x1, box.y1),
        series=names,
        categories=categories,
        values=values,
        value_sources=sources,
        shares=shares,
        total=total,
        total_source=total_source,
        legend=legend,
        confidence=0.95 if total_source == "chart_data_label" else 0.8,
    )
    if not categories:
        chart.warnings.append("label kategori (sumbu x) tidak terbaca")
    return chart


def _find_total(page, stacks, values, categories, pies, used, numbers):
    """The printed grand total (donut centre text or an annotation)."""
    candidates: list[tuple[float, int]] = []
    for pie in pies:
        inner = pymupdf.Rect(pie)
        inner.x0 += 0.28 * pie.width
        inner.x1 -= 0.28 * pie.width
        inner.y0 += 0.28 * pie.height
        inner.y1 -= 0.28 * pie.height
        for ni, (nr, nt) in enumerate(numbers):
            if "%" in nt:
                continue
            cx, cy = (nr.x0 + nr.x1) / 2, (nr.y0 + nr.y1) / 2
            if inner.x0 <= cx <= inner.x1 and inner.y0 <= cy <= inner.y1:
                v = _parse_number(nt)
                if v is not None:
                    candidates.append((v, ni))
    if candidates:
        value, ni = max(candidates)
        used.add(ni)
        return value, "chart_data_label"
    return None, None


def _find_shares(page, numbers, used, values, categories, total):
    """Percentage labels of a pie chart, matched to their series."""
    pcts = []
    for ni, (nr, nt) in enumerate(numbers):
        if "%" in nt and nt.strip().endswith("%"):
            v = _parse_number(nt.rstrip("%"))
            if v is not None:
                pcts.append((ni, v))
    if not pcts or not total:
        return {}
    latest = categories[-1] if categories else None
    derived = {
        s: v / total * 100.0 for (s, c), v in values.items() if c == latest
    }
    shares: dict[str, float] = {}
    for ni, pct in pcts:
        best = min(derived.items(), key=lambda kv: abs(kv[1] - pct)) if derived else None
        if best and abs(best[1] - pct) <= 0.25:
            shares[best[0]] = pct
            used.add(ni)
    return shares


def _pie_chart(page, pies, legend) -> ChartData:
    pie = pies[0]
    numbers = _num_words(page)
    inner = pymupdf.Rect(pie)
    inner.x0 += 0.28 * pie.width
    inner.x1 -= 0.28 * pie.width
    inner.y0 += 0.28 * pie.height
    inner.y1 -= 0.28 * pie.height
    total = None
    for nr, nt in numbers:
        if "%" in nt:
            continue
        cx, cy = (nr.x0 + nr.x1) / 2, (nr.y0 + nr.y1) / 2
        if inner.x0 <= cx <= inner.x1 and inner.y0 <= cy <= inner.y1:
            total = _parse_number(nt)
    chart = ChartData(
        page=page.number, kind="pie", bbox=(pie.x0, pie.y0, pie.x1, pie.y1),
        total=total, total_source="chart_data_label" if total else None,
        confidence=0.6,
        warnings=["hanya total grafik lingkaran yang terbaca"],
    )
    return chart


def _attach_title(page: PageView, chart: ChartData) -> None:
    """Take the caption below (or the heading above) the chart as its title."""
    x0, y0, x1, y1 = chart.bbox
    below = [
        (r, t) for r, t in page.words
        if r.y0 >= y1 - 2 and r.y0 <= y1 + 70 and r.x0 <= x1 + 30
    ]
    above = [
        (r, t) for r, t in page.words
        if r.y1 <= y0 + 2 and r.y1 >= y0 - 80
    ]
    def _best(words) -> str:
        if not words:
            return ""
        bands = _cluster(words, lambda w: round(w[0].y0 / 4) * 4, 1.0)
        usable = [
            b for b in bands
            if not all(_NUM.match(t.strip()) for _, t in b) and len(b) >= 2
        ]
        band = max(usable or bands, key=len)
        return normalise(" ".join(t for _, t in sorted(band, key=lambda w: w[0].x0)))

    text = _best(below) or _best(above)
    chart.title = text
    chart.title_years = [int(y) for y in re.findall(r"\b((?:19|20)\d{2})\b", text)]

    # unit: "Million BOE" / "(GJ)" next to the total or on the axis
    words = [
        t for r, t in page.words
        if not _NUM.match(t.strip()) and re.search(r"(?i)^(million|thousand|trillion|gj|gwh|mwh|kwh|toe|boe|kl|ton|%|rp)$", t)
    ]
    if words:
        chart.unit = normalise(" ".join(dict.fromkeys(words))[:40])
    m = re.search(r"(?i)\((million\s+boe|thousand\s+boe|gj|gwh|toe|boe)\)", text)
    if m:
        chart.unit = m.group(1)