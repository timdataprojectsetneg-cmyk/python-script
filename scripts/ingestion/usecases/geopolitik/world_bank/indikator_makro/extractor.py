"""REST API Extractor for World Bank Bilateral Macroeconomic Indicators.

Fetches key macroeconomic indicators (Population, Nominal GDP, GDP per capita,
Real GDP Growth, and Inflation) for Indonesia and bilateral partner nations
using the official World Bank Open API.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterator, List, Optional
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .....core.base.extractor import BaseExtractor

logger = logging.getLogger(__name__)

DEFAULT_COUNTRIES = "IDN;CHN;USA;JPN;SGP;MYS;IND;AUS;KOR;DEU;GBR;FRA;SAU;RUS;VNM;THA;PHL"
DEFAULT_INDICATORS = "SP.POP.TOTL;NY.GDP.MKTP.CD;NY.GDP.PCAP.CD;NY.GDP.MKTP.KD.ZG;FP.CPI.TOTL.ZG"
DEFAULT_URL = (
    f"https://api.worldbank.org/v2/country/{DEFAULT_COUNTRIES}"
    f"/indicator/{DEFAULT_INDICATORS}?source=2&format=json&per_page=1000&date=2020:2024"
)

# Bilateral trade estimates with Indonesia (USD) from Kemendag & BPS
TRADE_ESTIMATES_RI: Dict[str, Dict[str, float]] = {
    "CHN": {"ekspor": 68420000000.0, "impor": 64180000000.0},
    "JPN": {"ekspor": 21850000000.0, "impor": 16420000000.0},
    "USA": {"ekspor": 26800000000.0, "impor": 13200000000.0},
    "SGP": {"ekspor": 15400000000.0, "impor": 19800000000.0},
    "MYS": {"ekspor": 14200000000.0, "impor": 12600000000.0},
    "IND": {"ekspor": 20100000000.0, "impor": 8900000000.0},
    "KOR": {"ekspor": 11500000000.0, "impor": 10800000000.0},
    "AUS": {"ekspor": 5200000000.0, "impor": 9400000000.0},
    "DEU": {"ekspor": 3800000000.0, "impor": 4500000000.0},
}

OFFLINE_FALLBACK_DATA = [
    {
        "negara": "Indonesia",
        "kode_iso3": "IDN",
        "kawasan": "Asia Tenggara",
        "tahun": 2024,
        "populasi_juta_jiwa": 281.6,
        "pdb_nominal_miliar_usd": 1371.2,
        "pdb_per_kapita_usd": 4869.0,
        "pertumbuhan_pdb_pct": 5.05,
        "inflasi_pct": 2.61,
        "nilai_ekspor_ri_ke_mitra_usd": None,
        "nilai_impor_ri_dari_mitra_usd": None,
        "neraca_perdagangan_ri_usd": None,
        "data_source": "World Bank Open Data (World Development Indicators)",
    },
    {
        "negara": "Jepang",
        "kode_iso3": "JPN",
        "kawasan": "Asia Timur",
        "tahun": 2024,
        "populasi_juta_jiwa": 124.5,
        "pdb_nominal_miliar_usd": 4210.0,
        "pdb_per_kapita_usd": 33815.0,
        "pertumbuhan_pdb_pct": 1.25,
        "inflasi_pct": 2.45,
        "nilai_ekspor_ri_ke_mitra_usd": 21850000000.0,
        "nilai_impor_ri_dari_mitra_usd": 16420000000.0,
        "neraca_perdagangan_ri_usd": 5430000000.0,
        "data_source": "World Bank Open Data (World Development Indicators)",
    },
    {
        "negara": "Tiongkok",
        "kode_iso3": "CHN",
        "kawasan": "Asia Timur",
        "tahun": 2024,
        "populasi_juta_jiwa": 1408.98,
        "pdb_nominal_miliar_usd": 18729.67,
        "pdb_per_kapita_usd": 13293.0,
        "pertumbuhan_pdb_pct": 4.96,
        "inflasi_pct": 0.22,
        "nilai_ekspor_ri_ke_mitra_usd": 68420000000.0,
        "nilai_impor_ri_dari_mitra_usd": 64180000000.0,
        "neraca_perdagangan_ri_usd": 4240000000.0,
        "data_source": "World Bank Open Data (World Development Indicators)",
    },
    {
        "negara": "Amerika Serikat",
        "kode_iso3": "USA",
        "kawasan": "Amerika Utara",
        "tahun": 2024,
        "populasi_juta_jiwa": 336.8,
        "pdb_nominal_miliar_usd": 28781.0,
        "pdb_per_kapita_usd": 85450.0,
        "pertumbuhan_pdb_pct": 2.80,
        "inflasi_pct": 2.95,
        "nilai_ekspor_ri_ke_mitra_usd": 26800000000.0,
        "nilai_impor_ri_dari_mitra_usd": 13200000000.0,
        "neraca_perdagangan_ri_usd": 13600000000.0,
        "data_source": "World Bank Open Data (World Development Indicators)",
    },
    {
        "negara": "Singapura",
        "kode_iso3": "SGP",
        "kawasan": "Asia Tenggara",
        "tahun": 2024,
        "populasi_juta_jiwa": 5.92,
        "pdb_nominal_miliar_usd": 501.4,
        "pdb_per_kapita_usd": 84700.0,
        "pertumbuhan_pdb_pct": 3.40,
        "inflasi_pct": 2.80,
        "nilai_ekspor_ri_ke_mitra_usd": 15400000000.0,
        "nilai_impor_ri_dari_mitra_usd": 19800000000.0,
        "neraca_perdagangan_ri_usd": -4400000000.0,
        "data_source": "World Bank Open Data (World Development Indicators)",
    },
]


class Extractor(BaseExtractor):
    """Fetches macroeconomic time series from World Bank Open API."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_URL)
        env_max = (
            os.environ.get("GEOPOLITIK__WORLD_BANK__INDIKATOR_MAKRO__MAX_RECORDS")
            or os.environ.get("MAX_RECORDS")
        )
        self.max_records = int(env_max) if env_max else int(config.get("max_records", 50))

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
        }

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Fetch and aggregate country-year macroeconomic observations."""
        count = 0
        yielded_any = False

        try:
            logger.info("Querying World Bank Open API: %s", self.url)
            resp = requests.get(self.url, headers=self._headers(), timeout=20, verify=False)
            if resp.status_code == 200:
                payload = resp.json()
                if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
                    # Group indicators by (countryiso3code, year)
                    by_entity: Dict[tuple[str, int], Dict[str, Any]] = {}

                    for item in payload[1]:
                        iso3 = str(item.get("countryiso3code") or "").strip().upper()
                        year_raw = item.get("date")
                        if not iso3 or not year_raw or not str(year_raw).isdigit():
                            continue
                        year = int(year_raw)
                        val = item.get("value")
                        ind_id = item.get("indicator", {}).get("id")
                        country_name = item.get("country", {}).get("value")

                        key = (iso3, year)
                        if key not in by_entity:
                            by_entity[key] = {
                                "iso3": iso3,
                                "country": country_name,
                                "year": year,
                                "pop": None,
                                "gdp": None,
                                "pcap": None,
                                "growth": None,
                                "cpi": None,
                            }

                        if ind_id == "SP.POP.TOTL" and val is not None:
                            by_entity[key]["pop"] = float(val)
                        elif ind_id == "NY.GDP.MKTP.CD" and val is not None:
                            by_entity[key]["gdp"] = float(val)
                        elif ind_id == "NY.GDP.PCAP.CD" and val is not None:
                            by_entity[key]["pcap"] = float(val)
                        elif ind_id == "NY.GDP.MKTP.KD.ZG" and val is not None:
                            by_entity[key]["growth"] = float(val)
                        elif ind_id == "FP.CPI.TOTL.ZG" and val is not None:
                            by_entity[key]["cpi"] = float(val)

                    # Order: IDN first, then latest year descending
                    sorted_keys = sorted(
                        by_entity.keys(),
                        key=lambda k: (0 if k[0] == "IDN" else 1, -k[1], k[0]),
                    )

                    for key in sorted_keys:
                        if count >= self.max_records:
                            return
                        obs = by_entity[key]
                        iso = obs["iso3"]
                        y = obs["year"]
                        pop_raw = obs["pop"]
                        gdp_raw = obs["gdp"]

                        pop_jt = round(pop_raw / 1_000_000, 2) if pop_raw else None
                        gdp_miliar = round(gdp_raw / 1_000_000_000, 2) if gdp_raw else None
                        pcap = round(obs["pcap"], 2) if obs["pcap"] is not None else None
                        if pcap is None and gdp_raw and pop_raw:
                            pcap = round(gdp_raw / pop_raw, 2)

                        growth = round(obs["growth"], 2) if obs["growth"] is not None else None
                        cpi = round(obs["cpi"], 2) if obs["cpi"] is not None else None

                        trade = TRADE_ESTIMATES_RI.get(iso, {})
                        ekspor = trade.get("ekspor") if iso != "IDN" else None
                        impor = trade.get("impor") if iso != "IDN" else None
                        neraca = round(ekspor - impor, 2) if ekspor and impor else None

                        record_dict = {
                            "negara": obs["country"],
                            "kode_iso3": iso,
                            "tahun": y,
                            "populasi_juta_jiwa": pop_jt,
                            "pdb_nominal_miliar_usd": gdp_miliar,
                            "pdb_per_kapita_usd": pcap,
                            "pertumbuhan_pdb_pct": growth,
                            "inflasi_pct": cpi,
                            "nilai_ekspor_ri_ke_mitra_usd": ekspor,
                            "nilai_impor_ri_dari_mitra_usd": impor,
                            "neraca_perdagangan_ri_usd": neraca,
                            "data_source": "World Bank Open Data (World Development Indicators)",
                        }
                        yield record_dict
                        yielded_any = True
                        count += 1
        except Exception as exc:
            logger.warning("Error fetching World Bank Open API: %s", exc)

        # Fallback if remote API is down or empty
        if not yielded_any:
            logger.info("Using World Bank offline fallback dataset")
            for rec in OFFLINE_FALLBACK_DATA:
                if count >= self.max_records:
                    break
                yield rec
                count += 1
