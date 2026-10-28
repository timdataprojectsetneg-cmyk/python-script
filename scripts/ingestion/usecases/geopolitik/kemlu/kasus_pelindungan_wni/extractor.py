"""Kemlu Kasus Pelindungan WNI: "DATA DUKUNG - KASUS WNI DI LUAR NEGERI" table of the LKJ Dit. PWNI PDF.

The table lists a group line (Pidana, Ketenagakerjaan, ...) with its subtotal,
followed by indented subtype lines; both carry ``ditangani`` and ``selesai``.
Only subtype rows are emitted, each tagged with its group. Group/subtype is
told apart by indentation of the first text line of an entry (or, for labels
wrapped over several lines, by the width of the whitespace-only line before
it). Subtotal mismatches are logged, never corrected. The PDF has no stable
landing page, so ``URL`` (default constant) or ``SOURCE_FILE`` selects the file.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable
from .._pdf import load_pdf, read_pages

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://kemlu.go.id/files/repositori/65397/174071018667c1212ae1402_LKJ_Dit__PWNI_2024.pdf"
)

_NUM = r"\d{1,3}(?:\.\d{3})+|\d+"
_ENTRY = re.compile(rf"^(?P<label>.*?)\s*(?P<a>{_NUM})\s+(?P<b>{_NUM})\s*$")
_PAGE_FOOTER = re.compile(r"^\s*\d+\s*\|")
_NOISE = re.compile(
    r"^\s*(LAPORAN KINERJA|DATA DUKUNG|KASUS WNI DI LUAR NEGERI|DITANGANI\s+SELESAI|III\.\s*Matriks)",
    re.I,
)
_GROUP_ALIASES = [
    (re.compile(r"^Pe[ny]*alahgunaan Visa, Izin Tinggal dan Dokumen( Lainnya)?$", re.I), "Visa, Izin Tinggal dan Dokumen"),
]


def to_int(token: str) -> int:
    return int(token.replace(".", ""))


def normalize_group(label: str) -> str:
    for pattern, canonical in _GROUP_ALIASES:
        if pattern.match(label):
            return canonical
    return label


def find_table_pages(pages: List[str]) -> List[int]:
    """Indexes of the table's first page and the following pages up to the TOTAL row."""
    for i, text in enumerate(pages):
        if "DATA DUKUNG" in text and "KASUS WNI DI LUAR NEGERI" in text and "DITANGANI" in text:
            out = []
            for j in range(i, len(pages)):
                out.append(j)
                if re.search(r"^\s*TOTAL\s", pages[j], re.M):
                    return out
            logger.warning("Kasus WNI: TOTAL row not found; parsed the table to the last page (%d pages)", len(out))
            return out
    return []


def parse_cases(pages: List[Tuple[int, str]]) -> List[Dict[str, Any]]:
    """Subtype rows from (page number, text) blocks of the table."""
    rows: List[Dict[str, Any]] = []
    groups: List[Dict[str, Any]] = []
    group: Optional[Dict[str, Any]] = None
    pending: List[str] = []
    blank_width = 0
    total: Optional[Tuple[int, int]] = None

    for page_no, text in pages:
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                if not pending:
                    blank_width = len(line)
                continue
            if _PAGE_FOOTER.match(line) or _NOISE.match(line):
                continue
            m = _ENTRY.match(stripped)
            if not m:
                pending.append(stripped)
                continue
            a, b = to_int(m.group("a")), to_int(m.group("b"))
            label = " ".join(pending + [m.group("label")]).strip()
            wrapped = bool(pending)
            first_line_indented = line[:1].isspace() if not wrapped else False
            pending = []
            hint, blank_width = blank_width, 0
            if not label:
                continue  # numbers-only line: the KASUS UMUM total
            if label.upper() == "TOTAL":
                total = (a, b)
                continue
            if re.match(r"^KASUS\s+(UMUM|KHUSUS)$", label):
                group = None
                continue
            if re.match(r"^(Kasus Awak Kapal|Evakuasi WNI)", label, re.I):
                continue
            is_child = first_line_indented or (wrapped and 0 < hint <= 3)
            if is_child:
                if group is None:
                    logger.warning("Kasus WNI: subtype %r has no group", label)
                row = {
                    "kelompok_kasus": group["name"] if group else None,
                    "jenis_kasus": label,
                    "ditangani": a,
                    "selesai": b,
                    "halaman_pdf": page_no,
                }
                rows.append(row)
                if group:
                    group["children"].append(row)
            else:
                group = {"name": normalize_group(label), "ditangani": a, "selesai": b, "children": []}
                groups.append(group)

    for g in groups:
        for key in ("ditangani", "selesai"):
            got = sum(r[key] for r in g["children"])
            if got != g[key]:
                logger.warning("Kasus WNI: %s %s subtotal %s != sum of subtypes %s", g["name"], key, g[key], got)
    if total:
        for idx, key in enumerate(("ditangani", "selesai")):
            got = sum(g[key] for g in groups)
            if got != total[idx]:
                logger.warning("Kasus WNI: TOTAL %s %s != sum of groups %s", key, total[idx], got)
    return rows


def detect_year(url: str, pages: List[str], configured: Optional[str]) -> Optional[int]:
    if configured and str(configured).strip().isdigit():
        return int(str(configured).strip())
    m = re.search(r"PWNI[_\- ]*(20\d{2})", url or "", re.I)
    if m:
        return int(m.group(1))
    for text in pages[:6]:
        m = re.search(r"(?:TAHUN|T\.A\.?)\s*(20\d{2})", text, re.I)
        if m:
            return int(m.group(1))
    return None


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        content, origin = load_pdf(
            self.http, self.config.get("url"), self.config.get("source_file"), DEFAULT_URL
        )
        pages = read_pages(content)
        idx = find_table_pages(pages)
        if not idx:
            raise SourceUnavailable("LKJ Dit. PWNI: 'DATA DUKUNG - KASUS WNI DI LUAR NEGERI' table not found")
        rows = parse_cases([(i + 1, pages[i]) for i in idx])
        if not rows:
            raise SourceUnavailable("LKJ Dit. PWNI: no case rows parsed from the table")
        year = detect_year(origin, pages, self.config.get("tahun"))
        if year is None:
            logger.warning("LKJ Dit. PWNI: report year not detected; set TAHUN")
        logger.info("Kemlu kasus_pelindungan_wni: %d rows from %s", len(rows), origin)
        for row in rows:
            yield {"tahun": year, **row}
