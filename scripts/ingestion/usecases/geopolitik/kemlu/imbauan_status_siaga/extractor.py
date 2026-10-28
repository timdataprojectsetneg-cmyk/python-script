"""Kemlu Imbauan dan Status Siaga: country, status and WNI count from Kemlu news/press releases.

kemlu.go.id is a JS single-page app (static HTML is an empty shell) and its
search endpoint is not usable, so article pages are given explicitly:

* ``URL``: one or more article/page URLs (comma or newline separated) whose HTML
  contains the article text, e.g. a static mirror or a Perwakilan site page.
* ``SOURCE_FILE``: a saved HTML/text file, or a directory of ``*.html``/``*.htm``/``*.txt``.

Extraction is rule based and conservative; a field that the text does not state
explicitly stays empty (None), never guessed:

* status: ``Siaga I..IV`` (or 1..4) written in the text; if several levels are
  mentioned one record per level is emitted using the sentences of that level;
  otherwise articles with "imbauan/himbauan" give ``Imbauan`` (plus a topic word
  such as penipuan/ketenagakerjaan/keamanan) and evacuation-only articles
  give ``Evakuasi``. Anything else is skipped.
* negara: a known country name in the title, else in the first paragraph.
* jumlah WNI: only when the text states exactly one distinct number next to "WNI".
* penerbit: first KBRI/KJRI/KONSULAT mention, else Kemlu RI.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from html import unescape
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

COUNTRIES = [
    "Afghanistan", "Arab Saudi", "Armenia", "Aljazair", "Bahrain", "Bangladesh", "Belarus", "Brunei Darussalam",
    "Ethiopia", "Filipina", "Haiti", "India", "Irak", "Iran", "Israel", "Jepang", "Kamboja", "Kongo", "Korea Selatan",
    "Korea Utara", "Kuwait", "Laos", "Lebanon", "Libanon", "Libya", "Malaysia", "Mali", "Mesir", "Myanmar", "Niger",
    "Nigeria", "Oman", "Pakistan", "Palestina", "Qatar", "Rusia", "Somalia", "Sudan Selatan", "Sudan", "Suriah",
    "Taiwan", "Thailand", "Tiongkok", "Turki", "Ukraina", "Uni Emirat Arab", "Venezuela", "Yaman", "Yordania",
    "Myanmar", "Nepal", "Sri Lanka", "Kyrgyzstan", "Mozambik", "Burkina Faso", "Tunisia", "Maroko",
]
_COUNTRY_RE = re.compile(r"\b(" + "|".join(sorted({re.escape(c) for c in COUNTRIES}, key=len, reverse=True)) + r")\b")
_ROMAN = {"1": "I", "2": "II", "3": "III", "4": "IV", "I": "I", "II": "II", "III": "III", "IV": "IV"}
_SIAGA = re.compile(r"\bSiaga\s*(IV|III|II|I|[1-4])\b(?![a-zA-Z])", re.I)
_IMBAUAN = re.compile(r"(?:im|him)bau(?:an|kan)?\b", re.I)
_EVAKUASI = re.compile(r"\bevakuasi\b", re.I)
_NUMBER = r"(\d{1,3}(?:\.\d{3})+|\d+)"
_WNI_BEFORE = re.compile(_NUMBER + r"\s+(?:orang\s+)?(?:WNI|warga negara Indonesia)\b", re.I)
_WNI_AFTER = re.compile(
    r"\b(?:WNI|warga negara Indonesia)\b[^.\n]{0,60}?\b(?:sebanyak|sejumlah|berjumlah|sekitar|total)\s+" + _NUMBER,
    re.I,
)
_PERWAKILAN = re.compile(r"\b(?:KBRI|KJRI|KRI|Konsulat\s+\w+)\s+[A-Z][\w'’-]+(?:\s+[A-Z][\w'’-]+)?")
_TOPICS = [
    ("penipuan", "Imbauan penipuan"),
    ("ketenagakerjaan", "Imbauan ketenagakerjaan"),
    ("pekerja", "Imbauan ketenagakerjaan"),
    ("keamanan", "Imbauan keamanan"),
    ("cuaca", "Imbauan cuaca/bencana"),
    ("bencana", "Imbauan cuaca/bencana"),
]
_ACTION = re.compile(
    r"evakuasi|imbau|himbau|meninggalkan|menghindari|tidak (?:bepergian|melakukan perjalanan)|memantau|kontingensi|"
    r"lapor diri|menunda perjalanan",
    re.I,
)
_MONTHS = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
    "september": 9, "oktober": 10, "november": 11, "desember": 12,
}
_DATE_TEXT = re.compile(r"\b(\d{1,2})\s+(" + "|".join(_MONTHS) + r")\s+(20\d{2})\b", re.I)
_DATE_ISO = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")


def html_to_text(html: str) -> Tuple[str, str]:
    """(title, body text with paragraph breaks)."""
    html = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", html)
    title_m = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", html) or re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    title = unescape(re.sub(r"<[^>]+>", " ", title_m.group(1))) if title_m else ""
    body = re.sub(r"(?i)</(p|div|li|h\d|br|tr)>|<br\s*/?>", "\n", html)
    body = unescape(re.sub(r"<[^>]+>", " ", body))
    lines = [" ".join(ln.split()) for ln in body.splitlines()]
    return " ".join(title.split()), "\n".join(ln for ln in lines if ln)


def find_date(html: str, text: str, url: str = "") -> Optional[date]:
    for pattern in (
        r'(?i)article:published_time"?\s+content="([^"]+)"',
        r'(?i)<time[^>]*datetime="([^"]+)"',
        r'(?i)"datePublished"\s*:\s*"([^"]+)"',
    ):
        m = re.search(pattern, html)
        iso = _DATE_ISO.search(m.group(1)) if m else None
        if iso:
            return date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
    m = _DATE_TEXT.search(text[:600])
    if m:
        return date(int(m.group(3)), _MONTHS[m.group(2).lower()], int(m.group(1)))
    m = _DATE_ISO.search(url or "")
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n", text) if s.strip()]


def find_country(title: str, text: str) -> Optional[str]:
    for scope in (title, text.split("\n", 1)[0] if text else ""):
        m = _COUNTRY_RE.search(scope)
        if m:
            return "Lebanon" if m.group(1) == "Libanon" else m.group(1)
    return None


def find_wni_count(text: str) -> Optional[int]:
    values = {int(m.group(1).replace(".", "")) for m in _WNI_BEFORE.finditer(text)}
    values |= {int(m.group(1).replace(".", "")) for m in _WNI_AFTER.finditer(text)}
    return values.pop() if len(values) == 1 else None


def find_perwakilan(text: str) -> str:
    m = _PERWAKILAN.search(text)
    return " ".join(m.group(0).split()) if m else "Kemlu RI"


def find_action(sents: List[str]) -> Optional[str]:
    hits = [s for s in sents if _ACTION.search(s)][:2]
    return " ".join(hits)[:500] or None


def find_wilayah(text: str) -> Optional[str]:
    m = re.search(r"\bwilayah\s+((?:[A-Z][\w’'-]+)(?:(?:\s*[,;]\s*|\s+dan\s+|\s+)[A-Z][\w’'-]+){0,5})", text)
    return m.group(1).strip() if m else None


def parse_article(html: str, url: str = "") -> List[Dict[str, Any]]:
    """Zero or more records from one article; empty when the page is not a relevant, country-specific notice."""
    title, text = html_to_text(html)
    if len(text) < 80:
        return []
    negara = find_country(title, text)
    if negara is None:
        return []
    sents = sentences(title + "\n" + text)
    base = {
        "tanggal_acuan": find_date(html, text, url),
        "negara": negara,
        "wilayah": find_wilayah(text) or negara,
        "perwakilan_penerbit": find_perwakilan(text),
        "jumlah_wni_disebut_sumber": find_wni_count(text),
        "url_bukti": url or None,
    }
    levels: Dict[str, List[str]] = {}
    for sent in sents:
        for m in _SIAGA.finditer(sent):
            levels.setdefault("Siaga " + _ROMAN[m.group(1).upper()], []).append(sent)
    if levels:
        return [
            {**base, "status_jenis_imbauan": level, "tindakan_yang_diumumkan": find_action(sn) or find_action(sents)}
            for level, sn in levels.items()
        ]
    low = (title + " " + text).lower()
    if _IMBAUAN.search(low):
        status = next((label for key, label in _TOPICS if key in low), "Imbauan")
    elif _EVAKUASI.search(low):
        status = "Evakuasi"
    else:
        return []
    return [{**base, "status_jenis_imbauan": status, "tindakan_yang_diumumkan": find_action(sents)}]


class Extractor(BaseExtractor):
    def _documents(self) -> Iterator[Tuple[str, str]]:
        local = (self.config.get("source_file") or "").strip()
        if local:
            path = Path(local)
            if path.is_dir():
                files = sorted(p for p in path.iterdir() if p.suffix.lower() in (".html", ".htm", ".txt"))
            elif path.is_file():
                files = [path]
            else:
                raise ConfigError(f"SOURCE_FILE not found: {local}")
            for p in files:
                yield p.read_text(encoding="utf-8", errors="ignore"), p.as_uri()
            return
        urls = [u.strip() for u in re.split(r"[,\n]", self.config.get("url") or "") if u.strip()]
        if not urls:
            raise ConfigError(
                "imbauan_status_siaga needs URL (Kemlu article page URL(s)) or SOURCE_FILE: "
                "kemlu.go.id is a JS app, so news pages cannot be discovered from its listing"
            )
        for url in urls:
            yield self.http.get(url, timeout=60).text, url

    def extract(self) -> Iterator[Dict[str, Any]]:
        count = 0
        for html, url in self._documents():
            for record in parse_article(html, url):
                count += 1
                yield record
        if count == 0:
            raise SourceUnavailable(
                "No Siaga/imbauan record extracted: the pages are empty shells (JS-rendered) or state no status/country"
            )
        logger.info("Kemlu imbauan_status_siaga: %d records", count)
