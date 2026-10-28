"""Shared reader for Satu Data Perdagangan "Total Ekspor Impor" (Kemendag).

https://satudata.kemendag.go.id/data-informasi/perdagangan-luar-negeri/ekspor-impor
serves server-rendered monthly tables (``#example`` = ekspor per sektor,
``#impor`` = impor per golongan, Juta US$). A year is selected by POSTing the
``period`` form field together with the CodeIgniter CSRF token/cookie.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple

from bs4 import BeautifulSoup

from ....core.base.http import HttpClient
from ....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://satudata.kemendag.go.id/data-informasi/perdagangan-luar-negeri/ekspor-impor"

MONTHS = {
    "januari": 1, "january": 1,
    "februari": 2, "february": 2,
    "maret": 3, "march": 3,
    "april": 4,
    "mei": 5, "may": 5,
    "juni": 6, "june": 6,
    "juli": 7, "july": 7,
    "agustus": 8, "august": 8,
    "september": 9,
    "oktober": 10, "october": 10,
    "november": 11,
    "desember": 12, "december": 12,
}

_CSRF_RE = re.compile(r'name="(csrf_[^"]+)"\s+value="([^"]+)"')


def parse_number(text: Any) -> Optional[float]:
    """``'26,612.18'`` -> 26612.18; ``'-'``/empty -> None."""
    value = str(text or "").replace("\xa0", " ").strip().replace(",", "").replace(" ", "")
    if value in ("", "-", "--", "n/a", "NA"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_years(value: Any, available: List[int]) -> List[int]:
    """Years to fetch: ``YEARS`` (``2023,2024`` / ``2020-2026``) or every year the portal offers."""
    text = str(value or "").strip()
    if not text:
        return sorted(available)
    years: List[int] = []
    for part in re.split(r"[;,]", text):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            years.extend(range(int(start), int(end) + 1))
        else:
            years.append(int(part))
    return sorted(y for y in set(years) if y in available)


def parse_year_options(html: str) -> List[int]:
    soup = BeautifulSoup(html, "html.parser")
    select = soup.find("select", id="choices-tahun") or soup.find("select", attrs={"name": "period"})
    if select is None:
        return []
    years = []
    for option in select.find_all("option"):
        value = (option.get("value") or option.get_text()).strip()
        if value.isdigit():
            years.append(int(value))
    return years


def parse_csrf(html: str) -> Optional[Tuple[str, str]]:
    match = _CSRF_RE.search(html)
    return (match.group(1), match.group(2)) if match else None


def parse_table(html: str, table_id: str, columns: Dict[str, str], year: int) -> List[Dict[str, Any]]:
    """Parse one monthly table into records.

    ``columns`` maps lower-cased header text -> dictionary field name. Raises
    ``SourceUnavailable`` when the table or an expected column is missing
    (layout change) so the run fails loudly instead of loading nothing.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id=table_id)
    if table is None:
        raise SourceUnavailable(f"Satu Data Kemendag: table #{table_id} not found (layout changed?)")
    headers = [th.get_text(" ", strip=True).lower() for th in table.find_all("th")]
    index = {}
    for field_header, field in columns.items():
        if field_header not in headers:
            raise SourceUnavailable(
                f"Satu Data Kemendag: column '{field_header}' missing in #{table_id} (headers: {headers})"
            )
        index[field] = headers.index(field_header)

    records = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(cells) < len(headers):
            continue
        month = MONTHS.get(cells[0].strip().lower())
        if not month:
            continue
        record: Dict[str, Any] = {"periode": f"{year:04d}-{month:02d}"}
        for field, idx in index.items():
            record[field] = parse_number(cells[idx])
        records.append(record)
    records.sort(key=lambda r: r["periode"])
    return records


class SatuDataSession:
    """Fetches the yearly pages (session cookie + CSRF handled)."""

    def __init__(self, http: HttpClient, url: str = DEFAULT_URL):
        self.http = http
        self.url = url
        self._csrf: Optional[Tuple[str, str]] = None

    def open(self) -> List[int]:
        html = self.http.get(self.url, timeout=45).text
        self._csrf = parse_csrf(html)
        years = parse_year_options(html)
        if not self._csrf or not years:
            raise SourceUnavailable(
                f"Satu Data Kemendag: form/CSRF token or year list not found on {self.url}"
            )
        return years

    def fetch_year(self, year: int) -> str:
        if not self._csrf:
            raise ConfigError("SatuDataSession.open() must be called first")
        name, token = self._csrf
        resp = self.http.post(self.url, data={name: token, "period": str(year)}, timeout=60)
        refreshed = parse_csrf(resp.text)
        if refreshed:
            self._csrf = refreshed
        return resp.text


def iter_records(
    http: HttpClient,
    url: str,
    years_config: Any,
    table_id: str,
    columns: Dict[str, str],
) -> Iterator[Dict[str, Any]]:
    session = SatuDataSession(http, url)
    available = session.open()
    years = parse_years(years_config, available)
    if not years:
        raise SourceUnavailable(f"Satu Data Kemendag: no requested year in available years {available}")
    total = 0
    for year in years:
        html = session.fetch_year(year)
        rows = parse_table(html, table_id, columns, year)
        logger.info("Satu Data Kemendag #%s %s: %d months", table_id, year, len(rows))
        for row in rows:
            total += 1
            yield row
    if total == 0:
        raise SourceUnavailable(f"Satu Data Kemendag #{table_id}: no monthly rows for years {years}")
