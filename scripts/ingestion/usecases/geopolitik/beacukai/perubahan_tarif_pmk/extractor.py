"""Perubahan Tarif PMK 50-2026 (Bea Cukai): tarif bea masuk khusus dari Pasal II PMK.

The Direktori Peraturan DJBC detail page links the official PDF and shows the
"Mulai Berlaku" date. The whole PDF is read with ``pypdf`` (every page, no cap):
Pasal II yields the HS codes, tarif and tarif period, the "Menimbang" recitals
yield the policy context, and the Lampiran III tariff table (hundreds of pages, rows
continuing across page breaks) yields every changed tariff line (rows not marked
"Tetap"). ``PDF_URL`` skips the landing page; ``MAX_PAGES`` (optional) limits pages
and logs a warning.
"""

from __future__ import annotations

import io
import logging
import re
from datetime import date
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "may": 5, "jun": 6, "jul": 7,
    "agu": 8, "agt": 8, "ags": 8, "aug": 8, "sep": 9, "okt": 10, "oct": 10,
    "nov": 11, "des": 12, "dec": 12,
}
HS_CODE = re.compile(r"\b\d{4}\.\d{2}\.\d{2}\b")
Fragment = Tuple[float, float, str]  # (x, y, text) in content-stream order
COL_CODE, COL_ID, COL_EN, COL_RATE = 118.0, 190.0, 330.0, 470.0


def squash(text: str) -> str:
    return " ".join((text or "").split())


def parse_effective_date(html: str) -> Optional[str]:
    """``Mulai Berlaku : 28-Jul-2026 s/d`` -> ``2026-07-28``."""
    text = squash(BeautifulSoup(html, "html.parser").get_text(" "))
    match = re.search(r"Mulai Berlaku\s*:\s*(\d{1,2})-([A-Za-z]{3})[a-z]*-(\d{4})", text)
    if not match:
        return None
    month = MONTHS.get(match.group(2).lower())
    if not month:
        return None
    return date(int(match.group(3)), month, int(match.group(1))).isoformat()


def find_pdf_url(html: str, base_url: str) -> Optional[str]:
    """First regulation PDF on the detail page (skips the DJBC user-manual PDF)."""
    for anchor in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        href = anchor["href"]
        lowered = href.lower()
        if lowered.split("?")[0].endswith(".pdf") and "/peraturan/" in lowered:
            return urljoin(base_url, href)
    return None


def parse_peraturan(first_page: str) -> Optional[str]:
    match = re.search(
        r"PERATURAN MENTERI KEUANGAN\b.*?\bNOMOR\s+(\d+)\s+TAHUN\s+(\d{4})",
        squash(first_page),
        flags=re.IGNORECASE,
    )
    return f"PMK Nomor {match.group(1)} Tahun {match.group(2)}" if match else None


def parse_context(pages: List[str], commodity: Optional[str]) -> Optional[str]:
    """The "Menimbang" clause that mentions the commodity, else the first clause."""
    text = squash(" ".join(pages))
    start = re.search(r"Menimbang\s*:", text)
    if not start:
        return None
    body = text[start.end():]
    end = re.search(r"\bMengingat\s*:", body)
    if end:
        body = body[: end.start()]
    clauses = [c.strip(" ;") for c in re.split(r"(?:^|\s)[a-e]\.\s+(?=bahwa\b)", body) if c.strip()]
    if not clauses:
        return None
    if commodity:
        for clause in clauses:
            if commodity.lower() in clause.lower() and "sebagaimana dimaksud" not in clause.lower():
                return clause
    return clauses[0]


