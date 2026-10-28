"""Agenda Forum ASEAN: ASEAN Notional Calendar (public PDF).

Every numbered entry is "<n> <meeting> <date> <venue> <pillar>" wrapped over several
lines, so entries are split at the sequentially numbered line starts, then the date
is located by pattern and the trailing pillar code is peeled off. The default PDF
URL is the 2026 edition; ``asean.org`` HTML pages (``/events-calendar/``) sit behind
a JavaScript challenge, so the newest edition cannot be discovered automatically:
point ``URL`` (or ``SOURCE_FILE``) at a newer calendar PDF when ASEAN publishes it.
When ``URL`` is an HTML page, PDF links named "Notional Calendar" on it are used.
"""

from __future__ import annotations

import io
import logging
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin, urlsplit

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://asean.org/wp-content/uploads/2026/01/"
    "ASEAN-Notional-Calendar-2026-public-as-of-8-January-2026.pdf"
)

MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December"
)
# Section headings are upper-case ("AUGUST", "DECEMBER 2025"); a mixed-case "December 2026" is a wrapped date cell.
MONTH_HEADING = re.compile(
    rf"^(?:(?:{MONTHS.upper()})(?:\s+\d{{4}})?|(?:{MONTHS}))$"
)
PAGE_HEADER = re.compile(r"^ASEAN \d{4} PUBLIC NOTIONAL CALENDAR", re.IGNORECASE)
TABLE_HEADER = re.compile(r"^(?:No\. of|Meetings Meeting/ Specific Activity)", re.IGNORECASE)
ENTRY_START = re.compile(r"^(\d{1,4})(?:\s+(\S.*))?$")

DAY = r"\d{1,2}"
DATE = re.compile(
    rf"(?:{DAY}(?:\s+(?:{MONTHS}))?\s*[-–]\s*{DAY}\s+(?:{MONTHS})\s*\d{{4}}"
    rf"|{DAY}\s+(?:{MONTHS})\s*\d{{4}}"
    rf"|(?:{MONTHS})\s*\d{{4}}"
    rf"|Q[1-4]\b)"
    r"(?:\s*\(\d+\s+days?[^)]*\))?(?:\s*\(TBC\))?",
)
DEFERRED = re.compile(r"Defer to DFA on the\s+appropriate date", re.IGNORECASE)
PILLAR = re.compile(r"(?:^|\s)((?:AEC|APSC|ASCC|Cross-Pillar)(?:\s*[/,&]\s*(?:AEC|APSC|ASCC))*)\s*$")


def squash(text: str) -> str:
    return " ".join((text or "").split())


def split_entries(text: str) -> List[tuple]:
    """[(number, raw text)] taking only sequentially numbered line starts as entry starts."""
    entries: List[List[Any]] = []
    expected = 1
    text = re.sub(r"(AEC|APSC|ASCC|Cross-Pillar)(?=\d{1,4}\s)", r"\1\n", text)
    for raw_line in text.splitlines():
        line = squash(raw_line)
        if not line or PAGE_HEADER.match(line) or TABLE_HEADER.match(line) or MONTH_HEADING.match(line):
            continue
        match = ENTRY_START.match(line)
        rest = (match.group(2) or "") if match else ""
        if match and int(match.group(1)) == expected and not re.match(rf"^(?:{MONTHS})\b", rest, re.IGNORECASE):
            entries.append([expected, rest])
            expected += 1
        elif entries:
            entries[-1][1] += " " + line
    return [(number, squash(body)) for number, body in entries]


def parse_entry(number: int, body: str) -> Dict[str, Any]:
    pillar = None
    match = PILLAR.search(body)
    if match:
        pillar = squash(match.group(1))
        body = body[: match.start()].rstrip()
    schedule = None
    meeting, venue = body, ""
    found = DATE.search(body)
    if found:
        schedule = re.sub(rf"({MONTHS})(\d{{4}})", r"\1 \2", squash(found.group(0)))
        meeting, venue = body[: found.start()], body[found.end():]
    else:
        deferred = DEFERRED.search(body)
        if deferred:
            schedule = squash(deferred.group(0))
            meeting, venue = body[: deferred.start()], body[deferred.end():]
        elif re.search(r"\(TBC\)", body):
            schedule = "(TBC)"
            meeting = re.sub(r"\s*\(TBC\)", "", body)
            venue = ""
    return {
        "nomor_pada_kalender": number,
        "pertemuan": squash(meeting) or None,
        "jadwal_menurut_sumber": schedule,
        "lokasi_menurut_sumber": squash(venue) or None,
        "pilar": pillar,
    }


def parse_calendar_text(text: str) -> List[Dict[str, Any]]:
    return [parse_entry(number, body) for number, body in split_entries(text)]


def pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("pypdf is required for agenda_forum (pip install pypdf)") from exc
    try:
        reader = PdfReader(io.BytesIO(content))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the ASEAN calendar PDF: {exc}") from exc


def find_calendar_links(html: str, base_url: str) -> List[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    links: List[str] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        label = f"{anchor.get_text(' ')} {href}".lower()
        if href.lower().split("?")[0].endswith(".pdf") and "notional" in label and "calendar" in label:
            links.append(urljoin(base_url, href))
    return links


class Extractor(BaseExtractor):
    def _load_pdf(self) -> bytes:
        local = (self.config.get("source_file") or "").strip()
        if local:
            path = Path(local)
            if not path.is_file():
                raise ConfigError(f"SOURCE_FILE not found: {local}")
            return path.read_bytes()
        url = (self.config.get("url") or DEFAULT_URL).strip()
        if not urlsplit(url).path.lower().endswith(".pdf"):
            html = self.http.get(url, timeout=60).content.decode("utf-8", errors="replace")
            links = find_calendar_links(html, url)
            if not links:
                raise SourceUnavailable(
                    f"No ASEAN Notional Calendar PDF link found on {url}; set URL to the PDF or SOURCE_FILE"
                )
            url = links[0]
            logger.info("ASEAN notional calendar: %s", url)
        content = self.http.get(url, timeout=120).content
        if not content.startswith(b"%PDF"):
            raise SourceUnavailable(f"{url} did not return a PDF")
        return content

    def extract(self) -> Iterator[Dict[str, Any]]:
        rows = parse_calendar_text(pdf_text(self._load_pdf()))
        if not rows:
            raise SourceUnavailable("No calendar entries parsed from the ASEAN Notional Calendar PDF")
        logger.info("ASEAN notional calendar: %d entries", len(rows))
        yield from rows
