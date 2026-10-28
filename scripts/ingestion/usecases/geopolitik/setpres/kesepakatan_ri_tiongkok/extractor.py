"""Kesepakatan RI-Tiongkok: agreements named in a Setneg signing press release.

The default article reports the 12 MoUs signed during Premier Li Qiang's visit
(25 May 2025). The article is prose, so rows are extracted by rules: a sentence clause is an
agreement when it names its parties ("antara A dengan/dan B", "A dan B menyepakati ...",
"kerja sama A dengan B ...", "oleh otoritas ... kedua negara"). Counted enumerations
("dua dokumen ... mengenai X dan Y", "dua nota ... antara A dengan B serta C") become one row
per item. Parties are assigned to Indonesia/mitra by Tiongkok keywords.

``URL`` is the article (comma separated for several articles of the same kind).
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any, Dict, Iterator, List, Optional, Tuple

from bs4 import BeautifulSoup

from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = (
    "https://www.setneg.go.id/baca/index/"
    "presiden_prabowo_dan_premier_li_qiang_saksikan_penandatanganan_12_nota_kesepahaman_strategis_ri_tiongkok"
)

ID_MONTHS = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6, "juli": 7,
    "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12,
}
WIDGET_DATE_RE = re.compile(r"(\d{1,2})\s+(" + "|".join(ID_MONTHS) + r")\s+(\d{4})", re.IGNORECASE)
SLASH_DATE_RE = re.compile(r"\((\d{1,2})/(\d{1,2})/(\d{4})\)")

CHINA_RE = re.compile(
    r"RRT|Tiongkok|Tionghoa|China|Xinhua|Fujian|Rakyat Tiongkok|Komisi Pembangunan dan Reformasi Nasional",
    re.IGNORECASE,
)
AGREEMENT_RE = re.compile(r"nota kesepahaman|\bmou\b|kesepakatan|kerja ?sama|protokol|dokumen|menyepakati", re.IGNORECASE)
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")
CLAUSE_SPLIT = re.compile(r",\s+serta\s+(?=(?:kerja|penguatan|protokol|dokumen|nota|mou)\b)", re.IGNORECASE)
LEAD_CUT = re.compile(
    r"^.*?(?:mencakup|adalah|ditandatanganinya|ditandai dengan|ditandatangani pula|Di antaranya|ditandatangani)\s+",
    re.IGNORECASE,
)
TOPIC_MARKER = re.compile(r"\s+(?:mengenai|tentang|terkait|dalam bidang|dalam|di bidang)\s+", re.IGNORECASE)
GENERIC_TOPICS = {"kerja sama", "penguatan hubungan", "nota kesepahaman", "mou", "dokumen kerja sama", "dokumen"}
COUNT_WORDS = {"dua": 2, "tiga": 3, "empat": 4}
SIGNED_RE = re.compile(r"tanda ?tangan|menyepakati|disepakati", re.IGNORECASE)


def squash(text: str) -> str:
    return " ".join((text or "").replace("\xa0", " ").split())


def article_date(meta_text: str, body: str) -> Optional[date]:
    """Signing date from "(25/05/2025)" in the body, else the article date line."""
    match = SLASH_DATE_RE.search(body)
    try:
        if match:
            return date(int(match.group(3)), int(match.group(2)), int(match.group(1)))
        match = WIDGET_DATE_RE.search(meta_text)
        if match:
            return date(int(match.group(3)), ID_MONTHS[match.group(2).lower()], int(match.group(1)))
    except ValueError:
        pass
    return None


def parse_article(html: str) -> Dict[str, Any]:
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
        text = squash(p.get_text(" "))
        text = re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", text))
        if len(text) > 2 and not text.lower().startswith(("bagaimana pendapat anda", "(bpmi")):
            paragraphs.append(text)
    return {
        "title": squash(heading.get_text(" ")),
        "meta": squash(meta.get_text(" ")) if meta else "",
        "paragraphs": paragraphs,
    }


def _split_and(piece: str) -> List[str]:
    """Split "A dan B" at the " dan " that separates an Indonesian party from a Tiongkok one."""
    cuts = [m.start() for m in re.finditer(r"\s+dan\s+", piece)]
    for cut in reversed(cuts):
        left, right = piece[:cut], re.sub(r"^\s+dan\s+", "", piece[cut:])
        if bool(CHINA_RE.search(left)) != bool(CHINA_RE.search(right)):
            return [squash(left), squash(right)]
    if cuts:
        return [squash(piece[: cuts[-1]]), squash(re.sub(r"^\s+dan\s+", "", piece[cuts[-1]:]))]
    return [squash(piece)]


def split_parties(text: str) -> List[str]:
    parts: List[str] = []
    for piece in re.split(r",\s*(?:dan\s+)?|\s+serta\s+", text.strip(" ,.;")):
        parts.extend(_split_and(piece) if " dan " in piece else [squash(piece)])
    return [p for p in parts if p]


def assign_sides(parties: List[str]) -> Tuple[Optional[str], Optional[str]]:
    indonesia = [p for p in parties if not CHINA_RE.search(p)]
    mitra = [p for p in parties if CHINA_RE.search(p)]
    if parties and (not indonesia or not mitra) and len(parties) >= 2:
        indonesia, mitra = parties[:1], parties[1:]
    return ("; ".join(indonesia) or None, "; ".join(mitra) or None)


def _clean_topic(text: str) -> str:
    text = re.sub(r"\s+yang\s+ditandatangani.*$", "", squash(text).strip(" ,.;"), flags=re.IGNORECASE)
    return text[:1].upper() + text[1:] if text else text


def _topic_from(lead: str, tail: str) -> str:
    tail = squash(tail).strip(" ,.;")
    if tail:
        return _clean_topic(tail)
    lead = LEAD_CUT.sub("", squash(lead)).strip(" ,.;")
    lead = re.sub(r"^(Di bidang \w+,|Selain itu,|Sektor \w+ turut[^,]*,)\s*", "", lead, flags=re.IGNORECASE)
    return _clean_topic(lead)


def extract_agreements(clause: str) -> List[Dict[str, Any]]:
    """Agreements named in one clause: ``[{topic, indonesia, mitra}]`` (empty if no parties)."""
    clause = squash(clause)
    count_match = re.search(r"\b(dua|tiga|empat)\s+(?:dokumen|nota kesepahaman|mou)\b", clause, re.IGNORECASE)
    expected = COUNT_WORDS[count_match.group(1).lower()] if count_match else 1

    # protocol signed by the quarantine authorities of both countries
    both = re.search(r"oleh\s+(otoritas\s+\w+)\s+kedua negara", clause, re.IGNORECASE)
    if both:
        lead = clause[: both.start()]
        return [{
            "topic": _topic_from(re.sub(r"^.*?protokol", "Protokol", lead, flags=re.IGNORECASE), ""),
            "indonesia": f"{both.group(1)} Indonesia",
            "mitra": f"{both.group(1)} Tiongkok",
        }]

    # "antara A dengan/dan B [serta C] [mengenai/dalam ... X]"
    between = re.search(r"\bantara\s+(.+?)(?=\s+(?:mengenai|tentang|terkait|dalam|di bidang)\s|$)", clause, re.IGNORECASE)
    if between:
        parties_text = between.group(1)
        lead = clause[: between.start()]
        tail = clause[between.end():]
        tail = TOPIC_MARKER.sub("", " " + tail, count=1) if TOPIC_MARKER.match(" " + tail) else tail
        if " dengan " in parties_text:
            left, right = parties_text.split(" dengan ", 1)
            partners = split_parties(right) if expected > 1 else [squash(right).strip(" ,.;")]
            rows = []
            for partner in partners:
                sides = assign_sides([squash(left), partner])
                topic = _topic_from(lead, tail)
                if topic.lower() in GENERIC_TOPICS:
                    topic = f"{topic} {squash(left)} dengan {partner}"
                rows.append({"topic": topic, "indonesia": sides[0], "mitra": sides[1]})
            return rows
        parties = split_parties(parties_text)
        indonesia, mitra = assign_sides(parties)
        if expected > 1 and tail:
            items = [i for i in re.split(r"\s+dan\s+", squash(tail).strip(" ,.;")) if i]
            if len(items) == expected:
                return [{"topic": _clean_topic(i), "indonesia": indonesia, "mitra": mitra} for i in items]
        topic = _topic_from(lead, tail)
        if topic.lower() in GENERIC_TOPICS:
            topic = f"{topic} antara " + " dengan ".join(parties[:1] + [" dan ".join(parties[1:])]) if len(parties) > 1 else topic
        return [{"topic": topic, "indonesia": indonesia, "mitra": mitra}]

    # "A dan B menyepakati X"
    agree = re.search(r"([A-Z][^,]*?)\s+dan\s+([A-Z][^,]*?)\s+menyepakati\s+(.+)$", clause)
    if agree:
        indonesia, mitra = assign_sides([squash(agree.group(1)), squash(agree.group(2))])
        lead_in = re.sub(r"^Di bidang \w+,\s*", "", agree.group(1))
        indonesia, mitra = assign_sides([squash(lead_in), squash(agree.group(2))])
        return [{"topic": _clean_topic(agree.group(3)), "indonesia": indonesia, "mitra": mitra}]

    # "kerja sama A dengan B dalam/mengenai X"
    pair = re.search(r"kerja ?sama\s+(.+?)\s+dengan\s+(.+?)(?=\s+(?:mengenai|tentang|terkait|dalam|di bidang)\s|$)", clause, re.IGNORECASE)
    if pair:
        indonesia, mitra = assign_sides([squash(pair.group(1)), squash(pair.group(2))])
        tail = clause[pair.end():]
        tail = TOPIC_MARKER.sub("", " " + tail, count=1) if TOPIC_MARKER.match(" " + tail) else ""
        return [{"topic": _clean_topic(tail) or "Kerja sama " + squash(pair.group(1)) + " dengan " + squash(pair.group(2)),
                 "indonesia": indonesia, "mitra": mitra}]
    return []


def build_rows(article: Dict[str, Any], url: str) -> List[Dict[str, Any]]:
    body = " ".join(article["paragraphs"])
    when = article_date(article["meta"], body)
    signing_article = bool(re.search(r"penandatanganan|menandatangani", article["title"], re.IGNORECASE))
    rows: List[Dict[str, Any]] = []
    for paragraph in article["paragraphs"]:
        for sentence in SENTENCE_SPLIT.split(paragraph):
            if not AGREEMENT_RE.search(sentence):
                continue
            for clause in CLAUSE_SPLIT.split(sentence):
                for item in extract_agreements(clause):
                    signed = signing_article or bool(SIGNED_RE.search(sentence))
                    rows.append(
                        {
                            "tanggal": when.isoformat() if when else None,
                            "topik_kesepakatan": item["topic"],
                            "pihak_indonesia": item["indonesia"],
                            "pihak_mitra": item["mitra"],
                            "status_bukti": (
                                "Ditandatangani (menurut siaran pers Setneg)"
                                if signed
                                else "Diumumkan dalam siaran pers Setneg"
                            ),
                            "urutan_kesepakatan": len(rows) + 1,
                            "url_sumber": url,
                        }
                    )
    return rows


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.urls = [u.strip() for u in str(config.get("url") or DEFAULT_URL).split(",") if u.strip()]

    def extract(self) -> Iterator[Dict[str, Any]]:
        emitted = 0
        for url in self.urls:
            article = parse_article(self.http.get(url, timeout=60).text)
            for row in build_rows(article, url):
                emitted += 1
                yield row
        if emitted == 0:
            raise SourceUnavailable(f"No agreements recognised in Setneg article(s): {self.urls}")
