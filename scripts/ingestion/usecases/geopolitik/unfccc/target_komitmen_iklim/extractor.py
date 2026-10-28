"""Target Komitmen Iklim (UNFCCC): quantitative indicators of Indonesia's Second NDC (PDF).

Table 1 of the NDC (reference point and projected emission per sector) is an image,
so only figures written in the running text are extracted, with a rule per
sentence pattern (``RULES``). Each rule is matched page by page so ``halaman_pdf``
is the PDF page holding the evidence; identical facts repeated on several pages are
kept once (first page). If a re-issued NDC rewords these sentences the affected
rules simply stop matching; if no rule matches at all the run fails loudly.

UNFCCC sits behind Incapsula: the default request profile is ``impersonate=chrome``
(curl_cffi). The register page (``unfccc.int/NDCREG``) is a JavaScript challenge and
cannot be crawled, so ``URL`` is the NDC PDF itself (or ``SOURCE_FILE``).
"""

from __future__ import annotations

import io
import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urljoin, urlsplit

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://unfccc.int/sites/default/files/2025-10/Indonesia_Second%20NDC_2025.10.24.pdf"
DEFAULT_IMPERSONATE = "chrome"

GG = "Gg CO2e"
NUM = r"[\d][\d.,]*"

# (indikator, skenario, tahun, nilai_bawah, nilai_atas, satuan)
Fact = Tuple[str, str, Optional[int], float, float, str]


def squash(text: str) -> str:
    return " ".join((text or "").split())


def normalize(text: str) -> str:
    """Undo pypdf spacing artifacts ("Gg CO 2e", "LCCP _H", "6. 0%")."""
    text = squash(text)
    text = re.sub(r"Gg ?CO ?2 ?e", GG, text)
    text = re.sub(r"Mt ?CO ?2 ?e", "MtCO2e", text)
    text = re.sub(r"(LCCP) _([LH])", r"\1_\2", text)
    text = re.sub(r"(\d) %", r"\1%", text)
    text = re.sub(r"(\d)\. (\d+(?:\.\d+)?%)", r"\1.\2", text)
    return text


def parse_number(raw: str) -> float:
    """``1,345,707`` -> 1345707, ``55,5`` -> 55.5, ``17.5`` -> 17.5."""
    text = raw.strip().rstrip(".,")
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", text):
        return float(text.replace(",", ""))
    return float(text.replace(",", "."))


def single(indicator: str, scenario: str, year: Optional[int], value: str, unit: str) -> Fact:
    number = parse_number(value)
    return (indicator, scenario, year, number, number, unit)


def _ref_level(m: "re.Match[str]") -> List[Fact]:
    year = int(m.group("y"))
    return [single("Emisi GHG bersih tahun referensi (inventori)", f"Tahun referensi {year}", year, m.group("v"), GG)]


def _lccp_peak(m: "re.Match[str]") -> List[Fact]:
    year = int(m.group("y"))
    label = "Proyeksi emisi GHG nasional (puncak emisi)"
    return [
        single(label, "LCCP_L", year, m.group("l"), GG),
        single(label, "LCCP_H", year, m.group("h"), GG),
    ]


def _lccp_decline(m: "re.Match[str]") -> List[Fact]:
    year = int(m.group("y"))
    label = "Proyeksi emisi GHG nasional"
    return [
        single(label, "LCCP_L", year, m.group("l"), GG),
        single(label, "LCCP_H", year, m.group("h"), GG),
    ]


def _cm2_comparison(m: "re.Match[str]") -> List[Fact]:
    year = int(m.group("y"))
    return [
        single("Proyeksi emisi GHG nasional", "ENDC CM2", year, m.group("v"), GG),
        (
            "Emisi LCCP lebih rendah dibanding ENDC CM2",
            "LCCP_L dan LCCP_H vs ENDC CM2",
            year,
            parse_number(m.group("a")),
            parse_number(m.group("b")),
            "%",
        ),
    ]


def _above_reference(m: "re.Match[str]") -> List[Fact]:
    year = int(m.group("y"))
    label = "Level emisi relatif terhadap emisi tahun referensi 2019"
    unit = "% di atas tahun referensi"
    return [
        single(label, "CPOS", year, m.group("c"), unit),
        single(label, "LCCP_L", year, m.group("l"), unit),
        single(label, "LCCP_H", year, m.group("h"), unit),
    ]