def parse_pasal_ii(pages: List[str]) -> Optional[Dict[str, Any]]:
    """Locate the ``Pasal II`` heading; return its page number and parsed article."""
    for index, page in enumerate(pages):
        heading = re.search(r"^\s*Pasal II\s*$", page, flags=re.MULTILINE)
        if not heading:
            continue
        article = squash(page[heading.end():] + " " + (pages[index + 1] if index + 1 < len(pages) else ""))
        article = re.split(r"\b2\.\s*Peraturan Menteri ini mulai berlaku", article)[0]
        codes = list(dict.fromkeys(HS_CODE.findall(article)))
        if not codes:
            continue
        tarif = re.search(r"sebesar\s+(\d+(?:[.,]\d+)?)\s*%", article)
        masa = re.search(r"selama\s+(\d+)\s*\([^)]*\)\s*(bulan|tahun|hari|minggu)", article, re.IGNORECASE)
        commodity = re.search(r"impor\s+(.+?)\s+yang termasuk dalam pos tarif", article, re.IGNORECASE)
        return {
            "halaman_pdf": index + 1,
            "kode_hs": codes,
            "tarif_bea_masuk": float(tarif.group(1).replace(",", ".")) if tarif else None,
            "masa_berlaku_tarif": f"{masa.group(1)} {masa.group(2).lower()}" if masa else None,
            "komoditas": commodity.group(1).strip() if commodity else None,
        }
    return None


_ROW_LINE = re.compile(r"^\s*(\d{4,6})\s+(\d{4}\.\d{2}\.\d{2})\b\s*(.*)$")
_HEADING_LINE = re.compile(r"^\s*\d{2}\.\d{2}\b")
_PAGE_NO_LINE = re.compile(r"^\s*-\s*\d+\s*-\s*$")
_TABLE_HEAD_LINE = re.compile(r"^\s*(No\. Pos Tarif/|HS Code Uraian|Import Duty|\(1\) \(2\) \(3\))")
_RATE_TOKEN = re.compile(r"\d\.\d{2}\s*%")


def _plain_blocks(pages: List[str]) -> Dict[str, str]:
    """HS code -> the row's plain text (Indonesian + English cells), following rows across page breaks."""
    blocks: Dict[str, List[str]] = {}
    cur: Optional[List[str]] = None
    for text in pages:
        for line in text.splitlines():
            if _PAGE_NO_LINE.match(line) or _TABLE_HEAD_LINE.match(line):
                continue
            if "MENTERI KEUANGAN REPUBLIK INDONESIA," in line or line.strip().startswith("Dokumen ini telah"):
                cur = None
                continue
            match = _ROW_LINE.match(line)
            if match:
                cur = blocks.setdefault(match.group(2), [])
                cur.append(match.group(3))
            elif _HEADING_LINE.match(line):
                cur = None
            elif cur is not None:
                cur.append(line)
    return {code: squash(_RATE_TOKEN.sub(" ", " ".join(lines))) for code, lines in blocks.items()}


def _respace(uraian: Optional[str], block: Optional[str]) -> Optional[str]:
    """Replace the kerning-split description by the properly spaced prefix of the plain-text row."""
    if not uraian or not block:
        return uraian
    target = re.sub(r"\s+", "", uraian)
    seen = 0
    for index, char in enumerate(block):
        if not char.isspace():
            seen += 1
        if seen == len(target):
            candidate = block[: index + 1]
            return squash(candidate) if re.sub(r"\s+", "", candidate) == target else uraian
    return uraian


def _repair_spacing(uraian: Optional[str], vocabulary: set) -> Optional[str]:
    """Fallback when the plain-text row is scrambled: restore gaps lost between same-line pieces."""
    if not uraian:
        return uraian
    uraian = re.sub(r",(?=\d{4}\.\d{2}\.\d{2})", ", ", uraian)

    def split_word(match):
        word = match.group(0)
        if word.lower() in vocabulary or len(word) < 6:
            return word
        for cut in range(2, len(word) - 1):
            if word[:cut].lower() in vocabulary and word[cut:].lower() in vocabulary:
                return f"{word[:cut]} {word[cut:]}"
        return word

    return re.sub(r"[A-Za-z]+", split_word, uraian)


