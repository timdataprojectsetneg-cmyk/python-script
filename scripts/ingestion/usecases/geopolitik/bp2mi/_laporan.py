"""Shared helpers for the BP2MI "Laporan Publikasi Data PMI" monthly PDF.

One PDF carries both the placement (penempatan) and complaint (pengaduan)
tables; each source picks its own "Berdasarkan Negara" table by page title.
``URL`` may be a direct PDF link (``.pdf``) or a landing page that links to
the reports. A landing page can list several reports: the newest report of each
data year (date inside the file name) is read, one year per report; reports
without the monthly country table (e.g. narrative monthly reports) are skipped
with a warning.
"""

from __future__ import annotations

import io
import logging
import re
from datetime import date
from html import unescape
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urljoin

from ....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_LANDING_URLS = (
    "https://jabar.bp2mi.go.id/statpenempatan/",
    "https://sdi.bp2mi.go.id/dataset/?q=2024",
)
MONTHS = ["jan", "feb", "mar", "apr", "mei", "jun", "jul", "agu", "sep", "okt", "nov", "des"]

_HREF = re.compile(r"""href\s*=\s*["']([^"']+?\.pdf[^"']*)["']""", re.I)
_FILE_DATE = re.compile(r"data_(\d{2})-(\d{2})-(\d{4})_", re.I)
_NUM = r"(?:\d{1,3}(?:\.\d{3})*|\d+|-)"
_ROW = re.compile(rf"^\s*(\d+)\s+(.+?)\s+((?:{_NUM})(?:\s+{_NUM}){{12}})\s*$")
_TOTAL = re.compile(rf"^\s*Jumlah\s+((?:{_NUM})(?:\s+{_NUM}){{12}})\s*$", re.I)


def to_int(token: str) -> Optional[int]:
    token = token.strip()
    if token in ("", "-"):
        return None
    return int(token.replace(".", ""))


def report_date(url: str) -> date:
    m = _FILE_DATE.search(url)
    if not m:
        return date.min
    day, month, year = (int(g) for g in m.groups())
    try:
        return date(year, month, day)
    except ValueError:
        return date.min


def find_report_links(html: str, base_url: str) -> List[str]:
    """Report PDF links in a landing page, newest first (de-duplicated)."""
    seen: List[str] = []
    for href in _HREF.findall(html or ""):
        full = urljoin(base_url, unescape(href).strip())
        if full not in seen and re.search(r"laporan_publikasi", full, re.I):
            seen.append(full)
    return sorted(seen, key=report_date, reverse=True)


def report_year(url: str) -> int:
    """Data year of a report: the last 4-digit year in the file name (``..._Desember_2024.pdf``)."""
    years = re.findall(r"(?<!\d)(20\d{2})(?!\d)", url.rsplit("/", 1)[-1])
    return int(years[-1]) if years else report_date(url).year


def _report_links(http: Any, url: Optional[str], landing_urls: Optional[List[str]] = None) -> List[str]:
    candidates = [url] if url else list(landing_urls or DEFAULT_LANDING_URLS)
    if url:
        candidates += [u for u in DEFAULT_LANDING_URLS if u != url]
    links: List[str] = []
    for landing in candidates:
        try:
            html = http.get(landing, timeout=60, max_retries=2).text
        except Exception as exc:  # unreachable mirror: try the next landing page
            logger.warning("BP2MI landing page %s unavailable: %s", landing, exc)
            continue
        links += [link for link in find_report_links(html, landing) if link not in links]
    if not links:
        raise SourceUnavailable(
            "No BP2MI 'Laporan Publikasi' PDF link found on: " + ", ".join(candidates)
            + ". Set URL to a direct PDF link or SOURCE_FILE to a saved copy."
        )
    return sorted(links, key=report_date, reverse=True)


def resolve_report_url(http: Any, url: Optional[str], landing_urls: Optional[List[str]] = None) -> str:
    """The newest report only."""
    if url and url.lower().split("?")[0].endswith(".pdf"):
        return url
    return _report_links(http, url, landing_urls)[0]


def resolve_report_urls(http: Any, url: Optional[str], landing_urls: Optional[List[str]] = None) -> List[str]:
    """Newest report of every data year, newest first (an older report of the same year is superseded)."""
    if url and url.lower().split("?")[0].endswith(".pdf"):
        return [url]
    latest: Dict[int, str] = {}
    for link in _report_links(http, url, landing_urls):
        latest.setdefault(report_year(link), link)
    return list(latest.values())


def load_pdf(http: Any, url: Optional[str], source_file: Optional[str]) -> Tuple[bytes, str]:
    local = (source_file or "").strip()
    if local:
        path = Path(local)
        if not path.is_file():
            raise ConfigError(f"SOURCE_FILE not found: {local}")
        return path.read_bytes(), path.name
    pdf_url = resolve_report_url(http, (url or "").strip() or None)
    content = http.get(pdf_url, timeout=240).content
    if not content.startswith(b"%PDF"):
        raise SourceUnavailable(f"{pdf_url} did not return a PDF")
    return content, pdf_url