def _growth(scenario: str) -> Callable[["re.Match[str]"], List[Fact]]:
    def build(m: "re.Match[str]") -> List[Fact]:
        label = "Asumsi pertumbuhan ekonomi"
        return [
            single(label, scenario, int(m.group("y1")), m.group("a"), "%"),
            single(label, scenario, int(m.group("y2")), m.group("b"), "%"),
        ]

    return build


def _lts(m: "re.Match[str]") -> List[Fact]:
    scenario = "LCCP (LTS-LCCR 2050, kompatibel 1,5 C)"
    return [
        single("Emisi GHG puncak (jalur jangka panjang)", scenario, int(m.group("y1")), m.group("peak"), "MtCO2e"),
        single("Emisi GHG jalur jangka panjang", scenario, int(m.group("y2")), m.group("end"), "MtCO2e"),
    ]


def _net_zero(m: "re.Match[str]") -> List[Fact]:
    year = int(m.group("y"))
    return [("Target net zero emission (tahun)", "LCCP", year, float(year), float(year), "tahun")]


def _endc(m: "re.Match[str]") -> List[Fact]:
    year = int(m.group("y"))
    label = "Target penurunan emisi terhadap BAU"
    return [
        single(label, "ENDC tanpa syarat (unconditional)", year, m.group("u"), "%"),
        single(label, "ENDC bersyarat (conditional)", year, m.group("c"), "%"),
    ]


def _first_ndc(m: "re.Match[str]") -> List[Fact]:
    label = "Target penurunan emisi terhadap BAU"
    return [
        single(label, "First NDC/Intended NDC tanpa syarat (unconditional)", 2030, m.group("u"), "%"),
        single(label, "First NDC/Intended NDC bersyarat (conditional)", 2030, m.group("c"), "%"),
    ]


def _finance(m: "re.Match[str]") -> List[Fact]:
    year = int(m.group("e"))
    label = f"Kebutuhan pendanaan mitigasi {m.group('s')}-{m.group('e')}"
    return [
        single(label, "Bersyarat (conditional), Third BUR", year, m.group("c"), "USD miliar"),
        single(label, "Tanpa syarat (unconditional), Third BUR", year, m.group("u"), "USD miliar"),
    ]


def _investment(m: "re.Match[str]") -> List[Fact]:
    return [single("Estimasi total investasi untuk mencapai Second NDC", "Second NDC", None, m.group("v"), "USD miliar")]


