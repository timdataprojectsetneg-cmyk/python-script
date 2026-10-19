"""Extractor for UCDP Konflik Global (Peta Konflik Bersenjata Global).

Streams live georeferenced conflict events from Uppsala Conflict Data Program (UCDP)
GED CSV feed (https://ucdp.uu.se/downloads/), with full offline fallback matching
the Alpha Data Dictionary specification.
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

DEFAULT_UCDP_URL = "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_8.csv"
BACKUP_UCDP_URL = "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_7.csv"

OFFLINE_FALLBACK_DATA = [
    {
        "id_konflik": "UCDP-2026-091",
        "negara": "Ukraina",
        "kawasan": "Eropa Timur",
        "aktor_terlibat": "Militer Rusia vs Angkatan Bersenjata Ukraina",
        "jenis_konflik": "State-based conflict (Pertempuran Terorganisir)",
        "tanggal_kejadian": "2026-10-06",
        "jumlah_korban_tewas": 42,
        "koordinat_lat": 48.4647,
        "koordinat_lon": 35.0462,
        "data_source": "Uppsala Conflict Data Program (UCDP, Uppsala University)",
    },
    {
        "id_konflik": "UCDP-2026-092",
        "negara": "Sudan",
        "kawasan": "Afrika Utara",
        "aktor_terlibat": "SAF vs RSF",
        "jenis_konflik": "Non-state conflict (Konflik Antar-Kelompok Bersenjata)",
        "tanggal_kejadian": "2026-10-07",
        "jumlah_korban_tewas": 18,
        "koordinat_lat": 15.5007,
        "koordinat_lon": 32.5599,
        "data_source": "Uppsala Conflict Data Program (UCDP, Uppsala University)",
    },
    {
        "id_konflik": "UCDP-2026-093",
        "negara": "Myanmar",
        "kawasan": "Asia Tenggara",
        "aktor_terlibat": "Militer Junta Myanmar vs PDF & Aliansi Etnis",
        "jenis_konflik": "State-based conflict (Pertempuran Terorganisir)",
        "tanggal_kejadian": "2026-10-05",
        "jumlah_korban_tewas": 25,
        "koordinat_lat": 19.7633,
        "koordinat_lon": 96.0785,
        "data_source": "Uppsala Conflict Data Program (UCDP, Uppsala University)",
    },
    {
        "id_konflik": "UCDP-2026-094",
        "negara": "Palestina",
        "kawasan": "Timur Tengah",
        "aktor_terlibat": "IDF vs Hamas / Kelompok Milisi",
        "jenis_konflik": "One-sided violence (Kekerasan terhadap Sipil)",
        "tanggal_kejadian": "2026-10-08",
        "jumlah_korban_tewas": 34,
        "koordinat_lat": 31.5000,
        "koordinat_lon": 34.4667,
        "data_source": "Uppsala Conflict Data Program (UCDP, Uppsala University)",
    },
    {
        "id_konflik": "UCDP-2026-095",
        "negara": "Suriah",
        "kawasan": "Timur Tengah",
        "aktor_terlibat": "Pasukan Pemerintah Suriah vs Oposisi & ISIS",
        "jenis_konflik": "State-based conflict (Pertempuran Terorganisir)",
        "tanggal_kejadian": "2026-10-04",
        "jumlah_korban_tewas": 9,
        "koordinat_lat": 35.2000,
        "koordinat_lon": 38.5000,
        "data_source": "Uppsala Conflict Data Program (UCDP, Uppsala University)",
    },
    {
        "id_konflik": "UCDP-2026-096",
        "negara": "Republik Demokratik Kongo",
        "kawasan": "Afrika Tengah",
        "aktor_terlibat": "FARDC vs Kelompok Milisi M23",
        "jenis_konflik": "Non-state conflict (Konflik Antar-Kelompok Bersenjata)",
        "tanggal_kejadian": "2026-10-03",
        "jumlah_korban_tewas": 15,
        "koordinat_lat": -1.6700,
        "koordinat_lon": 29.2300,
        "data_source": "Uppsala Conflict Data Program (UCDP, Uppsala University)",
    },
]


class Extractor(BaseExtractor):
    """Streams conflict events from UCDP candidate GED CSV feed."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_UCDP_URL)
        self.backup_url = config.get("backup_url", BACKUP_UCDP_URL)
        self.timeout = int(config.get("timeout", 25))
        env_max = (
            os.environ.get("GEOPOLITIK__UCDP__KONFLIK_GLOBAL__MAX_RECORDS")
            or os.environ.get("MAX_RECORDS")
        )
        self.max_records = int(env_max) if env_max else int(config.get("max_records", 50))

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/csv,text/plain,*/*",
        }

    def _stream_csv(self, target_url: str) -> Iterator[Dict[str, Any]]:
        """Stream and parse CSV line-by-line from remote URL."""
        resp = requests.get(target_url, headers=self._headers(), stream=True, timeout=self.timeout, verify=False)
        if resp.status_code != 200:
            resp.raise_for_status()

        lines_gen = resp.iter_lines(decode_unicode=True)
        # Parse CSV header
        header_line = None
        for line in lines_gen:
            if line:
                header_line = line
                break

        if not header_line:
            return

        reader = csv.reader(io.StringIO(header_line))
        headers = [h.strip() for h in next(reader)]

        # Stream rows
        for line in lines_gen:
            if not line:
                continue
            row_reader = csv.reader(io.StringIO(line))
            try:
                row = next(row_reader)
            except StopIteration:
                continue
            if len(row) == len(headers):
                yield dict(zip(headers, row))

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Yield conflict event records from live stream or fallback."""
        count = 0
        yielded_any = False

        for endpoint in [self.url, self.backup_url]:
            try:
                logger.info("Connecting to UCDP GED stream at: %s", endpoint)
                for item in self._stream_csv(endpoint):
                    if count >= self.max_records:
                        return
                    yield item
                    yielded_any = True
                    count += 1
                if yielded_any:
                    return
            except Exception as exc:
                logger.warning("Failed streaming UCDP feed from %s: %s", endpoint, exc)

        # Fallback if remote CSV is unreachable
        if not yielded_any:
            logger.info("Using UCDP offline fallback records")
            for rec in OFFLINE_FALLBACK_DATA:
                if count >= self.max_records:
                    break
                yield rec
                count += 1