def load_pdfs(http: Any, url: Optional[str], source_file: Optional[str]) -> Iterator[Tuple[bytes, str]]:
    """(bytes, origin) of every report to read: SOURCE_FILE, else one PDF per data year."""
    local = (source_file or "").strip()
    if local:
        yield load_pdf(http, None, local)
        return
    for pdf_url in resolve_report_urls(http, (url or "").strip() or None):
        content = http.get(pdf_url, timeout=240).content
        if not content.startswith(b"%PDF"):
            logger.warning("%s did not return a PDF; skipped", pdf_url)
            continue
        yield content, pdf_url


def read_pages(content: bytes) -> List[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("pypdf is required for BP2MI sources (pip install pypdf)") from exc
    try:
        return [(page.extract_text() or "") for page in PdfReader(io.BytesIO(content)).pages]
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the BP2MI PDF: {exc}") from exc


def parse_country_table(text: str) -> Tuple[List[Dict[str, Any]], Optional[List[Optional[int]]]]:
    """Rows of one 'NO NEGARA JAN..DES JUMLAH' page plus its 'Jumlah' totals row."""
    rows: List[Dict[str, Any]] = []
    totals: Optional[List[Optional[int]]] = None
    for line in text.splitlines():
        total = _TOTAL.match(line)
        if total:
            totals = [to_int(t) for t in total.group(1).split()]
            continue
        m = _ROW.match(line)
        if not m:
            continue
        values = [to_int(t) for t in m.group(3).split()]
        row: Dict[str, Any] = {"negara": " ".join(m.group(2).split())}
        row.update(dict(zip(MONTHS + ["jumlah"], values)))
        rows.append(row)
    return rows, totals


def check_rows(rows: List[Dict[str, Any]], totals: Optional[List[Optional[int]]], label: str) -> None:
    """Log (never alter) mismatches between rows, their yearly total and the 'Jumlah' row."""
    for row in rows:
        months = [row[m] for m in MONTHS]
        if all(v is not None for v in months) and sum(months) != row["jumlah"]:
            logger.warning("%s: %s monthly sum %s != JUMLAH %s", label, row["negara"], sum(months), row["jumlah"])
    if totals:
        for key, expected in zip(MONTHS + ["jumlah"], totals):
            got = sum(r[key] or 0 for r in rows)
            if expected is not None and got != expected:
                logger.warning("%s: column %s sums to %s but report total is %s", label, key, got, expected)


_SECTION_TITLE = re.compile(r"Berdasarkan\s+\w+", re.I)


def extract_country_table(
    pages: List[str], title_regex: "re.Pattern[str]", label: str
) -> Iterator[Dict[str, Any]]:
    """Rows of the first table whose page text matches ``title_regex`` (group 1 = year).

    The title sits below the table, so a table that spills over several pages is
    followed back over earlier pages that carry rows without a section title or
    'Jumlah' row, and forward over later pages until the 'Jumlah' row appears.
    """
    for index, text in enumerate(pages):
        m = title_regex.search(text)
        if not m or "NEGARA" not in text:
            continue
        year = int(m.group(1))
        rows, totals = parse_country_table(text)
        page_rows = [(index + 1, rows)]
        prev = index - 1
        while prev >= 0 and not _SECTION_TITLE.search(pages[prev]):
            earlier, earlier_totals = parse_country_table(pages[prev])
            if not earlier or earlier_totals is not None:
                break
            page_rows.insert(0, (prev + 1, earlier))
            prev -= 1
        nxt = index + 1
        while totals is None and rows and nxt < len(pages):
            more, totals = parse_country_table(pages[nxt])
            if not more:
                break
            page_rows.append((nxt + 1, more))
            nxt += 1
        flat = [r for _p, rs in page_rows for r in rs]
        check_rows(flat, totals, label)
        for page_no, rs in page_rows:
            for row in rs:
                yield {"tahun": year, **row, "halaman_pdf": page_no}
        return
    raise SourceUnavailable(f"{label}: table 'Berdasarkan Negara' not found in the BP2MI PDF")


def extract_reports(
    http: Any, url: Optional[str], source_file: Optional[str], title_regex: "re.Pattern[str]", label: str
) -> Iterator[Dict[str, Any]]:
    """Country-table rows of every report (one per data year); a report without the table is skipped."""
    seen: Dict[int, str] = {}
    failures: List[str] = []
    for content, origin in load_pdfs(http, url, source_file):
        try:
            rows = list(extract_country_table(read_pages(content), title_regex, label))
        except SourceUnavailable as exc:
            logger.warning("%s: %s skipped (%s)", label, origin, exc)
            failures.append(f"{origin}: {exc}")
            continue
        year = rows[0]["tahun"]
        if year in seen:
            logger.info("%s: %s repeats year %s already read from %s; skipped", label, origin, year, seen[year])
            continue
        seen[year] = origin
        logger.info("%s: %d rows for %s from %s", label, len(rows), year, origin)
        yield from rows
    if not seen:
        detail = f" ({'; '.join(failures)})" if failures else ""
        raise SourceUnavailable(f"{label}: table 'Berdasarkan Negara' not found in any BP2MI report{detail}")
