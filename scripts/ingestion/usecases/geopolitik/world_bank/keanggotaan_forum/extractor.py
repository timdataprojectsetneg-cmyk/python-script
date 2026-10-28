"""Keanggotaan Forum (World Bank): Indonesia's membership in the World Bank Group.

``worldbank.org/en/about/leadership/members`` is static HTML with one table per
organisation (IBRD, IDA, IFC, MIGA, ICSID); each cell is ``<b>Country</b>, Mon D, YYYY``.
The organisation name sits in the line above each "N countries" caption. One record
is emitted per organisation for the configured country (``COUNTRY``, default Indonesia).
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from bs4 import BeautifulSoup

from .....core.base.extractor import BaseExtractor
from .....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.worldbank.org/en/about/leadership/members"
DEFAULT_COUNTRY = "Indonesia"
COUNT_CAPTION = re.compile(r"^\d+\s+countries$", re.IGNORECASE)


def squash(text: str) -> str:
    return " ".join((text or "").split())


def parse_membership_date(raw: str) -> Optional[str]:
    """``Apr 13, 1967`` -> ``1967-04-13``."""
    text = squash(raw).strip(" ,")
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def organisation_names(soup: BeautifulSoup, tables: List[Any]) -> List[str]:
    """Organisation heading preceding each table (text above the 'N countries' caption)."""
    names: List[str] = []
    for table in tables:
        caption = table.find_previous(string=lambda s: s and COUNT_CAPTION.match(squash(s)))
        heading = None
        if caption is not None:
            heading = caption.find_previous(
                string=lambda s: s and squash(s) and not COUNT_CAPTION.match(squash(s))
            )
        names.append(squash(heading) if heading else "")
    return names


def parse_members(html: str) -> List[Tuple[str, Dict[str, str]]]:
    """[(organisation name, {country: raw date})] for every member table on the page."""
    soup = BeautifulSoup(html, "html.parser")
    tables = [t for t in soup.find_all("table") if "Date of Membership" in t.get_text()]
    result: List[Tuple[str, Dict[str, str]]] = []
    for name, table in zip(organisation_names(soup, tables), tables):
        members: Dict[str, str] = {}
        for cell in table.find_all("td"):
            bold = cell.find("b")
            if bold is None or "Date of Membership" in bold.get_text():
                continue
            country = squash(bold.get_text())
            remainder = squash(cell.get_text(" ")).replace(country, "", 1)
            members[country] = squash(remainder).lstrip(", ").strip()
        result.append((name, members))
    return result


def build_records(html: str, country: str, url: str) -> List[Dict[str, Any]]:
    wanted = country.strip().lower()
    records: List[Dict[str, Any]] = []
    for name, members in parse_members(html):
        for member, raw_date in members.items():
            if member.lower() != wanted:
                continue
            records.append(
                {
                    "organisasi_forum": name,
                    "status_peran": "Member",
                    "tanggal_tahun_periode": parse_membership_date(raw_date) or raw_date or None,
                    "keterangan_periode": "Date of Membership pada daftar anggota resmi World Bank Group",
                    "url_sumber": url,
                    "negara": member,
                }
            )
    return records


class Extractor(BaseExtractor):
    def _load_html(self, url: str) -> str:
        local = (self.config.get("source_file") or "").strip()
        if local:
            path = Path(local)
            if not path.is_file():
                raise ConfigError(f"SOURCE_FILE not found: {local}")
            return path.read_text(encoding="utf-8", errors="replace")
        return self.http.get(url, timeout=60).content.decode("utf-8", errors="replace")

    def extract(self) -> Iterator[Dict[str, Any]]:
        url = (self.config.get("url") or DEFAULT_URL).strip()
        country = (self.config.get("country") or DEFAULT_COUNTRY).strip()
        records = build_records(self._load_html(url), country, url)
        if not records:
            raise SourceUnavailable(f"No World Bank Group membership rows for {country} on {url}")
        logger.info("World Bank membership %s: %d organisations", country, len(records))
        yield from records
