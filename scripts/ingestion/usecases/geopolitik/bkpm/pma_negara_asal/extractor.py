"""PMA Negara Asal (BKPM): lima besar negara asal PMA dari paparan realisasi investasi.

The BKPM landing page (``.../info/realisasi-investasi/<year>``) lists each release
as a download button whose ``data-remote`` carries ``saved_name=<id>.pdf``; the
file itself is served from ``/storage/file/pdf/<id>.pdf``. Every release on the
page is read (newest first); when a period appears in several releases the
newest release wins. Every page of a PDF is scanned for a "5 Besar Negara ...
PMA" header. Three layouts exist: an infographic whose values sit above bars and
country names below (Q1 and Q4/FY releases, paired by x position), and a vertical
list of "<negara> / USD x,y Miliar" (Q2 and Q3 releases, paired by order).
"Bidang Hilirisasi" pages are not the country ranking and are skipped.
The sibling year pages linked from the landing page (e.g. 2024 and 2026) are read
too. ``PDF_URL`` pins a specific file; ``MAX_PAGES`` (optional) limits the pages read
per PDF and logs a warning.
"""

from __future__ import annotations

import io
import logging
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

CELL_GAP = 55  # pieces of one printed value sit closer than this on the x axis
LINE_TOLERANCE = 3.0
Fragment = Tuple[float, float, str]  # x, y, text

_PERIOD = (
    r"Triwulan\s+[IV]+(?:\s+[IV]+)?\s+(?:Tahun\s+)?\d{4}"
    r"|Semester\s+[IV]+(?:\s+[IV]+)?\s+(?:Tahun\s+)?\d{4}"
    r"|Januari\s*[–-]\s*[A-Za-z]+\s+\d{4}"
)
HEADERS = [
    re.compile(rf"Realisasi\s+(?P<period>{_PERIOD})\s*:?\s*5\s+Besar\s+Negara\s+Asal\s+PMA", re.IGNORECASE),
    re.compile(rf"5\s+Besar\s+Negara\s+Realisasi(?:\s+Investasi)?(?:\s+PMA)?\s*:?\s*(?P<period>{_PERIOD})", re.IGNORECASE),
]
VALUE = re.compile(r"^(?:US\$|USD)?\s*\d+[,.]\d+\s*(?:M|Miliar)?$", re.IGNORECASE)
LIST_VALUE = re.compile(r"USD\s*(\d[\d\s]*[,.][\d\s]*\d)\s*Miliar", re.IGNORECASE)
YEAR_PAGE = re.compile(r"/realisasi-investasi/(\d{4})/?$")
YEAR_LINK = re.compile(r"/realisasi-investasi/(\d{4})(?![\d/])")
NON_NAMES = {"USD", "US$", "M", "Miliar"}
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4}
MONTH_NUMBER = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7,
    "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
}


def squash(text: str) -> str:
    return " ".join((text or "").split())


def normalize_period(raw: str) -> Optional[str]:
    """``Triwulan IV Tahun 2025`` -> ``2025-Q4``; ``Semester I 2025`` -> ``2025-YTD06``; ``Januari - Desember 2025`` -> ``2025-FY``."""
    text = squash(raw)
    quarter = re.match(r"Triwulan\s+([IV]+(?:\s+[IV]+)?)\s+(?:Tahun\s+)?(\d{4})$", text, re.IGNORECASE)
    if quarter:
        number = ROMAN.get(re.sub(r"\s+", "", quarter.group(1)).upper())
        return f"{quarter.group(2)}-Q{number}" if number else None
    semester = re.match(r"Semester\s+(I)\s+(?:Tahun\s+)?(\d{4})$", text, re.IGNORECASE)
    if semester:
        return f"{semester.group(2)}-YTD06"
    cumulative = re.match(r"Januari\s*[–-]\s*([A-Za-z]+)\s+(\d{4})$", text, re.IGNORECASE)
    if cumulative:
        month = MONTH_NUMBER.get(cumulative.group(1).lower())
        if month == 12:
            return f"{cumulative.group(2)}-FY"
        if month:
            return f"{cumulative.group(2)}-YTD{month:02d}"
    return None


def parse_value(text: str) -> float:
    cleaned = re.sub(r"US\$|USD|Miliar|M", "", text, flags=re.IGNORECASE)
    return float(re.sub(r"\s+", "", cleaned).replace(",", "."))


