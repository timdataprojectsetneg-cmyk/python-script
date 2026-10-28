"""Posisi Resmi Indonesia: issue-level positions from Setneg joint-press statements.

Each statement page (``setneg.go.id/baca/index/<slug>``) is split into paragraphs; a paragraph
whose text hits an issue keyword group becomes a row (consecutive paragraphs of the same issue
are merged). ``isu`` is a deterministic keyword classification and ``posisi_yang_dinyatakan`` is
the extractive passage itself (no paraphrase, no sentiment inference).

``URL`` is a statement page (comma separated for several). Optional: ``LIST_URL`` (a Setneg
``/listcontent/listberita/<category>`` page) and ``SLUG_FILTER`` (regex on
article slugs) to discover more statements. Every list page is followed until one has no articles;
``LIST_PAGES`` / ``MAX_ARTICLES`` are optional debug caps (default unlimited). Passages are kept in full.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any, Dict, Iterator, List, Optional, Tuple

from bs4 import BeautifulSoup

from .....config import get as env_get
from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable
from .config import PUBLISHER, SOURCE

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://www.setneg.go.id/baca/index/"
    "pernyataan_pers_bersama_presiden_ri_usai_pertemuan_bilateral_dengan_presiden_republik_prancis"
)
DEFAULT_SLUG_FILTER = r"(pernyataan|keterangan)_pers.*(bilateral|bersama|kunjungan|pertemuan|kenegaraan)"
LIST_PAGE_SIZE = 10
NAV_SLUGS = {"protokol"}
SETNEG_ORIGIN = "https://www.setneg.go.id"

ID_MONTHS = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7,
    "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
}
DATE_RE = re.compile(r"(\d{1,2})\s+(" + "|".join(ID_MONTHS) + r")\s+(\d{4})", re.IGNORECASE)

ISSUES: List[Tuple[str, "re.Pattern[str]"]] = [
    ("Palestina dan Timur Tengah", re.compile(r"palestin|gaza|two[- ]states|israel|timur tengah", re.I)),
    ("Ukraina dan konflik global", re.compile(r"ukraina|rusia|perang|konflik|gencatan", re.I)),
    ("Maritim dan Laut China Selatan", re.compile(r"maritim|laut china selatan|samudra|konferensi laut", re.I)),
    ("Energi dan transisi hijau", re.compile(r"energi|nikel|hilirisasi|iklim|karbon|baterai|mineral kritis", re.I)),
    ("Pertahanan dan keamanan", re.compile(r"pertahanan|alutsista|militer|keamanan|angkatan|terorisme", re.I)),
    ("Perdagangan dan investasi", re.compile(r"perdagangan|dagang|investasi|cepa|ekonomi|ekspor|impor|oecd|tarif|bea masuk", re.I)),
    ("Ketahanan pangan dan kesehatan", re.compile(r"pangan|pertanian|makan bergizi|kesehatan|vaksin", re.I)),
    ("Pendidikan dan kebudayaan", re.compile(r"pendidikan|mahasiswa|kebudayaan|budaya|pariwisata|ekonomi kreatif", re.I)),
    ("Hukum internasional dan multilateralisme", re.compile(r"hukum internasional|perserikatan bangsa|\bpbb\b|multilateral|\basean\b|\bg20\b|brics", re.I)),
    ("Kemitraan bilateral", re.compile(r"kemitraan|hubungan diplomatik|bilateral|kerja ?sama", re.I)),
]
SKIP_PARAGRAPH = re.compile(r"^(bagaimana pendapat anda|\(?bpmi|\(?sumber)", re.I)


def squash(text: str) -> str:
    return " ".join((text or "").replace("\xa0", " ").split())


def parse_id_date(text: str) -> Optional[date]:
    match = DATE_RE.search(text or "")
    if not match:
        return None
    try:
        return date(int(match.group(3)), ID_MONTHS[match.group(2).lower()], int(match.group(1)))
    except ValueError:
        return None


def classify(paragraph: str) -> Optional[str]:
    """Issue label whose keyword group matches earliest in the paragraph."""
    best: Optional[Tuple[int, str]] = None
    for label, pattern in ISSUES:
        found = pattern.search(paragraph)
        if found and (best is None or found.start() < best[0]):
            best = (found.start(), label)
    return best[1] if best else None


def parse_article(html: str) -> Dict[str, Any]:
    """Return ``{title, date, paragraphs}`` from a Setneg article page."""
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h1", id="title-page") or soup.find("h1")
    container = soup.select_one("div.article-content")
    if heading is None or container is None:
        raise SourceUnavailable("Setneg article layout not recognised (no h1/article-content)")
    meta = container.select_one("p.widget-metas")
    paragraphs: List[str] = []
    for p in container.find_all("p"):
        if p is meta or p.find_parent(class_="col-related") is not None:
            continue
        for br in p.find_all("br"):
            br.replace_with(" ")
        text = squash(p.get_text(""))
        if len(text) > 2 and not SKIP_PARAGRAPH.match(text):
            paragraphs.append(text)
    return {
        "title": squash(heading.get_text(" ")),
        "date": parse_id_date(meta.get_text(" ") if meta else ""),
        "paragraphs": paragraphs,
    }


def infer_official(title: str, text: str) -> Optional[str]:
    if re.search(r"wakil presiden", title, re.I):
        return "Wakil Presiden RI"
    if re.search(r"menteri luar negeri", title, re.I):
        return "Menteri Luar Negeri RI"
    if re.search(r"presiden", title, re.I):
        return "Presiden RI Prabowo Subianto" if re.search(r"prabowo", text, re.I) else "Presiden RI"
    return None


def build_rows(article: Dict[str, Any], url: str) -> List[Dict[str, Any]]:
    paragraphs: List[str] = article["paragraphs"]
    context = article["title"]
    if paragraphs and re.match(r"^Di\s", paragraphs[0]) and len(paragraphs[0]) < 120:
        context = f"{context} ({paragraphs[0]})"
    official = infer_official(article["title"], " ".join(paragraphs))
    tanggal = article["date"].isoformat() if article["date"] else None

    grouped: List[Tuple[str, List[str]]] = []
    for paragraph in paragraphs:
        issue = classify(paragraph)
        if issue is None:
            continue
        if grouped and grouped[-1][0] == issue:
            grouped[-1][1].append(paragraph)
        else:
            grouped.append((issue, [paragraph]))

    return [
        {
            "tanggal_pernyataan": tanggal,
            "pejabat": official,
            "forum_konteks": context,
            "isu": issue,
            "posisi_yang_dinyatakan": " ".join(parts),
            "urutan_isu": number,
            "url_sumber": url,
        }
        for number, (issue, parts) in enumerate(grouped, start=1)
    ]


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.urls = [u.strip() for u in str(config.get("url") or DEFAULT_URL).split(",") if u.strip()]

    def _opt(self, key: str, default: Any = None) -> Any:
        value = self.config.get(key.lower())
        if value in (None, ""):
            value = env_get(self.config.get("usecase", "geopolitik"), PUBLISHER, SOURCE, key.upper())
        return default if value in (None, "") else value

    def discover_urls(self, list_url: str) -> List[str]:
        pattern = re.compile(str(self._opt("slug_filter", DEFAULT_SLUG_FILTER)), re.I)
        max_pages = int(self._opt("list_pages", 0))
        max_articles = int(self._opt("max_articles", 0))
        found: List[str] = []
        page = 0
        while not max_pages or page < max_pages:
            page_url = list_url.rstrip("/") + (f"/{page * LIST_PAGE_SIZE}" if page else "")
            soup = BeautifulSoup(self.http.get(page_url, timeout=60).text, "html.parser")
            slugs = {
                m.group(1)
                for a in soup.find_all("a", href=True)
                if (m := re.search(r"/baca/index/([^/?#]+)$", a["href"])) and m.group(1) not in NAV_SLUGS
            }
            if not slugs:
                return found
            for anchor in soup.find_all("a", href=True):
                match = re.search(r"/baca/index/([^/?#]+)$", anchor["href"])
                if match and pattern.search(match.group(1)):
                    url = f"{SETNEG_ORIGIN}/baca/index/{match.group(1)}"
                    if url not in found:
                        found.append(url)
                        if max_articles and len(found) >= max_articles:
                            logger.warning("Setneg: stopped at MAX_ARTICLES=%s", max_articles)
                            return found
            page += 1
        logger.warning("Setneg: stopped at LIST_PAGES=%s; unset LIST_PAGES to scan the whole list", max_pages)
        return found

    def extract(self) -> Iterator[Dict[str, Any]]:
        urls = list(self.urls)
        list_url = self._opt("list_url")
        if list_url:
            urls += [u for u in self.discover_urls(str(list_url)) if u not in urls]
        emitted = 0
        for url in urls:
            article = parse_article(self.http.get(url, timeout=60).text)
            for row in build_rows(article, url):
                emitted += 1
                yield row
        if emitted == 0:
            raise SourceUnavailable(f"No issue passages found in Setneg statements: {urls}")
