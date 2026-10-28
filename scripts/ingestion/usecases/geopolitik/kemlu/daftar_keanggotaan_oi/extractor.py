"""Daftar Keanggotaan OI (Kemlu): "Keanggotaan Indonesia pada Organisasi Internasional".

The Kemlu PDF is a 6-column table per government body (DPR, BPK, ...). Text order
is unreliable, so every text fragment is assigned to a column by its x position
and rows start at the numbers in the first column. A row (notably its
Keterangan cell) may continue on the next page. The landing page
(``kemlu.go.id/kebijakan/organisasi-internasional``) is a JS app, so the PDF URL
is a default constant; ``URL`` (or ``SOURCE_FILE`` for a saved copy) overrides it.
"""

from __future__ import annotations

import io
import logging
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://kemlu.go.id/files/submenu/additional_file/"
    "1717469031665e7f67a011c_KEANGGOTAAN_INDONESIA_PADA_ORGANISASI_INTERNASIONAL.pdf"
)

Span = Tuple[float, float, str, float, float]  # x, y, text, font size, end x

# (column name, x start inclusive); fixed layout of the Kemlu table
COLUMNS = [
    ("no", 0.0),
    ("nama", 90.0),
    ("status", 224.0),
    ("dasar", 306.0),
    ("unit", 485.5),
    ("keterangan", 570.0),
]
NUMBER_COLUMN_END = 90.0
PAGE_MARGIN_X = 700.0  # page numbers sit right of the table
LINE_TOLERANCE = 2.5
HEADING = re.compile(r"^(\d+)\)\.?\s*(.+)$")


def squash(text: str) -> str:
    return " ".join((text or "").split())


def column_of(x: float) -> str:
    name = COLUMNS[0][0]
    for col, start in COLUMNS:
        if x >= start:
            name = col
    return name


def join_spans(spans: List[Span]) -> str:
    """Join same-line fragments; fragments split inside a word are glued back."""
    out = ""
    prev_end: Optional[float] = None
    for x, _y, text, size, end in sorted(spans, key=lambda s: s[0]):
        size = size or 8.0
        gap_is_space = prev_end is not None and x - prev_end > 0.12 * size
        if gap_is_space and not out.endswith(" ") and not text.startswith((" ", ",", ".", ")", ":")):
            out += " "
        out += text
        prev_end = end
    return out


def group_lines(spans: List[Span]) -> List[List[Span]]:
    """Spans grouped into visual lines, top to bottom."""
    lines: List[List[Span]] = []
    for span in sorted(spans, key=lambda s: (-s[1], s[0])):
        if lines and abs(lines[-1][0][1] - span[1]) <= LINE_TOLERANCE:
            lines[-1].append(span)
        else:
            lines.append([span])
    return lines


def _is_number(span: Span) -> bool:
    return span[0] < NUMBER_COLUMN_END and re.fullmatch(r"\d{1,3}", span[2].strip()) is not None


def parse_pages(pages: List[List[Span]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    group: Optional[str] = None
    current: Optional[Dict[str, List[str]]] = None
    meta: Dict[str, Any] = {}
    in_table = False

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        cells = {col: squash(" ".join(parts)) or None for col, parts in current.items()}
        rows.append(
            {
                "kelompok_instansi": meta["group"],
                "no_pada_kelompok": meta["no"],
                "nama_organisasi_internasional": cells["nama"],
                "status_dan_tahun": cells["status"],
                "dasar_hukum": cells["dasar"],
                "unit_terkait_di_kemlu": cells["unit"],
                "keterangan": cells["keterangan"],
                "halaman_pdf": meta["page"],
            }
        )
        current = None

    for page_number, spans in enumerate(pages, start=1):
        for line in group_lines([s for s in spans if s[0] < PAGE_MARGIN_X]):
            line = sorted(line, key=lambda s: s[0])
            text = squash(join_spans(line))
            if not text:
                continue
            first = line[0]
            if sum(1 for s in line if re.fullmatch(r"\d{1,3}", s[2].strip())) >= 3:
                flush()  # the "1 2 3 4 6 7" column-number row opens the table
                in_table = True
                continue
            if first[0] < NUMBER_COLUMN_END:
                heading = HEADING.match(text)  # kerning can split "19)." so test the joined line first
                if heading:
                    flush()
                    in_table = False
                    group = squash(heading.group(2))
                    continue
            if first[0] < NUMBER_COLUMN_END and not _is_number(first):
                if text.upper().startswith("FOCAL POINT") or not in_table:
                    flush()
                    in_table = False
                    continue
                if text.upper() in ("NO", "N O"):
                    continue
            if not in_table:
                continue
            if _is_number(first):
                flush()
                current = {col: [] for col, _ in COLUMNS}
                meta = {"group": group, "no": int(first[2].strip()), "page": page_number}
                line = line[1:]
            if current is None:
                continue
            by_col: Dict[str, List[Span]] = {}
            for span in line:
                by_col.setdefault(column_of(span[0]), []).append(span)
            for col, col_spans in by_col.items():
                current[col].append(join_spans(col_spans))
    flush()
    return rows


def _text_width(text: str, font_dict: Any, size: float) -> float:
    """Advance width of ``text`` from the font's /Widths (average glyph width as fallback)."""
    try:
        first = int(font_dict.get("/FirstChar", 0))
        widths = font_dict.get("/Widths")
        widths = widths.get_object() if widths is not None else []
        total = 0.0
        for ch in text:
            idx = ord(ch) - first
            total += float(widths[idx]) if 0 <= idx < len(widths) else 500.0
        return total / 1000.0 * size
    except Exception:
        return len(text) * 0.5 * size


def read_pdf_spans(content: bytes) -> List[List[Span]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("pypdf is required for daftar_keanggotaan_oi (pip install pypdf)") from exc
    try:
        reader = PdfReader(io.BytesIO(content))
        pages: List[List[Span]] = []
        for page in reader.pages:
            spans: List[Span] = []

            def visit(text, cm, tm, font_dict, font_size, bucket=spans):
                if text and text.strip():
                    size = float(font_size or 8.0)
                    x = float(tm[4])
                    bucket.append((x, float(tm[5]), text, size, x + _text_width(text, font_dict, size)))

            page.extract_text(visitor_text=visit)
            pages.append(spans)
        return pages
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the Kemlu PDF: {exc}") from exc


class Extractor(BaseExtractor):
    def _load_pdf(self) -> bytes:
        local = (self.config.get("source_file") or "").strip()
        if local:
            path = Path(local)
            if not path.is_file():
                raise ConfigError(f"SOURCE_FILE not found: {local}")
            return path.read_bytes()
        url = (self.config.get("url") or DEFAULT_URL).strip()
        content = self.http.get(url, timeout=180).content
        if not content.startswith(b"%PDF"):
            raise SourceUnavailable(f"{url} did not return a PDF")
        return content

    def extract(self) -> Iterator[Dict[str, Any]]:
        rows = parse_pages(read_pdf_spans(self._load_pdf()))
        if not rows:
            raise SourceUnavailable("No membership rows parsed from the Kemlu PDF")
        logger.info("Kemlu keanggotaan OI: %d rows", len(rows))
        yield from rows