def _column(x: float) -> str:
    if x < COL_CODE:
        return "no"
    if x < COL_ID:
        return "code"
    if x < COL_EN:
        return "id"
    return "rate" if x >= COL_RATE else "en"


def _cells(pieces: List[Fragment]) -> Iterator[Tuple[str, str]]:
    """Merge consecutive pieces of one column into cells (PDF kerning splits a number/word into pieces)."""
    column, parts, last_y = "", "", None
    for x, y, text in pieces:
        col = _column(x)
        if col != column:
            if parts.strip():
                yield column, parts
            column, parts, last_y = col, "", None
        if parts and last_y is not None and abs(y - last_y) > 1 and not parts.endswith(" "):
            parts += " "
        parts += text
        last_y = y
    if parts.strip():
        yield column, parts


def parse_tariff_lines(fragments: Dict[int, List[Fragment]]) -> List[Dict[str, Any]]:
    """Changed rows (not "Tetap") of the Lampiran III table, in stream order across pages.

    ``fragments`` maps a 1-based page number to ``(x, y, text)`` pieces in content-stream
    order. Columns: No, HS code, Indonesian description, English description, Bea Masuk.
    A row's cells follow its number in the stream, so a row that continues on the next page
    keeps accumulating after the repeated table header.
    """
    rows: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None
    for page in sorted(fragments):
        pieces = fragments[page]
        start = next((i for i, (_, _, t) in enumerate(pieces) if t.strip() == "(5)"), None)
        if start is None:
            continue
        for column, raw in _cells(pieces[start + 1:]):
            token = squash(raw)
            if "MENTERI KEUANGAN" in token or token.startswith("Dokumen ini telah"):
                cur = None
            elif column == "no":
                if token.isdigit() and len(token) >= 4:
                    cur = {"kode_hs": None, "id": [], "rate": [], "halaman_pdf": page}
            elif column == "code":
                if re.fullmatch(r"\d{2}\.\d{2}", token):
                    cur = None
                elif cur is not None and cur["kode_hs"] is None and HS_CODE.fullmatch(token):
                    cur["kode_hs"] = token
                    rows.append(cur)
            elif cur is not None and column == "id":
                cur["id"].append(token)
            elif cur is not None and column == "rate":
                cur["rate"].append(token)
    lines = []
    for row in rows:
        uraian = squash(" ".join(row["id"]))
        if "Tetap" in uraian or "Tetap" in " ".join(row["rate"]):
            continue
        rate = re.search(r"(\d+(?:[.,]\d+)?)\s*%", " ".join(row["rate"]))
        lines.append(
            {
                "kode_hs": row["kode_hs"],
                "uraian": uraian or None,
                "tarif_bea_masuk": float(rate.group(1).replace(",", ".")) if rate else None,
                "halaman_pdf": row["halaman_pdf"],
            }
        )
    return lines


def build_records(
    pages: List[str], tanggal_berlaku: Optional[str], fragments: Optional[Dict[int, List[Fragment]]] = None
) -> List[Dict[str, Any]]:
    article = parse_pasal_ii(pages)
    if article is None:
        raise SourceUnavailable("Pasal II with HS codes not found in the PMK PDF")
    peraturan = parse_peraturan(pages[0]) if pages else None
    pasal_context = parse_context(pages, article["komoditas"])
    general_context = parse_context(pages, None)

    def record(code, komoditas, tarif, masa, konteks, halaman):
        return {
            "peraturan": peraturan,
            "tanggal_berlaku": tanggal_berlaku,
            "kode_hs": code,
            "komoditas": komoditas,
            "tarif_bea_masuk": tarif,
            "masa_berlaku_tarif": masa,
            "konteks_kebijakan": konteks,
            "halaman_pdf": halaman,
        }

    tariff_lines = parse_tariff_lines(fragments or {})
    if tariff_lines:
        blocks = _plain_blocks(pages)
        vocabulary = {w.lower() for w in re.findall(r"[A-Za-z]+", " ".join(pages))}
        for line in tariff_lines:
            fixed = _respace(line["uraian"], blocks.get(line["kode_hs"]))
            line["uraian"] = fixed if fixed != line["uraian"] else _repair_spacing(fixed, vocabulary)
    seen = {line["kode_hs"] for line in tariff_lines}
    out = []
    for line in tariff_lines:
        in_article = line["kode_hs"] in article["kode_hs"]
        tarif = line["tarif_bea_masuk"]
        if tarif is None and in_article:
            tarif = article["tarif_bea_masuk"]
        out.append(
            record(
                line["kode_hs"],
                line["uraian"],
                tarif,
                article["masa_berlaku_tarif"] if in_article else None,
                pasal_context if in_article else general_context,
                line["halaman_pdf"],
            )
        )
    for code in article["kode_hs"]:
        if code not in seen:
            out.append(
                record(
                    code,
                    article["komoditas"],
                    article["tarif_bea_masuk"],
                    article["masa_berlaku_tarif"],
                    pasal_context,
                    article["halaman_pdf"],
                )
            )
    return out