def group_lines(fragments: List[Fragment]) -> List[List[Fragment]]:
    """Fragments grouped into visual lines, top (largest y) first."""
    lines: List[List[Fragment]] = []
    for fragment in sorted(fragments, key=lambda f: (-f[1], f[0])):
        if lines and abs(lines[-1][0][1] - fragment[1]) <= LINE_TOLERANCE:
            lines[-1].append(fragment)
        else:
            lines.append([fragment])
    return lines


def line_text(line: List[Fragment]) -> str:
    return squash(" ".join(text for _, _, text in sorted(line, key=lambda f: f[0])))


def header_period(fragments: List[Fragment]) -> Optional[str]:
    """Normalized period of the "5 Besar Negara ... PMA" header, if the page has one."""
    text = " ".join(line_text(line) for line in group_lines(fragments))
    for pattern in HEADERS:
        match = pattern.search(text)
        if match:
            return normalize_period(match.group("period"))
    return None


def parse_list(fragments: List[Fragment]) -> List[Tuple[str, float]]:
    """``(negara, nilai)`` of the vertical "<negara> / USD x,y Miliar" layout, in page order."""
    pairs: List[Tuple[str, float]] = []
    name: Optional[str] = None
    for line in group_lines(fragments):
        text = line_text(line)
        value = LIST_VALUE.fullmatch(text)
        if value:
            if name:
                pairs.append((name, parse_value(value.group(1))))
            else:
                logger.warning("PMA list: value %r without a country label", text)
            name = None
        elif text and not text.endswith("%") and not text.lower().startswith("keterangan"):
            name = text
    return pairs


def parse_podium(fragments: List[Fragment]) -> List[Tuple[int, str, float]]:
    """Rank the page's five countries: list layout by order, infographic by x position."""
    pairs = parse_list(fragments)
    if not pairs:
        pairs = _parse_infographic(fragments)
    ranked = sorted(pairs, key=lambda pair: -pair[1])
    return [(rank, name, nilai) for rank, (name, nilai) in enumerate(ranked, start=1)]


def _value_cells(fragments: List[Fragment]) -> List[List[Fragment]]:
    """Pieces of one printed value ("2" "," "24" "M" after kerning) merged per line; only numeric cells."""
    cells: List[List[Fragment]] = []
    for line in group_lines(fragments):
        group: List[Fragment] = []
        for fragment in sorted(line, key=lambda f: f[0]):
            if group and fragment[0] - group[-1][0] > CELL_GAP:
                cells.append(group)
                group = []
            group.append(fragment)
        if group:
            cells.append(group)
    return [c for c in cells if VALUE.match("".join(t for _, _, t in c).strip())]


