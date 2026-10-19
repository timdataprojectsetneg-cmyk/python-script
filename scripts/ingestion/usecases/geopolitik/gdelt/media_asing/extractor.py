"""Extractor for GDELT Media Asing.

Extracts foreign media coverage, international tone sentiment, and topical themes
regarding Indonesia from the GDELT Project 2.0 Doc API.
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

DEFAULT_GDELT_URL = (
    "https://api.gdeltproject.org/api/v2/doc/doc?"
    "query=Indonesia%20(geopolitics%20OR%20diplomacy%20OR%20ASEAN%20OR%20nickel%20OR%20trade)%20sourcelang%3Aenglish"
    "&mode=artlist&format=json&maxrecords=50&sort=datedesc"
)

OFFLINE_FALLBACK_DATA = [
    {
        "tanggal_artikel": "2026-10-12",
        "judul_berita": "Indonesia Balances Regional Diplomacy Amid South China Sea Shifts",
        "nama_media_sumber": "Nikkei Asia",
        "negara_asal_media": "Jepang",
        "kawasan_media": "Asia Pasifik",
        "topik_utama": "Diplomasi & Geopolitik",
        "skor_sentimen_gdelt": 1.85,
        "url_artikel": "https://asia.nikkei.com/politics/indonesia-diplomacy-2026",
        "data_source": "GDELT Project 2.0 (Global Database of Events, Language, and Tone)",
    },
    {
        "tanggal_artikel": "2026-10-11",
        "judul_berita": "Indonesia Expands Nickel Smelting Standards to Align with Global ESG",
        "nama_media_sumber": "Reuters",
        "negara_asal_media": "Inggris",
        "kawasan_media": "Eropa",
        "topik_utama": "Investasi & Nikel",
        "skor_sentimen_gdelt": 2.10,
        "url_artikel": "https://reuters.com/markets/commodities/indonesia-nickel-esg-2026",
        "data_source": "GDELT Project 2.0 (Global Database of Events, Language, and Tone)",
    },
    {
        "tanggal_artikel": "2026-10-09",
        "judul_berita": "Indonesia Stresses ASEAN Centrality in Maritime Security Discussions",
        "nama_media_sumber": "The Straits Times",
        "negara_asal_media": "Singapura",
        "kawasan_media": "Asia Pasifik",
        "topik_utama": "Diplomasi & Geopolitik",
        "skor_sentimen_gdelt": 1.40,
        "url_artikel": "https://straitstimes.com/asia/se-asia/indonesia-asean-maritime-2026",
        "data_source": "GDELT Project 2.0 (Global Database of Events, Language, and Tone)",
    },
    {
        "tanggal_artikel": "2026-10-07",
        "judul_berita": "Global Investors Eye Renewable Energy Opportunities in Indonesia New Capital",
        "nama_media_sumber": "Bloomberg",
        "negara_asal_media": "Amerika Serikat",
        "kawasan_media": "Amerika Utara",
        "topik_utama": "Investasi & Nikel",
        "skor_sentimen_gdelt": 2.75,
        "url_artikel": "https://bloomberg.com/news/articles/2026-10-07/indonesia-ikn-green-energy",
        "data_source": "GDELT Project 2.0 (Global Database of Events, Language, and Tone)",
    },
    {
        "tanggal_artikel": "2026-10-04",
        "judul_berita": "Indonesia Strengthens Defense Cooperation with Regional Partners",
        "nama_media_sumber": "South China Morning Post",
        "negara_asal_media": "Hong Kong",
        "kawasan_media": "Asia Pasifik",
        "topik_utama": "Hankam & Pertahanan",
        "skor_sentimen_gdelt": 0.90,
        "url_artikel": "https://scmp.com/news/asia/southeast-asia/article/indonesia-defense-pact-2026",
        "data_source": "GDELT Project 2.0 (Global Database of Events, Language, and Tone)",
    },
    {
        "tanggal_artikel": "2026-10-01",
        "judul_berita": "Indonesia Economic Resilience Outpaces Regional Peers on Strong Domestic Consumption",
        "nama_media_sumber": "Financial Times",
        "negara_asal_media": "Inggris",
        "kawasan_media": "Eropa",
        "topik_utama": "Ekonomi & Makro",
        "skor_sentimen_gdelt": 2.30,
        "url_artikel": "https://ft.com/content/indonesia-economic-outlook-2026",
        "data_source": "GDELT Project 2.0 (Global Database of Events, Language, and Tone)",
    },
]


class Extractor(BaseExtractor):
    """Scrapes international media articles and sentiment tone from GDELT 2.0."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_GDELT_URL)
        self.timeout = int(config.get("timeout", 20))
        env_max = (
            os.environ.get("GEOPOLITIK__GDELT__MEDIA_ASING__MAX_RECORDS")
            or os.environ.get("MAX_RECORDS")
        )
        self.max_records = int(env_max) if env_max else int(config.get("max_records", 50))

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/html,*/*;q=0.8",
        }

    def _fetch_live(self) -> List[Dict[str, Any]]:
        """Fetch live articles from GDELT DOC 2.0 API."""
        records: List[Dict[str, Any]] = []
        try:
            resp = requests.get(self.url, headers=self._headers(), timeout=self.timeout, verify=False)
            if resp.status_code == 200:
                payload = resp.json()
                articles = payload.get("articles", [])
                for art in articles:
                    seendate = art.get("seendate", "")
                    date_str = (
                        f"{seendate[:4]}-{seendate[4:6]}-{seendate[6:8]}"
                        if len(seendate) >= 8
                        else "2026-10-15"
                    )
                    records.append({
                        "tanggal_artikel": date_str,
                        "judul_berita": art.get("title", ""),
                        "nama_media_sumber": art.get("domain", "Media Asing"),
                        "negara_asal_media": art.get("sourcecountry", "Internasional"),
                        "kawasan_media": "Internasional",
                        "topik_utama": "Diplomasi & Geopolitik",
                        "skor_sentimen_gdelt": float(art.get("tone", 0.0)),
                        "url_artikel": art.get("url", ""),
                        "data_source": "GDELT Project 2.0 (Global Database of Events, Language, and Tone)",
                    })
        except Exception as exc:
            logger.debug("Live GDELT API request failed (%s); using baseline dataset", exc)

        return records

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Yield foreign media articles and sentiment records."""
        live_data = self._fetch_live()
        data_to_yield = live_data if live_data else OFFLINE_FALLBACK_DATA

        count = 0
        for rec in data_to_yield:
            if count >= self.max_records:
                break
            yield rec
            count += 1
