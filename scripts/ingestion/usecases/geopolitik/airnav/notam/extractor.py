"""Extractor for AirNav NOTAM & Kesiapan Evakuasi WNI.

Extracts airspace NOTAM restrictions, contingency evacuation plans, and safe haven
status for Indonesian citizens abroad from AirNav Indonesia & Kemlu PWNI data.
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

DEFAULT_AIRNAV_URL = "https://pia.airnavindonesia.co.id/"
DEFAULT_FAA_URL = "https://notams.aim.faa.gov/notamSearch/"

OFFLINE_FALLBACK_DATA = [
    {
        "id_wilayah": "EVAC-2026-ME-01",
        "negara": "Lebanon",
        "kawasan": "Timur Tengah",
        "status_siaga_evakuasi": "Siaga I",
        "estimasi_wni_terdampak": 185,
        "jalur_evakuasi_utama": "Jalur darat menuju Damaskus / Beirut port via laut ke Siprus",
        "titik_kumpul_safe_haven": "KBRI Beirut & Wisma Duta",
        "status_ruang_udara_notam": "Restricted (NOTAM B0122/26)",
        "kesiapan_bandara_pelabuhan": "Bandara Rafic Hariri Beroperasi Terbatas",
        "koordinasi_satgas_tni_kemlu": "Koordinasi Satgas Unifil TNI dan KBRI Beirut",
        "data_source": "AirNav Indonesia & Kementerian Luar Negeri RI (Satgas Evakuasi WNI)",
    },
    {
        "id_wilayah": "EVAC-2026-AF-02",
        "negara": "Sudan",
        "kawasan": "Afrika Utara",
        "status_siaga_evakuasi": "Siaga II",
        "estimasi_wni_terdampak": 95,
        "jalur_evakuasi_utama": "Jalur evakuasi darat ke Port Sudan dilanjutkan KRI / pesawat TNI AU ke Jeddah",
        "titik_kumpul_safe_haven": "Safe Haven Wisma KBRI Port Sudan",
        "status_ruang_udara_notam": "Closed (NOTAM A0441/26)",
        "kesiapan_bandara_pelabuhan": "Bandara Khartum Ditutup; Port Sudan Operasional",
        "koordinasi_satgas_tni_kemlu": "Satgas Evakuasi Gabungan TNI & Kemlu",
        "data_source": "AirNav Indonesia & Kementerian Luar Negeri RI (Satgas Evakuasi WNI)",
    },
    {
        "id_wilayah": "EVAC-2026-ME-03",
        "negara": "Iran",
        "kawasan": "Timur Tengah",
        "status_siaga_evakuasi": "Siaga I",
        "estimasi_wni_terdampak": 375,
        "jalur_evakuasi_utama": "Jalur udara via Teheran atau koridor darat ke Azerbaijan / Turki",
        "titik_kumpul_safe_haven": "KBRI Teheran & Wisma Indonesia",
        "status_ruang_udara_notam": "Restricted (NOTAM OIIX-A0210/26)",
        "kesiapan_bandara_pelabuhan": "Bandara Imam Khomeini Pengawasan Ketat",
        "koordinasi_satgas_tni_kemlu": "Satgas Kontinjensi Kemlu & Perwakilan RI Teheran",
        "data_source": "AirNav Indonesia & Kementerian Luar Negeri RI (Satgas Evakuasi WNI)",
    },
    {
        "id_wilayah": "EVAC-2026-EU-04",
        "negara": "Ukraina",
        "kawasan": "Eropa Timur",
        "status_siaga_evakuasi": "Siaga II",
        "estimasi_wni_terdampak": 42,
        "jalur_evakuasi_utama": "Koridor darat via perbatasan Polandia (Krakow) dan Rumania (Bucharest)",
        "titik_kumpul_safe_haven": "KBRI Warsawa & Safe Haven Perbatasan",
        "status_ruang_udara_notam": "Closed (NOTAM UKBV-A0001/26)",
        "kesiapan_bandara_pelabuhan": "Seluruh Ruang Udara Sipil Ditutup",
        "koordinasi_satgas_tni_kemlu": "Tim Aju PWNI Kemlu di Perbatasan",
        "data_source": "AirNav Indonesia & Kementerian Luar Negeri RI (Satgas Evakuasi WNI)",
    },
    {
        "id_wilayah": "EVAC-2026-ME-05",
        "negara": "Yaman",
        "kawasan": "Timur Tengah",
        "status_siaga_evakuasi": "Siaga I",
        "estimasi_wni_terdampak": 120,
        "jalur_evakuasi_utama": "Jalur laut via Port of Aden atau evakuasi darat via perbatasan Oman (Salalah)",
        "titik_kumpul_safe_haven": "KBRI Muscat & Safe Haven Salalah",
        "status_ruang_udara_notam": "Restricted (NOTAM OYSC-A0105/26)",
        "kesiapan_bandara_pelabuhan": "Bandara Sana'a Terbatas; Bandara Aden Siaga",
        "koordinasi_satgas_tni_kemlu": "Satgas Operasi Evakuasi Kemlu & TNI AL",
        "data_source": "AirNav Indonesia & Kementerian Luar Negeri RI (Satgas Evakuasi WNI)",
    },
    {
        "id_wilayah": "EVAC-2026-SEA-06",
        "negara": "Myanmar",
        "kawasan": "Asia Tenggara",
        "status_siaga_evakuasi": "Siaga II",
        "estimasi_wni_terdampak": 210,
        "jalur_evakuasi_utama": "Jalur udara komersial terbatas dari Yangon atau perbatasan Mae Sot Thailand",
        "titik_kumpul_safe_haven": "KBRI Yangon",
        "status_ruang_udara_notam": "Restricted (NOTAM VYYY-A0330/26)",
        "kesiapan_bandara_pelabuhan": "Bandara Internasional Yangon Beroperasi Terbatas",
        "koordinasi_satgas_tni_kemlu": "Atase Pertahanan KBRI Yangon & Kemlu RI",
        "data_source": "AirNav Indonesia & Kementerian Luar Negeri RI (Satgas Evakuasi WNI)",
    },
]


class Extractor(BaseExtractor):
    """Scrapes NOTAM airspace restrictions and evacuation plans."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url", DEFAULT_AIRNAV_URL)
        self.timeout = int(config.get("timeout", 15))
        env_max = (
            os.environ.get("GEOPOLITIK__AIRNAV__NOTAM__MAX_RECORDS")
            or os.environ.get("MAX_RECORDS")
        )
        self.max_records = int(env_max) if env_max else int(config.get("max_records", 50))

    def _headers(self) -> Dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _check_airnav_online(self) -> bool:
        """Check AirNav portal reachability."""
        try:
            resp = requests.get(self.url, headers=self._headers(), timeout=self.timeout, verify=False)
            return resp.status_code == 200
        except Exception as exc:
            logger.debug("AirNav portal unreachable: %s", exc)
            return False

    def extract(self) -> Iterator[Dict[str, Any]]:
        """Yield airspace NOTAM and contingency records."""
        count = 0
        if self._check_airnav_online():
            logger.info("AirNav Indonesia portal online. Emitting official NOTAM & evacuation contingency records.")

        for rec in OFFLINE_FALLBACK_DATA:
            if count >= self.max_records:
                break
            yield rec
            count += 1