def _parse_infographic(fragments: List[Fragment]) -> List[Tuple[str, float]]:
    """Pair each value with the country label nearest to it on the x axis (one column per country)."""
    cells = sorted(_value_cells(fragments), key=lambda c: c[0][0])
    if not cells:
        return []
    used = {id(f) for cell in cells for f in cell}
    xs = [c[0][0] for c in cells]
    pitch = sorted(b - a for a, b in zip(xs, xs[1:]))
    reach = 0.75 * pitch[len(pitch) // 2] if pitch else 150.0
    top = min(c[0][1] for c in cells)
    note = [f[1] for f in fragments if f[2].strip().lower().startswith("keterangan")]
    floor = max(note) + 5 if note else 0
    columns: List[List[Fragment]] = [[] for _ in cells]
    for fragment in fragments:
        text = fragment[2].strip()
        if (
            id(fragment) in used
            or not floor < fragment[1] < top
            or text in NON_NAMES
            or text.endswith("%")
            or re.fullmatch(r"[\d\s,.]+", text)
        ):
            continue
        nearest = min(range(len(xs)), key=lambda i: abs(xs[i] - fragment[0]))
        if abs(xs[nearest] - fragment[0]) <= reach:
            columns[nearest].append(fragment)
    pairs: List[Tuple[str, float]] = []
    for cell, labels in zip(cells, columns):
        if not labels:
            logger.warning("PMA podium: value %r has no country label, page skipped", "".join(t for _, _, t in cell))
            return []
        name = squash(" ".join(line_text(line) for line in group_lines(labels)))
        pairs.append((name, parse_value("".join(t for _, _, t in cell))))
    return pairs


def parse_pages(pages: List[List[Fragment]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for number, fragments in enumerate(pages, start=1):
        periode = header_period(fragments)
        if not periode:
            continue
        for rank, name, nilai in parse_podium(fragments):
            records.append(
                {
                    "periode": periode,
                    "peringkat": rank,
                    "negara_asal": name,
                    "realisasi_pma": nilai,
                    "halaman_pdf": number,
                }
            )
    return records


def parse_releases(html: str, base_url: str) -> List[Tuple[str, str]]:
    """``(title, pdf_url)`` for each release on the landing page, newest first."""
    parts = urlsplit(base_url)
    origin = f"{parts.scheme}://{parts.netloc}"
    releases: List[Tuple[str, str]] = []
    for button in BeautifulSoup(html, "html.parser").find_all(attrs={"data-remote": True}):
        saved = parse_qs(urlsplit(button["data-remote"]).query).get("saved_name", [""])[0]
        if not saved.lower().endswith(".pdf"):
            continue
        heading = button.find_previous("h2")
        releases.append((squash(heading.get_text(" ")) if heading else "", f"{origin}/storage/file/pdf/{saved}"))
    return releases


def read_pdf_fragments(content: bytes, max_pages: Optional[int] = None) -> List[List[Fragment]]:
    """Positioned text pieces of every page, in device coordinates (y grows upwards)."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ConfigError("pypdf is required for PDF sources (pip install pypdf)") from exc
    try:
        reader = PdfReader(io.BytesIO(content))
        selected = list(reader.pages)
        if max_pages and len(selected) > max_pages:
            logger.warning("BKPM PDF: reading only %d of %d pages (MAX_PAGES)", max_pages, len(selected))
            selected = selected[:max_pages]
        pages: List[List[Fragment]] = []
        for page in selected:
            fragments: List[Fragment] = []

            def visit(text, cm, tm, font_dict, font_size, bucket=fragments):
                if text and text.strip():
                    x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
                    y = tm[5] * cm[3] + tm[4] * cm[1] + cm[5]
                    bucket.append((float(x), float(y), text.strip()))

            page.extract_text(visitor_text=visit)
            pages.append(fragments)
        return pages
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the BKPM PDF: {exc}") from exc


class Extractor(BaseExtractor):
    def _resolve_pdf_urls(self) -> List[str]:
        pinned = (self.config.get("pdf_url") or "").strip()
        if pinned:
            return [pinned]
        landing = (self.config.get("url") or "").strip()
        if not landing:
            raise ConfigError("Set URL (BKPM realisasi-investasi page) or PDF_URL for pma_negara_asal")
        if urlsplit(landing).path.lower().endswith(".pdf"):
            return [landing]
        html = self.http.get(landing, timeout=60).content.decode("utf-8", errors="replace")
        own = YEAR_PAGE.search(landing)
        pages = [(int(own.group(1)) if own else 0, landing, html)]
        if own:
            for year in sorted({int(y) for y in YEAR_LINK.findall(html)} - {int(own.group(1))}, reverse=True):
                sibling = YEAR_PAGE.sub(f"/realisasi-investasi/{year}", landing)
                try:
                    sibling_html = self.http.get(sibling, timeout=60).content.decode("utf-8", errors="replace")
                except Exception as exc:
                    logger.warning("BKPM year page %s unavailable: %s", sibling, exc)
                    continue
                pages.append((year, sibling, sibling_html))
        urls: List[str] = []
        for _year, page_url, page_html in sorted(pages, key=lambda page: page[0], reverse=True):
            for title, url in parse_releases(page_html, page_url):
                logger.info("BKPM release: %s -> %s", title, url)
                if url not in urls:
                    urls.append(url)
        if not urls:
            raise SourceUnavailable(f"No PDF releases found on {landing}")
        return urls

    def extract(self) -> Iterator[Dict[str, Any]]:
        urls = self._resolve_pdf_urls()
        max_pages = int(self.config.get("max_pages") or 0) or None
        seen: Dict[Tuple[str, int], str] = {}
        failures: List[str] = []
        for pdf_url in urls:
            try:
                content = self.http.get(pdf_url, timeout=180).content
                records = parse_pages(read_pdf_fragments(content, max_pages))
            except Exception as exc:
                if len(urls) == 1:
                    raise
                logger.warning("BKPM %s skipped: %s", pdf_url, exc)
                failures.append(f"{pdf_url}: {exc}")
                continue
            fresh = []
            for record in records:
                key = (record["periode"], record["peringkat"])
                if key not in seen:
                    seen[key] = pdf_url
                    fresh.append(record)
            logger.info("BKPM %s: %d rows (%d new)", pdf_url, len(records), len(fresh))
            yield from fresh
        if not seen:
            detail = f" ({'; '.join(failures)})" if failures else ""
            raise SourceUnavailable(f"No '5 Besar Negara PMA' pages parsed from {', '.join(urls)}{detail}")
