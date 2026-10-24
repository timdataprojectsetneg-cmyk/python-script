


"""Orchestration and the public :func:`extract_pdf` API (TDD section 12).

Pipeline (TDD section 6)::

    inputs -> page selection -> text layer preflight -> marker search
    -> candidate identification -> extraction -> dictionary mapping
    -> multi page stitching -> page context -> validation
    -> optional LLM -> result + provenance + errors
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import pymupdf

from .chart_extractor import ChartData, extract_charts
from .config import ExtractConfig, LLMConfig
from .dictionary_mapper import (
    MappedTable,
    load_dictionary,
    map_chart,
    map_columns,
    map_table,
)
from .llm_extractor import LLMUnavailable, extract_with_llm, is_available
from .marker_detector import MarkerMatch, find_markers
from .models import (
    Dictionary,
    ExtractionKind,
    ExtractionMethod,
    ExtractionResult,
    Provenance,
    SourceInfo,
    Status,
)
from .page_context import PageContext
from .page_selector import resolve_pages, resolve_printed_pages
from .pdf_reader import PdfOpenError, PdfSource, normalise
from .table_extractor import (
    TableBlock,
    analyse_structure,
    extract_table_blocks,
    header_band,
)
from .table_stitcher import (
    can_stitch_horizontal,
    header_similarity,
    stitch_horizontal,
    stitch_vertical,
)
from .validators import strip_internal, validate_records

log = logging.getLogger("pdf_extractor")

_YEAR = re.compile(r"\b((?:19|20)\d{2})\b")


# --------------------------------------------------------------------------
# candidates
# --------------------------------------------------------------------------
@dataclass
class Candidate:
    kind: str                       # "table" | "chart"
    page: int
    bbox: tuple[float, float, float, float]
    score: float = 0.0
    distance: float = 0.0
    block: TableBlock | None = None
    chart: ChartData | None = None
    note: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


def _distance(marker: MarkerMatch, bbox: Sequence[float]) -> float:
    """Vertical gap between the marker and a candidate object."""
    my0, my1 = (marker.y, marker.y) if marker.rect is None else (marker.rect.y0, marker.rect.y1)
    y0, y1 = bbox[1], bbox[3]
    if my1 < y0:
        return y0 - my1
    if my0 > y1:
        return my0 - y1
    return 0.0


_SEGMENT = re.compile(r"\s*(?:\||/|–|—|\bu2013|\s+-\s+)\s*")
_YEARISH = re.compile(r"(tahun|year|periode|(?:19|20)\d{2})", re.I)
_UNITISH = re.compile(r"(satuan|unit|uom|measure)", re.I)


def _marker_segments(marker: str) -> list[str]:
    """Split a bilingual marker such as ``"Judul | Title"`` into its sides.

    Indonesian energy reports print every heading twice, so a marker usually
    carries both languages.  Matching each side on its own keeps a paraphrased
    heading ("Energy *Consumed* ... by Energy Source") recognisable.
    """
    parts = [p.strip() for p in _SEGMENT.split(marker) if p and p.strip()]
    return parts or [marker]


def _token_overlap(marker: str, text: str) -> float:
    """Share of the marker's words that also appear in ``text`` (0..1).

    ``Consumption``/``Consumed`` and ``Production``/``Produced`` are treated as
    the same word -- the marker is written by a human, the document by its
    author, so exact equality is too strict.
    """
    def toks(s: str) -> set[str]:
        return {t for t in re.findall(r"[a-z0-9]+", s.lower()) if len(t) > 2}

    mt, tt = toks(marker), toks(text)
    if not mt or not tt:
        return 0.0
    hits = 0
    for t in mt:
        if t in tt:
            hits += 1
            continue
        if any((t[:5] == o[:5] and len(t) >= 5 and len(o) >= 5) for o in tt):
            hits += 1
    return hits / len(mt)


def _marker_relevance(marker: str, text: str) -> float:
    """Relevance of ``text`` (a title/context band) to the marker (0..1)."""
    best = _token_overlap(marker, text)
    for seg in _marker_segments(marker):
        if len(re.findall(r"[a-z0-9]+", seg.lower())) < 2:
            continue  # a one word segment matches far too easily
        best = max(best, _token_overlap(seg, text))
    return best


def _context_text(page, bbox: Sequence[float], header: Sequence[str]) -> str:
    """Text printed just above a table/chart plus its own header row."""
    y0 = max(0.0, bbox[1] - 90.0)
    above = page.text_in_rect((bbox[0] - 20, y0, bbox[2] + 20, bbox[1] + 2))
    return f"{above} {' '.join(str(h) for h in header)}"


def _dict_coverage(header: Sequence[str], dictionary: Dictionary) -> float:
    if not dictionary.fields:
        return 0.0
    non_derived = [f for f in dictionary.fields if not f.derived]
    if not non_derived:
        return 0.0
    return len(map_columns(header, dictionary)) / len(non_derived)


def _chart_coverage(chart: ChartData, dictionary: Dictionary) -> float:
    """How many dictionary fields a chart can actually fill (0..1).

    A chart is only a real candidate when it carries values; without a series
    there is nothing to map, so the coverage is zero.
    """
    fields = [f for f in dictionary.fields if not f.derived]
    if not fields or not chart.series:
        return 0.0
    has_year = bool(chart.title_years) or bool(re.search(r"(?:19|20)\d{2}", chart.title))
    hits = 0
    for f in fields:
        joined = " ".join([f.name, *f.aliases])
        if _YEARISH.search(joined):
            hits += 1 if has_year else 0
        elif f.derived == "share_of_total":
            hits += 1 if (chart.shares or chart.total) else 0
        elif f.derived == "yoy":
            hits += 1 if len(chart.categories) > 1 else 0
        elif _UNITISH.search(joined):
            hits += 1 if chart.unit else 0
        elif f.kind in ("int", "float"):
            hits += 1 if chart.values else 0
        else:
            hits += 1 if (chart.series or chart.categories) else 0
    return hits / len(fields)


def _header_is_weak(header: Sequence[str]) -> bool:
    """True when the detected header row is not a header at all.

    Word based row rebuilding sometimes starts a "table" inside a paragraph or
    on a row of numbers; such a block must not outrank a real table/chart.
    """
    cells = [str(h).strip() for h in header if str(h).strip()]
    if not cells:
        return True
    alpha = [c for c in cells if re.search(r"[A-Za-zÀ-ɏ]", c)]
    if not alpha:
        return True
    numeric = sum(1 for c in cells if re.fullmatch(r"[\d.,%()\s]+", c))
    return numeric > len(alpha)


# --------------------------------------------------------------------------
# main API
# --------------------------------------------------------------------------
def extract_pdf(
    pdf_path: str | Path,
    dictionary: Any,
    marker: str,
    pages: Iterable[int] | str | None = None,
    mode: str = "auto",
    page_numbering: str = "auto",
    config: ExtractConfig | None = None,
    llm: LLMConfig | None = None,
    **kwargs: Any,
) -> ExtractionResult:
    """Extract structured records for ``marker`` from ``pdf_path``.

    Parameters
    ----------
    pdf_path:
        PDF file to read.
    dictionary:
        Path to a ``.json``/``.py`` dictionary, a ``dict``, a Pydantic model
        class or a :class:`Dictionary`.
    marker:
        Text that identifies the wanted table/chart (above *or* below it).
    pages:
        ``1``, ``"1,3,5"``, ``"5-8"``, ``"all"`` or a list.  ``None`` means
        *page 1* (TDD section 4.2).
    mode:
        ``auto`` | ``table`` | ``chart``.
    page_numbering:
        ``auto`` | ``physical`` | ``printed``.
    """
    cfg = config or ExtractConfig()
    if pages is not None:
        cfg.pages = pages
    if mode:
        cfg.mode = mode
    if page_numbering:
        cfg.page_numbering = page_numbering
    if llm is not None:
        cfg.llm = llm
    for key, value in kwargs.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)
    if isinstance(cfg.output, str):
        cfg.output = Path(cfg.output)
    if cfg.verbose:
        logging.getLogger("pdf_extractor").setLevel(logging.DEBUG)

    source_info = SourceInfo(file_name=Path(pdf_path).name, file_path=str(pdf_path))
    try:
        dictionary_obj = load_dictionary(dictionary, cfg.model_class)
    except Exception as exc:  # noqa: BLE001
        return ExtractionResult(
            status=Status.SCHEMA_MAPPING_FAILED, marker=marker, source=source_info,
            errors=[f"dictionary tidak valid: {exc}"],
        )

    try:
        source = PdfSource(pdf_path)
    except PdfOpenError as exc:
        return ExtractionResult(
            status=Status.INVALID_PDF, marker=marker, source=source_info,
            errors=[str(exc)],
        )

    with source:
        return _run(source, source_info, dictionary_obj, marker, cfg)


def _run(
    source: PdfSource,
    source_info: SourceInfo,
    dictionary: Dictionary,
    marker: str,
    cfg: ExtractConfig,
) -> ExtractionResult:
    result = ExtractionResult(
        marker=marker, source=source_info,
        metadata={"mode": cfg.mode, "method": ExtractionMethod.DETERMINISTIC.value},
    )
    source_info.page_count = source.page_count

    # -- 1. page selection ---------------------------------------------------
    # Reports label their pages; "halaman 110" almost always means the page
    # *printed* as 110.  In ``auto`` mode both interpretations are searched and
    # the printed one is treated as the primary target.
    numbering = cfg.page_numbering
    physical = resolve_pages(cfg.pages, source.page_count, default=[1])
    printed: list[int] = []
    mapping: dict[int, int] = {}
    if numbering in ("auto", "printed") and cfg.pages is not None:
        printed, mapping = resolve_printed_pages(cfg.pages, source)
    if numbering == "printed":
        search = printed
        primary = printed
    elif numbering == "physical" or not printed:
        search = physical
        primary = physical
    else:
        search = sorted(set(physical) | set(printed))
        primary = printed
    if mapping and printed != physical:
        result.metadata["page_numbering"] = "printed"
        result.metadata["printed_to_physical"] = mapping
    if not search:
        result.status = Status.INVALID_PAGE_RANGE
        result.errors.append(
            f"rentang halaman tidak valid: {cfg.pages!r} (dokumen {source.page_count} halaman)"
        )
        return result

    # -- 2. text layer preflight --------------------------------------------
    good: list[int] = []
    for n in search:
        ok, why = source.page(n).check_text_layer(cfg.min_chars, cfg.max_garbled)
        if ok:
            good.append(n)
        else:
            result.warnings.append(f"halaman {n}: {why}")
    if not good:
        result.status = Status.INSUFFICIENT_TEXT_LAYER
        result.errors.append("tidak ada halaman dengan text layer yang memadai")
        return result

    # -- 3. marker search ----------------------------------------------------
    matches = find_markers(
        [source.page(n) for n in good], marker, cfg.marker_match, cfg.marker_threshold
    )
    if not matches and numbering != "physical" and cfg.pages not in (None, "all"):
        # fall back to the plain physical reading of the same numbers
        extra = [n for n in physical if n not in good and 1 <= n <= source.page_count]
        if extra:
            good = sorted(set(good) | set(extra))
            matches = find_markers(
                [source.page(n) for n in good], marker, cfg.marker_match, cfg.marker_threshold
            )
    if not matches:
        result.status = Status.MARKER_NOT_FOUND
        result.errors.append(
            f"marker {marker!r} tidak ditemukan pada halaman {good}"
        )
        return result

    result.metadata["marker_hits"] = [
        {"page": m.page, "text": m.text, "score": round(m.score, 2), "kind": m.kind}
        for m in matches
    ]

    # -- 4. candidates -------------------------------------------------------
    best_match = matches[0]
    field_names = [a for f in dictionary.fields for a in f.candidates()]
    candidates: list[Candidate] = _collect_candidates(
        source, best_match, marker, dictionary, field_names, cfg, primary, search
    )
    if not candidates:
        result.status = Status.DATA_CANDIDATE_NOT_FOUND
        result.errors.append(
            f"marker ditemukan di halaman {best_match.page} tetapi tabel/grafik "
            "terkait tidak teridentifikasi"
        )
        return result

    candidates.sort(key=lambda c: -c.score)
    best = candidates[0]
    ambiguous = len(candidates) > 1 and candidates[1].score >= best.score * 0.9
    if ambiguous:
        result.warnings.append(
            "ambiguous_candidate: lebih dari satu kandidat relevan "
            f"({best.kind} halaman {best.page} vs {candidates[1].kind} "
            f"halaman {candidates[1].page}) -- dipilih yang skornya tertinggi"
        )
    result.metadata["candidate"] = {
        "kind": best.kind, "page": best.page, "score": round(best.score, 2),
        "distance": round(best.distance, 1), "note": best.note,
    }

    # -- 5. extraction + mapping --------------------------------------------
    page_view = source.page(best.page)
    context = PageContext.from_page(page_view)
    result.metadata["page_title"] = context.title
    if context.years:
        result.metadata["years"] = context.years
    if context.unit:
        result.metadata["unit"] = context.unit

    if best.kind == "table":
        mapped, pages = _extract_table(source, best, dictionary, field_names, cfg,
                                       context, source_info.file_name, marker)
        # a spread prints the unit on the facing page only, so the remaining
        # pages of the table are searched as well
        if not context.unit:
            for n in pages:
                if n == best.page:
                    continue
                other = PageContext.from_page(source.page(n))
                if other.unit:
                    context.unit = other.unit
                    result.metadata["unit"] = other.unit
                    break
    else:
        mapped, pages = _extract_chart(best, dictionary, context, source_info.file_name,
                                       marker)
        result.metadata["chart_title"] = best.chart.title if best.chart else ""
        if best.chart and best.chart.unit:
            result.metadata["unit"] = best.chart.unit

    result.source.pages = pages
    result.metadata["kind"] = best.kind
    result.metadata["extraction"] = best.block.strategy if best.block else best.chart.kind
    if mapped.unmapped:
        result.warnings.append("schema_mapping_failed: " + ", ".join(mapped.unmapped))
    result.warnings.extend(mapped.warnings)
    if not mapped.records:
        result.status = Status.SCHEMA_MAPPING_FAILED
        result.errors.append("field dictionary tidak dapat dipetakan ke data sumber")
        return result

    # -- 6. validation -------------------------------------------------------
    records, warns, errors = validate_records(
        mapped.records, dictionary, cfg.min_confidence, cfg.max_records
    )
    result.records = records
    result.warnings.extend(warns)
    result.errors.extend(errors)
    result.provenance = mapped.provenance[: len(records)]
    for prov in result.provenance:
        prov.file_name = source_info.file_name
        prov.marker = marker
        prov.kind = ExtractionKind(best.kind)
        if not prov.pages:
            prov.pages = pages
        if not prov.page:
            prov.page = best.page

    # -- 7. optional LLM -----------------------------------------------------
    if cfg.llm.enabled and is_available(cfg.llm):
        # "fallback" = only step in when the deterministic pass is clearly not
        # good enough (nothing found, schema not covered, ambiguous choice);
        # "all" = always ask the model.
        unsatisfactory = bool(errors) or ambiguous or any(
            w.startswith(("schema_mapping_failed", "field tidak terpetakan"))
            for w in result.warnings
        )
        if cfg.llm.mode == "all" or unsatisfactory:
            _assist_llm(source, pages, dictionary, marker, cfg, result)

    # -- 8. status -----------------------------------------------------------
    if result.errors:
        result.status = Status.VALIDATION_FAILED
    elif result.warnings:
        result.status = Status.PARTIAL
    else:
        result.status = Status.SUCCESS
    result.metadata["record_count"] = len(result.records)
    return result


# --------------------------------------------------------------------------
# candidate discovery
# --------------------------------------------------------------------------
def _collect_candidates(
    source: PdfSource,
    match: MarkerMatch,
    marker: str,
    dictionary: Dictionary,
    field_names: list[str],
    cfg: ExtractConfig,
    primary_pages: Sequence[int] = (),
    requested_pages: Sequence[int] = (),
) -> list[Candidate]:
    """Tables/charts around the marker, scored by dictionary fit + relevance.

    The dominant term is *how much of the dictionary the object can fill* --
    a "table" that maps no field at all is almost always prose that the row
    builder mistook for a grid, and it must never outrank a real table or a
    chart that carries the requested measures.
    """
    out: list[Candidate] = []
    pages = [match.page]
    if cfg.allow_cross_page:
        pages += [
            n for n in range(match.page + 1,
                             min(source.page_count, match.page + cfg.max_neighbour_pages) + 1)
        ]
    for n in pages:
        page = source.page(n)
        if n in primary_pages:
            page_bonus = 2.0          # the page the user asked for
        elif n in requested_pages:
            page_bonus = 0.0          # the other numbering interpretation
        else:
            page_bonus = -1.0         # a neighbour page
        if cfg.mode in ("auto", "table"):
            for block in extract_table_blocks(page):
                bbox = (block.bbox.x0, block.bbox.y0, block.bbox.x1, block.bbox.y1)
                dist = _distance(match, bbox)
                if dist > cfg.search_radius and n == match.page:
                    continue
                structure = analyse_structure(block, field_names=field_names)
                coverage = _dict_coverage(structure.header, dictionary)
                if coverage == 0 and cfg.mode == "table":
                    continue
                relevance = _marker_relevance(marker, _context_text(page, bbox,
                                                                    structure.header))
                score = (1.0 + 4.0 * coverage + 2.0 * relevance
                         + 0.3 * min(len(structure.data_rows), 40) / 10.0
                         + page_bonus)
                if _header_is_weak(structure.header) and coverage < 0.5:
                    score -= 2.5
                score -= min(dist, 600) / 600.0
                out.append(Candidate("table", n, bbox, score, dist, block=block,
                                     note=f"kolom={len(structure.header)}",
                                     meta={"coverage": round(coverage, 2),
                                           "relevance": round(relevance, 2)}))
        if cfg.mode in ("auto", "chart"):
            for chart in extract_charts(page, cfg.min_bars, cfg.calibrate):
                dist = _distance(match, chart.bbox)
                if dist > cfg.search_radius and n == match.page:
                    continue
                coverage = _chart_coverage(chart, dictionary)
                relevance = _marker_relevance(marker, chart.title)
                if any(f.derived for f in dictionary.fields):
                    coverage = min(1.0, coverage + 0.05)
                score = (1.0 + 4.0 * coverage + 2.0 * relevance
                         + 0.15 * min(len(chart.series), 12) + page_bonus)
                if cfg.mode == "chart" and coverage == 0:
                    continue
                score -= min(dist, 600) / 600.0
                out.append(Candidate("chart", n, chart.bbox, score, dist, chart=chart,
                                     note=chart.title[:60],
                                     meta={"series": len(chart.series),
                                           "coverage": round(coverage, 2)}))
    return out


# --------------------------------------------------------------------------
# table / chart extraction
# --------------------------------------------------------------------------
def _extract_table(
    source: PdfSource,
    candidate: Candidate,
    dictionary: Dictionary,
    field_names: list[str],
    cfg: ExtractConfig,
    context: PageContext,
    file_name: str | None,
    marker: str,
) -> tuple[MappedTable, list[int]]:
    block = candidate.block
    structure = analyse_structure(block, field_names=field_names)
    blocks = [block]
    pages = [block.page]

    if cfg.allow_cross_page:
        limit = min(source.page_count, block.page + cfg.max_neighbour_pages)
        # 1. a wide table continues on the *facing* page with more columns
        for n in range(block.page + 1, limit + 1):
            for other in extract_table_blocks(source.page(n)):
                if other.bbox.y0 > block.bbox.y1 + 40:  # not the same spread
                    continue
                if can_stitch_horizontal(block, other):
                    header = other.rows[0] if other.rows else []
                    usable = [c for c in header if normalise(c)]
                    if usable and all(re.fullmatch(r"-?[\d.,()%\s]+", normalise(c))
                                      for c in usable):
                        # the names are printed above the detected grid
                        band = min(140.0, max(48.0, other.bbox.y0))
                        header = header_band(source.page(n), other, band)
                    block = stitch_horizontal(block, other, header)
                    structure = analyse_structure(block, field_names=field_names)
                    blocks = [block]
                    pages.append(n)
                    break
            if len(pages) > 1:
                break
        # 2. otherwise a long table simply continues on the next page
        if len(pages) == 1:
            for n in range(block.page + 1, limit + 1):
                page = source.page(n)
                for other in extract_table_blocks(page):
                    if other.bbox.y0 > block.bbox.y1 + 40:  # not directly below
                        continue
                    st = analyse_structure(other, field_names=field_names)
                    if header_similarity(structure.header, st.header) >= cfg.stitch_header_tolerance:
                        blocks.append(other)
                        pages.append(n)
                        break

    if len(blocks) > 1:
        rows, pages = stitch_vertical(blocks, structure.header, cfg.stitch_header_tolerance)
        combined = TableBlock(
            page=block.page,
            bbox=block.bbox,
            rows=[structure.header] + rows,
            strategy=f"{block.strategy}+stitched",
            col_bounds=block.col_bounds,
        )
        structure = analyse_structure(combined, header_index=0, field_names=field_names)
        block = combined

    mapped = map_table(block, structure, dictionary, context, file_name, marker)
    for prov in mapped.provenance:
        prov.pages = list(pages)
    return mapped, sorted(set(pages))


def _extract_chart(
    candidate: Candidate,
    dictionary: Dictionary,
    context: PageContext,
    file_name: str | None,
    marker: str,
) -> tuple[MappedTable, list[int]]:
    chart = candidate.chart
    if context.years and not chart.title_years:
        chart.title_years = context.years
    mapped = map_chart(chart, dictionary, context, file_name, marker)
    return mapped, [chart.page]


# --------------------------------------------------------------------------
# LLM assistance
# --------------------------------------------------------------------------
def _assist_llm(
    source: PdfSource,
    pages: Sequence[int],
    dictionary: Dictionary,
    marker: str,
    cfg: ExtractConfig,
    result: ExtractionResult,
) -> None:
    try:
        texts = {
            n: source.page(n).normalised_text
            for n in pages[: max(1, cfg.llm.max_pages_per_request)]
        }
        records, provenance = extract_with_llm(dictionary, marker, texts, cfg.llm)
    except LLMUnavailable as exc:
        result.warnings.append(f"llm_request_failed: {exc}")
        return
    clean, warns, errors = validate_records(
        [strip_internal([r])[0] for r in records], dictionary
    )
    if clean and not errors:
        # LLM output replaces the deterministic one only when it validates
        result.records = clean
        result.provenance = provenance[: len(clean)]
        result.metadata["method"] = ExtractionMethod.LLM.value
        result.errors = []
        result.warnings.extend(warns + ["sebagian nilai berasal dari LLM"])
    else:
        result.warnings.append("llm_request_failed: hasil LLM tidak lolos validasi")
        result.warnings.extend(errors)