"""Excel Extractor for SIPRI Military Expenditure Database.

Downloads and parses the official SIPRI Milex Database Excel workbook:
https://www.sipri.org/sites/default/files/SIPRI-Milex-data-1949-2024.xlsx
Consolidates military expenditure in current USD million, percentage of GDP,
and share of government spending across global countries.
"""

from __future__ import annotations

import io
import logging
import os
from typing import Any, Dict, Iterator, List
import openpyxl
import requests

from .....core.base.extractor import BaseExtractor

logger = logging.getLogger(__name__)

DEFAULT_URL = "https://www.sipri.org/sites/default/files/SIPRI-Milex-data-1949-2024.xlsx"


class Extractor(BaseExtractor):
    """Excel extractor for SIPRI Military Expenditure database."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_URL)
        self.target_years = config.get("target_years", [2020, 2021, 2022, 2023, 2024])

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Download SIPRI Excel workbook and extract country records."""
        logger.info("Fetching SIPRI Military Expenditure workbook from %s", self.url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        try:
            resp = requests.get(self.url, headers=headers, timeout=40)
            resp.raise_for_status()
            content = resp.content
        except Exception as exc:
            logger.error("Failed to download SIPRI Milex workbook: %s", exc)
            return

        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        logger.info("Loaded SIPRI workbook with sheets: %s", wb.sheetnames)

        # 1. Parse Current US$
        ws_usd = wb["Current US$"]
        header_usd = [c.value for c in ws_usd[6]]
        year_indices_usd = {yr: header_usd.index(yr) for yr in self.target_years if yr in header_usd}

        # 2. Parse Share of GDP
        ws_gdp = wb["Share of GDP"]
        header_gdp = [c.value for c in ws_gdp[6]]
        year_indices_gdp = {yr: header_gdp.index(yr) for yr in self.target_years if yr in header_gdp}

        # 3. Parse Share of Govt. spending
        ws_govt = wb["Share of Govt. spending"]
        header_govt = [c.value for c in ws_govt[8]]
        year_indices_govt = {yr: header_govt.index(yr) for yr in self.target_years if yr in header_govt}

        country_data: Dict[tuple, Dict[str, Any]] = {}

        for r in range(7, ws_usd.max_row + 1):
            cname = ws_usd.cell(row=r, column=1).value
            if cname and isinstance(cname, str):
                cname = cname.strip()
                # Skip region headers
                if cname.lower() in ("africa", "americas", "asia & oceania", "europe", "middle east"):
                    continue

                for yr, col_idx in year_indices_usd.items():
                    val = ws_usd.cell(row=r, column=col_idx + 1).value
                    if val and val not in (". .", "xxx"):
                        key = (cname, yr)
                        country_data[key] = {
                            "country": cname,
                            "year": yr,
                            "expenditure_usd_million": val,
                            "gdp_pct": None,
                            "govt_pct": None,
                        }

        # Attach Share of GDP
        for r in range(7, ws_gdp.max_row + 1):
            cname = ws_gdp.cell(row=r, column=1).value
            if cname and isinstance(cname, str):
                cname = cname.strip()
                for yr, col_idx in year_indices_gdp.items():
                    key = (cname, yr)
                    if key in country_data:
                        country_data[key]["gdp_pct"] = ws_gdp.cell(row=r, column=col_idx + 1).value

        # Attach Share of Govt. spending
        for r in range(9, ws_govt.max_row + 1):
            cname = ws_govt.cell(row=r, column=1).value
            if cname and isinstance(cname, str):
                cname = cname.strip()
                for yr, col_idx in year_indices_govt.items():
                    key = (cname, yr)
                    if key in country_data:
                        country_data[key]["govt_pct"] = ws_govt.cell(row=r, column=col_idx + 1).value

        # Calculate annual rankings
        yearly_records: Dict[int, List[Dict[str, Any]]] = {}
        for (cname, yr), rec in country_data.items():
            yearly_records.setdefault(yr, []).append(rec)

        for yr, records in yearly_records.items():
            # Sort by expenditure descending
            records.sort(
                key=lambda x: float(x["expenditure_usd_million"]) if isinstance(x["expenditure_usd_million"], (int, float)) else 0.0,
                reverse=True
            )
            for rank_idx, r in enumerate(records, 1):
                r["rank"] = rank_idx

        # Yield flattened records
        logger.info("Yielding %d consolidated country-year records from SIPRI", len(country_data))
        for key in sorted(country_data.keys()):
            yield country_data[key]