def _pdf_reader(content: bytes):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ConfigError("pypdf is required for PDF sources (pip install pypdf)") from exc
    try:
        return PdfReader(io.BytesIO(content))
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the PMK PDF: {exc}") from exc


def read_pdf_pages(content: bytes, max_pages: Optional[int] = None) -> List[str]:
    reader = _pdf_reader(content)
    pages = list(reader.pages)
    if max_pages and len(pages) > max_pages:
        logger.warning("PMK PDF: reading only %d of %d pages (MAX_PAGES)", max_pages, len(pages))
        pages = pages[:max_pages]
    try:
        return [page.extract_text() or "" for page in pages]
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the PMK PDF: {exc}") from exc


def read_tariff_fragments(content: bytes, pages: List[str]) -> Dict[int, List[Fragment]]:
    """Positioned text pieces of the table pages that hold changed lines (the rest are all "Tetap")."""
    reader = _pdf_reader(content)
    fragments: Dict[int, List[Fragment]] = {}
    for number, text in enumerate(pages, start=1):
        if "Bea Masuk/" not in text:
            continue
        if "Tetap" in text and not re.search(r"\d\.\d{2}\s*%", text):
            continue
        pieces: List[Fragment] = []

        def visit(piece, cm, tm, font_dict, font_size, _out=pieces):
            if piece.strip():
                _out.append((tm[4] * cm[0] + tm[5] * cm[2] + cm[4], tm[5] * cm[3] + tm[4] * cm[1] + cm[5], piece))

        try:
            reader.pages[number - 1].extract_text(visitor_text=visit)
        except Exception as exc:
            raise SourceUnavailable(f"Could not read PMK PDF page {number}: {exc}") from exc
        fragments[number] = pieces
    return fragments


class Extractor(BaseExtractor):
    def extract(self) -> Iterator[Dict[str, Any]]:
        tanggal_berlaku: Optional[str] = None
        pdf_url = (self.config.get("pdf_url") or "").strip()
        landing_url = (self.config.get("url") or "").strip()
        if landing_url:
            html = self.http.get(landing_url, timeout=60).content.decode("utf-8", errors="replace")
            tanggal_berlaku = parse_effective_date(html)
            if not pdf_url:
                pdf_url = find_pdf_url(html, landing_url) or ""
        if not pdf_url:
            raise ConfigError("Set URL (regulation detail page) or PDF_URL for perubahan_tarif_pmk")

        content = self.http.get(pdf_url, timeout=300).content
        max_pages = int(self.config.get("max_pages") or 0) or None
        pages = read_pdf_pages(content, max_pages)
        records = build_records(pages, tanggal_berlaku, read_tariff_fragments(content, pages))
        logger.info("PMK %s: %d pages, %d tarif lines (effective %s)", pdf_url, len(pages), len(records), tanggal_berlaku)
        yield from records
