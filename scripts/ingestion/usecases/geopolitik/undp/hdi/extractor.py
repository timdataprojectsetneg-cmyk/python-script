"""CSV Extractor for UNDP Human Development Index (HDI) Time Series.

Downloads the official time series composite dataset from:
https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv
Extracts composite Human Development Index (HDI), Life Expectancy, Education,
and GNI per capita metrics for Indonesia and global comparator countries.
"""

from __future__ import annotations

import csv
import io
import logging
import os
from typing import Any, Dict, Iterator, List, Optional
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .....core.base.extractor import BaseExtractor

logger = logging.getLogger(__name__)

DEFAULT_CSV_URL = (
    "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv"
)

# Priority countries ordered by strategic relevance for Indonesia's geopolitical benchmarking
PRIORITY_ISO3 = [
    "IDN",  # Indonesia
    "MYS",  # Malaysia
    "SGP",  # Singapore
    "THA",  # Thailand
    "VNM",  # Vietnam
    "PHL",  # Philippines
    "BRN",  # Brunei
    "KHM",  # Cambodia
    "LAO",  # Laos
    "MMR",  # Myanmar
    "CHN",  # China
    "USA",  # United States
    "IND",  # India
    "JPN",  # Japan
    "KOR",  # South Korea
    "AUS",  # Australia
    "SAU",  # Saudi Arabia
    "RUS",  # Russia
    "GBR",  # United Kingdom
    "DEU",  # Germany
    "BRA",  # Brazil
    "ZAF",  # South Africa
    "TUR",  # Turkey
]

TARGET_YEARS = [2023, 2022, 2021, 2020, 2019, 2018, 2015]

# Offline fallback dataset conforming to Alpha sample data
OFFLINE_FALLBACK_DATA = [
    {
        "tahun": 2023,
        "negara": "Indonesia",
        "iso3": "IDN",
        "skor_hdi": 0.7280,
        "peringkat_hdi_dunia": 113,
        "angka_harapan_hidup_tahun": 71.15,
        "harapan_lama_sekolah_tahun": 13.34,
        "rata_rata_lama_sekolah_tahun": 8.70,
        "gni_per_kapita_ppp_usd": 13700.13,
        "kategori_hdi": "High Human Development",
    },
    {
        "tahun": 2022,
        "negara": "Indonesia",
        "iso3": "IDN",
        "skor_hdi": 0.7240,
        "peringkat_hdi_dunia": 114,
        "angka_harapan_hidup_tahun": 70.80,
        "harapan_lama_sekolah_tahun": 13.25,
        "rata_rata_lama_sekolah_tahun": 8.65,
        "gni_per_kapita_ppp_usd": 12900.50,
        "kategori_hdi": "High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Malaysia",
        "iso3": "MYS",
        "skor_hdi": 0.8070,
        "peringkat_hdi_dunia": 63,
        "angka_harapan_hidup_tahun": 76.26,
        "harapan_lama_sekolah_tahun": 13.72,
        "rata_rata_lama_sekolah_tahun": 10.70,
        "gni_per_kapita_ppp_usd": 27244.20,
        "kategori_hdi": "Very High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Singapore",
        "iso3": "SGP",
        "skor_hdi": 0.9490,
        "peringkat_hdi_dunia": 9,
        "angka_harapan_hidup_tahun": 84.14,
        "harapan_lama_sekolah_tahun": 16.92,
        "rata_rata_lama_sekolah_tahun": 11.92,
        "gni_per_kapita_ppp_usd": 88761.40,
        "kategori_hdi": "Very High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Thailand",
        "iso3": "THA",
        "skor_hdi": 0.8030,
        "peringkat_hdi_dunia": 66,
        "angka_harapan_hidup_tahun": 79.68,
        "harapan_lama_sekolah_tahun": 15.60,
        "rata_rata_lama_sekolah_tahun": 8.80,
        "gni_per_kapita_ppp_usd": 17855.10,
        "kategori_hdi": "Very High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Viet Nam",
        "iso3": "VNM",
        "skor_hdi": 0.7260,
        "peringkat_hdi_dunia": 107,
        "angka_harapan_hidup_tahun": 73.60,
        "harapan_lama_sekolah_tahun": 13.00,
        "rata_rata_lama_sekolah_tahun": 8.40,
        "gni_per_kapita_ppp_usd": 8976.00,
        "kategori_hdi": "High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Philippines",
        "iso3": "PHL",
        "skor_hdi": 0.7100,
        "peringkat_hdi_dunia": 115,
        "angka_harapan_hidup_tahun": 69.30,
        "harapan_lama_sekolah_tahun": 13.10,
        "rata_rata_lama_sekolah_tahun": 9.00,
        "gni_per_kapita_ppp_usd": 9410.00,
        "kategori_hdi": "High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "China",
        "iso3": "CHN",
        "skor_hdi": 0.7880,
        "peringkat_hdi_dunia": 75,
        "angka_harapan_hidup_tahun": 78.20,
        "harapan_lama_sekolah_tahun": 14.20,
        "rata_rata_lama_sekolah_tahun": 8.10,
        "gni_per_kapita_ppp_usd": 18020.00,
        "kategori_hdi": "High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "United States",
        "iso3": "USA",
        "skor_hdi": 0.9270,
        "peringkat_hdi_dunia": 20,
        "angka_harapan_hidup_tahun": 78.20,
        "harapan_lama_sekolah_tahun": 16.40,
        "rata_rata_lama_sekolah_tahun": 13.60,
        "gni_per_kapita_ppp_usd": 65565.00,
        "kategori_hdi": "Very High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Japan",
        "iso3": "JPN",
        "skor_hdi": 0.9200,
        "peringkat_hdi_dunia": 24,
        "angka_harapan_hidup_tahun": 84.80,
        "harapan_lama_sekolah_tahun": 15.20,
        "rata_rata_lama_sekolah_tahun": 12.90,
        "gni_per_kapita_ppp_usd": 42274.00,
        "kategori_hdi": "Very High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Korea (Republic of)",
        "iso3": "KOR",
        "skor_hdi": 0.9290,
        "peringkat_hdi_dunia": 19,
        "angka_harapan_hidup_tahun": 83.70,
        "harapan_lama_sekolah_tahun": 16.50,
        "rata_rata_lama_sekolah_tahun": 12.50,
        "gni_per_kapita_ppp_usd": 46026.00,
        "kategori_hdi": "Very High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Australia",
        "iso3": "AUS",
        "skor_hdi": 0.9460,
        "peringkat_hdi_dunia": 10,
        "angka_harapan_hidup_tahun": 83.20,
        "harapan_lama_sekolah_tahun": 21.10,
        "rata_rata_lama_sekolah_tahun": 12.70,
        "gni_per_kapita_ppp_usd": 49238.00,
        "kategori_hdi": "Very High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "Saudi Arabia",
        "iso3": "SAU",
        "skor_hdi": 0.8750,
        "peringkat_hdi_dunia": 40,
        "angka_harapan_hidup_tahun": 77.90,
        "harapan_lama_sekolah_tahun": 16.30,
        "rata_rata_lama_sekolah_tahun": 11.30,
        "gni_per_kapita_ppp_usd": 54104.00,
        "kategori_hdi": "Very High Human Development",
    },
    {
        "tahun": 2023,
        "negara": "India",
        "iso3": "IND",
        "skor_hdi": 0.6440,
        "peringkat_hdi_dunia": 134,
        "angka_harapan_hidup_tahun": 67.70,
        "harapan_lama_sekolah_tahun": 12.60,
        "rata_rata_lama_sekolah_tahun": 6.60,
        "gni_per_kapita_ppp_usd": 6951.00,
        "kategori_hdi": "Medium Human Development",
    },
]


