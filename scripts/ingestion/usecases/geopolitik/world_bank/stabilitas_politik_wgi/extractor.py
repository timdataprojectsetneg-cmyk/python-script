"""Extractor for the World Bank Worldwide Governance Indicators (Political Stability).

Downloads the indicator's CSV bulk archive (same data and Metadata_Country as the
Excel download, but readable without legacy .xls support) and melts the year columns.
Aggregates (regions / income groups, blank Region in the metadata) are dropped unless
``include_aggregates`` is enabled.
"""

from __future__ import annotations

import csv
import io
import logging
import zipfile
from typing import Any, Dict, Iterator, List

from .....core.base.extractor import BaseExtractor, is_truthy
from .....exceptions import SourceUnavailable

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://api.worldbank.org/v2/en/indicator/GOV_WGI_PV.EST?downloadformat=csv"


def _read_csv(zf: zipfile.ZipFile, name: str) -> List[List[str]]:
    text = zf.read(name).decode("utf-8-sig")
    return [row for row in csv.reader(io.StringIO(text, newline="")) if any(cell.strip() for cell in row)]


def _find(zf: zipfile.ZipFile, prefix: str) -> str:
    for name in zf.namelist():
        if name.startswith(prefix):
            return name
    raise SourceUnavailable(f"'{prefix}*' not found in WGI archive: {zf.namelist()}")


def parse_archive(content: bytes, include_aggregates: bool = False) -> Iterator[Dict[str, Any]]:
    try:
        zf = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise SourceUnavailable("WGI download is not a zip archive") from exc

    meta_rows = _read_csv(zf, _find(zf, "Metadata_Country_"))
    meta_header = meta_rows[0]
    meta: Dict[str, Dict[str, str]] = {
        r[0]: dict(zip(meta_header, r)) for r in meta_rows[1:] if r and r[0]
    }

    rows = _read_csv(zf, _find(zf, "API_"))
    header_idx = next((i for i, r in enumerate(rows) if r and r[0] == "Country Name"), None)
    if header_idx is None:
        raise SourceUnavailable("WGI data file has no 'Country Name' header row")
    header = rows[header_idx]
    year_cols = [(i, int(c)) for i, c in enumerate(header) if c.strip().isdigit() and len(c.strip()) == 4]

    for row in rows[header_idx + 1:]:
        rec = dict(zip(header, row))
        code = rec.get("Country Code", "").strip()
        info = meta.get(code, {})
        region = (info.get("Region") or "").strip()
        if not region and not include_aggregates:
            continue
        for idx, year in year_cols:
            raw = row[idx].strip() if idx < len(row) else ""
            if not raw:
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            yield {
                "Country Name": rec.get("Country Name", "").strip(),
                "Country Code": code,
                "Indicator Name": rec.get("Indicator Name"),
                "Indicator Code": rec.get("Indicator Code"),
                "year": year,
                "value": value,
                "Region": region or None,
                "IncomeGroup": (info.get("IncomeGroup") or "").strip() or None,
            }


class Extractor(BaseExtractor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url") or DEFAULT_URL
        self.timeout = int(config.get("timeout") or 120)
        self.include_aggregates = is_truthy(config.get("include_aggregates", "false"))

    def extract(self) -> Iterator[Dict[str, Any]]:
        content = self.http.get(self.url, timeout=self.timeout).content
        yield from parse_archive(content, self.include_aggregates)
