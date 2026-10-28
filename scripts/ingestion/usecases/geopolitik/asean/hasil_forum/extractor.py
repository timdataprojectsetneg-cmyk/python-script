"""Hasil Forum ASEAN: Chairman's Statement of an ASEAN Summit (PDF), one row per paragraph.

The statement is a title + "VENUE, DD MONTH YYYY" header followed by sequentially
numbered paragraphs grouped under UPPERCASE section headings. The default URL is the
46th Summit statement; set ``URL`` (or ``SOURCE_FILE``) to another Chairman's
Statement PDF to ingest a different summit. ``asean.org`` HTML is behind a JavaScript
challenge, so documents cannot be discovered automatically.
"""

from __future__ import annotations

import io
import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://asean.org/wp-content/uploads/2025/05/"
    "01.-FINAL-Chairmans-Statement-of-the-46th-ASEAN-Summit.pdf"
)

MONTHS = (
    "JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER"
)
DATE_LINE = re.compile(rf"(\d{{1,2}})\s+({MONTHS})\s+(\d{{4}})\s*$", re.IGNORECASE)
PARAGRAPH_START = re.compile(r"^(\d{1,3})\.\s+(\S.*)$")
ACRONYMS = {"ASEAN", "APT", "EAS", "ARF", "IAI", "ASCN", "APSC", "ASCC", "AEC", "US", "UN", "EU"}
SMALL_WORDS = {"of", "the", "and", "in", "for", "on", "to", "a", "an", "at", "by"}


def squash(text: str) -> str:
    return " ".join((text or "").split())


def smart_title(text: str) -> str:
    """UPPERCASE heading -> Title Case keeping acronyms, ordinals and hyphenated parts."""
    words: List[str] = []
    for index, word in enumerate(squash(text).split(" ")):
        parts = []
        for part in word.split("-"):
            core = re.sub(r"^[^\w]+|[^\w]+$", "", part)
            lowered = part.lower()
            if core.upper() in ACRONYMS:
                parts.append(part.upper())
            elif re.fullmatch(r"\d+(ST|ND|RD|TH)", core.upper()):
                parts.append(lowered)
            elif index > 0 and core.lower() in SMALL_WORDS:
                parts.append(lowered)
            else:
                parts.append(re.sub(r"[A-Za-z]", lambda m: m.group(0).upper(), lowered, count=1))
        words.append("-".join(parts))
    return " ".join(words)


def parse_header(lines: List[str]) -> Tuple[Optional[str], Optional[date]]:
    """Title (first uppercase 'STATEMENT' line) and the date on the line after it."""
    title: Optional[str] = None
    when: Optional[date] = None
    for index, line in enumerate(lines[:30]):
        text = squash(line)
        if title is None and re.search(r"STATEMENT|DECLARATION", text.upper()) and text.upper() == text:
            title = smart_title(text)
            continue
        if title is not None:
            found = DATE_LINE.search(text)
            if found:
                day, month, year = found.groups()
                when = datetime.strptime(f"{day} {month.title()} {year}", "%d %B %Y").date()
                break
    return title, when


def is_heading(text: str) -> bool:
    letters = re.sub(r"[^A-Za-z]", "", text)
    return len(letters) >= 4 and text.upper() == text and not re.match(r"^\d", text)


def clean_paragraph(text: str) -> str:
    text = squash(text)
    text = re.sub(r"(\w) -(?=\w)", r"\1-", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    return text


def join_lines(parts: List[str]) -> str:
    out = ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if out.endswith("-"):
            out = out.rstrip() + part
        else:
            out = f"{out} {part}" if out else part
    return out


def parse_statement(text: str) -> List[Dict[str, Any]]:
    lines = text.splitlines()
    forum, forum_date = parse_header(lines)
    rows: List[Dict[str, Any]] = []
    heading: Optional[str] = None
    pending: List[str] = []
    current: Optional[Dict[str, Any]] = None
    expected = 1
    page = 0
    previous_blank = True

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        body = clean_paragraph(join_lines(current["lines"]))
        rows.append(
            {
                "tanggal_forum": forum_date,
                "forum": forum,
                "paragraf": current["no"],
                "isu": current["isu"],
                "hasil_sikap_bersama": body or None,
            }
        )
        current = None

    def commit_heading() -> None:
        nonlocal heading, pending
        if pending:
            flush()
            heading = smart_title(" ".join(pending))
            pending = []

    for raw in lines:
        line = raw.strip()
        if not line:
            previous_blank = True
            continue
        was_blank, previous_blank = previous_blank, False
        if re.fullmatch(r"\d{1,3}", line) and int(line) == page + 1:
            page += 1  # running page number
            previous_blank = was_blank
            continue
        if expected > 1 and is_heading(line) and (was_blank or pending):
            pending.append(line)
            continue
        commit_heading()
        match = PARAGRAPH_START.match(line)
        if match and int(match.group(1)) == expected:
            flush()
            current = {"no": expected, "isu": heading, "lines": [match.group(2)]}
            expected += 1
        elif current is not None:
            current["lines"].append(line)
    commit_heading()
    flush()
    return rows


def pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("pypdf is required for hasil_forum (pip install pypdf)") from exc
    try:
        reader = PdfReader(io.BytesIO(content))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the ASEAN statement PDF: {exc}") from exc


class Extractor(BaseExtractor):
    def _load_pdf(self) -> bytes:
        local = (self.config.get("source_file") or "").strip()
        if local:
            path = Path(local)
            if not path.is_file():
                raise ConfigError(f"SOURCE_FILE not found: {local}")
            return path.read_bytes()
        url = (self.config.get("url") or DEFAULT_URL).strip()
        content = self.http.get(url, timeout=120).content
        if not content.startswith(b"%PDF"):
            raise SourceUnavailable(f"{url} did not return a PDF")
        return content

    def extract(self) -> Iterator[Dict[str, Any]]:
        rows = parse_statement(pdf_text(self._load_pdf()))
        if not rows:
            raise SourceUnavailable("No numbered paragraphs parsed from the ASEAN statement PDF")
        logger.info("ASEAN statement: %d paragraphs", len(rows))
        yield from rows
