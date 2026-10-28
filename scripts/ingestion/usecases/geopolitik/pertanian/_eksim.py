"""Shared scraper for the Kementan Eksim portal (app3.pertanian.go.id/eksim).

The portal is a classic PHP form: the report page (``eksporHs.php`` /
``imporHs.php``) lists the selectable years and subsectors, and a POST to the
matching ``hasil*Hs.php`` returns one HTML table per commodity group with
Volume (Kg) and Nilai (US$) for each of the 12 months plus a Total.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ....core.base.extractor import BaseExtractor, is_truthy
from ....exceptions import ConfigError, SourceUnavailable

logger = logging.getLogger(__name__)

MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]
MIN_CELLS = 2 + 12 * 2 + 2  # HS, description, 12 x (volume, nilai), total x 2


def to_number(text: str) -> Optional[float]:
    cleaned = (text or "").replace(",", "").replace("\xa0", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_select_options(html: str, select_name: str) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    select = soup.find("select", attrs={"name": select_name})
    if select is None:
        return []
    return [
        (opt.get("value", "").strip(), opt.get_text(strip=True))
        for opt in select.find_all("option")
        if opt.get("value", "").strip()
    ]


def parse_years(value: Any, available: List[int]) -> List[int]:
    """``2024``, ``2022-2025`` or ``2022,2024``; empty -> every year the portal offers."""
    text = str(value or "").strip()
    if not text:
        return sorted(available)
    years: List[int] = []
    for part in re.split(r"[,;\s]+", text):
        if not part:
            continue
        match = re.fullmatch(r"(\d{4})\s*-\s*(\d{4})", part)
        if match:
            years.extend(range(int(match.group(1)), int(match.group(2)) + 1))
        elif part.isdigit():
            years.append(int(part))
        else:
            raise ConfigError(f"Invalid YEARS value: {part!r}")
    return sorted(set(years))


def parse_result_tables(
    html: str,
    *,
    tahun: int,
    arus: str,
    subsektor: str,
    include_zero: bool = False,
) -> List[Dict[str, Any]]:
    """Flatten the per-commodity-group tables into one record per HS code and month."""
    soup = BeautifulSoup(html, "html.parser")
    records: List[Dict[str, Any]] = []
    for header in soup.find_all("td", string=lambda s: s and s.strip() == "Kode HS"):
        table = header.find_parent("table")
        if table is None:
            continue
        title = table.find_previous("b")
        kelompok = title.get_text(strip=True) if title else None
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < MIN_CELLS:
                continue
            kode = cells[0].get_text(strip=True).lstrip("'").strip()
            if not kode or kode.lower() == "kode hs":
                continue
            deskripsi = cells[1].get_text(" ", strip=True)
            for index, bulan in enumerate(MONTHS):
                volume = to_number(cells[2 + index * 2].get_text())
                nilai = to_number(cells[3 + index * 2].get_text())
                if not include_zero and not volume and not nilai:
                    continue
                records.append(
                    {
                        "tahun": tahun,
                        "arus": arus,
                        "subsektor": subsektor,
                        "kelompok_komoditas": kelompok,
                        "kode_hs": kode,
                        "deskripsi_hs": deskripsi,
                        "nomor_bulan": index + 1,
                        "bulan": bulan,
                        "volume": volume,
                        "nilai": nilai,
                    }
                )
    return records


class EksimHsExtractor(BaseExtractor):
    ARUS = ""
    DEFAULT_URL = ""
    RESULT_PAGE = ""

    def _option(self, key: str) -> Any:
        """Read an extra option from the config, else from the ``PARAMS`` JSON object."""
        if self.config.get(key) not in (None, ""):
            return self.config[key]
        params = self.config.get("params")
        if isinstance(params, str) and params.strip():
            try:
                params = json.loads(params)
            except ValueError as exc:
                raise ConfigError(f"PARAMS must be a JSON object: {exc}") from exc
        if isinstance(params, dict):
            return params.get(key)
        return None

    def _text(self, resp: Any) -> str:
        return resp.content.decode("utf-8", errors="replace")

    def extract(self) -> Iterator[Dict[str, Any]]:
        form_url = self.url or self.DEFAULT_URL
        form_html = self._text(self.http.get(form_url, timeout=60))
        available = [
            int(value) for value, _ in parse_select_options(form_html, "prop") if value.isdigit()
        ]
        subsectors = parse_select_options(form_html, "subsektor")
        if not available or not subsectors:
            raise SourceUnavailable(f"Eksim form at {form_url} has no year/subsector options")

        years = parse_years(self.config.get("years"), available)
        wanted = {s.strip() for s in str(self._option("subsektor") or "").split(",") if s.strip()}
        if wanted:
            subsectors = [item for item in subsectors if item[0] in wanted]
        include_zero = is_truthy(self._option("include_zero"))
        result_url = urljoin(form_url, self.RESULT_PAGE)

        total = 0
        for year in years:
            if year not in available:
                logger.warning("Year %s not offered by %s, skipped", year, form_url)
                continue
            for sub_id, sub_name in subsectors:
                resp = self.http.post(
                    result_url,
                    data={
                        "prop": str(year),
                        "kab": "01",
                        "kec": "12",
                        "subsektor": sub_id,
                        "txtTahun": "",
                        "txtBulanAwal": "",
                        "txtBulanAkhir": "",
                        "txtSubsektor": "",
                        "txtKlasifik": "",
                    },
                    timeout=120,
                )
                rows = parse_result_tables(
                    self._text(resp),
                    tahun=year,
                    arus=self.ARUS,
                    subsektor=sub_name,
                    include_zero=include_zero,
                )
                logger.info("Eksim %s %s %s: %d rows", self.ARUS, year, sub_name, len(rows))
                total += len(rows)
                yield from rows
        if total == 0:
            raise SourceUnavailable(f"Eksim {self.ARUS} returned no rows for years {years}")