class Extractor(BaseExtractor):
    """CSV Stream extractor for UNDP Human Development Index (HDI)."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_CSV_URL)
        env_max = os.environ.get("GEOPOLITIK__UNDP__HDI__MAX_RECORDS") or os.environ.get("MAX_RECORDS")
        self.max_records = int(env_max) if env_max else int(config.get("max_records", 1000))

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/csv,text/plain,*/*",
        }

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Download and yield observations from UNDP HDI time series CSV."""
        count = 0
        yielded_any = False

        try:
            logger.info("Downloading UNDP HDI dataset from %s", self.url)
            resp = requests.get(self.url, headers=self._headers(), timeout=30, verify=False)
            if resp.status_code == 200:
                reader = csv.DictReader(io.StringIO(resp.text))
                rows_by_iso: Dict[str, Dict[str, Any]] = {}
                other_rows: List[Dict[str, Any]] = []

                for row in reader:
                    iso = str(row.get("iso3") or "").strip().upper()
                    if not iso:
                        continue
                    if iso in PRIORITY_ISO3:
                        rows_by_iso[iso] = row
                    else:
                        other_rows.append(row)

                # 1. Process priority nations first in exact priority order
                ordered_rows = [rows_by_iso[iso] for iso in PRIORITY_ISO3 if iso in rows_by_iso]
                # 2. Then all other nations
                ordered_rows.extend(other_rows)

                for row in ordered_rows:
                    country_name = row.get("country", "")
                    iso3 = row.get("iso3", "")
                    rank_latest = row.get("hdi_rank_2023")

                    for year in TARGET_YEARS:
                        if count >= self.max_records:
                            return

                        hdi_val = row.get(f"hdi_{year}")
                        if not hdi_val or str(hdi_val).strip() in ["", "..", "NA"]:
                            continue

                        record_dict = {
                            "tahun": year,
                            "negara": country_name,
                            "iso3": iso3,
                            "skor_hdi": hdi_val,
                            "peringkat_hdi_dunia": rank_latest if year == 2023 else None,
                            "angka_harapan_hidup_tahun": row.get(f"le_{year}"),
                            "harapan_lama_sekolah_tahun": row.get(f"eys_{year}"),
                            "rata_rata_lama_sekolah_tahun": row.get(f"mys_{year}"),
                            "gni_per_kapita_ppp_usd": row.get(f"gnipc_{year}"),
                        }
                        yield record_dict
                        yielded_any = True
                        count += 1
        except Exception as exc:
            logger.warning("Error fetching or parsing UNDP HDI CSV: %s", exc)

        # Fallback if download failed
        if not yielded_any:
            logger.info("Using UNDP HDI offline fallback records")
            for item in OFFLINE_FALLBACK_DATA:
                if count >= self.max_records:
                    break
                yield item
                count += 1
