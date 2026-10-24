
"""Page level context: title, year, unit and free text around the data.

Context fields are values that are *not* present as a table column or chart
label -- e.g. the year written in a section title.  They are applied to all
records of a candidate, but always with an explicit provenance source so an
inferred value can never be mistaken for a printed one (TDD section 8).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pymupdf

from .models import FieldSpec
from .pdf_reader import PageView, normalise

_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_UNIT = re.compile(r"\(([A-Za-z][A-Za-z0-9/&\.\s%]{0,24})\)")
_UNIT_WORD = re.compile(r"\b(Million|Thousand|Trillion|TWh|GWh|MWh|GJ|BOE|TOE|kL|MMSCF|Rp)\b", re.I)
# bare abbreviations that are a unit on their own (no "Million"/"Thousand" in
# front of them).  Without this whitelist a parenthesis such as "(PLN)" would
# be reported as the unit of the page.
_UNIT_BARE = {
    "GJ", "TJ", "PJ", "MJ", "BOE", "TOE", "MTOE", "KTOE", "TWH", "GWH", "MWH", "KWH",
    "MW", "GW", "KW", "KL", "MMSCF", "MMSCFD", "SCF", "BBL", "MMBBL", "RP", "%",
    "MT", "KT", "MMCF", "BCF", "MSCF", "KG", "TON", "TONNES", "LITRE", "LITER",
}
_ID_MONTHS = {
    "januari": "January", "februari": "February", "maret": "March", "april": "April",
    "mei": "May", "juni": "June", "juli": "July", "agustus": "August",
    "september": "September", "oktober": "October", "november": "November",
    "desember": "December", "agu": "Aug", "okt": "Oct", "des": "Dec",
}
_DATE_FORMATS = ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y")


def to_number(raw: str) -> float:
    """Parse a number written with Indonesian *or* US separators."""
    s = re.sub(r"(?i)rp\.?|\s|%", "", str(raw)).strip().rstrip(".,")
    if not s:
        raise ValueError(f"bukan angka: {raw!r}")
    neg = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    s = s.strip("()").lstrip("-")
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".") if s.rindex(".") < s.rindex(",") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".") if re.search(r",\d{1,2}$", s) else s.replace(",", "")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    val = float(s)
    return -val if neg else val


def to_date(raw: str):
    from datetime import datetime

    s = str(raw).strip()
    for k, v in _ID_MONTHS.items():
        s = re.sub(rf"(?i)\b{k}\b", v, s)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"format tanggal tidak dikenali: {raw!r}")


def coerce(raw, kind: str):
    """Coerce ``raw`` to ``kind``; return the raw value when parsing fails."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return raw
    s = normalise(str(raw))
    if s in {"", "-", "–", "—", "n/a", "N/A", "na"}:
        return None
    try:
        if kind == "int":
            return int(round(to_number(s)))
        if kind == "float":
            return to_number(s)
        if kind == "date":
            return to_date(s).isoformat()
        if kind == "bool":
            return s.lower() in {"ya", "yes", "true", "1", "y"}
    except ValueError:
        return s
    return s


@dataclass
class PageContext:
    """Everything we know about a page besides the tables/charts."""

    page: int
    title: str = ""
    text: str = ""
    years: list[int] = field(default_factory=list)
    unit: str | None = None

    @classmethod
    def from_page(cls, page: PageView) -> "PageContext":
        text = normalise(page.text)
        return cls(
            page=page.number,
            title=cls._title(page),
            text=text,
            years=[int(y) for y in _YEAR.findall(text)],
            unit=cls._unit(text),
        )

    # -- helpers ----------------------------------------------------------
    @staticmethod
    def _title(page: PageView) -> str:
        """Heading-ish text at the top of the page (largest font)."""
        try:
            spans = page.page.get_text("dict").get("blocks", [])
        except Exception:  # noqa: BLE001
            return ""
        best: tuple[float, str] | None = None
        for block in spans:
            for line in block.get("lines", []):
                if not line.get("spans"):
                    continue
                txt = normalise(" ".join(s.get("text", "") for s in line["spans"]))
                if not txt:
                    continue
                size = max(s.get("size", 0) for s in line["spans"])
                y0 = min(s.get("bbox", (0, 999, 0, 0))[1] for s in line["spans"])
                if y0 > page.rect.height * 0.35:
                    continue
                score = size - y0 * 0.01
                if best is None or score > best[0]:
                    best = (score, txt)
        return best[1] if best else ""

    @staticmethod
    def _unit(text: str) -> str | None:
        """First parenthesis that actually looks like a unit.

        ``(Thousand BOE)`` qualifies, ``(PLN)`` or ``(Non-PLN)`` do not -- a
        report is full of parenthesised abbreviations that are *not* units.
        """
        for m in _UNIT.finditer(text or ""):
            cand = m.group(1).strip()
            if not (0 < len(cand) <= 24) or re.fullmatch(r"(?i)\d+", cand):
                continue
            if _UNIT_WORD.search(cand):
                return cand
            if cand.replace(".", "").replace(" ", "").upper() in _UNIT_BARE:
                return cand
        return None

    # -- context field lookup --------------------------------------------
    def find(self, spec: FieldSpec) -> tuple[object, str] | None:
        """Look for a value for ``spec`` in the page context.

        Returns ``(value, source)`` where source is one of
        ``page_title`` / ``nearby_text``, or ``None``.
        """
        for source, text in (("page_title", self.title), ("nearby_text", self.text)):
            value = self._match(spec, text)
            if value is not None:
                return value, source
        return None

    def _match(self, spec: FieldSpec, text: str):
        if not text:
            return None
        labels = [a for a in spec.candidates() if a]
        low = text.lower()
        for label in labels:
            lab = re.escape(normalise(label).lower()).replace(r"\ ", r"\s+")
            if spec.kind in ("int", "float"):
                pat = rf"(?i)\b{lab}\b\s*[:\-]?\s*(-?[\d.,]+)"
            elif spec.kind == "date":
                pat = rf"(?i)\b{lab}\b\s*[:\-]?\s*([\w /,-]{{6,20}})"
            else:
                pat = rf"(?i)\b{lab}\b\s*[:\-]\s*([^\n.;|]{{1,60}})"
            m = re.search(pat, text)
            if not m:
                continue
            value = coerce(m.group(1).strip(), spec.kind)
            if value is not None and not (isinstance(value, str) and not value.strip()):
                return value
        # generic year fallback for year-like integer fields
        if spec.kind == "int" and re.search(r"(?i)tahun|year", " ".join(labels)):
            years = [int(y) for y in _YEAR.findall(text)]
            if years:
                return max(years)
        if spec.kind == "str" and re.search(r"(?i)\bsatuan\b|\bunit\b", " ".join(labels)):
            return self.unit
        del low  # (kept for readability)
        return None


def unit_from_header(header: str) -> str | None:
    """Extract the unit part of a header such as ``"Volume (GJ)"``."""
    m = _UNIT.search(header or "")
    if m:
        return m.group(1).strip()
    m = _UNIT_WORD.search(header or "")
    return m.group(1) if m else None