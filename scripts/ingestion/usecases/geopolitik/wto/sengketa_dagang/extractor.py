"""Sengketa Dagang Indonesia: WTO dispute chronology (one row per dated milestone).

Each case page (``.../cases_e/dsNNN_e.htm``) carries a "Summary of the dispute to date"
narrative; every sentence that contains a date becomes one milestone row (undated
sentences are appended to the previous milestone).

Cases crawled: the case in ``URL`` plus Indonesia-related disputes discovered from the
WTO dispute catalogue (``dispute_case_arrays_e.js``: complainant or respondent = IDN,
consultations requested in or after ``SINCE_YEAR``, default 0 = every year). Set ``DS_NUMBERS``
(comma separated, e.g. ``592,593``) to crawl exactly those cases, or ``DISCOVER=false`` to
use only ``URL``. If discovery fails the crawl falls back to DS592 and DS593.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any, Dict, Iterator, List, Optional

from bs4 import BeautifulSoup

from .....config import get as env_get
from .....core.base.extractor import BaseExtractor, is_truthy
from .....exceptions import SourceUnavailable
from .config import PUBLISHER, SOURCE

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.wto.org/english/tratop_e/dispu_e/cases_e/ds593_e.htm"
CASE_URL = "https://www.wto.org/english/tratop_e/dispu_e/cases_e/ds{number}_e.htm"
CATALOGUE_URL = "https://www.wto.org/library/disputes/dispute_case_arrays_e.js"
FALLBACK_CASES = ("592", "593")
DEFAULT_SINCE_YEAR = 0
INDONESIA_CODE = "IDN"

MONTHS = {
    m: i
    for i, m in enumerate(
        ["january", "february", "march", "april", "may", "june", "july",
         "august", "september", "october", "november", "december"],
        start=1,
    )
}
DATE_RE = re.compile(r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{4})\b", re.IGNORECASE)
SENTENCE_SPLIT = re.compile(r"(?<=[.;])\s+(?=[A-Z])")
TEMPLATE_NOISE = ("dd Month", "goes here", "add following", "-->")


def squash(text: str) -> str:
    return " ".join((text or "").replace("\xa0", " ").split())


def parse_date(text: str) -> Optional[date]:
    match = DATE_RE.search(text)
    if not match:
        return None
    try:
        return date(int(match.group(3)), MONTHS[match.group(2).lower()], int(match.group(1)))
    except ValueError:
        return None


def parse_catalogue(js_text: str, since_year: int = DEFAULT_SINCE_YEAR) -> List[str]:
    """DS numbers where Indonesia is complainant or respondent (consultations >= since_year)."""
    numbers: List[str] = []
    for match in re.finditer(r"ds_array\[(\d+)\]\s*=\s*\{(.*?)\n\};", js_text, re.S):
        body = match.group(2)

        def field(name: str) -> str:
            found = re.search(name + r':\s*"(.*?)"', body)
            return found.group(1) if found else ""

        parties = field("origin").split("#") + field("destination").split("#")
        year = field("start_date")[:4]
        if INDONESIA_CODE in parties and year.isdigit() and int(year) >= since_year:
            numbers.append(match.group(1))
    return sorted(numbers, key=int)


def parse_case_page(html: str, url: str) -> List[Dict[str, Any]]:
    """Parse one WTO dispute page into milestone rows."""
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    if soup.title and soup.title.string:
        title = squash(soup.title.string)
    match = re.search(r"(DS\d+)\s*:\s*(.+)$", title)
    if match:
        nomor, isu = match.group(1), match.group(2)
    else:
        # older pages: <title> only holds "DSnnn"; the case name sits in an "DS: <name>" heading
        number = re.search(r"DS\d+", title) or re.search(r"/(ds\d+)_e", url, re.IGNORECASE)
        name = next(
            (
                squash(h.get_text(" "))
                for h in soup.find_all(["h1", "h2"])
                if re.match(r"^DS\d*\s*:?\s*\S+.*—", squash(h.get_text(" ")))
            ),
            None,
        )
        if not number or not name:
            raise SourceUnavailable(f"WTO dispute page has no 'DSnnn: title' header: {url}")
        nomor = number.group(0).upper()
        isu = re.sub(r"^DS\d*\s*:?\s*", "", name)
    isu = squash(isu.replace("—", "-"))

    heading = soup.find(id="summary")
    if heading is None:
        raise SourceUnavailable(f"WTO dispute page has no summary section: {url}")

    milestones: List[Dict[str, Any]] = []
    for node in heading.find_all_next(["h2", "p", "li"]):
        if node.name == "h2":
            break
        if node.find_parent(class_="panel-group") is not None:
            continue
        for sentence in SENTENCE_SPLIT.split(squash(node.get_text(" "))):
            if not sentence or any(noise in sentence for noise in TEMPLATE_NOISE):
                continue
            when = parse_date(sentence)
            if when is not None:
                milestones.append({"date": when, "text": sentence})
            elif milestones:
                milestones[-1]["text"] += " " + sentence

    rows: List[Dict[str, Any]] = []
    seen = set()
    for item in milestones:
        key = (item["date"], item["text"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "nomor_sengketa": nomor,
                "isu": isu,
                "tanggal_tahapan": item["date"].isoformat(),
                "tahapan": item["text"],
                "urutan_tahapan": len(rows) + 1,
                "url_kasus": url,
            }
        )
    return rows


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url") or DEFAULT_URL

    def _opt(self, key: str, default: Any = None) -> Any:
        value = self.config.get(key.lower())
        if value in (None, ""):
            value = env_get(self.config.get("usecase", "geopolitik"), PUBLISHER, SOURCE, key.upper())
        return default if value in (None, "") else value

    def _get_text(self, url: str) -> str:
        resp = self.http.get(url, timeout=60)
        return resp.content.decode("cp1252", errors="replace")

    def case_urls(self) -> List[str]:
        explicit = self._opt("ds_numbers")
        if explicit:
            numbers = [n.strip().lower().lstrip("ds") for n in str(explicit).split(",") if n.strip()]
            return [CASE_URL.format(number=n) for n in numbers]

        urls = [self.url]
        if is_truthy(self._opt("discover", "true")):
            try:
                found = parse_catalogue(
                    self._get_text(CATALOGUE_URL), int(self._opt("since_year", DEFAULT_SINCE_YEAR))
                )
            except SourceUnavailable as exc:
                logger.warning("WTO dispute catalogue unavailable (%s); using DS592/DS593", exc)
                found = list(FALLBACK_CASES)
            urls += [CASE_URL.format(number=n) for n in found]
        return list(dict.fromkeys(urls))

    def extract(self) -> Iterator[Dict[str, Any]]:
        emitted = 0
        failures: List[str] = []
        for url in self.case_urls():
            try:
                rows = parse_case_page(self._get_text(url), url)
            except SourceUnavailable as exc:
                logger.warning("Skipping WTO case %s: %s", url, exc)
                failures.append(url)
                continue
            for row in rows:
                emitted += 1
                yield row
        if emitted == 0:
            raise SourceUnavailable(f"No WTO dispute milestones could be extracted (failed: {failures})")
