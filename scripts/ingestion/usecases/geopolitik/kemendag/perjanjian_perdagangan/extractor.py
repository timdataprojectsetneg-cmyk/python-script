"""Extractor for the list of Indonesian trade agreements in force (FTA Support Center, Kemendag)."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterator, List, Optional
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from .....core.base.extractor import BaseExtractor
from .....exceptions import SourceUnavailable

DEFAULT_URL = "https://ftasupportcenter.kemendag.go.id/sekilas-tentang-fta"
AGREEMENT_HOST = "ftacenter.kemendag.go.id"
NON_AGREEMENT_PATHS = {"", "/", "/tentang", "/kontak", "/layanan-konsultasi", "/layanan-informasi", "/faq"}

_MONTHS = "Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember"
_STATUS_RE = re.compile(r"\(\s*per\s+((?:" + _MONTHS + r")\s+\d{4})\s*\)", re.IGNORECASE)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def parse_status(text: str) -> Optional[str]:
    """``'... (per Juni 2025).'`` -> ``'Berlaku menurut daftar per Juni 2025'``; None when absent."""
    match = _STATUS_RE.search(_clean(text))
    return f"Berlaku menurut daftar per {match.group(1)}" if match else None


def _is_agreement_link(href: str) -> bool:
    parts = urlsplit(href)
    return parts.netloc == AGREEMENT_HOST and parts.path.rstrip("/") not in NON_AGREEMENT_PATHS


def _agreement_scope(soup: BeautifulSoup):
    """Smallest block that holds the status sentence and the agreement links."""
    marker = soup.find(string=re.compile(r"Di bawah ini adalah negara", re.IGNORECASE))
    node = marker.parent if marker else None
    while node is not None:
        if sum(1 for a in node.find_all("a", href=True) if _is_agreement_link(a["href"])) >= 3:
            return node
        node = node.parent
    return soup


def parse_agreements(html: str, base_url: str = DEFAULT_URL) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    scope = _agreement_scope(soup)
    status = parse_status(scope.get_text(" ")) or parse_status(soup.get_text(" "))

    names: Dict[str, str] = {}
    for anchor in scope.find_all("a", href=True):
        href = urljoin(base_url, anchor["href"].strip())
        if not _is_agreement_link(href):
            continue
        text = _clean(anchor.get_text(" "))
        if not text:
            continue
        current = names.get(href)
        if current is None:
            names[href] = text
        elif text not in current:
            names[href] = f"{current} {text}"

    return [
        {"nama_perjanjian": name, "status_menurut_sumber": status, "tautan_detail": href}
        for href, name in names.items()
    ]


class Extractor(BaseExtractor):
    """One record per agreement link on the FTA Support Center overview page."""

    def extract(self) -> Iterator[Dict[str, Any]]:
        url = self.config.get("url") or DEFAULT_URL
        html = self.http.get(url, timeout=45).text
        records = parse_agreements(html, url)
        if not records:
            raise SourceUnavailable(f"FTA Center: no agreement links found on {url} (layout changed?)")
        yield from records