I = re.IGNORECASE
RULES: List[Tuple["re.Pattern[str]", Callable[["re.Match[str]"], List[Fact]]]] = [
    (re.compile(rf"Level of Emission (?P<y>20\d\d) ?\d? ?: ?(?P<v>{NUM}) {GG}"), _ref_level),
    (
        re.compile(
            rf"peak emissions by (?P<y>\d{{4}}), with estimated emission levels of (?P<l>{NUM}) {GG} "
            rf"under the LCCP_L scenario and (?P<h>{NUM}) {GG} under the LCCP_H scenario"
        ),
        _lccp_peak,
    ),
    (
        re.compile(
            rf"decline in (?P<y>\d{{4}}) with the projection of GHG emission levels reaching "
            rf"(?P<l>{NUM}) {GG} under LCCP_L and (?P<h>{NUM}) {GG} under LCCP_H"
        ),
        _lccp_decline,
    ),
    (
        re.compile(
            rf"projects emissions of (?P<v>{NUM}) {GG} in (?P<y>\d{{4}}), Indonesia's emissions are "
            rf"expected to be (?P<a>[\d.]+) ?- ?(?P<b>[\d.]+)% lower"
        ),
        _cm2_comparison,
    ),
    (
        re.compile(
            rf"In (?P<y>\d{{4}}),? (?:the )?level of emission under CPOS will be (?P<c>{NUM})% above the "
            rf"reference (?:emission|year),? (?:and )?under LCCP_L,? and LCCP_H (?:emission level )?will be "
            rf"(?P<l>{NUM})% and (?P<h>{NUM})% above the reference year"
        ),
        _above_reference,
    ),
    (
        re.compile(
            rf"CPOS and LCCP_L scenarios apply economic growth of (?P<a>{NUM})% in (?P<y1>\d{{4}}) and "
            rf"(?P<b>{NUM})% in (?P<y2>\d{{4}})"
        ),
        _growth("CPOS dan LCCP_L"),
    ),
    (
        re.compile(
            rf"LCCP_H scenario applies higher economic growth assumption of (?P<a>{NUM})% in "
            rf"(?P<y1>\d{{4}}) and (?P<b>{NUM})% in (?P<y2>\d{{4}})"
        ),
        _growth("LCCP_H"),
    ),
    (
        re.compile(
            rf"\(LCCP\), greenhouse gas emissions will peak in (?P<y1>\d{{4}}) at (?P<peak>{NUM}) MtCO2e and then "
            rf"decline and continue to decline to reach (?P<end>{NUM}) MtCO2e in (?P<y2>\d{{4}})"
        ),
        _lts,
    ),
    (re.compile(r"net-zero emissions? in (?P<y>20\d\d) or sooner", I), _net_zero),
    (
        re.compile(
            rf"unconditional target to (?P<u>{NUM})% and conditional target to (?P<c>{NUM})% against "
            rf"Business as Usual in (?P<y>\d{{4}})"
        ),
        _endc,
    ),
    (
        re.compile(
            rf"emissions reduction of (?P<u>{NUM})% through domestic efforts \(unconditional\) and up to "
            rf"(?P<c>{NUM})% with international support \(conditional\)"
        ),
        _first_ndc,
    ),
    (
        re.compile(
            rf"will require USD (?P<c>{NUM}) billion for conditional and USD (?P<u>{NUM}) billion for "
            rf"unconditional targets between (?P<s>\d{{4}}) and (?P<e>\d{{4}})"
        ),
        _finance,
    ),
    (re.compile(rf"estimated total investment of USD (?P<v>{NUM}) billion"), _investment),
]


def extract_facts(pages: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    for page_number, raw in enumerate(pages, start=1):
        text = normalize(raw)
        for pattern, build in RULES:
            for match in pattern.finditer(text):
                for indicator, scenario, year, low, high, unit in build(match):
                    key = (indicator, scenario, year, low, high)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(
                        {
                            "indikator": indicator,
                            "skenario_konteks": scenario,
                            "tahun_target": year,
                            "nilai_bawah": low,
                            "nilai_atas": high,
                            "satuan": unit,
                            "halaman_pdf": page_number,
                        }
                    )
    return rows


def pdf_pages(content: bytes) -> List[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("pypdf is required for target_komitmen_iklim (pip install pypdf)") from exc
    try:
        return [(page.extract_text() or "") for page in PdfReader(io.BytesIO(content)).pages]
    except Exception as exc:
        raise SourceUnavailable(f"Could not read the NDC PDF: {exc}") from exc


def find_ndc_links(html: str, base_url: str) -> List[str]:
    from bs4 import BeautifulSoup

    links: List[str] = []
    for anchor in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        href = anchor["href"]
        label = f"{anchor.get_text(' ')} {href}".lower()
        if href.lower().split("?")[0].endswith(".pdf") and "indonesia" in label and "ndc" in label:
            links.append(urljoin(base_url, href))
    return links


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        config = dict(config)
        if not config.get("impersonate"):
            config["impersonate"] = DEFAULT_IMPERSONATE
        super().__init__(config)

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
            links = find_ndc_links(html, url)
            if not links:
                raise SourceUnavailable(
                    f"No Indonesia NDC PDF link found on {url} (register page is a JavaScript challenge); "
                    "set URL to the NDC PDF or SOURCE_FILE"
                )
            url = links[0]
        content = self.http.get(url, timeout=180).content
        if not content.startswith(b"%PDF"):
            raise SourceUnavailable(f"{url} did not return a PDF (bot protection?)")
        return content

    def extract(self) -> Iterator[Dict[str, Any]]:
        rows = extract_facts(pdf_pages(self._load_pdf()))
        if not rows:
            raise SourceUnavailable("No quantitative NDC indicators matched in the PDF text")
        logger.info("Second NDC: %d indicators", len(rows))
        yield from rows
